"""Figure 3 -- seasonal freshwater regime of the Kotzebue Sound rivers.

The gauged Kobuk shows the annual peak arriving in late summer in every year of
the SWOT era, against a long-record base rate of 14%.  SWOT is used to ask
whether the ungauged Selawik and Noatak -- which have no in-situ record at all
-- share that behaviour.

Statistical care: a 40-year regression on the day-of-year of the annual maximum
is NOT significant, so this is reported as a property of the 2023-2026 years,
not as a demonstrated trend.  See docs/WALKTHROUGH.md S5.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

import swotkot as sk

SPRING = (121, 196)      # 1 May - 15 Jul, nival freshet window
LATE = (197, 288)        # 16 Jul - mid Oct, rain-driven window.
# The upper bound is set by ice_clim_f, which is a fixed climatology that
# flags these rivers as ice-covered after about DOY 288, so no SWOT
# open-water observation exists beyond it.
RIVERS = ["Kobuk", "Selawik", "Noatak"]


def river_stage_anomaly(reaches, river, max_dist_km=150):
    """Mean WSE anomaly across the lower reaches of one river, per overpass.

    Each reach is referenced to its own median WSE first, so reaches at
    different elevations can be averaged; the result is a basin-scale stage
    index, not an absolute elevation.
    """
    s = reaches[(reaches.river == river) & (reaches.dist_out_km <= max_dist_km)].copy()
    s["anom"] = s.wse - s.groupby("reach_id").wse.transform("median")
    # one value per overpass, median over reaches to resist single-reach outliers
    out = (s.groupby(["cycle_id", "pass_id"])
           .agg(time=("time", "median"), anom=("anom", "median"),
                n_reach=("reach_id", "nunique"))
           .reset_index())
    out = out[out.n_reach >= 3].sort_values("time")
    out["doy"] = out.time.dt.dayofyear
    out["year"] = out.time.dt.year
    return out


def peak_stats(g, qcol, doycol="doy", require_doy=275, hi=None):
    """Score a year as spring- or late-peaking.

    A year is only scored if its record extends past `require_doy`.  The 2026
    SWOT record stops on 16 September (DOY 259) with the Kobuk stage index
    still rising, so scoring it would report a spring peak purely because the
    late-season peak had not been observed yet.  `require_doy` defaults to the
    SWOT open-water limit; the year-round gauge is scored with a later cutoff.
    """
    hi = LATE[1] if hi is None else hi
    ow = g[(g[doycol] >= 121) & (g[doycol] <= hi)]
    if len(ow) < 8 or ow[doycol].max() < require_doy:
        return None
    sp = ow[(ow[doycol] >= SPRING[0]) & (ow[doycol] <= SPRING[1])]
    la = ow[(ow[doycol] >= LATE[0]) & (ow[doycol] <= hi)]
    if not len(sp) or not len(la):
        return None
    return dict(doy_max=int(ow.loc[ow[qcol].idxmax(), doycol]),
                v_spring=sp[qcol].max(), v_late=la[qcol].max(),
                late_wins=bool(la[qcol].max() > sp[qcol].max()), n=len(ow))


def main():
    sk.mpl_setup()
    rch = sk.load_reaches()
    g = sk.load_gauges("daily")
    kb = g[g.site_no == "15744500"].dropna(subset=["q_cms"]).copy()
    kb["yr"] = kb.time.dt.year; kb["doy"] = kb.time.dt.dayofyear

    fig = plt.figure(figsize=(12.5, 8.2))
    gs = fig.add_gridspec(2, 2, hspace=0.33, wspace=0.24)

    # (a) gauge climatology vs SWOT era
    ax = fig.add_subplot(gs[0, 0])
    hist = kb[kb.yr < 2023]
    clim = hist.groupby("doy").q_cms.quantile([0.25, 0.5, 0.75]).unstack()
    ax.fill_between(clim.index, clim[0.25], clim[0.75], color="0.8",
                    label="1977-2022 IQR")
    ax.plot(clim.index, clim[0.5], color="0.35", lw=1.2, label="1977-2022 median")
    for yr, c in zip(range(2023, 2027), ["#1f6f8b", "#c1543a", "#4f7942", "#8a6fae"]):
        s = kb[kb.yr == yr]
        ax.plot(s.doy, s.q_cms, lw=1.4, color=c, label=str(yr))
    ax.axvspan(*SPRING, color="tab:blue", alpha=0.06)
    ax.axvspan(*LATE, color="tab:orange", alpha=0.08)
    ax.set_yscale("log"); ax.set_xlim(90, 310)
    ax.set_xlabel("day of year"); ax.set_ylabel("discharge (m$^3$ s$^{-1}$)")
    ax.set_title("(a) Kobuk at Kiana (USGS 15744500): SWOT-era years\n"
                 "peak in the late (orange) not the nival (blue) window")
    ax.legend(ncol=2, loc="lower center", fontsize=7.5)

    # (b) day-of-year of annual maximum, full record
    ax = fig.add_subplot(gs[0, 1])
    rows = []
    for yr, s in kb.groupby("yr"):
        st = peak_stats(s, "q_cms", require_doy=295, hi=304)
        if st and st["n"] >= 160:
            rows.append(dict(yr=yr, **st))
    d = pd.DataFrame(rows)
    ax.scatter(d.yr, d.doy_max, c=np.where(d.late_wins, "tab:orange", "tab:blue"),
               s=38, edgecolor="k", linewidth=0.4, zorder=3)
    r = stats.linregress(d.yr, d.doy_max)
    xs = np.array([d.yr.min(), d.yr.max()])
    ax.plot(xs, r.intercept + r.slope * xs, "--", color="0.4", lw=1.1,
            label=f"trend {r.slope:+.2f} d/yr, p = {r.pvalue:.2f} (n.s.)")
    ax.axhspan(*SPRING, color="tab:blue", alpha=0.06)
    ax.axhspan(*LATE, color="tab:orange", alpha=0.08)
    ax.set_xlabel("year"); ax.set_ylabel("day of year of annual maximum Q")
    pre = d[d.yr < 2023]; era = d[d.yr >= 2023]
    p_binom = stats.binomtest(int(era.late_wins.sum()), len(era),
                              pre.late_wins.mean(), alternative="greater").pvalue
    ax.set_title(f"(b) late-window peak: {pre.late_wins.sum()}/{len(pre)} "
                 f"({pre.late_wins.mean()*100:.0f}%) before 2023, "
                 f"{era.late_wins.sum()}/{len(era)} since\n"
                 f"binomial p = {p_binom:.3f}, but no significant long-term trend")
    ax.legend(loc="upper left")

    # (c) SWOT stage anomaly, all three rivers
    ax = fig.add_subplot(gs[1, 0])
    anoms = {}
    for riv in RIVERS:
        a = river_stage_anomaly(rch, riv)
        anoms[riv] = a
        # break the line across the ice-covered winters instead of drawing a
        # ramp through eight months with no observations
        aa = a.copy()
        aa.loc[aa.time.diff() > pd.Timedelta("30D"), "anom"] = np.nan
        ax.plot(aa.time, aa.anom, "-o", ms=2.6, lw=0.9,
                color=sk.RIVER_COLORS[riv], label=f"{riv} (n={len(a)})")
    ax.axhline(0, color="k", lw=0.7)
    ax.set_ylabel("SWOT stage anomaly, lower 150 km (m)")
    ax.set_xlabel("date")
    ax.set_xticks([pd.Timestamp(f"{y}-{m}-01", tz="UTC")
                   for y in range(2023, 2027) for m in ("01", "07")])
    ax.tick_params(axis="x", labelrotation=45, labelsize=7.5)
    ax.set_title("(c) SWOT basin stage index. Selawik and Noatak have no\n"
                 "in-situ gauge: this is the only stage record for them")
    ax.legend(loc="upper left", ncol=3)

    # (d) seasonal composite by river
    ax = fig.add_subplot(gs[1, 1])
    srows = []
    for riv in RIVERS:
        a = anoms[riv]
        ax.plot(a.doy, a.anom, "o", ms=3.4, alpha=0.55,
                color=sk.RIVER_COLORS[riv], label=riv)
        # loess-free smooth: median in 10-day bins
        b = a.groupby(pd.cut(a.doy, np.arange(120, 311, 10))).anom.median()
        ctr = [iv.mid for iv in b.index]
        ax.plot(ctr, b.values, "-", lw=2.2, color=sk.RIVER_COLORS[riv])
        for yr, s in a.groupby("year"):
            st = peak_stats(s, "anom")
            if st:
                srows.append(dict(river=riv, year=yr, **st))
            else:
                srows.append(dict(river=riv, year=yr, doy_max=np.nan,
                                  v_spring=np.nan, v_late=np.nan,
                                  late_wins=None, n=len(s), censored=True))
    ax.axvspan(*SPRING, color="tab:blue", alpha=0.06)
    ax.axvspan(*LATE, color="tab:orange", alpha=0.08)
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xlabel("day of year"); ax.set_ylabel("SWOT stage anomaly (m)")
    ax.set_title("(d) seasonal composite, 2023-2026\n"
                 "thick line = 10-day binned median")
    ax.legend(loc="upper left", ncol=3)

    sd = pd.DataFrame(srows)
    sd.to_csv(f"{sk.DATA}/../docs/swot_peak_timing.csv", index=False)
    d.to_csv(f"{sk.DATA}/../docs/kobuk_peak_timing.csv", index=False)

    out = f"{sk.FIGS}/fig03_seasonal_regime.png"
    fig.savefig(out); print("wrote", out)

    print("\nSWOT-derived peak timing by river and year "
          "(late_wins = max anomaly after 15 Jul):")
    print(sd.to_string(index=False))
    scored = sd[sd.late_wins.notna()]
    print(f"\nscored river-years (record reaches DOY 290): {len(scored)}; "
          f"censored: {len(sd) - len(scored)}")
    print(f"late-window peak fraction, SWOT rivers: "
          f"{int(scored.late_wins.sum())}/{len(scored)}")
    for riv, gg in scored.groupby("river"):
        print(f"  {riv:8s} {int(gg.late_wins.sum())}/{len(gg)} late  "
              f"(DOY of max: {sorted(gg.doy_max.astype(int))})")
    print(f"gauge base rate 1977-2022: {pre.late_wins.mean()*100:.0f}%")
    print(f"binomial p (SWOT era, gauge only) = {p_binom:.4f}")


if __name__ == "__main__":
    main()
