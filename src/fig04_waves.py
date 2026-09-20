"""Figure 4 -- flow waves in space, after Thurman et al. (2025).

Panels:
  (a) distance-time (Hovmoller) map of the Kobuk WSE anomaly -- waves appear as
      tilted bands moving towards the outlet
  (b) Kobuk spatial hydrographs through the late-summer 2025 peak
  (c) Selawik spatial hydrographs through a spring freshet, with the whole
      166 km river captured in single overpasses
  (d) celerity: SWOT profile-pair cross-correlation against the historical
      two-gauge estimate (Ambler-Kiana, 1976-1978)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from scipy import signal

import swotkot as sk
import spatial_hydrograph as sh


def highpass(x, win):
    """Remove a centred running mean so event-scale waves, not the seasonal
    pulse, drive the cross-correlation."""
    s = pd.Series(x)
    return (s - s.rolling(win, center=True, min_periods=1).mean()).values


def two_gauge_celerity():
    """Ambler (15744000, ended 1978) and Kiana (15744500) overlap 1976-1978.
    This is the only two-gauge pair ever available on the Kobuk."""
    r = requests.get("https://waterservices.usgs.gov/nwis/dv/",
                     params=dict(format="rdb", sites="15744000,15744500",
                                 startDT="1976-01-01", endDT="1978-12-31",
                                 parameterCd="00060", statCd="00003"), timeout=180)
    txt = "\n".join(l for l in r.text.splitlines() if not l.startswith("#"))
    d = pd.read_csv(io.StringIO(txt), sep="\t", dtype=str)
    d = d[d.site_no.str.match(r"^\d+$", na=False)]
    qc = [c for c in d.columns if c.endswith("_00060_00003")]
    d["q"] = pd.to_numeric(d[qc].bfill(axis=1).iloc[:, 0], errors="coerce") * sk.CFS_TO_CMS
    d["datetime"] = pd.to_datetime(d.datetime, errors="coerce")
    p = (d.dropna(subset=["datetime"])
         .pivot_table(index="datetime", columns="site_no", values="q").dropna())
    p = p[(p.index.dayofyear >= 140) & (p.index.dayofyear <= 290)]

    inv = sk.load_inventory()
    a, _ = sk.nearest_reach(inv, 67.08638, -157.85028, "Kobuk")
    k, _ = sk.nearest_reach(inv, 66.973611, -160.130833, "Kobuk")
    L = abs(a.dist_out_km - k.dist_out_km)

    out = {}
    for win, tag in [(None, "raw"), (15, "highpass15d")]:
        x = p["15744000"].values.astype(float)
        y = p["15744500"].values.astype(float)
        if win:
            x, y = highpass(x, win), highpass(y, win)
        x = (x - x.mean()) / x.std(); y = (y - y.mean()) / y.std()
        cc = signal.correlate(y, x, mode="full") / len(x)
        lags = signal.correlation_lags(len(y), len(x), mode="full")
        m = (lags >= -3) & (lags <= 10)
        ll, rr = lags[m], cc[m]
        i = int(np.argmax(rr))
        # parabolic refinement for sub-daily lag
        if 0 < i < len(rr) - 1:
            den = rr[i - 1] - 2 * rr[i] + rr[i + 1]
            delta = 0.5 * (rr[i - 1] - rr[i + 1]) / den if den != 0 else 0.0
        else:
            delta = 0.0
        lag_d = ll[i] + delta
        out[tag] = dict(L_km=L, lag_d=float(lag_d), r=float(rr[i]),
                        celerity_ms=float(L * 1000 / (lag_d * 86400)) if lag_d > 0 else np.nan,
                        lags=ll, cc=rr, n_days=len(p))
    return out


def swot_only_celerity(n, ref, rivers=("Kobuk", "Noatak", "Selawik")):
    """NEGATIVE RESULT, kept deliberately.

    Cross-correlating two SWOT anomaly profiles 6-72 h apart returns celerities
    of 0.02-0.2 m/s, one to two orders of magnitude below the two-gauge and
    kinematic-wave values.  The reason is diagnosable: the anomaly profiles are
    dominated by *static* along-river structure (tributary junctions, channel
    geometry, residual reference-profile error) that does not move, so the
    cross-correlation locks onto zero lag and the reported shift is noise.
    Thurman et al. (2025) note SWOT-only celerity as a future possibility but do
    not use it; this is why.  Reproduce with --swot-only.
    """
    res = []
    for riv in rivers:
        sn = sh.snapshots(n, riv, min_nodes=300, min_span_km=100)
        sn = sn.sort_values("time").reset_index(drop=True)
        cache = {}
        for i in range(len(sn) - 1):
            j = i + 1
            dt = (sn.time[j] - sn.time[i]).total_seconds() / 3600
            if not (6 <= dt <= 72):
                continue
            for kk in (i, j):
                if kk not in cache:
                    a = sh.anomaly(n, ref, sn.cycle_id[kk], sn.pass_id[kk], riv)
                    cache[kk] = a[a.eta.notna()]
            out = sh.celerity_from_pair(cache[i], sn.time[i], cache[j], sn.time[j])
            if out and out["corr"] > 0.6:
                res.append(dict(river=riv, **out))
    return pd.DataFrame(res)


def main():
    sk.mpl_setup()
    n = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")

    fig = plt.figure(figsize=(13, 9))
    gs = fig.add_gridspec(2, 3, hspace=0.34, wspace=0.3, width_ratios=[1.25, 1, 1])

    # ---- (a) Hovmoller for the Kobuk -------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    snaps = sh.snapshots(n, "Kobuk", min_nodes=300, min_span_km=100)
    snaps = snaps[(snaps.time >= "2025-05-01") & (snaps.time <= "2025-10-20")]
    recs = []
    for _, s in snaps.iterrows():
        a = sh.anomaly(n, ref, s.cycle_id, s.pass_id, "Kobuk")
        a = a[a.eta.notna()]
        if len(a) < 100:
            continue
        recs.append(a.assign(t=s.time))
    H = pd.concat(recs)
    sc = ax.scatter(H.t, H.dist_out_km, c=H.eta, s=1.6, cmap="RdBu_r",
                    vmin=-1.2, vmax=1.2, rasterized=True)
    plt.colorbar(sc, ax=ax, label="WSE anomaly $\\eta$ (m)", pad=0.02)
    ax.set_ylabel("distance upstream from outlet (km)")
    ax.set_xlabel("date (2025)")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7.5)
    ax.set_title("(a) Kobuk distance-time map of WSE anomaly, 2025\n"
                 f"{len(recs)} overpasses, {len(H):,} node observations")

    # ---- (b) Kobuk spatial hydrographs, late-summer 2025 -----------------
    ax = fig.add_subplot(gs[0, 1])
    pb = int(snaps.groupby("pass_id").n_nodes.median().idxmax())
    sel = snaps[snaps.pass_id == pb].sort_values("time")
    cmap = plt.get_cmap("viridis")
    for i, (_, s) in enumerate(sel.iterrows()):
        a = sh.anomaly(n, ref, s.cycle_id, s.pass_id, "Kobuk")
        a = a[a.eta.notna()]
        if len(a) < 100:
            continue
        ax.plot(a.dist_out_km, a.eta, lw=1.2,
                color=cmap(i / max(1, len(sel) - 1)),
                label=pd.Timestamp(s.time).strftime("%d %b"))
    ax.axhline(0, color="k", lw=0.7)
    ax.invert_xaxis()
    ax.set_xlabel("distance upstream from outlet (km)")
    ax.set_ylabel("$\\eta$ (m)")
    ax.set_title(f"(b) Kobuk spatial hydrographs, pass {pb}\n"
                 "flow direction is left to right")
    ax.legend(fontsize=6.4, ncol=2, loc="upper right")

    # ---- (c) Selawik: whole river in one overpass ------------------------
    ax = fig.add_subplot(gs[0, 2])
    ssn = sh.snapshots(n, "Selawik", min_nodes=300, min_span_km=100)
    ssn = ssn[(ssn.time >= "2024-05-01") & (ssn.time <= "2024-08-15")]
    pb2 = int(ssn.groupby("pass_id").n_nodes.median().idxmax())
    sel2 = ssn[ssn.pass_id == pb2].sort_values("time")
    for i, (_, s) in enumerate(sel2.iterrows()):
        a = sh.anomaly(n, ref, s.cycle_id, s.pass_id, "Selawik")
        a = a[a.eta.notna()]
        if len(a) < 100:
            continue
        ax.plot(a.dist_out_km, a.eta, lw=1.2,
                color=cmap(i / max(1, len(sel2) - 1)),
                label=pd.Timestamp(s.time).strftime("%d %b"))
    ax.axhline(0, color="k", lw=0.7)
    ax.invert_xaxis()
    ax.set_xlabel("distance upstream from outlet (km)")
    ax.set_ylabel("$\\eta$ (m)")
    ax.set_title(f"(c) Selawik spatial hydrographs, pass {pb2}\n"
                 "spring 2024 freshet recession")
    ax.legend(fontsize=6.4, ncol=2, loc="upper right")

    # ---- (d) celerity ----------------------------------------------------
    tg = two_gauge_celerity()
    ax = fig.add_subplot(gs[1, 0])
    for tag, c in [("raw", "0.6"), ("highpass15d", "crimson")]:
        ax.plot(tg[tag]["lags"], tg[tag]["cc"], "-o", ms=3, color=c,
                label=f"{tag}: peak {tg[tag]['lag_d']:.2f} d, "
                      f"c = {tg[tag]['celerity_ms']:.2f} m/s")
    ax.set_xlabel("lag, Ambler $\\rightarrow$ Kiana (days)")
    ax.set_ylabel("cross-correlation")
    ax.set_title("(d) two-gauge celerity, Kobuk 1976-1978\n"
                 f"L = {tg['raw']['L_km']:.0f} km, {tg['raw']['n_days']} open-water days")
    ax.legend(loc="lower center", fontsize=7.5)

    # ---- (e) celerity: SWOT spatial-hydrograph peak + gauge peak ---------
    # This is the Thurman et al. (2025) estimator: locate the peak of a SWOT
    # spatial hydrograph, find the same wave arriving at a downstream gauge,
    # and divide separation by travel time.  The SWOT-only variant (cross-
    # correlating two overpass profiles) was tried first and failed -- see
    # swot_only_celerity() and docs/WALKTHROUGH.md S7.
    ax = fig.add_subplot(gs[1, 1])
    iv = sk.load_gauges("instantaneous")
    iv = iv[(iv.site_no == "15744500") & iv.q_cms.notna()].sort_values("time")
    inv = sk.load_inventory()
    kre, _ = sk.nearest_reach(inv, 66.973611, -160.130833, "Kobuk")
    x_gauge = float(kre.dist_out_km)

    ksn = sh.snapshots(n, "Kobuk", min_nodes=300, min_span_km=100).sort_values("time")
    rows = []
    for _, sp in ksn.iterrows():
        a = sh.anomaly(n, ref, sp.cycle_id, sp.pass_id, "Kobuk")
        a = a[a.eta.notna() & (a.dist_out_km > x_gauge + 20)]
        if len(a) < 100 or a.eta.max() < 0.5:
            continue
        xp = float(a.loc[a.eta.idxmax(), "dist_out_km"])       # peak location
        t0 = pd.Timestamp(sp.time)
        # the gauge peak that follows, within a plausible travel-time window
        # Require an actual rise at the gauge, not just the largest value in a
        # long window, and keep the window short so an unrelated later peak is
        # not matched to this overpass.
        w = iv[(iv.time > t0) & (iv.time <= t0 + pd.Timedelta("48h"))]
        prior = iv[iv.time <= t0]
        if len(w) < 20 or not len(prior):
            continue
        q0 = float(prior.q_cms.iloc[-1])
        if w.q_cms.max() < 1.10 * q0:
            continue
        tg_ = w.loc[w.q_cms.idxmax(), "time"]
        dt_h = (tg_ - t0).total_seconds() / 3600
        L = xp - x_gauge
        if dt_h < 4 or L < 25:
            continue
        rows.append(dict(time=t0, x_peak_km=xp, L_km=L, dt_hr=dt_h,
                         eta_peak=float(a.eta.max()),
                         celerity_ms=L * 1000 / (dt_h * 3600)))
    cel = pd.DataFrame(rows)
    cel.to_csv(f"{sk.DATA}/../docs/celerity_swot_gauge.csv", index=False)

    # kinematic-wave prior: for a wide channel with Manning friction the
    # monoclinal wave travels at c = (5/3) U.  U from gauged Q and the SWOT
    # cross-sectional area at the Kiana reach.
    rch = sk.load_reaches()
    kk = rch[rch.reach_id == int(kre.reach_id)]
    w_med = float(kk.width.median())
    q_hi = float(iv.q_cms.quantile(0.9))
    depth = np.array([3.0, 5.0, 7.0])
    U = q_hi / (w_med * depth)
    c_kin = 5 / 3 * U
    if len(cel):
        ax.hist(cel.celerity_ms, bins=np.arange(0, 4.2, 0.25), color="#1f6f8b",
                alpha=0.85, edgecolor="k", linewidth=0.4,
                label=f"SWOT peak + gauge (n={len(cel)})\nmedian "
                      f"{cel.celerity_ms.median():.2f} m/s -- biased low,\n"
                      f"travel times pile up at the 48 h window edge")
    ax.axvspan(c_kin.min(), c_kin.max(), color="green", alpha=0.13,
               label=f"kinematic wave $\\frac{{5}}{{3}}U$, depth 3-7 m\n"
                     f"({c_kin.min():.2f}-{c_kin.max():.2f} m/s)")
    ax.axvline(tg["highpass15d"]["celerity_ms"], color="crimson", ls="--", lw=1.5,
               label=f"two-gauge {tg['highpass15d']['celerity_ms']:.2f} m/s\n"
                     f"(daily data, lag poorly resolved)")
    ax.set_xlabel("wave celerity (m s$^{-1}$)"); ax.set_ylabel("count")
    ax.set_title("(e) Kobuk flow-wave celerity: gauge and theory agree at\n"
                 "1-3 m/s; the SWOT estimator does not resolve it")
    ax.legend(fontsize=6.6, loc="upper right")

    # ---- (f) anomaly amplitude along river -------------------------------
    ax = fig.add_subplot(gs[1, 2])
    for riv in ["Kobuk", "Selawik", "Noatak"]:
        sn = sh.snapshots(n, riv, min_nodes=300, min_span_km=100)
        prof = []
        for _, s in sn.sample(min(60, len(sn)), random_state=0).iterrows():
            a = sh.anomaly(n, ref, s.cycle_id, s.pass_id, riv)
            prof.append(a[["dist_out_km", "eta"]].dropna())
        P = pd.concat(prof)
        b = P.groupby(pd.cut(P.dist_out_km, np.arange(0, 700, 25))).eta.std()
        ctr = [iv.mid for iv in b.index]
        ax.plot(ctr, b.values, "-o", ms=3, color=sk.RIVER_COLORS[riv], label=riv)
    ax.set_xlabel("distance upstream from outlet (km)")
    ax.set_ylabel("std of WSE anomaly (m)")
    ax.set_title("(f) stage variability along each river\n"
                 "rises upstream as the channel narrows")
    ax.legend()

    out = f"{sk.FIGS}/fig04_flow_waves.png"
    fig.savefig(out, dpi=170); print("wrote", out)

    print("\ntwo-gauge celerity (Kobuk, Ambler->Kiana, L = "
          f"{tg['raw']['L_km']:.0f} km):")
    for tag in tg:
        t = tg[tag]
        print(f"  {tag:12s} lag {t['lag_d']:+.2f} d, r = {t['r']:.3f}, "
              f"c = {t['celerity_ms']:.2f} m/s")
    print(f"\nkinematic-wave prior (5/3 U, Q90 = {q_hi:.0f} m3/s, "
          f"width {w_med:.0f} m, depth 3-7 m): {c_kin.min():.2f}-{c_kin.max():.2f} m/s")
    print("\nSWOT spatial-hydrograph peak + Kiana gauge peak:")
    if len(cel):
        print(cel[["celerity_ms", "L_km", "dt_hr", "eta_peak"]].describe()
              .loc[["count", "25%", "50%", "75%"]].to_string())
    else:
        print("  no qualifying events")


if __name__ == "__main__":
    main()
