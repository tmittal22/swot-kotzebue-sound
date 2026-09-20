"""Figure 9 + the data packet.

Figure: SWOT "virtual gauge" stage records at reaches spaced along each river.
Every one of these is a multi-year stage time series at a location that has
never been gauged.

Packet: flat CSVs under packet/ for a collaborator, with a manifest.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

import swotkot as sk
import fig05_river_ocean as f5

PACKET = os.path.join(sk.DATA, "..", "packet")
RIVERS = ["Kobuk", "Selawik", "Noatak"]
N_PER_RIVER = 4


def pick_stations(rch, inv, river, k=N_PER_RIVER):
    """Reaches spaced along the river with the longest records."""
    # SWOT is specified for rivers wider than 50-100 m; narrow headwater
    # reaches give noisy stage even after quality filtering, so they are not
    # offered as virtual gauges.
    wide = set(inv.loc[(inv.width >= 90) & (inv.type == 1), "reach_id"])
    s = rch[(rch.river == river) & rch.reach_id.isin(wide)]
    cnt = s.groupby("reach_id").agg(n=("wse", "size"),
                                    dist=("dist_out_km", "first"))
    cnt = cnt[cnt.n >= 40]
    if cnt.empty:
        return []
    edges = np.linspace(cnt.dist.min(), cnt.dist.max(), k + 1)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        w = cnt[(cnt.dist >= a) & (cnt.dist <= b)]
        if len(w):
            out.append(int(w.n.idxmax()))
    return out


def main():
    sk.mpl_setup()
    os.makedirs(PACKET, exist_ok=True)
    rch = sk.load_reaches()
    inv = sk.load_inventory()
    gd = sk.load_gauges("daily")

    fig, axes = plt.subplots(len(RIVERS), 1, figsize=(13, 10), sharex=True)
    station_rows = []
    for ax, river in zip(axes, RIVERS):
        ids = pick_stations(rch, inv, river)
        cmap = plt.get_cmap("plasma")
        for j, rid in enumerate(ids):
            s = rch[rch.reach_id == rid].sort_values("time")
            meta = inv[inv.reach_id == rid].iloc[0]
            off = j * 4.0
            ss = s.copy()
            ss["a"] = ss.wse - ss.wse.median() + off
            ss.loc[ss.time.diff() > pd.Timedelta("45D"), "a"] = np.nan
            ax.plot(ss.time, ss.a, "-o", ms=2.4, lw=0.8,
                    color=cmap(j / max(1, len(ids) - 1)))
            ax.annotate(f"{rid}  |  {meta.dist_out_km:.0f} km upstream  |  "
                        f"facc {meta.facc:.0f} km$^2$  |  n={len(s)}",
                        (ss.time.min(), off + 1.4), fontsize=6.8,
                        color=cmap(j / max(1, len(ids) - 1)))
            station_rows.append(dict(
                river=river, reach_id=rid, lat=meta.y, lon=meta.x,
                dist_out_km=meta.dist_out_km, facc_km2=meta.facc,
                width_m=meta.width, reach_length_m=meta.reach_length,
                n_obs=len(s), first=s.time.min(), last=s.time.max(),
                wse_median_m=s.wse.median(), wse_range_m=s.wse.max() - s.wse.min()))
        ax.set_ylabel(f"{river}\nWSE anomaly + offset (m)")
        ax.set_title(f"{river}: {len(ids)} SWOT virtual gauges"
                     + ("" if river == "Kobuk" else "  -- no in-situ gauge exists"),
                     loc="left", fontsize=9.5)
        if river == "Kobuk":
            g = gd[gd.site_no == "15744500"].dropna(subset=["q_cms"])
            a2 = ax.twinx(); a2.grid(False)
            a2.plot(g.time, g.q_cms, color="0.6", lw=0.7, zorder=0)
            a2.set_yscale("log"); a2.set_ylabel("USGS Q (m$^3$/s)", color="0.5")
    axes[-1].set_xlabel("date")
    axes[-1].set_xlim(pd.Timestamp("2023-03-01", tz="UTC"),
                      pd.Timestamp("2026-10-01", tz="UTC"))
    fig.suptitle("SWOT virtual-gauge stage records, Kotzebue Sound rivers "
                 "(quality-passed, ice-free; traces offset by 4 m)", y=0.995)
    out = f"{sk.FIGS}/fig09_virtual_gauges.png"
    fig.savefig(out, dpi=170, facecolor="white"); print("wrote", out)

    # ---------------- data packet ----------------
    st = pd.DataFrame(station_rows)
    st.to_csv(f"{PACKET}/virtual_gauge_index.csv", index=False)

    keep = ["reach_id", "river", "time", "dist_out_km", "wse", "wse_u", "width",
            "width_u", "slope", "slope2", "area_total", "d_x_area", "reach_q",
            "dark_frac", "ice_clim_f", "xovr_cal_q", "n_good_nod", "obs_frac_n",
            "cycle_id", "pass_id", "xtrk_dist", "facc", "reach_length", "type"]
    rch[[c for c in keep if c in rch.columns]].to_csv(
        f"{PACKET}/swot_reach_timeseries_qc.csv.gz", index=False,
        compression="gzip")

    nq = pd.read_parquet(f"{sk.DATA}/swot/node_qc.parquet")
    nq = nq[(nq.node_q <= 1) & (nq.ice_clim_f == 0) & nq.wse.notna()]
    nq.to_parquet(f"{PACKET}/swot_node_timeseries_qc.parquet", index=False)

    ref = pd.read_parquet(f"{sk.DATA}/swot/reference_profile.parquet")
    ref.to_csv(f"{PACKET}/reference_long_profiles.csv", index=False)

    gd.to_csv(f"{PACKET}/usgs_daily.csv", index=False)
    sk.load_gauges("instantaneous").to_csv(
        f"{PACKET}/usgs_instantaneous.csv.gz", index=False, compression="gzip")

    d = xr.open_dataset(f"{sk.DATA}/ocean/chla_weekly.nc")
    chl = d.chlor_a.squeeze("altitude", drop=True)
    frames = []
    for nm, r in f5.REGIONS.items():
        ser = f5.region_series(chl, r).assign(region=nm)
        frames.append(ser.reset_index().rename(columns={"index": "time"}))
    pd.concat(frames).to_csv(f"{PACKET}/chlorophyll_regional_weekly.csv",
                             index=False)

    inv.to_csv(f"{PACKET}/sword_reach_inventory.csv", index=False)
    sk.load_inventory("nodes").to_csv(f"{PACKET}/sword_node_inventory.csv.gz",
                                      index=False, compression="gzip")

    files = sorted(os.listdir(PACKET))
    man = []
    for f in files:
        if f == "MANIFEST.md":
            continue
        man.append((f, os.path.getsize(os.path.join(PACKET, f)) / 1e6))
    with open(f"{PACKET}/MANIFEST.md", "w") as fh:
        fh.write("# Data packet\n\nAll files are quality-controlled per "
                 "`docs/THEORY.md` section 4 unless the name says otherwise.\n"
                 "Times are UTC. WSE is metres above the EGM2008 geoid.\n\n"
                 "| file | MB | contents |\n|---|---|---|\n")
        desc = {
            "virtual_gauge_index.csv": "the 12 SWOT virtual gauges plotted in fig09: id, position, drainage area, record length",
            "swot_reach_timeseries_qc.csv.gz": "reach-level SWOT time series, quality-passed and ice-free",
            "swot_node_timeseries_qc.parquet": "200 m node time series, quality-passed and ice-free",
            "reference_long_profiles.csv": "per-node reference WSE long profile and its spread",
            "usgs_daily.csv": "USGS daily discharge and stage, 1976-2026, 3 gauges",
            "usgs_instantaneous.csv.gz": "USGS 15-minute values 2023-2026, converted to UTC",
            "chlorophyll_regional_weekly.csv": "VIIRS weekly chlorophyll medians for the 3 sound regions",
            "sword_reach_inventory.csv": "SWORD v17c reach attributes for the domain",
            "sword_node_inventory.csv.gz": "SWORD v17c node attributes for the domain",
        }
        for f, mb in man:
            fh.write(f"| `{f}` | {mb:.1f} | {desc.get(f, '')} |\n")
    print("\npacket:")
    for f, mb in man:
        print(f"  {f:42s} {mb:8.1f} MB")
    print("\nvirtual gauge index:")
    print(st[["river", "reach_id", "dist_out_km", "facc_km2", "n_obs",
              "wse_range_m"]].to_string(index=False))


if __name__ == "__main__":
    main()
