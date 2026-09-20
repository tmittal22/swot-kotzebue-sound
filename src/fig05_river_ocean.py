"""Figure 5 -- coupling between SWOT-observed river forcing and the
Kotzebue Sound bloom season.

Honest framing, carried into every panel:

  * VIIRS chlorophyll over Kotzebue Sound is a Case-2 retrieval.  The sound is
    shallow, turbid and CDOM-rich, and the Kobuk/Noatak plumes carry both
    sediment and dissolved organic matter.  The standard OC algorithm reads
    those as chlorophyll, so absolute values are biased high and a chlorophyll
    rise coincident with a river pulse may be the plume itself rather than
    phytoplankton.  These series are used for SEASON TIMING and interannual
    comparison, never as calibrated biomass.
  * Valid retrievals exist only from June to September at this latitude
    (0.0-0.6% valid in Oct-May).  Every statistic here is restricted to that
    window, and no annual mean is computed.
  * The analysis is correlational over 3-4 SWOT years.  It cannot establish
    that river forcing drives blooms.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy import stats

import swotkot as sk
import fig03_seasonal as f3

REGIONS = {
    "Hotham Inlet": dict(lat=(66.70, 67.05), lon=(-161.90, -160.90), c="#c1543a"),
    "Inner sound": dict(lat=(66.40, 67.00), lon=(-163.50, -161.90), c="#1f6f8b"),
    "Outer sound": dict(lat=(66.60, 67.35), lon=(-165.50, -163.50), c="#4f7942"),
}
MOUTHS = {"Kobuk": (66.92, -161.05), "Selawik": (66.57, -160.45),
          "Noatak": (67.10, -162.65)}


def region_series(da, reg):
    s = da.sel(latitude=slice(*sorted(reg["lat"])[::-1]),
               longitude=slice(*reg["lon"]))
    if s.latitude.size == 0:
        s = da.sel(latitude=slice(*sorted(reg["lat"])),
                   longitude=slice(*reg["lon"]))
    n_valid = s.notnull().sum(dim=["latitude", "longitude"])
    med = s.median(dim=["latitude", "longitude"], skipna=True)
    out = pd.DataFrame({"chl": med.values, "n_valid": n_valid.values},
                       index=pd.to_datetime(da.time.values))
    # a regional median from a handful of pixels is noise; require coverage
    out.loc[out.n_valid < 8, "chl"] = np.nan
    return out


def main():
    sk.mpl_setup()
    d = xr.open_dataset(f"{sk.DATA}/ocean/chla_weekly.nc")
    chl = d.chlor_a.squeeze("altitude", drop=True)
    t = pd.to_datetime(chl.time.values)
    summer = np.isin(t.month, [6, 7, 8, 9])

    fig = plt.figure(figsize=(13.5, 9.0))
    gs = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.42)

    # (a) August median chlorophyll map
    ax = fig.add_subplot(gs[0, 0])
    aug = chl.isel(time=np.where(t.month == 8)[0]).median("time", skipna=True)
    pm = ax.pcolormesh(chl.longitude, chl.latitude, np.log10(aug),
                       cmap="viridis", vmin=-0.3, vmax=1.6, shading="auto")
    plt.colorbar(pm, ax=ax, label="log$_{10}$ chl-a (mg m$^{-3}$)", pad=0.02)
    for nm, r in REGIONS.items():
        ax.add_patch(Rectangle((r["lon"][0], r["lat"][0]),
                               np.diff(r["lon"])[0], np.diff(r["lat"])[0],
                               fill=False, ec=r["c"], lw=1.8))
        ax.annotate(nm, (np.mean(r["lon"]), r["lat"][1]), color=r["c"],
                    fontsize=7.5, ha="center", va="bottom", weight="bold")
    for nm, (la, lo) in MOUTHS.items():
        ax.plot(lo, la, "v", ms=7, mfc="white", mec="k", mew=0.9)
        ax.annotate(f"{nm} mouth", (lo, la), textcoords="offset points",
                    xytext=(5, -9), fontsize=7)
    ax.set_aspect(1 / np.cos(np.radians(67)))
    ax.set_xlabel("longitude ($^\\circ$E)"); ax.set_ylabel("latitude ($^\\circ$N)")
    ax.set_title("(a) August median chlorophyll, VIIRS 2012-2026\n"
                 "Case-2 water: values biased high near river plumes", pad=10)

    # (b) seasonal cycle by region + SWOT river stage
    ax = fig.add_subplot(gs[0, 1])
    series = {nm: region_series(chl, r) for nm, r in REGIONS.items()}
    for nm, s in series.items():
        s = s.dropna()
        w = s.groupby(s.index.isocalendar().week).chl.median()
        ax.plot(w.index * 7, w.values, "-o", ms=3, color=REGIONS[nm]["c"], label=nm)
    ax.set_xlim(140, 290); ax.set_yscale("log")
    ax.set_xlabel("day of year"); ax.set_ylabel("chl-a (mg m$^{-3}$)", labelpad=1)
    ax2 = ax.twinx(); ax2.grid(False)
    rch = sk.load_reaches()
    for riv in ["Kobuk", "Selawik"]:
        a = f3.river_stage_anomaly(rch, riv)
        b = a.groupby(pd.cut(a.doy, np.arange(130, 291, 10))).anom.median()
        ax2.plot([iv.mid for iv in b.index], b.values, "--", lw=2,
                 color=sk.RIVER_COLORS[riv], alpha=0.75, label=f"{riv} stage")
    ax2.set_ylabel("SWOT stage anomaly (m)")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=6.8, loc="upper left", ncol=2)
    ax.set_title("(b) bloom season vs river forcing\nsolid = chl, dashed = SWOT stage")

    # (c) interannual Jun-Sep median chlorophyll
    ax = fig.add_subplot(gs[0, 2])
    rows = []
    for nm, s in series.items():
        ss = s[np.isin(s.index.month, [6, 7, 8, 9])].dropna()
        yr = ss.groupby(ss.index.year).chl.median()
        cnt = ss.groupby(ss.index.year).chl.size()
        yr = yr[cnt >= 6]
        ax.plot(yr.index, yr.values, "-o", ms=4, color=REGIONS[nm]["c"], label=nm)
        for y, v in yr.items():
            rows.append(dict(region=nm, year=y, chl=v))
    ax.axvspan(2022.5, 2026.5, color="gold", alpha=0.15)
    ax.annotate("SWOT era", (2024.5, ax.get_ylim()[1] * 0.97), fontsize=7.5,
                ha="center", va="top", color="0.35")
    ax.set_xlabel("year")
    ax.set_ylabel("Jun-Sep median chl-a (mg m$^{-3}$)", labelpad=1)
    ax.set_xticks(range(2012, 2027, 3))
    ax.set_title("(c) interannual bloom-season chlorophyll\n"
                 "(weeks with $\\geq$8 valid pixels only)")
    ax.legend(fontsize=7)
    yrdf = pd.DataFrame(rows)
    yrdf.to_csv(f"{sk.DATA}/../docs/chl_annual.csv", index=False)

    # (d) week-by-week: river stage vs chlorophyll, SWOT era
    ax = fig.add_subplot(gs[1, 0])
    kob = f3.river_stage_anomaly(rch, "Kobuk")
    # ERDDAP times are tz-naive UTC; SWOT times are tz-aware UTC
    kob_w = (kob.set_index("time").anom.resample("W").mean()
             .tz_convert("UTC").tz_localize(None))
    lagres = []
    for nm, s in series.items():
        c = s.chl.resample("W").mean()
        both = pd.concat([np.log10(c).rename("chl"), kob_w.rename("stage")],
                         axis=1).dropna()
        both = both[np.isin(both.index.month, [6, 7, 8, 9])]
        if len(both) < 10:
            continue
        for lag in range(0, 7):
            a = both.stage.shift(lag)
            m = pd.concat([a.rename("s"), both.chl], axis=1).dropna()
            if len(m) < 10:
                continue
            r = stats.pearsonr(m.s, m.chl)
            lagres.append(dict(region=nm, lag_weeks=lag, r=r.statistic,
                               p=r.pvalue, n=len(m)))
    L = pd.DataFrame(lagres)
    L.to_csv(f"{sk.DATA}/../docs/chl_stage_lag.csv", index=False)
    for nm in REGIONS:
        g = L[L.region == nm]
        if len(g):
            ax.plot(g.lag_weeks, g.r, "-o", ms=4, color=REGIONS[nm]["c"],
                    label=f"{nm} (n={g.n.iloc[0]})")
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xlabel("lag: Kobuk stage leads chlorophyll (weeks)")
    ax.set_ylabel("Pearson r  (log$_{10}$ chl vs stage)")
    n_tests = len(L)
    alpha_bonf = 0.05 / max(n_tests, 1)
    n_sig = int((L.p < alpha_bonf).sum())
    ax.set_title(f"(d) lagged correlation, Jun-Sep only\n"
                 f"{n_tests} tests; {n_sig} survive Bonferroni "
                 f"($p<{alpha_bonf:.4f}$)")
    ax.legend(fontsize=7)

    # (e) does the SWOT-era late-summer Kobuk pulse overlap the bloom?
    ax = fig.add_subplot(gs[1, 1])
    g = sk.load_gauges("daily")
    kb = g[g.site_no == "15744500"].dropna(subset=["q_cms"]).copy()
    kb["doy"] = kb.time.dt.dayofyear; kb["yr"] = kb.time.dt.year
    clim = kb[kb.yr < 2023].groupby("doy").q_cms.median()
    era = kb[kb.yr >= 2023].groupby("doy").q_cms.median()
    ax.plot(clim.index, clim.values, color="0.45", lw=1.5, label="Kobuk Q 1977-2022")
    ax.plot(era.index, era.values, color=sk.RIVER_COLORS["Kobuk"], lw=1.8,
            label="Kobuk Q 2023-2026")
    ax.set_yscale("log"); ax.set_xlim(140, 290)
    ax.set_xlabel("day of year"); ax.set_ylabel("discharge (m$^3$ s$^{-1}$)")
    ax3 = ax.twinx(); ax3.grid(False)
    inner = series["Inner sound"].dropna()
    wk = inner.groupby(inner.index.isocalendar().week).chl.median()
    ax3.fill_between(wk.index * 7, 0, wk.values, color="seagreen", alpha=0.22,
                     label="inner-sound chl (climatology)")
    ax3.set_ylabel("chl-a (mg m$^{-3}$)", color="seagreen")
    h1, l1 = ax.get_legend_handles_labels(); h3, l3 = ax3.get_legend_handles_labels()
    ax.legend(h1 + h3, l1 + l3, fontsize=7, loc="upper right")
    ax.set_title("(e) SWOT-era Kobuk flow is elevated through\n"
                 "the Aug-Sep bloom window relative to climatology")

    # (f) data-availability honesty panel
    ax = fig.add_subplot(gs[1, 2])
    vf = chl.notnull().mean(dim=["latitude", "longitude"]).to_series()
    vf.index = pd.to_datetime(vf.index)
    mv = vf.groupby(vf.index.month).mean()
    ax.bar(mv.index, mv.values * 100, color="0.55", edgecolor="k", linewidth=0.4)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("month"); ax.set_ylabel("valid VIIRS pixels (%)")
    ax.set_title("(f) ocean colour exists only Jun-Sep here\n"
                 "polar night, sea ice and low sun angle elsewhere")

    out = f"{sk.FIGS}/fig05_river_ocean_coupling.png"
    fig.savefig(out, dpi=170); print("wrote", out)

    print(f"\nmultiple comparisons: {len(L)} tests, Bonferroni alpha = "
          f"{0.05/len(L):.5f}, surviving = {int((L.p < 0.05/len(L)).sum())}")
    print("\nlagged correlation, Kobuk stage vs log10 chl (Jun-Sep):")
    print(L.sort_values(["region", "lag_weeks"]).to_string(index=False))
    print("\nJun-Sep median chl by region and year:")
    print(yrdf.pivot(index="year", columns="region", values="chl").round(2).to_string())


if __name__ == "__main__":
    main()
