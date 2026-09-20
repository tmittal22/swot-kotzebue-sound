"""Figure 20 -- which distributary actually carries the Kobuk into Hotham Inlet?

SWOT measures no discharge per channel, so this cannot be answered directly.
What it can do is rank the channels on four independent proxies, each with a
stated assumption, and see whether they agree.

  1 facc        SWORD's drainage-area attribution to each channel.  Mass-based,
                but it is an attribution by the network algorithm, not a
                measurement.
  2 width       Flow splits broadly with conveyance, and width is its most
                visible component.  Weak here: SWOT width is 8% unstable
                between versions and aggregates across threads.
  3 amplitude   A channel carrying a large share of the flow should swing
                further in stage as the upstream hydrograph moves.  A minor or
                blind channel is backwater-dominated and damped.
  4 coupling    Correlation with upstream main-stem stage.  A primary
                conveyance channel tracks the river; a marginal one tracks the
                inlet instead.

None is a discharge.  Agreement across four independent proxies is the
argument; a single proxy would not be.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import swotkot as sk
import fig17_channels_lakes as f17

# the distributary / inlet flow paths, from SWORD main_path_id
PATHS = {7000490: "Kobuk main + arms", 7001381: "Hotham channel A",
         7000383: "Hotham channel B", 7003121: "minor inlet channel"}


def main():
    sk.mpl_setup()
    box = pd.read_csv(f"{sk.DATA}/aux/hotham_box_reaches.csv")
    ts = f17.load_all()
    inv = sk.load_inventory()

    # upstream forcing: Kobuk main stem well above the delta
    up = ts[(ts.river == "Kobuk") & (ts.dist_out_km.between(100, 260))].copy()
    up["a"] = up.wse - up.groupby("reach_id").wse.transform("median")
    upw = up.groupby(up.time.dt.to_period("W").dt.start_time).a.median()

    rows = []
    for _, r in box[(box.type != 6)].iterrows():
        s = ts[ts.reach_id == int(r.reach_id)]
        if len(s) < 40:
            continue
        a = s.copy()
        a["an"] = a.wse - a.wse.median()
        w = a.groupby(a.time.dt.to_period("W").dt.start_time).an.median()
        D = pd.concat([w.rename("c"), upw.rename("u")], axis=1).dropna()
        if len(D) < 15:
            continue
        rows.append(dict(
            reach_id=int(r.reach_id), path=PATHS.get(int(r.mp), f"other {int(r.mp)}"),
            mp=int(r.mp), type=int(r.type), lon=r.x, lat=r.y,
            facc=r.facc, width=r.width, nchan=r.nch, dist=r.dist,
            wse_med=s.wse.median(),
            amp=float(s.wse.quantile(.95) - s.wse.quantile(.05)),
            coupling=float(stats.pearsonr(D.c, D.u).statistic), n=len(s)))
    C = pd.DataFrame(rows)
    C = C[C.path.str.contains("Kobuk|Hotham|minor")]
    C.to_csv(f"{sk.DATA}/../docs/channel_partition.csv", index=False)

    grp = (C.groupby("path")
           .agg(reaches=("reach_id", "size"), facc=("facc", "median"),
                width=("width", "median"), amp=("amp", "median"),
                coupling=("coupling", "median"), wse=("wse_med", "median"),
                n=("n", "sum"))
           .sort_values("facc", ascending=False))
    # normalised share on each proxy
    for c in ["facc", "width", "amp", "coupling"]:
        grp[c + "_share"] = grp[c].clip(lower=0) / grp[c].clip(lower=0).sum()

    fig = plt.figure(figsize=(14, 8.6))
    gs = fig.add_gridspec(2, 3, hspace=0.38, wspace=0.3)
    cols = {"Kobuk main + arms": "#1f6f8b", "Hotham channel A": "#d9a441",
            "Hotham channel B": "#b07d20", "minor inlet channel": "#9aa7ae"}

    # (a) map
    ax = fig.add_subplot(gs[0, 0])
    ninv = sk.load_inventory("nodes")
    ax.scatter(ninv.x, ninv.y, s=0.5, c="0.9", linewidths=0)
    for p, g in C.groupby("path"):
        ax.scatter(g.lon, g.lat, s=50, color=cols.get(p, "0.5"),
                   edgecolor="k", linewidth=0.4, label=p, zorder=3)
    for nm, (la, lo) in {"Hotham Inlet": (67.02, -161.45),
                         "Kotzebue": (66.898, -162.597)}.items():
        ax.annotate(nm, (lo, la), fontsize=8, style="italic", color="#2f4858")
    ax.set_xlim(-162.3, -160.2); ax.set_ylim(66.55, 67.15)
    ax.set_aspect(1 / np.cos(np.radians(66.8)))
    ax.set_xlabel("lon"); ax.set_ylabel("lat")
    ax.set_title("(a) The channels that reach Hotham Inlet", fontsize=9.5)
    ax.legend(fontsize=6.6, loc="lower left")

    # (b-e) the four proxies
    for k, (col, lab, note) in enumerate([
            ("facc_share", "drainage area (facc)", "mass-based, but an attribution"),
            ("width_share", "channel width", "8% version-unstable"),
            ("amp_share", "stage amplitude", "conveyance proxy"),
            ("coupling_share", "coupling to main stem", "connectivity proxy")]):
        ax = fig.add_subplot(gs[(k + 1) // 3, (k + 1) % 3])
        g = grp.sort_values(col, ascending=True)
        ax.barh(range(len(g)), g[col] * 100,
                color=[cols.get(i, "0.6") for i in g.index],
                edgecolor="k", linewidth=0.5)
        ax.set_yticks(range(len(g)))
        ax.set_yticklabels([i.replace(" ", "\n", 1) for i in g.index], fontsize=7.5)
        for i, v in enumerate(g[col]):
            ax.text(v * 100 + 1, i, f"{v*100:.0f}%", va="center", fontsize=8.5)
        ax.set_xlim(0, 100); ax.set_xlabel("share (%)")
        ax.set_title(f"({'bcde'[k]}) {lab}\n{note}", fontsize=9)

    # (f) agreement across proxies
    ax = fig.add_subplot(gs[1, 2])
    sh = grp[["facc_share", "width_share", "amp_share", "coupling_share"]] * 100
    x = np.arange(len(sh))
    for j, c in enumerate(sh.columns):
        ax.plot(x + (j - 1.5) * 0.12, sh[c], "o", ms=8, alpha=0.8,
                label=c.replace("_share", ""))
    ax.set_xticks(x)
    ax.set_xticklabels([i.replace(" ", "\n", 1) for i in sh.index], fontsize=7.5)
    ax.set_ylabel("share (%)")
    spread = (sh.max(axis=1) - sh.min(axis=1))
    ax.set_title(f"(f) Do the proxies agree?\nspread {spread.min():.0f}-"
                 f"{spread.max():.0f} percentage points", fontsize=9)
    ax.legend(fontsize=7)

    fig.suptitle("Which distributary carries the Kobuk into Hotham Inlet? "
                 "Four proxies, no discharge measurement", fontsize=11.5, y=0.97)
    o = f"{sk.FIGS}/fig20_channel_partition.png"
    fig.savefig(o, dpi=170, facecolor="white"); print("wrote", o)
    print("\nchannel groups:")
    print(grp.round(3).to_string())
    print("\nspread between proxies (percentage points):")
    print(spread.round(1).to_string())


if __name__ == "__main__":
    main()
