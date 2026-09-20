"""Figures 12-15: which river does what to Kotzebue Sound.

A four-step sequence, one figure per step:

  12  WHAT EACH RIVER DOES      SWOT stage time series for all six rivers,
                                with the map and an inventory table.
  13  ARE THEY INDEPENDENT?     Seasonal phasing and the inter-river
                                correlation matrix.  Attribution is only
                                possible for rivers that are not collinear.
  14  WHAT THE OCEAN DOES       Chlorophyll, nLw(671) and Kd(PAR) time series
                                for five receiving basins, 2012-2026.
  15  WHO DRIVES WHAT           River-by-region correlation, with the sediment
                                control and an explicit power statement.

A note carried through: SWORD `facc` is inflated at merged coastal outlets.
Noatak reads 62,101 km2 against a published ~32,000, and Selawik 11,616
against ~8,160.  Published basin areas are used for any size weighting.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.patches import Rectangle
from scipy import stats

import swotkot as sk

RIVERS = ["Noatak", "Kobuk", "Selawik", "Buckland", "Squirrel", "Wulik"]
AREA_KM2 = {"Noatak": 32000, "Kobuk": 31000, "Selawik": 8160,
            "Buckland": 7300, "Squirrel": 4700, "Wulik": 2300}
DRAINS_TO = {"Noatak": "Inner sound (at Kotzebue)",
             "Kobuk": "Hotham Inlet",
             "Selawik": "Selawik Lake -> Hotham Inlet",
             "Buckland": "Eschscholtz Bay",
             "Squirrel": "Kobuk tributary (not independent)",
             "Wulik": "Chukchi coast, NOT the sound"}

REGIONS = {
    "Selawik Lake": dict(lat=(66.40, 66.65), lon=(-160.90, -159.90), c="#c1543a"),
    "Hotham Inlet": dict(lat=(66.70, 67.05), lon=(-161.90, -160.90), c="#d18b2c"),
    "Inner sound": dict(lat=(66.40, 67.00), lon=(-163.50, -161.90), c="#1f6f8b"),
    "Outer sound": dict(lat=(66.60, 67.35), lon=(-165.50, -163.50), c="#4f7942"),
    "Eschscholtz Bay": dict(lat=(66.05, 66.35), lon=(-162.20, -161.00), c="#8a6fae"),
}

BANDS = [("chlor_a", "chla_weekly.nc", "chl-a (mg m$^{-3}$)", True),
         ("nLw_671", "nlw671_weekly.nc", "nLw(671) sediment", False),
         ("kd_par", "kdpar_weekly.nc", "Kd(PAR) (m$^{-1}$)", True)]


def river_index(rch, river, max_dist_km=200):
    s = rch[(rch.river == river) & (rch.dist_out_km <= max_dist_km)].copy()
    if not len(s):
        return None
    s["anom"] = s.wse - s.groupby("reach_id").wse.transform("median")
    out = (s.groupby(["cycle_id", "pass_id"])
           .agg(time=("time", "median"), anom=("anom", "median"),
                nr=("reach_id", "nunique")).reset_index())
    out = out[out.nr >= 2].sort_values("time")
    out["doy"] = out.time.dt.dayofyear
    return out


def region_series(path, var):
    d = xr.open_dataset(f"{sk.DATA}/ocean/{path}")
    v = d[var].squeeze("altitude", drop=True)
    res = {}
    for nm, r in REGIONS.items():
        s = v.sel(latitude=slice(*sorted(r["lat"])[::-1]), longitude=slice(*r["lon"]))
        if s.latitude.size == 0:
            s = v.sel(latitude=slice(*sorted(r["lat"])), longitude=slice(*r["lon"]))
        nv = s.notnull().sum(dim=["latitude", "longitude"])
        med = s.median(dim=["latitude", "longitude"], skipna=True)
        ser = pd.Series(med.values, index=pd.to_datetime(v.time.values))
        ser[nv.values < 6] = np.nan
        res[nm] = ser[~ser.index.duplicated(keep="first")].sort_index()
    return res, v


def main():
    sk.mpl_setup()
    rch = sk.load_reaches()
    inv = sk.load_inventory()
    ninv = sk.load_inventory("nodes")
    idx = {r: river_index(rch, r) for r in RIVERS}
    idx = {k: v for k, v in idx.items() if v is not None and len(v) > 20}

    # =================== FIG 12: what each river does ===================
    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(len(idx), 3, width_ratios=[1.1, 2.2, 0.9],
                          hspace=0.28, wspace=0.22)
    axm = fig.add_subplot(gs[:, 0])
    axm.scatter(ninv.x, ninv.y, s=0.5, c="0.88", linewidths=0)
    for r in idx:
        s = ninv[ninv.river == r]
        axm.scatter(s.x, s.y, s=2.2, color=sk.RIVER_COLORS[r], linewidths=0)
        c = s[["x", "y"]].median()
        axm.annotate(r, (c.x, c.y), fontsize=7.5, weight="bold",
                     color=sk.RIVER_COLORS[r])
    for nm, rg in REGIONS.items():
        axm.add_patch(Rectangle((rg["lon"][0], rg["lat"][0]),
                                np.diff(rg["lon"])[0], np.diff(rg["lat"])[0],
                                fill=False, ec=rg["c"], lw=1.3, ls="--"))
    axm.set_aspect(1 / np.cos(np.radians(67)))
    axm.set_xlim(-166, -154.8); axm.set_ylim(65.4, 68.7)
    axm.set_xlabel("lon"); axm.set_ylabel("lat")
    axm.set_title("(a) rivers (solid) and\nreceiving basins (dashed)", fontsize=9)

    for k, (r, d) in enumerate(idx.items()):
        ax = fig.add_subplot(gs[k, 1])
        dd = d.copy()
        dd.loc[dd.time.diff() > pd.Timedelta("40D"), "anom"] = np.nan
        ax.plot(dd.time, dd.anom, "-o", ms=2.2, lw=0.8,
                color=sk.RIVER_COLORS[r])
        ax.axhline(0, color="k", lw=0.6)
        ax.set_ylabel(f"{r}\n$\\Delta$WSE (m)", fontsize=8)
        ax.set_xlim(pd.Timestamp("2023-04-01", tz="UTC"),
                    pd.Timestamp("2026-10-01", tz="UTC"))
        if k < len(idx) - 1:
            ax.set_xticklabels([])
        if k == 0:
            ax.set_title("(b) SWOT stage index, lower 200 km of each river",
                         fontsize=9.5)
        axt = fig.add_subplot(gs[k, 2]); axt.axis("off")
        axt.text(0, 0.5, f"{AREA_KM2[r]:,} km$^2$\n{len(d)} overpasses\n"
                         f"$\\to$ {DRAINS_TO[r]}", fontsize=7, va="center")
    fig.suptitle("Fig 12 | STEP 1: what each river does. Six rivers reach "
                 "Kotzebue Sound; only the Kobuk is gauged.", y=0.965)
    fig.savefig(f"{sk.FIGS}/fig12_rivers_overview.png", dpi=165,
                facecolor="white")
    print("wrote fig12")

    # =================== FIG 13: are they independent? ===================
    fig = plt.figure(figsize=(13.5, 5.6))
    gs = fig.add_gridspec(1, 3, wspace=0.3)

    ax = fig.add_subplot(gs[0])
    for r, d in idx.items():
        b = d.groupby(pd.cut(d.doy, np.arange(130, 301, 12))).anom.median()
        ax.plot([iv.mid for iv in b.index], b.values, "-o", ms=3.4,
                color=sk.RIVER_COLORS[r], label=f"{r}")
    ax.axvspan(121, 196, color="tab:blue", alpha=0.07)
    ax.axvspan(197, 288, color="tab:orange", alpha=0.09)
    ax.axhline(0, color="k", lw=0.7)
    ax.set_xlabel("day of year"); ax.set_ylabel("median stage anomaly (m)")
    ax.set_title("(a) seasonal phasing\nblue = nival window, orange = rain")
    ax.legend(fontsize=7, ncol=2)

    # weekly matrix for correlation
    W = {}
    for r, d in idx.items():
        s = d.set_index("time").anom.resample("W").mean()
        W[r] = s.tz_convert("UTC").tz_localize(None)
    Wd = pd.DataFrame(W)
    Wd = Wd[np.isin(Wd.index.month, [5, 6, 7, 8, 9])]
    C = Wd.corr(min_periods=15)
    ax = fig.add_subplot(gs[1])
    im = ax.imshow(C.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(C))); ax.set_xticklabels(C.columns, rotation=45,
                                                     ha="right", fontsize=7.5)
    ax.set_yticks(range(len(C))); ax.set_yticklabels(C.index, fontsize=7.5)
    for i in range(len(C)):
        for j in range(len(C)):
            v = C.values[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                        color="w" if abs(v) > 0.6 else "k")
    plt.colorbar(im, ax=ax, label="Pearson r", pad=0.02)
    off = C.values[np.triu_indices(len(C), 1)]
    off = off[np.isfinite(off)]
    ax.set_title(f"(b) inter-river correlation\n"
                 f"weekly May-Sep; median off-diag r = {np.median(off):.2f}",
                 fontsize=9)

    ax = fig.add_subplot(gs[2])
    ax.hist(off, bins=np.arange(-0.2, 1.05, 0.1), color="0.6", edgecolor="k",
            linewidth=0.5)
    ax.axvline(np.median(off), color="crimson", lw=1.6,
               label=f"median {np.median(off):.2f}")
    ax.set_xlabel("pairwise r between rivers"); ax.set_ylabel("count")
    hi = int((off > 0.7).sum())
    ax.set_title(f"(c) {hi} of {len(off)} river pairs exceed r=0.7\n"
                 "high collinearity limits attribution")
    ax.legend(fontsize=7.5)
    fig.suptitle("Fig 13 | STEP 2: are the rivers independent forcings? "
                 "Only separable where they are not collinear.", y=1.0)
    fig.savefig(f"{sk.FIGS}/fig13_river_independence.png", dpi=165,
                facecolor="white", bbox_inches="tight")
    C.to_csv(f"{sk.DATA}/../docs/river_correlation_matrix.csv")
    print("wrote fig13")

    # =================== FIG 14: what the ocean does ===================
    SER, GRID = {}, {}
    for var, fn, lab, logit in BANDS:
        SER[var], GRID[var] = region_series(fn, var)
    fig = plt.figure(figsize=(14, 8.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[2.3, 1], hspace=0.3, wspace=0.2)
    for k, (var, fn, lab, logit) in enumerate(BANDS):
        ax = fig.add_subplot(gs[k, 0])
        for nm in REGIONS:
            s = SER[var][nm].dropna()
            # ocean colour only exists Jun-Sep here; break the line across the
            # eight-month polar-night gap instead of drawing a ramp through it
            s = s.reindex(s.index.union(
                s.index[s.index.to_series().diff() > pd.Timedelta("30D")]
                - pd.Timedelta("1D")))
            ax.plot(s.index, s.values, "-", lw=0.7, color=REGIONS[nm]["c"],
                    label=nm if k == 0 else None)
        if logit:
            ax.set_yscale("log")
        ax.set_ylabel(lab, fontsize=8)
        if k == 0:
            ax.legend(fontsize=6.5, ncol=5, loc="upper center",
                      bbox_to_anchor=(0.5, 1.32))
            ax.set_title("(a-c) weekly optical time series by receiving basin, "
                         "2012-2026 (Jun-Sep only; no valid data otherwise)",
                         fontsize=9.5)
        ax2 = fig.add_subplot(gs[k, 1])
        for nm in REGIONS:
            s = SER[var][nm].dropna()
            b = s.groupby(s.index.isocalendar().week).median()
            ax2.plot(b.index * 7, b.values, "-o", ms=2.6,
                     color=REGIONS[nm]["c"])
        if logit:
            ax2.set_yscale("log")
        ax2.set_xlim(150, 285); ax2.set_ylabel(lab, fontsize=8)
        if k == 0:
            ax2.set_title("(d-f) seasonal climatology", fontsize=9.5)
        if k == 2:
            ax.set_xlabel("date"); ax2.set_xlabel("day of year")
    fig.suptitle("Fig 14 | STEP 3: what the receiving basins do. Chlorophyll "
                 "and the two turbidity proxies move together.", y=0.965)
    fig.savefig(f"{sk.FIGS}/fig14_ocean_timeseries.png", dpi=165,
                facecolor="white")
    print("wrote fig14")

    # =================== FIG 15: who drives what ===================
    g = sk.load_gauges("daily")
    kb = g[g.site_no == "15744500"].dropna(subset=["q_cms"]).copy()
    kb["t"] = kb.time.dt.tz_convert("UTC").dt.tz_localize(None)
    Qg = np.log10(kb.set_index("t").q_cms.resample("W").mean())

    forcings = {f"{r} (SWOT)": W[r] for r in W}
    forcings["Kobuk (gauge Q)"] = Qg

    rows = []
    for fname, fser in forcings.items():
        for nm in REGIONS:
            c = np.log10(SER["chlor_a"][nm].resample("W").mean())
            nl = SER["nLw_671"][nm].resample("W").mean()
            for lag in (1, 2):
                D = pd.concat([c.rename("c"), nl.rename("n"),
                               fser.shift(lag).rename("f")], axis=1).dropna()
                D = D[np.isin(D.index.month, [6, 7, 8, 9])]
                D = D[np.isfinite(D).all(axis=1)]
                if len(D) < 15:
                    continue
                raw = stats.pearsonr(D.f, D.c)
                rxy = raw.statistic
                rxz = stats.pearsonr(D.f, D.n).statistic
                ryz = stats.pearsonr(D.c, D.n).statistic
                den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
                pr = (rxy - rxz * ryz) / den if den > 0 else np.nan
                dof = len(D) - 3
                t = pr * np.sqrt(dof / (1 - pr ** 2)) if abs(pr) < 1 else np.inf
                pp = 2 * (1 - stats.t.cdf(abs(t), dof))
                rows.append(dict(forcing=fname, region=nm, lag=lag, n=len(D),
                                 r_raw=rxy, p_raw=raw.pvalue,
                                 r_partial=pr, p_partial=pp))
    A = pd.DataFrame(rows)
    A.to_csv(f"{sk.DATA}/../docs/attribution_matrix.csv", index=False)

    fig = plt.figure(figsize=(14, 6.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.25, 1], wspace=0.62)
    best = (A.sort_values("p_partial").groupby(["forcing", "region"]).first()
            .reset_index())
    alpha = 0.05 / len(A)
    for k, (col, ttl) in enumerate([("r_raw", "(a) raw correlation"),
                                    ("r_partial",
                                     "(b) controlling for nLw(671) sediment")]):
        ax = fig.add_subplot(gs[k])
        M = best.pivot(index="forcing", columns="region", values=col)
        M = M.reindex(columns=list(REGIONS))
        im = ax.imshow(M.values, cmap="RdBu_r", vmin=-0.5, vmax=0.5)
        ax.set_xticks(range(M.shape[1]))
        ax.set_xticklabels(M.columns, rotation=40, ha="right", fontsize=7.5)
        ax.set_yticks(range(M.shape[0]))
        ax.set_yticklabels(M.index, fontsize=7.5)
        N = best.pivot(index="forcing", columns="region", values="n").reindex(
            columns=list(REGIONS))
        P = best.pivot(index="forcing", columns="region",
                       values="p_partial" if col == "r_partial" else "p_raw"
                       ).reindex(columns=list(REGIONS))
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                v = M.values[i, j]
                if np.isfinite(v):
                    star = "*" if P.values[i, j] < alpha else ""
                    ax.text(j, i, f"{v:.2f}{star}", ha="center", va="center",
                            fontsize=6.8,
                            color="w" if abs(v) > 0.32 else "k")
        plt.colorbar(im, ax=ax, label="Pearson r", pad=0.04, shrink=0.72)
        ax.set_title(f"{ttl}\n* = survives Bonferroni (p<{alpha:.4f})",
                     fontsize=9)

    ax = fig.add_subplot(gs[2])
    ns = best.groupby("forcing").n.median().sort_values()
    ax.barh(range(len(ns)), ns.values, color="0.6", edgecolor="k", linewidth=0.5)
    ax.set_yticks(range(len(ns)))
    ax.set_yticklabels([x.replace(" (SWOT)", "").replace(" (gauge Q)", "\n(gauge)")
                        for x in ns.index], fontsize=7.5)
    ax.axvline(30, color="crimson", ls="--", lw=1.4, label="n=30")
    ax.set_xlabel("weekly points available")
    ax.set_title("(c) why only the gauge can answer this:\n"
                 "SWOT spans 4 summers, the gauge spans 15 years")
    ax.legend(fontsize=7.5)
    fig.suptitle("Fig 15 | STEP 4: who drives what. Rows are river forcings, "
                 "columns are receiving basins.", y=0.99)
    fig.savefig(f"{sk.FIGS}/fig15_attribution.png", dpi=165,
                facecolor="white", bbox_inches="tight")
    print("wrote fig15")

    print("\ninter-river correlation (weekly, May-Sep):")
    print(C.round(2).to_string())
    print(f"\nmedian off-diagonal r = {np.median(off):.2f}; "
          f"{hi}/{len(off)} pairs above 0.7")
    print("\nattribution, strongest lag per pair (partial, sediment removed):")
    print(best[["forcing", "region", "lag", "n", "r_raw", "r_partial",
                "p_partial"]].sort_values("p_partial").head(16).to_string(index=False))
    print(f"\nsurviving Bonferroni (alpha={alpha:.5f}): "
          f"{int((A.p_partial < alpha).sum())} of {len(A)}")


if __name__ == "__main__":
    main()
