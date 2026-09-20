"""Hydrocron client: pull SWOT RiverSP reach and node time series for the
Kotzebue inventory.

Hydrocron serves SWOT_L2_HR_RiverSP Version D (SWORD v17b) without
authentication.  SWORD type-6 reaches are "ghost" placeholders that SWOT never
observes, so they are excluded; types 1 (river), 3 (lake on river) and 5
(unreliable topology) are all real observations and are kept, with `type`
carried through so the analysis can decide what to trust.

Responses are cached per feature so re-runs are free.
"""
import argparse, io, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "swot")
CACHE = os.path.join(DATA, "cache")
BASE = "https://soto.podaac.earthdatacloud.nasa.gov/hydrocron/v1/timeseries"

START, END = "2023-01-01T00:00:00Z", "2026-09-20T00:00:00Z"

REACH_FIELDS = ("reach_id,time_str,wse,wse_u,slope,slope2,width,width_u,"
                "area_total,d_x_area,reach_q,reach_q_b,dark_frac,ice_clim_f,"
                "ice_dyn_f,xovr_cal_q,n_good_nod,obs_frac_n,partial_f,"
                "xtrk_dist,cycle_id,pass_id,p_dist_out,p_length,sword_version")

NODE_FIELDS = ("node_id,reach_id,time_str,wse,wse_u,width,width_u,node_q,"
               "node_q_b,dark_frac,ice_clim_f,ice_dyn_f,xovr_cal_q,"
               "n_good_pix,xtrk_dist,cycle_id,pass_id,p_dist_out,"
               "sword_version")

# Hydrocron writes these sentinels for observations with no valid retrieval.
NODATA = -999999999999.0


def fetch_one(feature, fid, fields, retries=4):
    path = os.path.join(CACHE, feature.lower(), f"{fid}.csv")
    if os.path.exists(path):
        return path, "cached"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    params = dict(feature=feature, feature_id=str(fid), start_time=START,
                  end_time=END, output="csv", fields=fields)
    for k in range(retries):
        try:
            r = requests.get(BASE, params=params, timeout=180)
            if r.status_code == 400 and "were not found" in r.text:
                open(path, "w").write("")           # genuinely absent, cache the miss
                return path, "absent"
            if r.status_code == 200:
                open(path, "w").write(r.json()["results"]["csv"])
                return path, "ok"
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** k)
                continue
            return None, f"http{r.status_code}"
        except Exception as e:
            if k == retries - 1:
                return None, type(e).__name__
            time.sleep(2 ** k)
    return None, "retries"


def fetch_many(feature, ids, fields, workers):
    out, stats = [], {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_one, feature, i, fields): i for i in ids}
        for n, f in enumerate(as_completed(futs), 1):
            path, why = f.result()
            stats[why] = stats.get(why, 0) + 1
            if path and os.path.getsize(path) > 0:
                out.append(path)
            if n % 250 == 0 or n == len(ids):
                print(f"  {n}/{len(ids)}  {stats}", flush=True)
    return out, stats


def assemble(paths, id_col):
    frames = []
    for p in paths:
        try:
            df = pd.read_csv(p)
        except Exception:
            continue
        if len(df):
            frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df = df[df.time_str != "no_data"].copy()
    df["time"] = pd.to_datetime(df["time_str"], format="ISO8601", utc=True)
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df.loc[df[c] <= NODATA / 10, c] = pd.NA
    df[id_col] = df[id_col].astype("int64")
    return df.sort_values([id_col, "time"]).reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--what", choices=["reach", "node"], required=True)
    ap.add_argument("--rivers", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()

    if a.what == "reach":
        inv = pd.read_parquet(f"{DATA}/inventory_reaches.parquet")
        inv = inv[inv.type != 6]
        if a.rivers:
            inv = inv[inv.river.isin(a.rivers)]
        ids = inv.reach_id.astype("int64").tolist()
        print(f"fetching {len(ids)} reaches ({sorted(inv.river.unique())})")
        paths, stats = fetch_many("Reach", ids, REACH_FIELDS, a.workers)
        df = assemble(paths, "reach_id")
        df = df.merge(inv[["reach_id", "river", "dist_out_km", "type",
                           "facc", "reach_length"]], on="reach_id", how="left")
        out = f"{DATA}/reach_timeseries.parquet"
    else:
        rinv = pd.read_parquet(f"{DATA}/inventory_reaches.parquet")
        rinv = rinv[rinv.type != 6]
        ninv = pd.read_parquet(f"{DATA}/inventory_nodes.parquet")
        ninv = ninv[ninv.reach_id.isin(rinv.reach_id)]
        if a.rivers:
            ninv = ninv[ninv.river.isin(a.rivers)]
        ids = ninv.node_id.astype("int64").tolist()
        print(f"fetching {len(ids)} nodes ({sorted(ninv.river.unique())})")
        paths, stats = fetch_many("Node", ids, NODE_FIELDS, a.workers)
        df = assemble(paths, "node_id")
        df = df.merge(ninv[["node_id", "river", "dist_out_km"]],
                      on="node_id", how="left")
        out = f"{DATA}/node_timeseries.parquet"

    df.to_parquet(out, index=False)
    print(f"\n{stats}")
    print(f"wrote {out}: {df.shape}, {df.time.min()} -> {df.time.max()}")
    print(df.groupby("river").agg(n=("wse", "size"),
                                  wse_valid=("wse", "count")).to_string())


if __name__ == "__main__":
    main()
