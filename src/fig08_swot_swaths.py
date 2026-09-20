"""Figure 8 -- what SWOT actually measured over this basin.

These are renderings of the SWOT *vector* product: every 200 m node KaRIn
returned, positioned and coloured by its measurement.  They are not the
L2_HR_Raster image product, which is a gridded 100/250 m WSE and water-mask
raster and requires an Earthdata Login to download (see README).  What is shown
here is the same underlying KaRIn retrieval, aggregated to the SWORD
centreline.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import contextily as cx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj

import swotkot as sk
import spatial_hydrograph as sh

TO_M = pyproj.Transformer.from_crs(4326, 3857, always_xy=True)
LON, LAT = (-164.8, -155.2), (66.0, 68.5)


def merc(lon, lat):
    return TO_M.transform(np.asarray(lon), np.asarray(lat))


def frame(ax, zoom=7, basemap=True):
    x0, y0 = merc(LON[0], LAT[0]); x1, y1 = merc(LON[1], LAT[1])
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    if basemap:
        cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery,
                       crs="EPSG:3857", zoom=zoom, attribution_size=4)
        # mute the imagery so the SWOT measurements read as the signal
        ax.set_facecolor("k")
        for im in ax.get_images():
            im.set_alpha(0.55)
    for nm, (la, lo) in [("Kotzebue Sound", (66.55, -163.3)),
                         ("Hotham Inlet", (66.95, -161.5)),
                         ("Selawik Lake", (66.50, -160.5))]:
        mx, my = merc(lo, la)
        ax.annotate(nm, (mx, my), color="#d8e8ff", fontsize=6.8, style="italic",
                    ha="center", zorder=9)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    sk.mpl_setup()
    n = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    n = n[(n.node_q <= 1) & (n.ice_clim_f == 0) & n.wse.notna()]
    ninv = sk.load_inventory("nodes")
    xy = ninv.set_index("node_id")[["x", "y"]]
    n = n.join(xy, on="node_id")
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")

    fig = plt.figure(figsize=(14.5, 9.2))
    gs = fig.add_gridspec(2, 2, hspace=0.2, wspace=0.12)

    # ---- (a) one overpass, absolute WSE ---------------------------------
    cand = (n.groupby(["cycle_id", "pass_id"])
            .agg(k=("node_id", "nunique"), t=("time", "median")))
    best = cand.nlargest(1, "k").index[0]
    one = n[(n.cycle_id == best[0]) & (n.pass_id == best[1])]
    ax = fig.add_subplot(gs[0, 0]); frame(ax)
    mx, my = merc(one.x.values, one.y.values)
    sc = ax.scatter(mx, my, c=one.wse, s=4, cmap="turbo", vmin=0, vmax=250,
                    linewidths=0)
    plt.colorbar(sc, ax=ax, label="SWOT WSE (m, EGM2008)", pad=0.01, shrink=0.8)
    t = pd.Timestamp(cand.loc[best, "t"])
    ax.set_title(f"(a) A single SWOT overpass: cycle {best[0]}, pass {best[1]}, "
                 f"{t:%d %b %Y %H:%M} UTC\n{len(one):,} quality-passed 200 m "
                 f"nodes; colour is the measured water-surface elevation", fontsize=9.5,
                 loc="left")

    # ---- (b) same overpass, anomaly -------------------------------------
    ax = fig.add_subplot(gs[0, 1]); frame(ax)
    parts = []
    for riv in ["Kobuk", "Selawik", "Noatak"]:
        a = sh.anomaly(n, ref, best[0], best[1], riv)
        if len(a):
            parts.append(a)
    if parts:
        A = pd.concat(parts).join(xy, on="node_id", rsuffix="_i")
        A = A[A.eta.notna()]
        mx, my = merc(A.x.values, A.y.values)
        sc = ax.scatter(mx, my, c=A.eta, s=5, cmap="RdBu_r", vmin=-1.5, vmax=1.5,
                        linewidths=0)
        plt.colorbar(sc, ax=ax, label="WSE anomaly $\\eta$ (m)", pad=0.01,
                     shrink=0.8)
    ax.set_title("(b) The same overpass after removing the reference long "
                 "profile\nred = water above its normal level, blue = below",
                 fontsize=9.5, loc="left")

    # ---- (c) pass coverage ----------------------------------------------
    ax = fig.add_subplot(gs[1, 0]); frame(ax)
    passes = n.pass_id.value_counts()
    cmap = plt.get_cmap("tab20")
    for k, pid in enumerate(passes.index[:12]):
        s = n[n.pass_id == pid].drop_duplicates("node_id")
        mx, my = merc(s.x.values, s.y.values)
        ax.scatter(mx, my, s=3.2, color=cmap(k % 20), linewidths=0,
                   label=f"pass {pid} (n={passes[pid]:,})")
    ax.legend(fontsize=5.8, loc="lower left", ncol=3, framealpha=0.8,
              facecolor="black", labelcolor="white")
    ax.set_title(f"(c) SWOT ground-track passes crossing the basin\n"
                 f"{n.pass_id.nunique()} distinct passes give a ~1 day median "
                 "revisit despite the 21 day repeat", fontsize=9.5, loc="left")

    # ---- (d) observation density ----------------------------------------
    ax = fig.add_subplot(gs[1, 1]); frame(ax)
    cnt = n.groupby("node_id").size().rename("nobs")
    g = ninv.join(cnt, on="node_id").dropna(subset=["nobs"])
    mx, my = merc(g.x.values, g.y.values)
    sc = ax.scatter(mx, my, c=g.nobs, s=4, cmap="viridis", linewidths=0)
    plt.colorbar(sc, ax=ax, label="quality-passed observations per node",
                 pad=0.01, shrink=0.8)
    ax.set_title(f"(d) Observation count per 200 m node, 2023-2026\n"
                 f"{len(g):,} nodes, median {g.nobs.median():.0f} observations "
                 f"each, {int(g.nobs.sum()):,} total", fontsize=9.5, loc="left")

    fig.suptitle("SWOT KaRIn measurements over the Kotzebue Sound rivers "
                 "(vector product; L2_HR_Raster imagery needs an Earthdata login)",
                 fontsize=11.5, y=0.965)
    out = f"{sk.FIGS}/fig08_swot_swaths.png"
    fig.savefig(out, dpi=175, facecolor="white"); print("wrote", out)
    print(f"\nbest overpass: cycle {best[0]} pass {best[1]} at {t}")
    print(f"passes crossing basin: {n.pass_id.nunique()}")
    print(f"nodes with data: {len(g):,}; median obs/node {g.nobs.median():.0f}; "
          f"total {int(g.nobs.sum()):,}")


if __name__ == "__main__":
    main()
