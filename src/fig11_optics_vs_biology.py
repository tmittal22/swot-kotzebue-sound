"""Figure 11 -- is the discharge-chlorophyll correlation optics or biology?

Kotzebue Sound is Case-2 water, so a standard chlorophyll retrieval responds to
suspended sediment and CDOM as well as to phytoplankton.  The red-band
normalised water-leaving radiance nLw(671) responds to suspended sediment and
is nearly blind to chlorophyll, so it can be used as a control.

Test: partial correlation of log Q against log chlorophyll, controlling for
nLw(671).  If the correlation collapses, it was the plume.  If it survives, a
biological signal remains.

LIMIT OF THIS TEST, stated up front: nLw(671) controls for *sediment*, not for
*CDOM*.  Coloured dissolved organic matter absorbs in the blue, not the red, so
it is invisible to nLw(671) and is a major constituent of Arctic river plumes.
Anything surviving this control is therefore "not sediment"; it is not yet
"phytoplankton".
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

import swotkot as sk
import fig05_river_ocean as f5

BANDS = {"chlor_a": ("chla_weekly.nc", "chl-a (mg m$^{-3}$)"),
         "nLw_671": ("nlw671_weekly.nc", "nLw(671)"),
         "kd_par": ("kdpar_weekly.nc", "Kd(PAR) (m$^{-1}$)")}


def region_band(path, var):
    d = xr.open_dataset(f"{sk.DATA}/ocean/{path}")
    v = d[var].squeeze("altitude", drop=True)
    res = {}
    for nm, r in f5.REGIONS.items():
        s = v.sel(latitude=slice(*sorted(r["lat"])[::-1]), longitude=slice(*r["lon"]))
        if s.latitude.size == 0:
            s = v.sel(latitude=slice(*sorted(r["lat"])), longitude=slice(*r["lon"]))
        nv = s.notnull().sum(dim=["latitude", "longitude"])
        med = s.median(dim=["latitude", "longitude"], skipna=True)
        ser = pd.Series(med.values, index=pd.to_datetime(v.time.values))
        ser[nv.values < 8] = np.nan
        # the yearly ERDDAP chunks overlap at boundaries, so drop repeats
        ser = ser[~ser.index.duplicated(keep="first")].sort_index()
        res[nm] = ser
    return res, v


def partial(x, y, z):
    rxy = stats.pearsonr(x, y).statistic
    rxz = stats.pearsonr(x, z).statistic
    ryz = stats.pearsonr(y, z).statistic
    den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    r = (rxy - rxz * ryz) / den if den > 0 else np.nan
    dof = len(x) - 3
    t = r * np.sqrt(dof / (1 - r ** 2)) if abs(r) < 1 else np.inf
    return r, 2 * (1 - stats.t.cdf(abs(t), dof))


def main():
    sk.mpl_setup()
    CHL, chl_g = region_band(*[BANDS["chlor_a"][0], "chlor_a"])
    NLW, nlw_g = region_band(*[BANDS["nLw_671"][0], "nLw_671"])
    KD, kd_g = region_band(*[BANDS["kd_par"][0], "kd_par"])

    g = sk.load_gauges("daily")
    kb = g[g.site_no == "15744500"].dropna(subset=["q_cms"]).copy()
    kb["t"] = kb.time.dt.tz_convert("UTC").dt.tz_localize(None)
    Q = kb.set_index("t").q_cms.resample("W").mean()

    fig = plt.figure(figsize=(14, 9.2))
    gs = fig.add_gridspec(2, 3, hspace=0.38, wspace=0.3)

    # (a-c) August median maps of the three optical quantities
    for k, (var, (fn, lab)) in enumerate(BANDS.items()):
        ax = fig.add_subplot(gs[0, k])
        grid = {"chlor_a": chl_g, "nLw_671": nlw_g, "kd_par": kd_g}[var]
        t = pd.to_datetime(grid.time.values)
        aug = grid.isel(time=np.where(t.month == 8)[0]).median("time", skipna=True)
        z = np.log10(aug) if var != "nLw_671" else aug
        pm = ax.pcolormesh(grid.longitude, grid.latitude, z, cmap="viridis",
                           shading="auto")
        plt.colorbar(pm, ax=ax, pad=0.02,
                     label=("log$_{10}$ " if var != "nLw_671" else "") + lab)
        for nm, r in f5.REGIONS.items():
            ax.add_patch(plt.Rectangle((r["lon"][0], r["lat"][0]),
                                       np.diff(r["lon"])[0], np.diff(r["lat"])[0],
                                       fill=False, ec=r["c"], lw=1.5))
        ax.set_aspect(1 / np.cos(np.radians(67)))
        ax.set_xlabel("lon"); ax.set_ylabel("lat" if k == 0 else "")
        ax.set_title(f"({'abc'[k]}) August median {lab.split('(')[0].strip()}\n"
                     "all three peak in the same plume-fed water", fontsize=9)

    # (d) chlorophyll vs nLw671
    ax = fig.add_subplot(gs[1, 0])
    for nm in f5.REGIONS:
        c = np.log10(CHL[nm]); n_ = NLW[nm]
        D = pd.concat([c.rename("c"), n_.rename("n")], axis=1).dropna()
        D = D[np.isin(D.index.month, [6, 7, 8, 9])]
        D = D[np.isfinite(D).all(axis=1)]
        r = stats.pearsonr(D.n, D.c).statistic
        ax.scatter(D.n, D.c, s=9, alpha=0.4, color=f5.REGIONS[nm]["c"],
                   linewidths=0, label=f"{nm}: r={r:.2f}")
    ax.set_xlabel("nLw(671)  -- suspended sediment proxy")
    ax.set_ylabel("log$_{10}$ chl-a")
    ax.set_title("(d) Apparent chlorophyll tracks sediment,\n"
                 "most strongly in the outer sound")
    ax.legend(fontsize=7)

    # (e) the partial-correlation test
    ax = fig.add_subplot(gs[1, 1])
    rows = []
    for nm in f5.REGIONS:
        c = np.log10(CHL[nm].resample("W").mean())
        n_ = NLW[nm].resample("W").mean()
        q = np.log10(Q)
        for lag in range(0, 4):
            D = pd.concat([c.rename("c"), n_.rename("n"),
                           q.shift(lag).rename("q")], axis=1).dropna()
            D = D[np.isin(D.index.month, [6, 7, 8, 9])]
            D = D[np.isfinite(D).all(axis=1)]
            if len(D) < 20:
                continue
            raw = stats.pearsonr(D.q, D.c)
            pr, pp = partial(D.q, D.c, D.n)
            rows.append(dict(region=nm, lag=lag, r_raw=raw.statistic,
                             p_raw=raw.pvalue, r_partial=pr, p_partial=pp,
                             r_q_nlw=stats.pearsonr(D.q, D.n).statistic,
                             n=len(D)))
    P = pd.DataFrame(rows)
    P.to_csv(f"{sk.DATA}/../docs/chl_optics_partial.csv", index=False)
    alpha = 0.05 / len(P)
    for nm in f5.REGIONS:
        s = P[P.region == nm]
        ax.plot(s.lag, s.r_raw, "--o", ms=4, color=f5.REGIONS[nm]["c"],
                alpha=0.45, label=f"{nm} raw")
        ax.plot(s.lag, s.r_partial, "-o", ms=6, color=f5.REGIONS[nm]["c"],
                label=f"{nm} controlled")
        sig = s[s.p_partial < alpha]
        ax.plot(sig.lag, sig.r_partial, "o", ms=12, mfc="none",
                mec=f5.REGIONS[nm]["c"], mew=1.8)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("lag: Kobuk discharge leads (weeks)")
    ax.set_ylabel("r (log Q vs log chl)")
    ax.set_xticks(range(0, 4))
    ax.set_title("(e) Dashed = raw, solid = controlling for nLw(671)\n"
                 f"ringed = survives Bonferroni ($p<{alpha:.4f}$)")
    ax.legend(fontsize=6, ncol=2, loc="lower left")

    # (f) why the inner sound survives: sediment decays, chlorophyll does not
    ax = fig.add_subplot(gs[1, 2])
    s = P[P.region == "Inner sound"]
    ax.plot(s.lag, s.r_q_nlw, "-s", ms=6, color="#8a6f4a",
            label="Q vs nLw(671)  (sediment)")
    ax.plot(s.lag, s.r_raw, "--o", ms=5, color="#1f6f8b", alpha=0.5,
            label="Q vs chl, raw")
    ax.plot(s.lag, s.r_partial, "-o", ms=6, color="#1f6f8b",
            label="Q vs chl, sediment removed")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("lag: Kobuk discharge leads (weeks)")
    ax.set_ylabel("Pearson r")
    ax.set_xticks(range(0, 4))
    ax.set_title("(f) Inner sound: the sediment signal decays with lag\n"
                 "but the chlorophyll signal does not -- consistent with growth")
    ax.legend(fontsize=7)

    fig.suptitle("Is the Kobuk discharge-chlorophyll link plume optics or "
                 "productivity?  nLw(671) controls for sediment, not for CDOM",
                 fontsize=11.5, y=0.98)
    out = f"{sk.FIGS}/fig11_optics_vs_biology.png"
    fig.savefig(out, dpi=175, facecolor="white"); print("wrote", out)

    print(f"\npartial-correlation test ({len(P)} tests, Bonferroni "
          f"alpha={alpha:.5f}):")
    print(P.to_string(index=False))
    print(f"\nsurviving after controlling for sediment: "
          f"{int((P.p_partial < alpha).sum())} of {len(P)}")
    print(P[P.p_partial < alpha][["region", "lag", "r_raw", "r_partial",
                                  "p_partial", "n"]].to_string(index=False))


if __name__ == "__main__":
    main()
