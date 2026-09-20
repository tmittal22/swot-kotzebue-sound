"""Figure 18 -- comparing SWOT product versions on identical reaches.

Two processing versions of the same KaRIn observations are available:

  Version D    SWORD v17b, current reprocessing, runs to Sep 2026
  Version 2.0  SWORD v16, older, stops in 2025, but is the ONLY version
               carrying the SoS discharge fields

Because the official v17b->v16 reach translation maps all 162 domain reaches,
the same physical reach can be compared directly between versions.  That is the
cleanest available check on how much the reprocessing moved things.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import swotkot as sk


def main():
    sk.mpl_setup()
    vd = sk.load_reaches()                                   # Version D
    v2 = pd.read_parquet(f"{sk.DATA}/swot/sos_discharge.parquet")  # Version 2.0
    v2 = v2[(v2.reach_q <= 1) & (v2.ice_clim_f == 0) & v2.wse.notna()]

    # match on reach_id (v17b) + observation time
    a = vd[["reach_id", "time", "wse", "width", "slope", "river",
            "dist_out_km"]].rename(columns={"wse": "wse_D", "width": "w_D",
                                            "slope": "s_D"})
    b = v2[["reach_id", "time", "wse", "width", "slope"]].rename(
        columns={"wse": "wse_2", "width": "w_2", "slope": "s_2"})
    m = pd.merge_asof(a.sort_values("time"), b.sort_values("time"),
                      on="time", by="reach_id", direction="nearest",
                      tolerance=pd.Timedelta("30min")).dropna(subset=["wse_2"])
    print(f"matched observations across versions: {len(m)} "
          f"on {m.reach_id.nunique()} reaches")

    fig = plt.figure(figsize=(13.5, 8.6))
    gs = fig.add_gridspec(2, 3, hspace=0.36, wspace=0.3)

    # (a) WSE agreement
    ax = fig.add_subplot(gs[0, 0])
    d = m.wse_D - m.wse_2
    ax.scatter(m.wse_2, m.wse_D, s=5, alpha=0.25,
               c=[sk.RIVER_COLORS.get(r, "0.5") for r in m.river], linewidths=0)
    lim = [m[["wse_D", "wse_2"]].min().min(), m[["wse_D", "wse_2"]].max().max()]
    ax.plot(lim, lim, "k--", lw=1)
    r = stats.pearsonr(m.wse_2, m.wse_D)
    ax.set_xlabel("Version 2.0 WSE (m)"); ax.set_ylabel("Version D WSE (m)")
    ax.set_title(f"(a) WSE: r = {r.statistic:.4f}\n"
                 f"median difference {d.median()*100:+.1f} cm", fontsize=9.5)

    # (b) difference distribution
    ax = fig.add_subplot(gs[0, 1])
    ax.hist(d.clip(-2, 2), bins=np.arange(-2, 2.05, 0.1), color="#1f6f8b",
            edgecolor="k", linewidth=0.3)
    ax.axvline(0, color="k", lw=1)
    ax.set_xlabel("Version D minus Version 2.0 WSE (m)")
    ax.set_ylabel("count")
    within = float((d.abs() < 0.10).mean())
    ax.set_title(f"(b) {within*100:.0f}% agree within 10 cm\n"
                 f"std {d.std():.2f} m, 95th pct |diff| {d.abs().quantile(.95):.2f} m",
                 fontsize=9.5)

    # (c) width and slope are much less stable
    ax = fig.add_subplot(gs[0, 2])
    rows = []
    for lab, x, y in [("WSE", m.wse_2, m.wse_D), ("width", m.w_2, m.w_D),
                      ("slope", m.s_2, m.s_D)]:
        ok = np.isfinite(x) & np.isfinite(y)
        rr = stats.pearsonr(x[ok], y[ok])
        rel = ((y[ok] - x[ok]).abs() / x[ok].abs().replace(0, np.nan)).median()
        rows.append(dict(field=lab, r=rr.statistic, n=int(ok.sum()),
                         median_rel_diff=float(rel)))
    V = pd.DataFrame(rows)
    ax.barh(V.field, V.r, color=["#1f6f8b", "#c1543a", "#4f7942"],
            edgecolor="k", linewidth=0.5)
    for i, row in V.iterrows():
        ax.text(row.r - 0.02, i, f"r={row.r:.3f}", va="center", ha="right",
                color="w", fontsize=9, weight="bold")
    ax.set_xlim(0, 1.05); ax.set_xlabel("correlation between versions")
    ax.set_title("(c) Elevation is stable across versions;\n"
                 "width and slope are not", fontsize=9.5)
    V.to_csv(f"{sk.DATA}/../docs/version_comparison.csv", index=False)

    # (d) does the difference depend on river?
    ax = fig.add_subplot(gs[1, 0])
    m["dif"] = d
    order = ["Noatak", "Kobuk", "Selawik", "Squirrel", "Buckland", "Wulik"]
    keep = [o for o in order if o in set(m.river)]
    ax.boxplot([m[m.river == o].dif.clip(-2, 2).dropna() for o in keep],
               labels=keep, showfliers=False,
               medianprops=dict(color="crimson", lw=1.6))
    ax.axhline(0, color="k", lw=0.8)
    ax.tick_params(axis="x", labelrotation=35, labelsize=8)
    ax.set_ylabel("Version D $-$ Version 2.0 WSE (m)")
    ax.set_title("(d) Reprocessing shifted every river the same way", fontsize=9.5)

    # (e) record length is the real difference
    ax = fig.add_subplot(gs[1, 1])
    for nm, s, c in [("Version D (SWORD v17b)", vd, "#1f6f8b"),
                     ("Version 2.0 (SWORD v16)", v2, "#c1543a")]:
        mo = s.groupby(s.time.dt.to_period("M").dt.to_timestamp()).size()
        ax.plot(mo.index, mo.values, "-", lw=1.5, color=c, label=nm)
    ax.set_ylabel("quality-passed observations per month")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7.5)
    ax.set_title("(e) Version 2.0 stops in 2025 — but it is the only\n"
                 "version carrying SoS discharge", fontsize=9.5)
    ax.legend(fontsize=7.5)

    # (f) what the version choice costs you
    ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
    tbl = [["", "Version D", "Version 2.0"],
           ["SWORD", "v17b", "v16"],
           ["Record ends", str(vd.time.max().date()), str(v2.time.max().date())],
           ["Observations", f"{len(vd):,}", f"{len(v2):,}"],
           ["SoS discharge", "no", "yes"],
           ["Node products", "yes", "yes"],
           ["Used here for", "everything", "discharge only"]]
    t = ax.table(cellText=tbl[1:], colLabels=tbl[0], loc="center",
                 cellLoc="left", colWidths=[.34, .33, .33])
    t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.5)
    for j in range(3):
        t[0, j].set_facecolor("#0B2F4A"); t[0, j].set_text_props(
            weight="bold", color="w")
    ax.set_title("(f) Choosing a version is a trade\n"
                 "between record length and discharge", fontsize=9.5)

    fig.suptitle("SWOT Version D vs Version 2.0 on identical reaches, "
                 "matched within 30 minutes", fontsize=11.5, y=0.97)
    o = f"{sk.FIGS}/fig18_version_comparison.png"
    fig.savefig(o, dpi=170, facecolor="white"); print("wrote", o)
    print("\nbetween-version agreement:")
    print(V.to_string(index=False))
    print(f"\nWSE difference: median {d.median()*100:+.1f} cm, "
          f"std {d.std():.2f} m, {within*100:.0f}% within 10 cm")


if __name__ == "__main__":
    main()
