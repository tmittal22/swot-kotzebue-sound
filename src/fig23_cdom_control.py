"""Figure 23 -- the CDOM control: does the inner-sound signal survive when BOTH
optical contaminants are removed?

fig11 controlled for suspended sediment via nLw(671) and the inner-sound
discharge-chlorophyll correlation survived.  The stated residual limitation was
that nLw(671) is blind to coloured dissolved organic matter, which absorbs in
the blue and is a major Arctic river-plume constituent.

nLw(410) is the most CDOM-sensitive VIIRS band on the identical grid and
processing chain: high CDOM gives LOW nLw(410).  Controlling for both bands
simultaneously removes the sediment and the CDOM pathways together.

If the correlation dies here, fig11's result was optics after all.  If it
survives, the remaining signal is neither sediment nor CDOM.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import swotkot as sk
import fig12_15_attribution as f12

REG = ["Hotham Inlet", "Inner sound", "Outer sound"]
COL = {"Hotham Inlet": "#d18b2c", "Inner sound": "#1f6f8b", "Outer sound": "#4f7942"}


def partial2(y, x, Z):
    """Partial correlation of y and x controlling for the columns of Z,
    via residuals of ordinary least squares."""
    Z = np.column_stack([np.ones(len(Z))] + [Z[:, j] for j in range(Z.shape[1])])
    ry = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
    rx = x - Z @ np.linalg.lstsq(Z, x, rcond=None)[0]
    r = stats.pearsonr(rx, ry)
    dof = len(y) - Z.shape[1] - 1
    t = r.statistic * np.sqrt(dof / (1 - r.statistic ** 2))
    return r.statistic, 2 * (1 - stats.t.cdf(abs(t), dof)), dof


def main():
    sk.mpl_setup()
    CHL, _ = f12.region_series("chla_weekly.nc", "chlor_a")
    NLW, _ = f12.region_series("nlw671_weekly.nc", "nLw_671")
    BLU, _ = f12.region_series("nlw410_weekly.nc", "nLw_410")

    g = sk.load_gauges("daily")
    kb = g[g.site_no == "15744500"].dropna(subset=["q_cms"]).copy()
    kb["t"] = kb.time.dt.tz_convert("UTC").dt.tz_localize(None)
    Q = np.log10(kb.set_index("t").q_cms.resample("W").mean())

    rows = []
    for nm in REG:
        c = np.log10(CHL[nm].resample("W").mean())
        sed = NLW[nm].resample("W").mean()
        cdm = BLU[nm].resample("W").mean()
        for lag in range(0, 4):
            D = pd.concat([c.rename("c"), sed.rename("s"), cdm.rename("b"),
                           Q.shift(lag).rename("q")], axis=1).dropna()
            D = D[np.isin(D.index.month, [6, 7, 8, 9])]
            D = D[np.isfinite(D).all(axis=1)]
            if len(D) < 20:
                continue
            raw = stats.pearsonr(D.q, D.c)
            r1, p1, _ = partial2(D.c.values, D.q.values, D[["s"]].values)
            r2, p2, _ = partial2(D.c.values, D.q.values, D[["s", "b"]].values)
            rows.append(dict(region=nm, lag=lag, n=len(D),
                             r_raw=raw.statistic, p_raw=raw.pvalue,
                             r_sed=r1, p_sed=p1, r_both=r2, p_both=p2,
                             r_q_cdom=stats.pearsonr(D.q, D.b).statistic,
                             r_chl_cdom=stats.pearsonr(D.c, D.b).statistic))
    A = pd.DataFrame(rows)
    A.to_csv(f"{sk.DATA}/../docs/chl_cdom_control.csv", index=False)
    alpha = 0.05 / len(A)

    fig = plt.figure(figsize=(13.5, 7.6))
    gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.3)

    # (a) is nLw(410) actually tracking the plume?
    ax = fig.add_subplot(gs[0, 0])
    for nm in REG:
        g_ = A[A.region == nm]
        ax.plot(g_.lag, g_.r_q_cdom, "-o", ms=5, color=COL[nm], label=nm)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(4)); ax.set_xlabel("lag (weeks)")
    ax.set_ylabel("r (log Q vs nLw410)")
    ax.set_title("(a) Does discharge drive the CDOM band?\n"
                 "negative = more CDOM with more flow", fontsize=9.5)
    ax.legend(fontsize=7)

    # (b-d) the three-step comparison per region
    for k, nm in enumerate(REG):
        ax = fig.add_subplot(gs[0, 1] if k == 0 else gs[0, 2] if k == 1 else gs[1, 0])
        g_ = A[A.region == nm]
        ax.plot(g_.lag, g_.r_raw, "--o", ms=4, color="0.6", label="raw")
        ax.plot(g_.lag, g_.r_sed, "-o", ms=5, color=COL[nm], alpha=0.55,
                label="− sediment")
        ax.plot(g_.lag, g_.r_both, "-o", ms=7, color=COL[nm],
                label="− sediment − CDOM")
        sig = g_[g_.p_both < alpha]
        ax.plot(sig.lag, sig.r_both, "o", ms=13, mfc="none", mec=COL[nm], mew=1.8)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(range(4)); ax.set_xlabel("lag: discharge leads (weeks)")
        ax.set_ylabel("r vs log chl")
        ax.set_title(f"({'bcd'[k]}) {nm}", fontsize=10)
        ax.legend(fontsize=7)

    # (e) summary table
    ax = fig.add_subplot(gs[1, 1:]); ax.axis("off")
    best = (A.loc[A.groupby("region").r_both.apply(lambda s: s.abs().idxmax())]
            .set_index("region").reindex(REG))
    tbl = [["region", "lag", "raw", "− sed", "− sed − CDOM", "p", "verdict"]]
    for nm, r in best.iterrows():
        verdict = ("survives both" if r.p_both < alpha else
                   "dies" if abs(r.r_both) < 0.15 else "weakened")
        tbl.append([nm, f"{int(r.lag)} wk", f"{r.r_raw:+.2f}", f"{r.r_sed:+.2f}",
                    f"{r.r_both:+.2f}", f"{r.p_both:.1e}", verdict])
    t = ax.table(cellText=tbl[1:], colLabels=tbl[0], loc="center", cellLoc="left",
                 colWidths=[.20, .09, .11, .12, .18, .14, .16])
    t.auto_set_font_size(False); t.set_fontsize(9.5); t.scale(1, 1.7)
    for j in range(7):
        t[0, j].set_facecolor("#0B2F4A"); t[0, j].set_text_props(weight="bold", color="w")
    for i, nm in enumerate(REG, start=1):
        if best.loc[nm, "p_both"] < alpha:
            for j in range(7):
                t[i, j].set_facecolor("#EAF4EE")
    ax.set_title(f"(e) Strongest lag per region. {len(A)} tests, Bonferroni "
                 f"p < {alpha:.4f}\nGreen rows survive BOTH optical controls",
                 fontsize=10)

    fig.suptitle("Controlling for CDOM as well as sediment: does the "
                 "discharge-chlorophyll link survive?", fontsize=11.5, y=0.975)
    o = f"{sk.FIGS}/fig23_cdom_control.png"
    fig.savefig(o, dpi=170, facecolor="white"); print("wrote", o)
    print(f"\n{len(A)} tests, Bonferroni alpha = {alpha:.5f}")
    print(A[["region", "lag", "n", "r_raw", "r_sed", "r_both", "p_both"]]
          .round(4).to_string(index=False))
    print(f"\nsurviving both controls: {int((A.p_both < alpha).sum())} of {len(A)}")


if __name__ == "__main__":
    main()
