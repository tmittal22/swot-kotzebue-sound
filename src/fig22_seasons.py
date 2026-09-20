"""Figures 22a-c -- season-by-season zoom, one figure per river.

The multi-year 2-D fields compress each open-water season into a narrow strip.
Zooming to one season per panel, on a common day-of-year axis, makes the
year-to-year differences directly comparable and shows the freshet and the
late-summer response at their real width.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

import swotkot as sk

RIVERS = {"Kobuk": "22a", "Selawik": "22b", "Noatak": "22c"}
YEARS = [2023, 2024, 2025, 2026]
DOY0, DOY1 = 135, 295
DKM, DDOY = 10.0, 3.0


def main():
    sk.mpl_setup()
    n = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    n = n[(n.node_q <= 1) & (n.ice_clim_f == 0) & n.wse.notna()]
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")
    gd = sk.load_gauges("daily")
    kb = gd[gd.site_no == "15744500"].dropna(subset=["q_cms"]).copy()
    kb["yr"] = kb.time.dt.year; kb["doy"] = kb.time.dt.dayofyear

    norm = TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5)
    for riv, tag in RIVERS.items():
        a = n[n.river == riv].merge(
            ref[["node_id", "wse_ref", "wse_mad", "width_med"]],
            on="node_id", how="inner")
        a = a[a.width_med >= 80]
        a["eta"] = a.wse - a.wse_ref
        lim = np.maximum(1.0, 4 * 1.4826 * a.wse_mad.fillna(0))
        a = a[a.eta.abs() <= lim]
        a["yr"] = a.time.dt.year
        a["doy"] = a.time.dt.dayofyear
        dmax = a.dist_out_km.max()

        fig = plt.figure(figsize=(14.5, 8.4))
        gs = fig.add_gridspec(2, 4, height_ratios=[3.0, 1.0], hspace=0.28,
                              wspace=0.16)
        db = np.arange(0, dmax + DKM, DKM)
        tb = np.arange(DOY0, DOY1 + DDOY, DDOY)
        stats_rows = []
        for k, yr in enumerate(YEARS):
            s = a[(a.yr == yr) & a.doy.between(DOY0, DOY1)]
            ax = fig.add_subplot(gs[0, k])
            if len(s):
                s = s.copy()
                s["ti"] = np.digitize(s.doy, tb) - 1
                s["di"] = np.digitize(s.dist_out_km, db) - 1
                g = s.groupby(["di", "ti"]).eta.median()
                M = np.full((len(db), len(tb)), np.nan)
                for (di, ti), v in g.items():
                    if 0 <= di < len(db) and 0 <= ti < len(tb):
                        M[di, ti] = v
                pm = ax.pcolormesh(tb, db, M, cmap="RdBu_r", norm=norm,
                                   shading="auto", rasterized=True)
                peak = s.groupby("doy").eta.median()
                if len(peak) > 3:
                    ax.axvline(int(peak.idxmax()), color="k", lw=1.2, ls="--")
                    ax.annotate(f"peak {int(peak.idxmax())}",
                                (int(peak.idxmax()), dmax * 0.97), fontsize=7.5,
                                rotation=90, va="top", ha="right")
                stats_rows.append(dict(year=yr, n=len(s),
                                       filled=float(np.isfinite(M).mean()),
                                       doy_peak=int(peak.idxmax()) if len(peak) > 3 else np.nan,
                                       eta_p95=float(s.eta.quantile(.95))))
            ax.axvspan(121, 196, color="tab:blue", alpha=0.05)
            ax.axvspan(197, 288, color="tab:orange", alpha=0.07)
            ax.set_xlim(DOY0, DOY1); ax.set_ylim(0, dmax)
            ax.set_title(f"{yr}" + ("  (truncated 16 Sep)" if yr == 2026 else ""),
                         fontsize=10.5)
            if k == 0:
                ax.set_ylabel("distance upstream (km)")
            else:
                ax.set_yticklabels([])
            ax.set_xticklabels([])

            # gauge context underneath (Kobuk only has one)
            axg = fig.add_subplot(gs[1, k])
            clim = kb[kb.yr < 2023].groupby("doy").q_cms.median()
            axg.plot(clim.index, clim.values, color="0.6", lw=1.0,
                     label="1977-2022 median" if k == 0 else None)
            y = kb[kb.yr == yr]
            axg.plot(y.doy, y.q_cms, color=sk.RIVER_COLORS["Kobuk"], lw=1.3,
                     label="that year" if k == 0 else None)
            axg.set_yscale("log"); axg.set_xlim(DOY0, DOY1)
            axg.set_xlabel("day of year")
            if k == 0:
                axg.set_ylabel("Kobuk gauge Q\n(m$^3$ s$^{-1}$)", fontsize=8.5)
                axg.legend(fontsize=7)
            else:
                axg.set_yticklabels([])

        cax = fig.add_axes([0.915, 0.42, 0.012, 0.42])
        cb = fig.colorbar(pm, cax=cax); cb.set_label("WSE anomaly $\\eta$ (m)",
                                                     fontsize=9)
        S = pd.DataFrame(stats_rows)
        S.to_csv(f"{sk.DATA}/../docs/season_zoom_{riv.lower()}.csv", index=False)
        fig.suptitle(f"{riv}: one open-water season per panel, common "
                     f"day-of-year axis\nblue band = nival window, orange = "
                     f"rain window; the bottom row is the single gauge, for context",
                     fontsize=11.5, y=0.975)
        o = f"{sk.FIGS}/fig{tag}_{riv.lower()}_seasons.png"
        fig.savefig(o, dpi=165, facecolor="white", bbox_inches="tight")
        print(f"wrote {o}")
        print(S.to_string(index=False))


if __name__ == "__main__":
    main()
