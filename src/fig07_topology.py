"""Figure 7 -- how the three rivers were identified from SWORD network topology.

The Kotzebue Sound box contains 292 SWORD reaches belonging to 9 separate
drainage systems and 34 flow paths.  SWORD's `river_name` is NODATA over most
of the lower Kobuk, so names cannot do the selection.  Topology can:

  best_outlet    every reach carries the id of the outlet it drains to, which
                 partitions the box into independent drainage systems
  main_path_id   within a system, the reaches lying on one continuous flow path
  dist_out       along-network distance to that outlet, giving the ordering
  facc           upstream drainage area, giving the ranking
  rch_id_up/dn   explicit reach-to-reach connectivity, used to draw the graph
  type           1 river, 3 lake-on-river, 5 unreliable topology, 6 ghost
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import swotkot as sk

SWORD = f"{sk.DATA}/aux/na_sword_v17c.nc"
SELECTED = {7000490: "Kobuk", 7001633: "Selawik", 7000142: "Noatak",
            7002175: "Squirrel", 7000958: "Buckland", 7000081: "Wulik",
            7001381: "HothamInletChannel"}
TYPE_LABEL = {1: "river", 3: "lake on river", 5: "unreliable topology",
              6: "ghost (never observed)"}


def load_domain():
    d = nc.Dataset(SWORD)
    R = d.groups["reaches"]
    rid = R["reach_id"][:].astype(np.int64)
    x, y = np.asarray(R["x"][:]), np.asarray(R["y"][:])
    m = ((x > -165.6) & (x < -154.5) & (y > 65.4) & (y < 68.6) &
         ((rid // 100000000) == 813))
    i = np.where(m)[0]
    df = pd.DataFrame(dict(
        reach_id=rid[i], x=x[i], y=y[i],
        facc=np.asarray(R["facc"][:])[i],
        dist_out_km=np.asarray(R["dist_out"][:])[i] / 1e3,
        type=np.asarray(R["type"][:])[i],
        main_path_id=np.asarray(R["main_path_id"][:])[i].astype(np.int64),
        best_outlet=np.asarray(R["best_outlet"][:])[i].astype(np.int64),
        reach_length=np.asarray(R["reach_length"][:])[i],
        river_name=np.asarray(R["river_name"][:])[i],
        n_up=np.asarray(R["n_rch_up"][:])[i],
        end_reach=np.asarray(R["end_reach"][:])[i]))
    dn = np.asarray(R["rch_id_dn"][:])[:, i]          # (4, n)
    df["dn0"] = dn[0]
    return df, dn


def main():
    sk.mpl_setup()
    df, dn = load_domain()
    df["river"] = df.main_path_id.map(SELECTED)
    print(f"domain reaches: {len(df)}; drainage systems (best_outlet): "
          f"{df.best_outlet.nunique()}; flow paths (main_path_id): "
          f"{df.main_path_id.nunique()}")

    fig = plt.figure(figsize=(14.5, 9.6))
    gs = fig.add_gridspec(2, 3, hspace=0.32, wspace=0.26,
                          height_ratios=[1, 0.92])

    # ---- (a) drainage systems from best_outlet --------------------------
    ax = fig.add_subplot(gs[0, 0])
    outs = df.best_outlet.value_counts()
    cmap = plt.get_cmap("tab10")
    for k, (o, cnt) in enumerate(outs.items()):
        s = df[df.best_outlet == o]
        ax.scatter(s.x, s.y, s=13, color=cmap(k % 10),
                   label=f"{o} (n={cnt})", linewidths=0)
        # mark the outlet reach itself
        t = s.nsmallest(1, "dist_out_km")
        ax.plot(t.x, t.y, "v", ms=9, mfc="none", mec=cmap(k % 10), mew=1.6)
    ax.set_aspect(1 / np.cos(np.radians(67)))
    ax.set_xlabel("longitude ($^\\circ$E)"); ax.set_ylabel("latitude ($^\\circ$N)")
    ax.set_title("(a) Step 1 - partition by `best_outlet`\n"
                 f"{len(df)} reaches fall into {df.best_outlet.nunique()} "
                 "independent drainage systems")
    ax.legend(fontsize=5.6, loc="upper center", ncol=3, title="outlet reach id",
              title_fontsize=6, bbox_to_anchor=(0.5, -0.14))

    # ---- (b) ranking flow paths by drainage area ------------------------
    ax = fig.add_subplot(gs[0, 1])
    agg = (df.groupby("main_path_id")
           .agg(facc_max=("facc", "max"), n=("reach_id", "size"),
                len_km=("reach_length", lambda s: s.sum() / 1e3),
                name=("river_name", lambda s: s.mode().iat[0] if len(s.mode()) else "NODATA"))
           .sort_values("facc_max", ascending=False))
    agg["selected"] = agg.index.map(lambda p: SELECTED.get(p))
    # why each of the top paths was or was not carried, so the selection is
    # auditable rather than asserted
    tmaj = df.groupby("main_path_id").type.agg(lambda s: s.mode().iat[0])
    agg["dom_type"] = tmaj.reindex(agg.index)
    def reason(p, r):
        # r.selected is NaN (a float, and truthy) when unmapped -- test the type
        if isinstance(r.selected, str):
            return "carried"
        if r.dom_type == 5:
            return "delta/inlet channel, type 5"
        nm = (r["name"] or "")
        for riv in ("Selawik", "Noatak", "Kobuk"):
            if riv in nm:
                return f"headwater branch of {riv}"
        return "separate small basin" if r.facc_max < 4000 else "tributary"
    agg["reason"] = [reason(p, r) for p, r in agg.iterrows()]
    for p, r in agg.iterrows():
        c = sk.RIVER_COLORS.get(r.selected, "0.75") if r.selected else "0.78"
        ax.scatter(r.len_km, r.facc_max, s=34 + 2.0 * r.n, color=c,
                   edgecolor="k" if r.selected else "none", linewidth=0.6,
                   zorder=3 if r.selected else 2)
        if r.selected in ("Kobuk", "Selawik", "Noatak"):
            ax.annotate(r.selected, (r.len_km, r.facc_max),
                        textcoords="offset points", xytext=(7, 4),
                        fontsize=9, weight="bold",
                        color=sk.RIVER_COLORS[r.selected])
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("total flow-path length (km)")
    ax.set_ylabel("max upstream drainage area, facc (km$^2$)")
    ax.set_title("(b) Step 2 - rank the 34 flow paths\n"
                 "marker area $\\propto$ number of reaches")
    ax.legend(handles=[
        Line2D([], [], marker="o", ls="", color="0.78", label="not selected"),
        Line2D([], [], marker="o", ls="", color=sk.RIVER_COLORS["Kobuk"],
               mec="k", label="selected")], loc="lower right", fontsize=7.5)

    # ---- (c) reach connectivity graph -----------------------------------
    ax = fig.add_subplot(gs[0, 2])
    pos = df.set_index("reach_id")[["dist_out_km", "facc"]]
    for _, r in df.iterrows():
        if r.dn0 in pos.index:
            a = pos.loc[r.reach_id]; b = pos.loc[r.dn0]
            c = (sk.RIVER_COLORS.get(r.river, "0.8") if r.river else "0.86")
            ax.plot([a.dist_out_km, b.dist_out_km],
                    [max(a.facc, 1), max(b.facc, 1)], "-",
                    color=c, lw=1.6 if r.river in ("Kobuk", "Selawik", "Noatak") else 0.6,
                    zorder=3 if r.river else 1, alpha=0.95 if r.river else 0.6)
    conf = df[df.n_up >= 2]
    ax.scatter(conf.dist_out_km, conf.facc.clip(lower=1), s=16, c="k",
               marker="x", zorder=5, label=f"confluence (n={len(conf)})")
    ax.set_yscale("log")
    ax.set_xlabel("distance to outlet, `dist_out` (km)")
    ax.set_ylabel("facc (km$^2$)")
    ax.set_title("(c) Step 3 - reach connectivity from `rch_id_dn`\n"
                 "mainstems are continuous; tributaries branch off")
    ax.legend(fontsize=7, loc="lower left")

    # ---- (d) selected mainstems in map view -----------------------------
    ax = fig.add_subplot(gs[1, 0])
    ax.scatter(df.x, df.y, s=7, c="0.85", linewidths=0, label="not selected")
    for riv in ["Kobuk", "Selawik", "Noatak", "Squirrel", "Buckland", "Wulik"]:
        s = df[df.river == riv]
        ax.scatter(s.x, s.y, s=17, color=sk.RIVER_COLORS[riv], label=riv,
                   linewidths=0)
    ax.set_aspect(1 / np.cos(np.radians(67)))
    ax.set_xlabel("longitude ($^\\circ$E)"); ax.set_ylabel("latitude ($^\\circ$N)")
    ax.set_title("(d) Step 4 - the selected flow paths\n"
                 "grey = Koyukuk/Yukon and small coastal basins, excluded")
    ax.legend(fontsize=6.6, loc="lower left", ncol=2, framealpha=0.85,
              frameon=True)

    # ---- (e) reach type along the three mainstems -----------------------
    ax = fig.add_subplot(gs[1, 1])
    yy = {"Kobuk": 2, "Noatak": 1, "Selawik": 0}
    tcol = {1: "#2a7f62", 3: "#3f7fc1", 5: "#d9a441", 6: "#b5453b"}
    for riv, yv in yy.items():
        s = df[df.river == riv].sort_values("dist_out_km")
        for _, r in s.iterrows():
            ax.barh(yv, r.reach_length / 1e3, left=r.dist_out_km,
                    height=0.55, color=tcol.get(int(r.type), "k"),
                    edgecolor="none")
    ax.set_yticks(list(yy.values())); ax.set_yticklabels(list(yy))
    ax.set_xlabel("distance to outlet (km)")
    ax.set_title("(e) Step 5 - SWORD reach `type` along each mainstem\n"
                 "types 3/5/6 near the outlets are why profiles start inland")
    ax.set_ylim(-0.6, 2.95)
    ax.legend(handles=[Line2D([], [], lw=6, color=tcol[k],
                              label=f"{k}: {TYPE_LABEL[k]}") for k in (1, 3, 5, 6)],
              fontsize=6.6, loc="upper center", ncol=2, framealpha=0.9,
              frameon=True)

    # ---- (f) the selection table ----------------------------------------
    ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
    rows = [["path id", "name in SWORD", "n", "km", "facc km2", "outcome"]]
    keep = []
    for p, r in agg.head(12).iterrows():
        sel = r.selected if isinstance(r.selected, str) else None
        keep.append(sel is not None)
        rows.append([str(p), (r["name"] or "NODATA")[:15], f"{r.n:d}",
                     f"{r.len_km:.0f}", f"{r.facc_max:.0f}",
                     sel if sel else r.reason[:24]])
    tb = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center",
                  cellLoc="left", colWidths=[.16, .24, .07, .09, .15, .29])
    tb.auto_set_font_size(False); tb.set_fontsize(6.3); tb.scale(1, 1.34)
    for j in range(len(rows[0])):
        tb[0, j].set_facecolor("#dfe6ec"); tb[0, j].set_text_props(weight="bold")
    for i2, k in enumerate(keep, start=1):
        for j in range(len(rows[0])):
            tb[i2, j].set_facecolor("#fdf3d8" if k else "white")
    ax.set_title("(f) top 12 flow paths by drainage area\n"
                 "highlighted rows were carried into the analysis", fontsize=9)

    fig.suptitle("Identifying the Kotzebue Sound rivers from SWORD network "
                 "topology, not from names\n"
                 "`river_name` is NODATA for 111 of 292 domain reaches, "
                 "including most of the lower Kobuk", fontsize=11, y=0.985)
    out = f"{sk.FIGS}/fig07_network_topology.png"
    fig.savefig(out, dpi=175, facecolor="white"); print("wrote", out)

    agg.to_csv(f"{sk.DATA}/../docs/flow_path_selection.csv")
    print("\nflow-path selection table (top 12 by facc):")
    print(agg.head(12).to_string())
    print("\nreach types on the three mainstems:")
    print(pd.crosstab(df[df.river.isin(['Kobuk','Selawik','Noatak'])].river,
                      df[df.river.isin(['Kobuk','Selawik','Noatak'])].type).to_string())


if __name__ == "__main__":
    main()
