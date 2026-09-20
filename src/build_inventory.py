"""Subset SWORD v17c to the Kotzebue Sound drainage and write a reach/node
inventory for the rivers that discharge into the sound.

SWORD's `river_name` is NODATA over much of the lower Kobuk, so mainstems are
identified by `main_path_id` (SWORD's own flow-path grouping) rather than by
name, and ordered by `dist_out` (distance along the network to the outlet).
"""
import os
import netCDF4 as nc
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SWORD = os.path.join(HERE, "..", "data", "aux", "na_sword_v17c.nc")
OUT = os.path.join(HERE, "..", "data", "swot")

# Kotzebue Sound drainage: the three rivers that dominate freshwater input,
# plus the two next-largest and a Kobuk tributary at the Kiana gauge.
PATHS = {
    7000490: "Kobuk",
    7001633: "Selawik",
    7000142: "Noatak",
    7002175: "Squirrel",
    7000958: "Buckland",
    7000081: "Wulik",
    7001381: "HothamInletChannel",
}

BBOX = dict(lon=(-165.6, -154.5), lat=(65.4, 68.6))

REACH_VARS = ["reach_id", "x", "y", "x_min", "x_max", "y_min", "y_max",
              "reach_length", "n_nodes", "wse", "width", "slope", "facc",
              "dist_out", "type", "lakeflag", "swot_obs", "n_chan_max",
              "n_chan_mod", "max_width", "low_slope_flag", "stream_order",
              "main_path_id", "is_mainstem", "path_order", "end_reach",
              "n_rch_up", "n_rch_down", "river_name"]

NODE_VARS = ["node_id", "reach_id", "x", "y", "node_length", "wse", "width",
             "dist_out", "facc", "n_chan_max", "max_width", "lakeflag",
             "sinuosity", "node_order"]


def main():
    d = nc.Dataset(SWORD)
    R, N = d.groups["reaches"], d.groups["nodes"]

    rid = R["reach_id"][:].astype(np.int64)
    rx, ry = np.asarray(R["x"][:]), np.asarray(R["y"][:])
    in_box = ((rx > BBOX["lon"][0]) & (rx < BBOX["lon"][1]) &
              (ry > BBOX["lat"][0]) & (ry < BBOX["lat"][1]) &
              ((rid // 100000000) == 813))
    mp = np.asarray(R["main_path_id"][:]).astype(np.int64)
    sel = in_box & np.isin(mp, list(PATHS))
    i = np.where(sel)[0]
    print(f"{in_box.sum()} reaches in the Arctic-NW-Alaska box; "
          f"{len(i)} on the seven target flow paths")

    cols = {}
    for v in REACH_VARS:
        a = np.asarray(R[v][:])
        cols[v] = a[i]
    rdf = pd.DataFrame(cols)
    rdf["reach_id"] = rdf["reach_id"].astype(np.int64)
    rdf["river"] = rdf["main_path_id"].astype(np.int64).map(PATHS)
    rdf = rdf.sort_values(["river", "dist_out"], ascending=[True, False])
    rdf["dist_out_km"] = rdf["dist_out"] / 1e3

    nid_reach = N["reach_id"][:].astype(np.int64)
    keep = np.isin(nid_reach, rdf["reach_id"].values)
    j = np.where(keep)[0]
    ncols = {v: np.asarray(N[v][:])[j] for v in NODE_VARS}
    ndf = pd.DataFrame(ncols)
    ndf["node_id"] = ndf["node_id"].astype(np.int64)
    ndf["reach_id"] = ndf["reach_id"].astype(np.int64)
    ndf = ndf.merge(rdf[["reach_id", "river"]], on="reach_id", how="left")
    ndf = ndf.sort_values(["river", "dist_out"], ascending=[True, False])
    ndf["dist_out_km"] = ndf["dist_out"] / 1e3

    os.makedirs(OUT, exist_ok=True)
    rdf.to_parquet(f"{OUT}/inventory_reaches.parquet", index=False)
    ndf.to_parquet(f"{OUT}/inventory_nodes.parquet", index=False)

    print(f"\n{'river':20s} {'reaches':>7s} {'nodes':>6s} {'len_km':>7s} "
          f"{'facc_max':>9s} {'width_med':>9s} {'swot_obs':>8s} {'lake_rch':>8s}")
    for r, g in rdf.groupby("river"):
        n = ndf[ndf.river == r]
        print(f"{r:20s} {len(g):7d} {len(n):6d} {g.reach_length.sum()/1e3:7.0f} "
              f"{g.facc.max():9.0f} {g.width.median():9.0f} "
              f"{g.swot_obs.median():8.0f} {(g.type == 3).sum():8d}")
    print(f"\nwrote {OUT}/inventory_reaches.parquet and inventory_nodes.parquet")


if __name__ == "__main__":
    main()
