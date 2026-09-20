"""Figure 16 -- what SWOT can do with no gauge anywhere in the analysis.

This matters because the Selawik and Noatak have no gauge and never have. If a
SWOT-only workflow cannot stand on its own, nothing quantitative can be said
about them at all.

The pivot is the SoS discharge product (SWOT Discharge Algorithm Working
Group), pulled from Hydrocron's Version 2.0 collection via the official
v17b->v16 reach translation. Validated at the single gauge, it turns out to be
an excellent SHAPE estimator and a poor MAGNITUDE estimator, and that
distinction sets what the rest of the figure is allowed to claim.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

import swotkot as sk
import fig12_15_attribution as f12

RIVERS = ["Noatak", "Kobuk", "Selawik", "Buckland", "Wulik"]
SPRING, LATE = (121, 196), (197, 288)


def outlet_series(d, river, min_n=25):
    """SoS discharge at the most downstream reach that has enough retrievals."""
    s = d[(d.river == river) & d.sos_consensus_q.notna()]
    if not len(s):
        return None, None
    cnt = s.groupby("reach_id").agg(n=("sos_consensus_q", "size"),
                                    dist=("dist_out_km", "first"))
    cnt = cnt[cnt.n >= min_n]
    if cnt.empty:
        return None, None
    rid = int(cnt.sort_values("dist").index[0])
    return s[s.reach_id == rid].sort_values("time"), rid


def main():
    sk.mpl_setup()
    d = pd.read_parquet(f"{sk.DATA}/swot/sos_discharge.parquet")
    d = d[(d.reach_q <= 1) & (d.ice_clim_f == 0)]
    inv = sk.load_inventory()

    fig = plt.figure(figsize=(14, 9.4))
    gs = fig.add_gridspec(2, 3, hspace=0.38, wspace=0.3)

    # ---- (a) validate SoS at the one gauge -------------------------------
    kre, _ = sk.nearest_reach(inv, 66.973611, -160.130833, "Kobuk")
    s = d[(d.reach_id == int(kre.reach_id)) & d.sos_consensus_q.notna()].sort_values("time")
    iv = sk.load_gauges("instantaneous")
    iv = iv[(iv.site_no == "15744500") & iv.q_cms.notna()].sort_values("time")
    m = pd.merge_asof(s[["time", "sos_consensus_q"]], iv[["time", "q_cms"]],
                      on="time", direction="nearest",
                      tolerance=pd.Timedelta("2h")).dropna()
    ax = fig.add_subplot(gs[0, 0])
    dv = sk.load_gauges("daily")
    dv = dv[dv.site_no == "15744500"].dropna(subset=["q_cms"])
    dv = dv[(dv.time >= "2023-05-01") & (dv.time <= "2025-06-01")]
    ax.plot(dv.time, dv.q_cms, lw=0.8, color="0.45", label="USGS gauge Q")
    ax.plot(s.time, s.sos_consensus_q, "o", ms=5, color="#1f6f8b",
            label="SWOT SoS discharge")
    ax.set_yscale("log"); ax.set_ylabel("discharge (m$^3$ s$^{-1}$)")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7.5)
    bias = (m.sos_consensus_q / m.q_cms).median()
    ax.set_title(f"(a) SWOT-only discharge vs the one gauge\n"
                 f"tracks the shape, sits {1/bias:.1f}x too low", fontsize=9.5)
    ax.legend(fontsize=7.5)

    # ---- (b) shape vs magnitude ------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    r = stats.pearsonr(np.log10(m.sos_consensus_q), np.log10(m.q_cms))
    nse = 1 - np.sum((m.sos_consensus_q - m.q_cms) ** 2) / \
        np.sum((m.q_cms - m.q_cms.mean()) ** 2)
    ax.scatter(m.q_cms, m.sos_consensus_q, s=45, color="#1f6f8b",
               edgecolor="k", linewidth=0.5, zorder=3)
    lim = [m[["q_cms", "sos_consensus_q"]].min().min() * 0.7,
           m[["q_cms", "sos_consensus_q"]].max().max() * 1.4]
    ax.plot(lim, lim, "k--", lw=1.2, label="1:1")
    ax.plot(lim, [l * bias for l in lim], "-", color="crimson", lw=1.4,
            label=f"median bias {bias:.2f}x")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("gauge Q (m$^3$ s$^{-1}$)")
    ax.set_ylabel("SWOT SoS Q (m$^3$ s$^{-1}$)")
    ax.set_title(f"(b) r(log) = {r.statistic:.2f} but NSE = {nse:.1f}\n"
                 f"excellent shape, unusable magnitude  (n = {len(m)})", fontsize=9.5)
    ax.legend(fontsize=7.5, loc="upper left")

    # ---- (c) SWOT-only discharge, all rivers -----------------------------
    ax = fig.add_subplot(gs[0, 2])
    series, rids = {}, {}
    for riv in RIVERS:
        ss, rid = outlet_series(d, riv)
        if ss is None:
            continue
        series[riv], rids[riv] = ss, rid
        sp = ss.copy()
        sp.loc[sp.time.diff() > pd.Timedelta("45D"), "sos_consensus_q"] = np.nan
        ax.plot(sp.time, sp.sos_consensus_q, "-o", ms=2.6, lw=0.8,
                color=sk.RIVER_COLORS[riv], label=f"{riv}")
    ax.set_yscale("log"); ax.set_ylabel("SWOT SoS Q (m$^3$ s$^{-1}$)")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7.5)
    ax.set_title("(c) SWOT-only discharge at each river outlet\n"
                 "no gauge used anywhere in this panel", fontsize=9.5)
    ax.legend(fontsize=7, ncol=2)

    # ---- (d) can SWOT alone recover the phase split? ---------------------
    ax = fig.add_subplot(gs[1, 0])
    rows = []
    for riv, ss in series.items():
        t = ss.copy()
        t["doy"] = t.time.dt.dayofyear
        b = t.groupby(pd.cut(t.doy, np.arange(130, 301, 15))).sos_consensus_q.median()
        ctr = [iv_.mid for iv_ in b.index]
        norm = b.values / np.nanmedian(b.values)
        ax.plot(ctr, norm, "-o", ms=3.6, color=sk.RIVER_COLORS[riv], label=riv)
        ow = t[(t.doy >= SPRING[0]) & (t.doy <= LATE[1])]
        sp = ow[(ow.doy >= SPRING[0]) & (ow.doy <= SPRING[1])].sos_consensus_q
        la = ow[(ow.doy >= LATE[0]) & (ow.doy <= LATE[1])].sos_consensus_q
        if len(sp) >= 3 and len(la) >= 3:
            ratio = la.max() / sp.max()
            rows.append(dict(river=riv, n=len(ow), reach=rids[riv],
                             q_spring=sp.max(), q_late=la.max(),
                             late_over_spring=ratio,
                             late_wins=bool(ratio > 1.0),
                             ambiguous=bool(0.9 < ratio < 1.1),
                             doy_max=int(ow.loc[ow.sos_consensus_q.idxmax(), "doy"])))
    ax.axvspan(*SPRING, color="tab:blue", alpha=0.07)
    ax.axvspan(*LATE, color="tab:orange", alpha=0.09)
    # the binned curves are noisy at n=25-50; mark the seasonal maximum of each
    # river so the phase split is legible rather than merely tabulated
    for rr in rows:
        ax.axvline(rr["doy_max"], color=sk.RIVER_COLORS[rr["river"]],
                   lw=2.2, alpha=0.75, ymin=0.0, ymax=0.08)
        ax.annotate(f"{rr['doy_max']}", (rr["doy_max"], 1.0),
                    xycoords=("data", "axes fraction"),
                    xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=7, color=sk.RIVER_COLORS[rr["river"]], weight="bold")
    ax.set_yscale("log")
    ax.set_xlabel("day of year"); ax.set_ylabel("Q / median Q")
    ax.set_title("(d) SWOT-only seasonality recovers the phase split\n"
                 "Selawik peaks day 154; Kobuk 236, Noatak 251", fontsize=9.5)
    ax.legend(fontsize=7, ncol=2)
    S = pd.DataFrame(rows)
    S.to_csv(f"{sk.DATA}/../docs/swot_only_seasonality.csv", index=False)

    # ---- (e) algorithm spread = the honest uncertainty --------------------
    ax = fig.add_subplot(gs[1, 1])
    algs = ["sos_sic4dvar_q", "sos_metroman_q", "sos_momma_q"]
    kk = d[(d.river == "Kobuk") & d.sos_consensus_q.notna()]
    for a, c in zip(algs, ["#1f6f8b", "#c1543a", "#4f7942"]):
        v = kk[[a, "sos_consensus_q"]].dropna()
        if len(v) < 5:
            continue
        ratio = v[a] / v.sos_consensus_q
        ax.hist(np.log10(ratio.replace(0, np.nan).dropna()),
                bins=np.arange(-1.0, 1.05, 0.1), histtype="step", lw=1.7,
                color=c, label=f"{a.replace('sos_','').replace('_q','')} "
                               f"(n={len(v)})")
    ax.axvline(0, color="k", lw=0.9)
    ax.set_xlabel("log$_{10}$ (algorithm Q / consensus Q)")
    ax.set_ylabel("count")
    ax.set_title("(e) spread between discharge algorithms\n"
                 "Kobuk reaches; consensus is not a consensus of many",
                 fontsize=9.5)
    ax.legend(fontsize=7)

    # ---- (f) SWOT-only forcing vs chlorophyll ----------------------------
    ax = fig.add_subplot(gs[1, 2])
    CHL, _ = f12.region_series("chla_weekly.nc", "chlor_a")
    NLW, _ = f12.region_series("nlw671_weekly.nc", "nLw_671")
    kob = series.get("Kobuk")
    out = []
    if kob is not None:
        q = np.log10(kob.set_index("time").sos_consensus_q.resample("W").mean()
                     .tz_convert("UTC").tz_localize(None))
        for nm in ["Hotham Inlet", "Inner sound", "Outer sound"]:
            c = np.log10(CHL[nm].resample("W").mean())
            nl = NLW[nm].resample("W").mean()
            for lag in range(0, 4):
                D = pd.concat([c.rename("c"), nl.rename("n"),
                               q.shift(lag).rename("q")], axis=1).dropna()
                D = D[np.isin(D.index.month, [6, 7, 8, 9])]
                D = D[np.isfinite(D).all(axis=1)]
                if len(D) < 10:
                    continue
                raw = stats.pearsonr(D.q, D.c)
                rxz = stats.pearsonr(D.q, D.n).statistic
                ryz = stats.pearsonr(D.c, D.n).statistic
                den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
                pr = (raw.statistic - rxz * ryz) / den if den > 0 else np.nan
                out.append(dict(region=nm, lag=lag, n=len(D),
                                r_raw=raw.statistic, r_partial=pr))
    O = pd.DataFrame(out)
    O.to_csv(f"{sk.DATA}/../docs/swot_only_chl.csv", index=False)
    cols = {"Hotham Inlet": "#d18b2c", "Inner sound": "#1f6f8b",
            "Outer sound": "#4f7942"}
    for nm, c in cols.items():
        g = O[O.region == nm]
        if len(g):
            ax.plot(g.lag, g.r_partial, "-o", ms=5, color=c,
                    label=f"{nm} (n={g.n.iloc[0]})")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(0, 4))
    ax.set_xlabel("lag: SWOT-only Kobuk Q leads (weeks)")
    ax.set_ylabel("partial r vs log chl")
    ax.set_title("(f) SWOT-only forcing vs chlorophyll: n = 12\n"
                 "signs flip against the gauge result -- this is the power limit",
                 fontsize=9.5)
    ax.annotate("gauge (n=201) gave +0.24 here", (1, 0.24), fontsize=6.8,
                color="0.35", xytext=(1.15, 0.30), textcoords="data")
    ax.plot([1], [0.237], "k*", ms=11, zorder=5)
    ax.legend(fontsize=7)

    fig.suptitle("SWOT-only: no gauge anywhere except panels (a) and (b), "
                 "which exist to say what SWOT-only discharge can be trusted for",
                 fontsize=11.5, y=0.975)
    out_f = f"{sk.FIGS}/fig16_swot_only.png"
    fig.savefig(out_f, dpi=170, facecolor="white"); print("wrote", out_f)

    print(f"\nSoS validation at Kiana: n={len(m)}, r(log)={r.statistic:.3f}, "
          f"median bias={bias:.2f}x, NSE={nse:.2f}")
    print("\nSWOT-only seasonality (no gauge):")
    print(S.to_string(index=False))
    print("\nSWOT-only Kobuk Q vs chlorophyll (partial, sediment removed):")
    print(O.to_string(index=False))


if __name__ == "__main__":
    main()
