"""Figure 19 -- the whole river network as 2-D fields: time on x, along-river
distance on y, SWOT water-surface anomaly in colour.

One panel per river.  This is the natural way to view a SWOT river record: the
satellite measures a whole river at once but at sparse times, so a time series
at a point throws away the spatial dimension and a long profile throws away
time.  The 2-D view keeps both.

The right-hand column carries the two quantities needed to interpret the
left-hand one: where tributaries add drainage area (steps in facc), and where
the channel is multi-threaded (n_chan_max), which is where a one-dimensional
reading of the river stops being valid.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

import swotkot as sk
import spatial_hydrograph as sh

RIVERS = ["Noatak", "Kobuk", "Selawik"]
DKM, DDAY = 10.0, 4.0      # grid: 10 km along-river, 4 days


def grid_river(n, ref, river):
    s = n[n.river == river]
    a = s.merge(ref[["node_id", "wse_ref", "wse_mad", "width_med"]],
                on="node_id", how="inner")
    a = a[a.width_med >= 80]
    a["eta"] = a.wse - a.wse_ref
    lim = np.maximum(1.0, 4 * 1.4826 * a.wse_mad.fillna(0))
    a = a[a.eta.abs() <= lim]
    a["t"] = (a.time - pd.Timestamp("2023-01-01", tz="UTC")).dt.total_seconds() / 86400
    tb = np.arange(a.t.min(), a.t.max() + DDAY, DDAY)
    db = np.arange(0, a.dist_out_km.max() + DKM, DKM)
    a["ti"] = np.digitize(a.t, tb) - 1
    a["di"] = np.digitize(a.dist_out_km, db) - 1
    g = a.groupby(["di", "ti"]).eta.median()
    M = np.full((len(db), len(tb)), np.nan)
    for (di, ti), v in g.items():
        if 0 <= di < len(db) and 0 <= ti < len(tb):
            M[di, ti] = v
    return M, tb, db, a


def main():
    sk.mpl_setup()
    n = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    n = n[(n.node_q <= 1) & (n.ice_clim_f == 0) & n.wse.notna()]
    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")
    inv = sk.load_inventory()

    fig = plt.figure(figsize=(14.5, 10.5))
    gs = fig.add_gridspec(3, 3, width_ratios=[3.1, 0.75, 0.75],
                          hspace=0.34, wspace=0.22)
    t0 = pd.Timestamp("2023-01-01", tz="UTC")
    norm = TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=1.5)

    for k, riv in enumerate(RIVERS):
        M, tb, db, a = grid_river(n, ref, riv)
        ax = fig.add_subplot(gs[k, 0])
        dates = [t0 + pd.Timedelta(days=float(x)) for x in tb]
        pm = ax.pcolormesh(dates, db, M, cmap="RdBu_r", norm=norm,
                           shading="auto", rasterized=True)
        ax.set_ylabel(f"{riv}\ndistance upstream (km)", fontsize=9)
        ax.set_xlim(t0, pd.Timestamp("2026-10-01", tz="UTC"))
        filled = float(np.isfinite(M).mean())
        ax.set_title(f"{riv}: {len(a):,} node observations, "
                     f"{filled*100:.0f}% of the {DKM:.0f} km x {DDAY:.0f} day grid filled",
                     fontsize=9.5, loc="left")
        if k < 2:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel("date")
        cb = plt.colorbar(pm, ax=ax, pad=0.01, fraction=0.03)
        cb.set_label("WSE anomaly $\\eta$ (m)", fontsize=8)

        # --- drainage-area steps = tributary contributions ---------------
        axf = fig.add_subplot(gs[k, 1])
        r = inv[(inv.river == riv) & (inv.type == 1)].sort_values("dist_out_km")
        axf.plot(r.facc / 1e3, r.dist_out_km, "-", lw=1.6,
                 color=sk.RIVER_COLORS[riv])
        # a step in facc larger than 5% of the local value is an inflow
        f = r.facc.values
        dd = r.dist_out_km.values
        jump = np.where(np.abs(np.diff(f)) > 0.05 * f[:-1])[0]
        for j in jump:
            axf.axhline(dd[j], color="0.55", lw=0.7, ls="--")
        axf.set_ylim(0, db.max()); axf.set_xlabel("facc (10$^3$ km$^2$)", fontsize=8)
        axf.set_yticklabels([])
        axf.set_title(f"{len(jump)} inflows", fontsize=8.5)
        axf.tick_params(labelsize=7)

        # --- multi-channel sections --------------------------------------
        axc = fig.add_subplot(gs[k, 2])
        axc.barh(r.dist_out_km, r.n_chan_max, height=6,
                 color=np.where(r.n_chan_max > 1, "#c1543a", "#9fb8c4"))
        axc.axvline(1.5, color="k", lw=0.8, ls=":")
        axc.set_ylim(0, db.max()); axc.set_xlabel("n channels", fontsize=8)
        axc.set_yticklabels([])
        multi = float((r.n_chan_max > 1).mean())
        axc.set_title(f"{multi*100:.0f}% multi-thread", fontsize=8.5)
        axc.tick_params(labelsize=7)

    fig.suptitle("Every SWOT observation, per river: time x along-river "
                 "distance x water-surface anomaly\n"
                 "dashed lines mark tributary inflows; red bars mark "
                 "multi-channel reaches where a 1-D reading breaks down",
                 fontsize=11.5, y=0.975)
    o = f"{sk.FIGS}/fig19_hovmoller.png"
    fig.savefig(o, dpi=165, facecolor="white"); print("wrote", o)

    rows = []
    for riv in RIVERS:
        r = inv[(inv.river == riv) & (inv.type == 1)]
        f = r.sort_values("dist_out_km").facc.values
        jump = int((np.abs(np.diff(f)) > 0.05 * f[:-1]).sum()) if len(f) > 1 else 0
        rows.append(dict(river=riv, reaches=len(r), inflows=jump,
                         frac_multichannel=float((r.n_chan_max > 1).mean()),
                         max_channels=int(r.n_chan_max.max()),
                         facc_span=f"{r.facc.min():.0f}-{r.facc.max():.0f}"))
    C = pd.DataFrame(rows)
    C.to_csv(f"{sk.DATA}/../docs/river_contributions.csv", index=False)
    print("\ncontribution / channel structure:")
    print(C.to_string(index=False))


if __name__ == "__main__":
    main()
