"""Figure 17 -- the Kobuk delta, its distributary channels, Hotham Inlet and
Selawik Lake: where the river water actually goes.

Earlier figures deliberately excluded SWORD type 3 (lake-on-river) and type 5
(unreliable topology) reaches, because they broke the long-profile analysis.
But those are precisely the reaches that cross the Kobuk delta, Hotham Inlet
and Selawik Lake -- they are observed by SWOT, they just cannot be placed on a
clean one-dimensional profile.  Here they are the subject rather than the
nuisance.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import swotkot as sk

BOX = dict(lon=(-162.6, -159.6), lat=(66.30, 67.20))
TYPE_C = {1: "#2a7f62", 3: "#3f7fc1", 5: "#d9a441", 6: "#b5453b"}
TYPE_L = {1: "river", 3: "lake on river", 5: "unreliable topology",
          6: "ghost (unobserved)"}


def load_all():
    a = pd.read_parquet(f"{sk.DATA}/swot/reach_timeseries.parquet")
    p = f"{sk.DATA}/swot/extra_channel_timeseries.parquet"
    if os.path.exists(p):
        b = pd.read_parquet(p)
        a = pd.concat([a, b], ignore_index=True)
    a = a[a.wse.notna() & (a.reach_q <= 1) & (a.ice_clim_f == 0)]
    # robust per-reach outlier rejection, as elsewhere
    g = a.groupby("reach_id").wse
    med, mad = g.transform("median"), g.transform(
        lambda s: (s - s.median()).abs().median())
    lim = np.maximum(3.0, 4.0 * 1.4826 * mad.fillna(0))
    return a[(a.wse - med).abs() <= lim]


def main():
    sk.mpl_setup()
    box = pd.read_csv(f"{sk.DATA}/aux/hotham_box_reaches.csv")
    ts = load_all()
    ninv = sk.load_inventory("nodes")

    fig = plt.figure(figsize=(14, 9.2))
    gs = fig.add_gridspec(2, 3, hspace=0.36, wspace=0.3,
                          width_ratios=[1.15, 1, 1])

    # ---- (a) the delta map ----------------------------------------------
    ax = fig.add_subplot(gs[:, 0])
    ax.scatter(ninv.x, ninv.y, s=0.6, c="0.9", linewidths=0)
    for t, c in TYPE_C.items():
        s = box[box.type == t]
        ax.scatter(s.x, s.y, s=44, color=c, edgecolor="k", linewidth=0.4,
                   label=f"{t}: {TYPE_L[t]} (n={len(s)})", zorder=3)
    obs = set(ts.reach_id.unique())
    s = box[box.reach_id.isin(obs)]
    ax.scatter(s.x, s.y, s=9, color="w", zorder=4)
    for nm, (la, lo) in {"Hotham Inlet": (67.02, -161.45),
                         "Selawik Lake": (66.44, -160.50),
                         "Kotzebue": (66.898, -162.597),
                         "Kiana": (66.974, -160.428)}.items():
        ax.annotate(nm, (lo, la), fontsize=8, style="italic", color="#2f4858",
                    ha="center", zorder=6)
    ax.set_xlim(*BOX["lon"]); ax.set_ylim(*BOX["lat"])
    ax.set_aspect(1 / np.cos(np.radians(66.8)))
    ax.set_xlabel("longitude ($^\\circ$E)"); ax.set_ylabel("latitude ($^\\circ$N)")
    ax.set_title("(a) Every SWORD reach around the Kobuk delta,\n"
                 "Hotham Inlet and Selawik Lake. White dot = SWOT observes it.",
                 fontsize=9.5)
    ax.legend(fontsize=6.6, loc="lower left")

    # ---- (b) flow splitting through the delta ---------------------------
    ax = fig.add_subplot(gs[0, 1])
    kob = box[(box.mp == 7000490) & (box.type != 6)].sort_values("dist")
    ax.step(kob.dist, kob.facc, where="mid", color=sk.RIVER_COLORS["Kobuk"],
            lw=1.8)
    ax.scatter(kob.dist, kob.facc, s=34,
               c=[TYPE_C[t] for t in kob.type], edgecolor="k", linewidth=0.4,
               zorder=3)
    ax.invert_xaxis()
    ax.set_xlabel("distance to outlet (km)")
    ax.set_ylabel("SWORD facc (km$^2$)")
    ax.set_title("(b) The Kobuk delta splits flow\n"
                 "facc DROPS downstream as distributaries divide", fontsize=9.5)
    ax.annotate("31,315 km$^2$\nsingle channel", (kob.dist.max(), kob.facc.max()),
                fontsize=7.5, ha="right", color="0.3")
    ax.annotate("15,162 km$^2$\none delta arm", (kob.dist.min(), kob.facc.min()),
                fontsize=7.5, ha="left", va="bottom", color="0.3")

    # ---- (c) channel water levels ---------------------------------------
    ax = fig.add_subplot(gs[0, 2])
    groups = {"Kobuk main stem": (7000490, 1),
              "Kobuk delta arms": (7000490, 5),
              "Hotham channel A": (7001381, 5),
              "Hotham channel B": (7000383, 5)}
    cols = {"Kobuk main stem": "#1f6f8b", "Kobuk delta arms": "#7fb2c8",
            "Hotham channel A": "#d9a441", "Hotham channel B": "#b07d20"}
    rows = []
    for nm, (mp, t) in groups.items():
        ids = box[(box.mp == mp) & (box.type == t)].reach_id
        s = ts[ts.reach_id.isin(ids)]
        if not len(s):
            continue
        w = (s.groupby(s.time.dt.to_period("W").dt.start_time)
             .wse.median().rename(nm))
        ax.plot(w.index, w.values, "-", lw=1.1, color=cols[nm],
                label=f"{nm} (n={len(s)})")
        rows.append(dict(group=nm, n_reach=s.reach_id.nunique(), n_obs=len(s),
                         wse_med=s.wse.median(), wse_std=s.wse.std(),
                         wse_range=s.wse.quantile(.95) - s.wse.quantile(.05)))
    ax.set_ylabel("SWOT WSE (m)")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7.5)
    ax.set_title("(c) Water level in the main stem vs the\n"
                 "delta and inlet channels", fontsize=9.5)
    ax.legend(fontsize=6.6)
    G = pd.DataFrame(rows)
    G.to_csv(f"{sk.DATA}/../docs/channel_groups.csv", index=False)

    # ---- (d) lake-flagged reaches = the inlet and the lake ---------------
    ax = fig.add_subplot(gs[1, 1])
    lake = box[(box.lakeflag == 3) & (box.type != 6)]
    hot = lake[(lake.y > 66.70) & (lake.x < -160.9)]
    sel = lake[(lake.y <= 66.70) | (lake.x >= -160.9)]
    for nm, sub, c in [("Hotham Inlet reaches", hot, "#d9a441"),
                       ("Selawik Lake reaches", sel, "#c1543a")]:
        s = ts[ts.reach_id.isin(sub.reach_id)]
        if not len(s):
            continue
        a = s.copy()
        a["anom"] = a.wse - a.groupby("reach_id").wse.transform("median")
        w = (a.groupby(a.time.dt.to_period("W").dt.start_time)
             .anom.median())
        ax.plot(w.index, w.values, "-o", ms=2.4, lw=0.9, color=c,
                label=f"{nm} ({sub.reach_id.nunique()} reaches, n={len(s)})")
    ax.axhline(0, color="k", lw=0.7)
    ax.set_ylabel("water-level anomaly (m)")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7.5)
    ax.set_title("(d) Hotham Inlet and Selawik Lake levels\n"
                 "from lake-flagged SWORD reaches", fontsize=9.5)
    ax.legend(fontsize=6.6)

    # ---- (e) does the inlet follow the river? ---------------------------
    ax = fig.add_subplot(gs[1, 2])
    from scipy import stats as st
    riv = ts[ts.river == "Kobuk"]
    riv = riv[riv.dist_out_km.between(90, 250)]
    ra = riv.copy()
    ra["anom"] = ra.wse - ra.groupby("reach_id").wse.transform("median")
    rw = ra.groupby(ra.time.dt.to_period("W").dt.start_time).anom.median()
    out = []
    for nm, sub, c in [("Hotham Inlet", hot, "#d9a441"),
                       ("Selawik Lake", sel, "#c1543a")]:
        s = ts[ts.reach_id.isin(sub.reach_id)]
        if not len(s):
            continue
        a = s.copy()
        a["anom"] = a.wse - a.groupby("reach_id").wse.transform("median")
        lw_ = a.groupby(a.time.dt.to_period("W").dt.start_time).anom.median()
        for lag in range(0, 4):
            D = pd.concat([rw.shift(lag).rename("r"), lw_.rename("l")],
                          axis=1).dropna()
            if len(D) < 12:
                continue
            r = st.pearsonr(D.r, D.l)
            out.append(dict(basin=nm, lag_w=lag, r=r.statistic, p=r.pvalue,
                            n=len(D)))
        g = pd.DataFrame([o for o in out if o["basin"] == nm])
        if len(g):
            ax.plot(g.lag_w, g.r, "-o", ms=5, color=c,
                    label=f"{nm} (n={g.n.iloc[0]})")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(0, 4))
    ax.set_xlabel("lag: Kobuk stage leads (weeks)")
    ax.set_ylabel("r (river vs basin level)")
    ax.set_title("(e) The inlet tracks the river;\nthe lake is a weaker, slower link",
                 fontsize=9.5)
    ax.legend(fontsize=7)
    L = pd.DataFrame(out)
    L.to_csv(f"{sk.DATA}/../docs/inlet_lake_lag.csv", index=False)

    fig.suptitle("Where Kobuk water goes: main stem, delta distributaries, "
                 "Hotham Inlet, Selawik Lake", fontsize=11.5, y=0.975)
    o = f"{sk.FIGS}/fig17_channels_and_lakes.png"
    fig.savefig(o, dpi=170, facecolor="white"); print("wrote", o)
    print("\nchannel groups:"); print(G.to_string(index=False))
    print("\nriver-to-basin lag:"); print(L.to_string(index=False))


if __name__ == "__main__":
    main()
