"""Figure 2 -- the Kotzebue Sound drainage as SWOT sees it, and the reference
long profiles that every later anomaly is measured against.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import swotkot as sk
import spatial_hydrograph as sh

PLACES = {"Kotzebue": (66.898, -162.597), "Kiana": (66.974, -160.428),
          "Selawik": (66.600, -160.005), "Noatak": (67.571, -162.966),
          "Ambler": (67.086, -157.850), "Buckland": (65.980, -161.128)}
WATERS = {"Hotham Inlet\n(Kobuk Lake)": (67.12, -161.45),
          "Selawik Lake": (66.44, -160.60),
          "Kotzebue Sound": (66.55, -163.60),
          "Eschscholtz\nBay": (66.10, -161.80)}
# offsets so village labels do not sit on top of the river they mark
LABEL_OFF = {"Kotzebue": (-34, -9), "Kiana": (2, 7), "Selawik": (4, -9),
             "Noatak": (-30, 4), "Ambler": (2, 5), "Buckland": (4, -9)}


def main():
    sk.mpl_setup()
    inv = sk.load_inventory()
    ninv = sk.load_inventory("nodes")
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")
    ref = ref.merge(ninv[["node_id", "x", "y"]], on="node_id", how="left")
    n = sk.load_nodes()

    fig = plt.figure(figsize=(12.5, 8.4))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.55, 1, 1], height_ratios=[1, 1],
                          hspace=0.3, wspace=0.28)

    # --- map ---------------------------------------------------------------
    ax = fig.add_subplot(gs[:, 0])
    obs = n.groupby("node_id").size().rename("nobs")
    nn = ninv.join(obs, on="node_id")
    ax.scatter(nn.x, nn.y, s=0.35, c="0.85", zorder=1)
    for riv in ["Kobuk", "Selawik", "Noatak"]:
        s = nn[(nn.river == riv) & nn.nobs.notna()]
        ax.scatter(s.x, s.y, s=0.9, c=sk.RIVER_COLORS[riv], zorder=2)
    for riv in ["Squirrel", "Buckland", "Wulik", "HothamInletChannel"]:
        s = ninv[ninv.river == riv]
        ax.scatter(s.x, s.y, s=0.5, c=sk.RIVER_COLORS[riv], alpha=0.8, zorder=2)

    g = sk.load_gauges("daily")
    sites = {"15744500": (66.9736, -160.1308), "15743850": (66.9456, -156.9118),
             "15747000": (67.8755, -163.6776)}
    for sid, (la, lo) in sites.items():
        ax.plot(lo, la, "*", ms=15, mfc="gold", mec="k", mew=0.8, zorder=5)
    for nm, (la, lo) in PLACES.items():
        ax.plot(lo, la, "s", ms=3.5, color="k", zorder=4)
        ax.annotate(nm, (lo, la), textcoords="offset points",
                    xytext=LABEL_OFF.get(nm, (4, 3)), fontsize=7.5, zorder=6)
    for nm, (la, lo) in WATERS.items():
        ax.annotate(nm, (lo, la), fontsize=7.5, style="italic", color="#2f4858",
                    ha="center", zorder=6)
    ax.set_xlim(-166.0, -154.8); ax.set_ylim(65.4, 68.7)
    ax.set_aspect(1 / np.cos(np.radians(67)))
    ax.set_xlabel("longitude ($^\\circ$E)"); ax.set_ylabel("latitude ($^\\circ$N)")
    ax.set_title("(a) SWOT-observed rivers draining to Kotzebue Sound\n"
                 "coloured nodes = quality-passed SWOT observations", pad=8)
    handles = [Line2D([], [], marker="o", ls="", color=sk.RIVER_COLORS[r], label=r)
               for r in ["Kobuk", "Selawik", "Noatak", "Squirrel", "Buckland", "Wulik"]]
    handles.append(Line2D([], [], marker="*", ls="", mfc="gold", mec="k", ms=12,
                          label="active USGS gauge"))
    ax.legend(handles=handles, loc="lower left", fontsize=7.5, ncol=2)

    # --- long profiles -----------------------------------------------------
    for k, riv in enumerate(["Kobuk", "Noatak", "Selawik"]):
        ax = fig.add_subplot(gs[0, 1] if k == 0 else gs[0, 2] if k == 1 else gs[1, 1])
        r = ref[ref.river == riv].sort_values("dist_out_km")
        ax.plot(r.dist_out_km, r.wse_ref_raw, ".", ms=1.2, color="0.75",
                label="node median")
        ax.plot(r.dist_out_km, r.wse_ref, "-", lw=1.3,
                color=sk.RIVER_COLORS[riv], label="5 km running median")
        ax.set_xlabel("distance upstream from outlet (km)")
        ax.set_ylabel("reference WSE (m)")
        rise = r.wse_ref.max() - r.wse_ref.min()
        span = r.dist_out_km.max()
        ax.set_title(f"({'bcd'[k]}) {riv}: {rise:.0f} m over {span:.0f} km\n"
                     f"mean slope {rise/span*100:.1f} cm km$^{{-1}}$", fontsize=9)
        ax.legend(loc="upper left")

    # --- revisit interval --------------------------------------------------
    # Count gaps between distinct observation DAYS, not between (cycle, pass)
    # records: several passes cross these rivers on the same day, and counting
    # those as revisits would report a 1-day revisit everywhere.  The 2023
    # calibration phase used a 1-day repeat orbit (cycle_id >= 400) and is
    # separated out, since it is not representative of the science mission.
    ax = fig.add_subplot(gs[1, 2])
    rows = []
    for riv in ["Kobuk", "Selawik", "Noatak"]:
        s_ = n[(n.river == riv) & (n.cycle_id < 400)]
        days = np.sort(s_.time.dt.floor("D").unique())
        gap = np.diff(days) / np.timedelta64(1, "D")
        gap = gap[gap < 30]
        ax.hist(gap, bins=np.arange(0.5, 15.5, 1), histtype="step", lw=1.6,
                color=sk.RIVER_COLORS[riv],
                label=f"{riv}: median {np.median(gap):.0f} d, "
                      f"90th pct {np.percentile(gap, 90):.0f} d")
        cal = n[(n.river == riv) & (n.cycle_id >= 400)]
        rows.append(dict(river=riv, median_gap_d=float(np.median(gap)),
                         p90_gap_d=float(np.percentile(gap, 90)),
                         n_science_days=len(days),
                         n_calval_days=int(cal.time.dt.floor("D").nunique())))
    ax.set_xlabel("days between successive observation days")
    ax.set_ylabel("count")
    ax.set_title("(e) revisit interval, science orbit,\nice-free and quality-passed")
    ax.legend(loc="upper right", fontsize=7)
    rv = pd.DataFrame(rows)
    rv.to_csv(f"{sk.DATA}/../docs/revisit_stats.csv", index=False)
    print("\nrevisit statistics (science orbit):")
    print(rv.to_string(index=False))

    out = f"{sk.FIGS}/fig02_domain_and_profiles.png"
    fig.savefig(out); print("wrote", out)

    print("\nlong-profile summary:")
    for riv in ["Kobuk", "Noatak", "Selawik"]:
        r = ref[ref.river == riv]
        rise = r.wse_ref.max() - r.wse_ref.min(); span = r.dist_out_km.max()
        print(f"  {riv:8s} rise {rise:6.1f} m over {span:5.0f} km -> "
              f"{rise/span*100:5.1f} cm/km")


if __name__ == "__main__":
    main()
