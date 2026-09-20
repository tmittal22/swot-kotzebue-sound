"""Figures 21a-c -- one river at a time: where it is, its full 2-D field, and
how the two product versions compare on that river alone.

The combined three-river figure (fig19) is good for comparison but crowded.
These give each river a full panel with its own map, so a reader can see which
river is being discussed without cross-referencing.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

import swotkot as sk
import fig19_hovmoller as f19

RIVERS = {
    "Kobuk":   dict(tag="21a", note="Drains to Hotham Inlet through a multi-threaded delta."),
    "Selawik": dict(tag="21b", note="Drains to Selawik Lake. Falls only 4 m in 166 km."),
    "Noatak":  dict(tag="21c", note="Enters Kotzebue Sound directly at Kotzebue."),
}
PLACES = {"Kotzebue": (66.898, -162.597), "Kiana": (66.974, -160.428),
          "Selawik": (66.600, -160.005), "Noatak": (67.571, -162.966),
          "Ambler": (67.086, -157.850)}


def main():
    sk.mpl_setup()
    n = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    n = n[(n.node_q <= 1) & (n.ice_clim_f == 0) & n.wse.notna()]
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")
    inv = sk.load_inventory()
    ninv = sk.load_inventory("nodes")
    rch = sk.load_reaches()
    v2 = pd.read_parquet(f"{sk.DATA}/swot/sos_discharge.parquet")
    v2 = v2[(v2.reach_q <= 1) & (v2.ice_clim_f == 0) & v2.wse.notna()]
    t0 = pd.Timestamp("2023-01-01", tz="UTC")

    for riv, meta in RIVERS.items():
        M, tb, db, a = f19.grid_river(n, ref, riv)
        fig = plt.figure(figsize=(14, 7.8))
        gs = fig.add_gridspec(2, 3, width_ratios=[1.45, 2.3, 0.72],
                              height_ratios=[1.35, 1], hspace=0.32, wspace=0.25)

        # ---- map -------------------------------------------------------
        ax = fig.add_subplot(gs[:, 0])
        ax.scatter(ninv.x, ninv.y, s=0.7, c="0.88", linewidths=0)
        sub = ninv[ninv.river == riv]
        sc = ax.scatter(sub.x, sub.y, s=5, c=sub.dist_out_km, cmap="viridis",
                        linewidths=0, zorder=3)
        cb = plt.colorbar(sc, ax=ax, orientation="horizontal", pad=0.11,
                          fraction=0.045)
        cb.set_label("distance upstream (km)", fontsize=8)
        cb.ax.tick_params(labelsize=7)
        for nm, (la, lo) in PLACES.items():
            ax.plot(lo, la, "s", ms=3.5, color="k", zorder=4)
            ax.annotate(nm, (lo, la), textcoords="offset points", xytext=(4, 3),
                        fontsize=7, zorder=5)
        ax.plot(-160.1308, 66.9736, "*", ms=14, mfc="gold", mec="k", mew=0.8, zorder=6)
        # zoom to this river plus padding, so it fills the panel
        px = 0.55; py = 0.35
        ax.set_xlim(sub.x.min() - px, sub.x.max() + px)
        ax.set_ylim(sub.y.min() - py, sub.y.max() + py)
        ax.set_aspect(1 / np.cos(np.radians(67)))
        ax.set_xlabel("longitude ($^\\circ$E)"); ax.set_ylabel("latitude ($^\\circ$N)")
        ax.set_title(f"(a) Where the {riv} is\ncolour = distance upstream, "
                     "matching (b)", fontsize=9.5)

        # ---- 2-D field -------------------------------------------------
        ax = fig.add_subplot(gs[0, 1])
        dates = [t0 + pd.Timedelta(days=float(x)) for x in tb]
        pm = ax.pcolormesh(dates, db, M, cmap="RdBu_r",
                           norm=TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5),
                           shading="auto", rasterized=True)
        cb = plt.colorbar(pm, ax=ax, pad=0.01, fraction=0.035)
        cb.set_label("WSE anomaly $\\eta$ (m)", fontsize=8)
        ax.set_ylabel("distance upstream (km)")
        ax.set_xlim(t0, pd.Timestamp("2026-10-01", tz="UTC"))
        ax.set_xticklabels([])
        filled = float(np.isfinite(M).mean())
        ax.set_title(f"(b) {riv}: every SWOT node observation, "
                     f"{len(a):,} records\n"
                     f"10 km x 4 day grid, {filled*100:.0f}% filled", fontsize=9.5)

        # ---- basin stage index under it ---------------------------------
        ax2 = fig.add_subplot(gs[1, 1])
        s = rch[rch.river == riv].copy()
        s["an"] = s.wse - s.groupby("reach_id").wse.transform("median")
        w = (s.groupby(["cycle_id", "pass_id"])
             .agg(time=("time", "median"), an=("an", "median")).reset_index()
             .sort_values("time"))
        w.loc[w.time.diff() > pd.Timedelta("40D"), "an"] = np.nan
        ax2.plot(w.time, w.an, "-o", ms=2.2, lw=0.8, color=sk.RIVER_COLORS[riv])
        ax2.axhline(0, color="k", lw=0.7)
        ax2.set_xlim(t0, pd.Timestamp("2026-10-01", tz="UTC"))
        ax2.set_ylabel("basin stage\nanomaly (m)", fontsize=8.5)
        ax2.set_xlabel("date")
        ax2.set_title("(c) The same record collapsed to one number per overpass "
                      "— what a conventional gauge would give you", fontsize=9)

        # ---- structure + versions --------------------------------------
        ax = fig.add_subplot(gs[0, 2])
        r = inv[(inv.river == riv) & (inv.type == 1)].sort_values("dist_out_km")
        ax.barh(r.dist_out_km, r.n_chan_max, height=7,
                color=np.where(r.n_chan_max > 1, "#c1543a", "#9fb8c4"))
        ax.axvline(1.5, color="k", lw=0.8, ls=":")
        ax.set_ylim(0, db.max()); ax.set_xlabel("n channels", fontsize=8)
        ax.set_yticklabels([])
        ax.set_title(f"(d) threading\n{(r.n_chan_max>1).mean()*100:.0f}% multi",
                     fontsize=8.5)
        ax.tick_params(labelsize=7)

        ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
        nD = int((rch.river == riv).sum())
        n2 = int((v2.river == riv).sum())
        rows = [["", "obs"],
                ["Version D", f"{nD:,}"],
                ["Version 2.0", f"{n2:,}"],
                ["nodes", f"{len(a):,}"],
                ["reaches", f"{len(r)}"],
                ["inflows", f"{int((np.abs(np.diff(r.facc.values))>0.05*r.facc.values[:-1]).sum())}"]]
        t = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center",
                     cellLoc="left", colWidths=[.55, .45])
        t.auto_set_font_size(False); t.set_fontsize(7.5); t.scale(1, 1.35)
        for j in range(2):
            t[0, j].set_facecolor("#0B2F4A"); t[0, j].set_text_props(
                weight="bold", color="w")
        ax.set_title("(e) coverage", fontsize=8.5)

        fig.suptitle(f"{riv} River — {meta['note']}", fontsize=12.5, y=0.975)
        o = f"{sk.FIGS}/fig{meta['tag']}_{riv.lower()}.png"
        fig.savefig(o, dpi=170, facecolor="white")
        print(f"wrote {o}  nodes={len(a):,} filled={filled*100:.0f}% "
              f"vD={nD:,} v2.0={n2:,}")


if __name__ == "__main__":
    main()
