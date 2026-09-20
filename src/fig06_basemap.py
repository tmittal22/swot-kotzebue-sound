"""Figure 6 -- the study area on satellite imagery, with everything labelled.

Orientation figure for a collaborator: where the rivers are, where they enter
the sound, which water bodies matter, and where the single active gauge sits.
Basemap is Esri World Imagery via contextily (no authentication).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import contextily as cx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyproj
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import swotkot as sk

TO_M = pyproj.Transformer.from_crs(4326, 3857, always_xy=True)

VILLAGES = {"Kotzebue": (66.898, -162.597), "Kiana": (66.974, -160.428),
            "Selawik": (66.600, -160.005), "Noatak": (67.571, -162.966),
            "Ambler": (67.086, -157.850), "Noorvik": (66.834, -161.043),
            "Kobuk": (66.912, -156.876), "Shungnak": (66.888, -157.140),
            "Buckland": (65.980, -161.128), "Deering": (66.070, -162.717)}

WATERS = {"KOTZEBUE SOUND": (66.55, -163.55), "Hotham Inlet": (66.95, -161.55),
          "Selawik Lake": (66.51, -160.55), "Eschscholtz Bay": (66.20, -161.60),
          "CHUKCHI SEA": (67.35, -165.00)}

GAUGES = {"USGS 15744500\nKobuk at Kiana": (66.9736, -160.1308)}

PANELS = [
    ("(a) Kotzebue Sound drainage", (-166.2, -155.4), (65.5, 68.4), 7),
    ("(b) Hotham Inlet and Selawik Lake: where the Kobuk and\n"
     "    Selawik meet the sound", (-162.9, -159.6), (66.35, 67.25), 9),
]


def to_merc(lon, lat):
    return TO_M.transform(np.asarray(lon), np.asarray(lat))


def draw(ax, title, lonlim, latlim, zoom, ninv, label_villages=True):
    x0, y0 = to_merc(lonlim[0], latlim[0])
    x1, y1 = to_merc(lonlim[1], latlim[1])
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    cx.add_basemap(ax, source=cx.providers.Esri.WorldImagery, crs="EPSG:3857",
                   zoom=zoom, attribution_size=5)
    for riv in ["Kobuk", "Selawik", "Noatak", "Squirrel", "Buckland", "Wulik"]:
        s = ninv[ninv.river == riv]
        if not len(s):
            continue
        mx, my = to_merc(s.x.values, s.y.values)
        ax.scatter(mx, my, s=2.6, c=sk.RIVER_COLORS[riv], zorder=3,
                   linewidths=0, alpha=0.95)
    for nm, (la, lo) in WATERS.items():
        if not (lonlim[0] < lo < lonlim[1] and latlim[0] < la < latlim[1]):
            continue
        mx, my = to_merc(lo, la)
        ax.annotate(nm, (mx, my), color="#cfe8ff", fontsize=8.5,
                    style="italic", ha="center", zorder=6,
                    path_effects=None)
    if label_villages:
        for nm, (la, lo) in VILLAGES.items():
            if not (lonlim[0] < lo < lonlim[1] and latlim[0] < la < latlim[1]):
                continue
            mx, my = to_merc(lo, la)
            ax.plot(mx, my, "o", ms=4, mfc="white", mec="k", mew=0.7, zorder=5)
            ax.annotate(nm, (mx, my), textcoords="offset points", xytext=(5, 3),
                        fontsize=7.2, color="white", zorder=6)
    for nm, (la, lo) in GAUGES.items():
        if not (lonlim[0] < lo < lonlim[1] and latlim[0] < la < latlim[1]):
            continue
        mx, my = to_merc(lo, la)
        ax.plot(mx, my, "*", ms=17, mfc="gold", mec="k", mew=0.9, zorder=7)
        ax.annotate(nm, (mx, my), textcoords="offset points", xytext=(8, -16),
                    fontsize=7, color="gold", weight="bold", zorder=7)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=10, loc="left")
    # scale bar
    km = 100 if (lonlim[1] - lonlim[0]) > 5 else 50
    lat0 = np.mean(latlim)
    dx = km * 1000 / np.cos(np.radians(lat0))
    xs = x0 + 0.06 * (x1 - x0); ys = y0 + 0.07 * (y1 - y0)
    ax.plot([xs, xs + dx], [ys, ys], "-", color="white", lw=3, zorder=8)
    ax.annotate(f"{km} km", (xs + dx / 2, ys), textcoords="offset points",
                xytext=(0, 5), ha="center", color="white", fontsize=7.5, zorder=8)


def main():
    sk.mpl_setup()
    ninv = sk.load_inventory("nodes")

    fig = plt.figure(figsize=(14, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1], wspace=0.06)

    ax = fig.add_subplot(gs[0])
    draw(ax, PANELS[0][0], PANELS[0][1], PANELS[0][2], PANELS[0][3], ninv)
    # box showing panel b
    bx0, by0 = to_merc(PANELS[1][1][0], PANELS[1][2][0])
    bx1, by1 = to_merc(PANELS[1][1][1], PANELS[1][2][1])
    ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fill=False,
                           ec="yellow", lw=1.6, ls="--", zorder=8))
    ax.annotate("(b)", (bx1, by1), textcoords="offset points", xytext=(-16, -14),
                color="yellow", fontsize=10, weight="bold", zorder=8)
    handles = [Line2D([], [], marker="o", ls="", ms=5, color=sk.RIVER_COLORS[r],
                      label=r) for r in ["Kobuk", "Selawik", "Noatak",
                                         "Squirrel", "Buckland", "Wulik"]]
    handles += [Line2D([], [], marker="*", ls="", ms=12, mfc="gold", mec="k",
                       label="active USGS gauge"),
                Line2D([], [], marker="o", ls="", ms=5, mfc="white", mec="k",
                       label="community")]
    leg = ax.legend(handles=handles, loc="lower right", fontsize=7.5, ncol=2,
                    facecolor="black", framealpha=0.55, labelcolor="white")
    leg.set_zorder(9)

    ax2 = fig.add_subplot(gs[1])
    draw(ax2, PANELS[1][0], PANELS[1][1], PANELS[1][2], PANELS[1][3], ninv)
    ax2.annotate("Kobuk delta:\nflow splits among\ndistributaries",
                 to_merc(-161.15, 66.83), color="yellow", fontsize=7.5,
                 ha="center", zorder=8)

    fig.suptitle("Kotzebue Sound, northwest Alaska: SWOT-observed rivers on "
                 "Esri World Imagery\ncoloured dots are 200 m SWOT/SWORD nodes "
                 "(8,841 in the domain)", fontsize=11, y=0.99)
    out = f"{sk.FIGS}/fig06_satellite_basemap.png"
    fig.savefig(out, dpi=185, facecolor="white")
    print("wrote", out)


if __name__ == "__main__":
    main()
