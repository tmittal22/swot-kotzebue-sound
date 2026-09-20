"""Spatial hydrographs from SWOT node WSE, after Thurman et al. (2025, GRL,
10.1029/2024GL113875).

Method, and where it departs from the paper:

  1. Quality filter node WSE (node_q<=1, ice_clim_f==0) -- see swotkot.
  2. Reference long profile: per node, the median WSE over all revisits, with
     revisits more than `mad_k` median-absolute-deviations from that median
     rejected first.
  3. An along-river running median (`win_km`) on the reference profile, to
     remove residual node-to-node measurement noise while preserving the real
     downstream gradient.
  4. For one (cycle, pass) snapshot, the WSE anomaly is
     eta(x) = WSE(x) - reference(x), smoothed along-river the same way.

  Thurman additionally apply a Bayes reconstruction that fills poor-quality
  nodes using the SWOT river processor's height covariance model.  That model
  is not distributed with the public vector product, so this implementation
  leaves gaps as gaps and reports the observed fraction with every profile.
  The consequence is noisier anomalies and no interpolation across long gaps;
  it never invents a measurement.

Physical check available on the reference profile: water flows downhill, so
reference WSE must increase monotonically with distance upstream.  Any
violation beyond measurement noise is a data or network-topology problem, not
hydrology.  `check_monotonic` quantifies it.
"""
import numpy as np
import pandas as pd


def reference_profile(nodes, win_km=5.0, mad_k=4.0, min_obs=5):
    """Median long profile per node, outlier-rejected, then spatially smoothed."""
    g = nodes.groupby("node_id")
    med = g.wse.median().rename("wse_med")
    mad = (g.wse.apply(lambda s: (s - s.median()).abs().median())
           .rename("wse_mad"))
    stat = pd.concat([med, mad], axis=1)
    j = nodes.join(stat, on="node_id")
    scale = j.wse_mad.replace(0, np.nan).fillna(j.wse_mad.median())
    keep = (j.wse - j.wse_med).abs() <= mad_k * 1.4826 * scale

    clean = nodes[keep.values]
    ref = (clean.groupby("node_id")
           .agg(wse_ref_raw=("wse", "median"),
                wse_mad=("wse", lambda s: (s - s.median()).abs().median()),
                width_med=("width", "median"),
                n_obs=("wse", "size"),
                dist_out_km=("dist_out_km", "first"),
                river=("river", "first")))
    ref = ref[ref.n_obs >= min_obs].reset_index()
    # Smooth PER RIVER.  dist_out is distance to that river's own outlet, so
    # different rivers reuse the same values; smoothing the globally sorted
    # array blends Kobuk, Noatak and Selawik nodes at equal dist_out.  The
    # monotonicity check in check_monotonic is what surfaces this if it breaks
    # again.
    out = []
    for _, g in ref.groupby("river", sort=False):
        g = g.sort_values("dist_out_km").copy()
        g["wse_ref"] = _running_median_km(g.dist_out_km.values,
                                          g.wse_ref_raw.values, win_km)
        out.append(g)
    return pd.concat(out, ignore_index=True)


def _running_median_km(x, y, win_km):
    """Running median over a fixed along-river window, not a fixed node count,
    so it behaves the same across gaps and variable node spacing."""
    out = np.full(len(y), np.nan)
    lo = np.searchsorted(x, x - win_km / 2, side="left")
    hi = np.searchsorted(x, x + win_km / 2, side="right")
    for i in range(len(y)):
        seg = y[lo[i]:hi[i]]
        seg = seg[np.isfinite(seg)]
        if seg.size:
            out[i] = np.median(seg)
    return out


def check_monotonic(ref, tol_m=0.0):
    """Water flows downhill: reference WSE must rise going upstream.

    Returns the fraction of adjacent node pairs that violate this beyond
    `tol_m`, and the total reversed drop, per river.
    """
    rows = []
    for riv, g in ref.groupby("river"):
        g = g.sort_values("dist_out_km")
        d = np.diff(g.wse_ref.values)          # upstream-positive difference
        d = d[np.isfinite(d)]
        bad = d < -tol_m
        rows.append(dict(river=riv, n_pairs=len(d),
                         frac_reversed=float(bad.mean()),
                         total_drop_m=float(-d[bad].sum()) if bad.any() else 0.0,
                         worst_reversal_m=float(-d.min()) if len(d) else np.nan,
                         total_rise_m=float(g.wse_ref.max() - g.wse_ref.min())))
    return pd.DataFrame(rows)


