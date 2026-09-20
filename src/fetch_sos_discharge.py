"""Pull SWOT-derived discharge (the SoS / Discharge Algorithm Working Group
product) from Hydrocron, for a SWOT-only analysis with no gauge anywhere in it.

The SoS fields live only on the Version 2.0 collection, which is built on SWORD
v16, while everything else in this project uses Version D / SWORD v17b.  The
official v17b->v16 reach translation table (Zenodo 22259077) maps between them;
all 162 domain reaches map cleanly.

Consequence to carry: Version 2.0 processing stops in 2025, so the SoS record is
shorter than the Version D water-surface record.
"""
import io, os, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "swot")
CACHE = os.path.join(DATA, "cache_sos")
BASE = "https://soto.podaac.earthdatacloud.nasa.gov/hydrocron/v1/timeseries"
FIELDS = ("reach_id,time_str,wse,width,slope,slope2,d_x_area,area_total,"
          "reach_q,ice_clim_f,dark_frac,sos_consensus_q,sos_hivdi_q,"
          "sos_metroman_q,sos_momma_q,sos_sad_q,sos_sic4dvar_q")
NODATA = -999999999999.0


def one(rid16):
    p = os.path.join(CACHE, f"{rid16}.csv")
    if os.path.exists(p):
        return p
    os.makedirs(CACHE, exist_ok=True)
    for k in range(4):
        try:
            r = requests.get(BASE, params=dict(
                feature="Reach", feature_id=str(rid16),
                collection_name="SWOT_L2_HR_RiverSP_2.0",
                start_time="2023-01-01T00:00:00Z",
                end_time="2026-09-20T00:00:00Z",
                output="csv", fields=FIELDS), timeout=180)
            if r.status_code == 200:
                open(p, "w").write(r.json()["results"]["csv"]); return p
            if r.status_code == 400 and "were not found" in r.text:
                open(p, "w").write(""); return p
            time.sleep(2 ** k)
        except Exception:
            time.sleep(2 ** k)
    return None


def main():
    xw = pd.read_csv(f"{DATA}/../aux/reach_id_v17_to_v16.csv")
    xw = xw.dropna(subset=["v16_reach_id"])
    xw["v16_reach_id"] = xw.v16_reach_id.astype("int64")
    ids = xw.v16_reach_id.unique().tolist()
    print(f"fetching SoS discharge for {len(ids)} v16 reaches")

    paths = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(one, i): i for i in ids}
        for n, f in enumerate(as_completed(futs), 1):
            p = f.result()
            if p and os.path.getsize(p) > 0:
                paths.append(p)
            if n % 50 == 0:
                print(f"  {n}/{len(ids)}", flush=True)

    frames = []
    for p in paths:
        try:
            d = pd.read_csv(p)
        except Exception:
            continue
        if len(d):
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df = df[df.time_str != "no_data"].copy()
    df["time"] = pd.to_datetime(df.time_str, format="ISO8601", utc=True)
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df.loc[df[c] <= NODATA / 10, c] = pd.NA
    df["v16_reach_id"] = df.reach_id.astype("int64")
    df = df.drop(columns=["reach_id"]).merge(
        xw[["v16_reach_id", "reach_id", "river", "dist_out_km", "type", "facc"]],
        on="v16_reach_id", how="left")
    df.to_parquet(f"{DATA}/sos_discharge.parquet", index=False)

    qcols = [c for c in df.columns if c.startswith("sos_")]
    print(f"\nwrote {DATA}/sos_discharge.parquet  {df.shape}")
    print(f"time range: {df.time.min()} -> {df.time.max()}")
    print("\nvalid counts by algorithm:")
    for c in qcols:
        print(f"  {c:20s} {df[c].notna().sum():6d}")
    print("\nby river (sos_consensus_q):")
    print(df.groupby("river").sos_consensus_q.agg(
        n="count", median="median").to_string())


if __name__ == "__main__":
    main()
