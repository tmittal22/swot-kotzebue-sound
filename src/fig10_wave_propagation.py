"""Figure 10 -- flow-wave propagation: length, amplitude, attenuation, and
explicit peak tracking.

Adds the Thurman et al. (2025) wave-LENGTH estimator, which does not depend on
the celerity machinery that failed in fig04:

  For each node, take the 90th percentile of its own WSE over the science-orbit
  record.  Within one overpass, a flow wave is a run of at least `min_run`
  consecutive nodes exceeding that threshold; its length is the along-river
  extent of the run.

Also tracks the along-river position of the anomaly maximum across consecutive
overpasses within an event.  Where a wave is coherent, x_peak(t) is a straight
line whose slope is the celerity -- and unlike a cross-correlation this shows
directly, per event, whether the wave is trackable at all.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import swotkot as sk
import spatial_hydrograph as sh

MIN_RUN = 10          # consecutive nodes, after Thurman et al.
RIVERS = ["Kobuk", "Selawik", "Noatak"]


def node_thresholds(n, q=0.90):
    return n.groupby("node_id").wse.quantile(q).rename("wse_p90")


def wave_runs(prof, thr, min_run=MIN_RUN):
    """Runs of consecutive nodes above their own 90th percentile."""
    p = prof.merge(thr, on="node_id", how="left").sort_values("dist_out_km")
    p = p[p.wse.notna() & p.wse_p90.notna()]
    if len(p) < min_run:
        return []
    over = (p.wse > p.wse_p90).values
    d = p.dist_out_km.values
    runs, i = [], 0
    while i < len(over):
        if over[i]:
            j = i
            while j + 1 < len(over) and over[j + 1]:
                j += 1
            if j - i + 1 >= min_run:
                runs.append(dict(n_nodes=j - i + 1,
                                 d_lo=float(d[i]), d_hi=float(d[j]),
                                 length_km=float(abs(d[j] - d[i]))))
            i = j + 1
        else:
            i += 1
    return runs


def main():
    sk.mpl_setup()
    n = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    n = n[(n.node_q <= 1) & (n.ice_clim_f == 0) & n.wse.notna()]
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")
    thr = node_thresholds(n[n.cycle_id < 400]).reset_index()

    fig = plt.figure(figsize=(13.5, 9.6))
    gs = fig.add_gridspec(2, 3, hspace=0.36, wspace=0.3)

    # ---- (a) wave lengths ------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    rows = []
    for riv in RIVERS:
        sn = sh.snapshots(n, riv, min_nodes=300, min_span_km=100)
        for _, s in sn.iterrows():
            prof = n[(n.river == riv) & (n.cycle_id == s.cycle_id) &
                     (n.pass_id == s.pass_id)]
            for r in wave_runs(prof, thr):
                rows.append(dict(river=riv, time=s.time, span_km=s.span_km, **r))
    W = pd.DataFrame(rows)
    W.to_csv(f"{sk.DATA}/../docs/wave_lengths.csv", index=False)
    for riv in RIVERS:
        w = W[W.river == riv]
        if len(w):
            ax.hist(w.length_km, bins=np.arange(0, 320, 20), histtype="step",
                    lw=1.7, color=sk.RIVER_COLORS[riv],
                    label=f"{riv}: n={len(w)}, median {w.length_km.median():.0f} km")
    ax.set_xlabel("flow-wave length (km)"); ax.set_ylabel("count")
    ax.set_title("(a) Wave length: runs of $\\geq$10 nodes above their own\n"
                 "90th-percentile WSE (Thurman et al. method)")
    ax.legend(fontsize=7)

    # ---- (b) THE ARTEFACT TEST -----------------------------------------
    # Deferred to after (c) because it needs the track table; the axis is
    # created here to keep the panel order.
    ax_artefact = fig.add_subplot(gs[0, 1])

    # ---- (c) peak tracking within events ---------------------------------
    ax = fig.add_subplot(gs[0, 2])
    track_rows, tracks = [], []
    for riv in RIVERS:
        sn = sh.snapshots(n, riv, min_nodes=300, min_span_km=100).sort_values("time")
        sn = sn.reset_index(drop=True)
        prof_cache = {}
        for i in range(len(sn)):
            if i not in prof_cache:
                a = sh.anomaly(n, ref, sn.cycle_id[i], sn.pass_id[i], riv)
                prof_cache[i] = a[a.eta.notna()]
        # group overpasses into events: consecutive obs <=4 d apart with eta>0.5
        cur = []
        for i in range(len(sn)):
            a = prof_cache[i]
            if len(a) < 100 or a.eta.max() < 0.5:
                if len(cur) >= 3:
                    tracks.append((riv, cur))
                cur = []
                continue
            t = pd.Timestamp(sn.time[i])
            xp = float(a.loc[a.eta.idxmax(), "dist_out_km"])
            if cur and (t - cur[-1][0]) > pd.Timedelta("4D"):
                if len(cur) >= 3:
                    tracks.append((riv, cur))
                cur = []
            cur.append((t, xp, float(a.eta.max())))
        if len(cur) >= 3:
            tracks.append((riv, cur))

    for riv, tr in tracks:
        t0 = tr[0][0]
        hrs = np.array([(t - t0).total_seconds() / 3600 for t, _, _ in tr])
        xs = np.array([x for _, x, _ in tr])
        if hrs.max() < 12:
            continue
        r = stats.linregress(hrs, xs)
        # negative slope = peak moving downstream (towards smaller dist_out)
        track_rows.append(dict(river=riv, t0=t0, n=len(tr),
                               span_hr=float(hrs.max()),
                               slope_km_per_hr=float(r.slope),
                               r2=float(r.rvalue ** 2),
                               celerity_ms=float(abs(r.slope) * 1000 / 3600)))
        coh = r.rvalue ** 2 > 0.7
        ax.plot(hrs, xs - xs[0], "-o", ms=3.4 if coh else 2,
                lw=1.5 if coh else 0.6,
                color=sk.RIVER_COLORS[riv] if coh else "0.82",
                alpha=1.0 if coh else 0.7, zorder=4 if coh else 1)
    T = pd.DataFrame(track_rows)
    T.to_csv(f"{sk.DATA}/../docs/wave_peak_tracks.csv", index=False)
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xlabel("hours since first overpass of the event")
    ax.set_ylabel("displacement of anomaly peak (km)")
    good = T[T.r2 > 0.7] if len(T) else T
    ndown = int((good.slope_km_per_hr < 0).sum()) if len(good) else 0
    cmed = good.celerity_ms.median() if len(good) else np.nan
    ax.set_title(f"(c) Peak tracking: {len(good)} of {len(T)} events coherent "
                 f"($r^2>0.7$, coloured)\nall {ndown}/{len(good)} appear to "
                 f"move downstream -- but see (b)")
    ax.annotate("downstream", (0.02, 0.06), xycoords="axes fraction",
                fontsize=7.5, color="0.35")
    ax.annotate("upstream", (0.02, 0.93), xycoords="axes fraction",
                fontsize=7.5, color="0.35")

    # ---- (b, filled) does the "wave" just follow the observation window? --
    # SWOT's consecutive passes over a river sweep along it.  If the centre of
    # the observed segment marches downstream at the same rate as the anomaly
    # peak, then the apparent celerity measures the ground track, not the
    # water.  This test is the reason no SWOT celerity is claimed.
    art = []
    for riv, tr in tracks:
        t0 = tr[0][0]
        sn2 = sh.snapshots(n, riv, min_nodes=300, min_span_km=100)
        sn2 = sn2.sort_values("time")
        sel = sn2[(pd.to_datetime(sn2.time) >= t0 - pd.Timedelta("1h")) &
                  (pd.to_datetime(sn2.time) <= tr[-1][0] + pd.Timedelta("1h"))]
        xs2, cs2, hs2 = [], [], []
        for _, s2 in sel.iterrows():
            a = sh.anomaly(n, ref, s2.cycle_id, s2.pass_id, riv)
            a = a[a.eta.notna()]
            if len(a) < 100:
                continue
            xs2.append(float(a.loc[a.eta.idxmax(), "dist_out_km"]))
            cs2.append(float(a.dist_out_km.median()))
            hs2.append((pd.Timestamp(s2.time) - t0).total_seconds() / 3600)
        if len(xs2) < 3:
            continue
        rp = stats.linregress(hs2, xs2); rc = stats.linregress(hs2, cs2)
        art.append(dict(river=riv, t0=t0, peak_slope=rp.slope,
                        seg_slope=rc.slope, r2=rp.rvalue ** 2,
                        c_peak=abs(rp.slope) * 1000 / 3600,
                        c_seg=abs(rc.slope) * 1000 / 3600))
    A = pd.DataFrame(art)
    A.to_csv(f"{sk.DATA}/../docs/wave_artefact_test.csv", index=False)
    ax = ax_artefact
    if len(A):
        coh = A[A.r2 > 0.7]
        ax.scatter(A.c_seg, A.c_peak, s=18, c="0.78", linewidths=0,
                   label=f"incoherent (n={len(A)-len(coh)})")
        ax.scatter(coh.c_seg, coh.c_peak, s=42, c=sk.RIVER_COLORS["Noatak"],
                   edgecolor="k", linewidth=0.5,
                   label=f"coherent, $r^2>0.7$ (n={len(coh)})")
        lim = [0, max(A.c_seg.max(), A.c_peak.max()) * 1.05]
        ax.plot(lim, lim, "r--", lw=1.4, label="1:1  = pure artefact")
        ax.set_xlim(lim); ax.set_ylim(lim)
        ratio = (coh.peak_slope / coh.seg_slope).median() if len(coh) else np.nan
        ax.set_title("(b) The apparent wave speed IS the ground-track speed\n"
                     f"median peak/window slope ratio = {ratio:.2f}; "
                     "celerity is not measured")
    ax.set_xlabel("speed of the observed segment centre (m s$^{-1}$)")
    ax.set_ylabel("apparent speed of the anomaly peak (m s$^{-1}$)")
    ax.legend(fontsize=7, loc="upper left")

    # ---- (d) amplitude vs distance ---------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    for riv in RIVERS:
        sn = sh.snapshots(n, riv, min_nodes=300, min_span_km=100)
        P = []
        for _, s in sn.sample(min(70, len(sn)), random_state=1).iterrows():
            a = sh.anomaly(n, ref, s.cycle_id, s.pass_id, riv)
            P.append(a[["dist_out_km", "eta"]].dropna())
        P = pd.concat(P)
        b = P.groupby(pd.cut(P.dist_out_km, np.arange(0, 700, 30))).eta.quantile(0.95)
        ctr = [iv.mid for iv in b.index]
        ax.plot(ctr, b.values, "-o", ms=3.5, color=sk.RIVER_COLORS[riv], label=riv)
    ax.set_xlabel("distance upstream from outlet (km)")
    ax.set_ylabel("95th percentile of $\\eta$ (m)")
    ax.set_title("(d) Wave amplitude grows upstream\n"
                 "narrower channel, same discharge change")
    ax.legend(fontsize=7.5)

    # ---- (e) seasonality of wave occurrence ------------------------------
    ax = fig.add_subplot(gs[1, 1])
    if len(W):
        W["doy"] = pd.to_datetime(W.time).dt.dayofyear
        for riv in RIVERS:
            w = W[W.river == riv]
            if len(w):
                h, e = np.histogram(w.doy, bins=np.arange(130, 300, 14))
                ax.plot(0.5 * (e[1:] + e[:-1]), h, "-o", ms=3.5,
                        color=sk.RIVER_COLORS[riv], label=riv)
    ax.axvspan(121, 196, color="tab:blue", alpha=0.07)
    ax.axvspan(197, 288, color="tab:orange", alpha=0.09)
    ax.set_xlabel("day of year"); ax.set_ylabel("wave detections per 14 d bin")
    ax.set_title("(e) When waves occur. Selawik is almost entirely nival;\n"
                 "Kobuk and Noatak are bimodal, with a rain-window peak")
    ax.legend(fontsize=7.5)

    # ---- (f) an example event --------------------------------------------
    ax = fig.add_subplot(gs[1, 2])
    # pick the best COHERENT event, not merely the longest sequence: the
    # longest is a 2023 one-day-repeat calval series over the Selawik freshet
    # recession, which is not a propagating wave.
    coh_keys = set()
    if len(good):
        coh_keys = {(r.river, pd.Timestamp(r.t0)) for _, r in good.iterrows()}
    cand = [(riv, tr) for riv, tr in tracks if (riv, tr[0][0]) in coh_keys]
    if cand:
        best_r2 = good.sort_values("r2", ascending=False).iloc[0]
        riv, tr = next((a, b) for a, b in cand
                       if a == best_r2.river
                       and b[0][0] == pd.Timestamp(best_r2.t0))
        sn = sh.snapshots(n, riv, min_nodes=300, min_span_km=100)
        cmap = plt.get_cmap("plasma")
        times = [t for t, _, _ in tr]
        for k, t in enumerate(times):
            row = sn.iloc[(pd.to_datetime(sn.time) - t).abs().argsort().iloc[0]]
            a = sh.anomaly(n, ref, row.cycle_id, row.pass_id, riv)
            a = a[a.eta.notna()]
            ax.plot(a.dist_out_km, a.eta, lw=1.3, color=cmap(k / max(1, len(times) - 1)),
                    label=f"{t:%d %b %H:%M}")
            ax.plot(tr[k][1], tr[k][2], "v", ms=7, color=cmap(k / max(1, len(times) - 1)))
        ax.invert_xaxis(); ax.axhline(0, color="k", lw=0.7)
        ax.set_xlabel("distance upstream from outlet (km)")
        ax.set_ylabel("$\\eta$ (m)")
        cms = float(best_r2.celerity_ms); rr2 = float(best_r2.r2)
        ax.set_title(f"(f) Best-'tracked' event: {riv}, {len(tr)} overpasses, "
                     f"{best_r2.span_hr:.0f} h\nthe three passes cover "
                     "DIFFERENT river segments -- that is the artefact")
        ax.legend(fontsize=7, ncol=1, loc="upper left")

    out = f"{sk.FIGS}/fig10_wave_propagation.png"
    fig.savefig(out, dpi=175, facecolor="white"); print("wrote", out)

    print("\nwave lengths (km):")
    print(W.groupby("river").length_km.describe()[["count", "25%", "50%", "75%", "max"]].to_string())
    frac = float((W.length_km > 0.9 * W.span_km).mean()) if len(W) else float("nan")
    print(f"\nfraction of detections filling >90% of the observed span: {frac:.2f}")
    if len(A):
        coh = A[A.r2 > 0.7]
        print("\nARTEFACT TEST (peak motion vs observation-window motion):")
        print(f"  coherent events: median peak/window slope ratio = "
              f"{(coh.peak_slope/coh.seg_slope).median():.2f} (1.0 = pure artefact)")
        print(f"  median c_peak {coh.c_peak.median():.2f} m/s vs "
              f"c_window {coh.c_seg.median():.2f} m/s")
    if len(T):
        print("\npeak-tracking events:")
        print(T.groupby("river").agg(n=("r2", "size"),
                                     coherent=("r2", lambda s: int((s > 0.7).sum())),
                                     med_r2=("r2", "median")).to_string())
        if len(good):
            print("\ncoherent events only:")
            print(good[["river", "t0", "n", "span_hr", "celerity_ms", "r2"]].to_string(index=False))


if __name__ == "__main__":
    main()