def snapshots(nodes, river, min_nodes=200, min_span_km=80):
    """Index the (cycle, pass) overpasses that see enough of one river."""
    s = nodes[nodes.river == river]
    g = s.groupby(["cycle_id", "pass_id"]).agg(
        n_nodes=("node_id", "nunique"),
        d_min=("dist_out_km", "min"), d_max=("dist_out_km", "max"),
        time=("time", "median"))
    g["span_km"] = g.d_max - g.d_min
    g = g[(g.n_nodes >= min_nodes) & (g.span_km >= min_span_km)]
    return g.reset_index().sort_values("time")


def anomaly(nodes, ref, cycle, pass_id, river, win_km=5.0,
            max_dark=0.5, min_width_m=80.0, sigma_k=4.0, eta_floor_m=1.0):
    """eta(x) for one overpass: WSE minus the reference long profile.

    Three filters beyond the node quality flag, each added because the raw
    profiles showed a specific artefact:

    max_dark      Dark water (specular or vegetated returns) biases KaRIn
                  heights; profiles showed metre-scale spikes at high
                  dark_frac.
    min_width_m   SWOT is specified for rivers wider than 50-100 m.  The
                  upper Noatak narrows below that and its anomalies were
                  dominated by retrieval noise, not stage.
    sigma_k       A point is rejected if it sits more than sigma_k robust
                  standard deviations from that node's own long-term spread.
                  The floor keeps genuinely large but real flood anomalies on
                  quiet nodes.
    """
    s = nodes[(nodes.river == river) & (nodes.cycle_id == cycle) &
              (nodes.pass_id == pass_id)]
    if "dark_frac" in s.columns:
        s = s[s.dark_frac.fillna(0) <= max_dark]
    m = s.merge(ref[["node_id", "wse_ref", "wse_mad", "width_med", "dist_out_km"]],
                on="node_id", suffixes=("", "_ref"))
    m = m[m.width_med >= min_width_m]
    m = m.sort_values("dist_out_km").copy()
    m["eta_raw"] = m.wse - m.wse_ref
    lim = np.maximum(eta_floor_m, sigma_k * 1.4826 * m.wse_mad.fillna(0))
    m["n_rejected"] = int((m.eta_raw.abs() > lim).sum())
    m.loc[m.eta_raw.abs() > lim, "eta_raw"] = np.nan
    m["eta"] = _running_median_km(m.dist_out_km.values, m.eta_raw.values, win_km)
    return m


def celerity_from_pair(eta_a, t_a, eta_b, t_b, min_shift_km=1.0):
    """Wave celerity from two overpasses of the same river.

    Cross-correlate the two anomaly profiles on a common along-river grid and
    take the lag that maximises correlation.  Positive shift means the pattern
    moved downstream (towards smaller dist_out) between t_a and t_b.

    This is the SWOT-only variant Thurman et al. flag as possible but do not
    use -- they estimate celerity from one SWOT profile plus one gauge peak.
    Here it is applied where the two overpasses are close enough in time that
    the wave has not decayed, and it is validated against a two-gauge lagged
    cross-correlation on the Kobuk.
    """
    lo = max(eta_a.dist_out_km.min(), eta_b.dist_out_km.min())
    hi = min(eta_a.dist_out_km.max(), eta_b.dist_out_km.max())
    if hi - lo < 40:
        return None
    grid = np.arange(lo, hi, 0.5)
    fa = np.interp(grid, eta_a.dist_out_km, eta_a.eta, left=np.nan, right=np.nan)
    fb = np.interp(grid, eta_b.dist_out_km, eta_b.eta, left=np.nan, right=np.nan)
    ok = np.isfinite(fa) & np.isfinite(fb)
    if ok.sum() < 100:
        return None
    fa, fb = fa[ok] - np.nanmean(fa[ok]), fb[ok] - np.nanmean(fb[ok])
    n = len(fa)
    maxlag = int(min(n // 3, 400))
    lags = np.arange(-maxlag, maxlag + 1)
    cc = np.array([np.corrcoef(fa[max(0, l):n + min(0, l)],
                               fb[max(0, -l):n - max(0, l)])[0, 1]
                   for l in lags])
    k = int(np.nanargmax(cc))
    shift_km = lags[k] * 0.5
    dt_s = (t_b - t_a).total_seconds()
    if abs(shift_km) < min_shift_km or dt_s == 0:
        return None
    return dict(shift_km=shift_km, dt_hr=dt_s / 3600,
                celerity_ms=abs(shift_km) * 1000 / abs(dt_s),
                corr=float(cc[k]), n_common=int(ok.sum()))
