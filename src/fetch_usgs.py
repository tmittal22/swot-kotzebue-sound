"""Pull USGS NWIS daily and instantaneous records for the Kotzebue Sound domain.

Only three gauges in the domain still report in the SWOT era; the Selawik and
Noatak have no active record at all, which is why SWOT carries the analysis
there.
"""
import io, os, sys
import pandas as pd
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "gauges")

SITES = {
    "15744500": "Kobuk R nr Kiana AK",
    "15743850": "Dahl C nr Kobuk AK",
    "15747000": "Wulik R bl Tutak C nr Kivalina AK",
}
PARAMS = {"00060": "discharge_cfs", "00065": "gage_height_ft"}

# NWIS instantaneous timestamps are local; Alaska uses AKST/AKDT.
TZ_OFFSET_HOURS = {"AKST": -9, "AKDT": -8, "UTC": 0, "GMT": 0}


def rdb(url, params):
    r = requests.get(url, params=params, timeout=180)
    r.raise_for_status()
    txt = "\n".join(l for l in r.text.splitlines() if not l.startswith("#"))
    df = pd.read_csv(io.StringIO(txt), sep="\t", dtype=str)
    return df.iloc[1:].reset_index(drop=True)      # drop the format-spec row


def tidy(df, tcol):
    """NWIS column names are <ts_id>_<parm>[_<stat>]; map them back to names.

    NWIS reports instantaneous times in station-local time with the zone in
    `tz_cd` (AKST/AKDT), so convert to UTC here -- the celerity and lag work
    compares SWOT overpass times (UTC) against gauge peaks at hour precision,
    and an 8-9 h offset would swamp the signal.
    """
    out = []
    for c in df.columns:
        parts = c.split("_")
        if len(parts) >= 2 and parts[1] in PARAMS and not c.endswith("_cd"):
            out.append((c, PARAMS[parts[1]]))
    if not out:
        return None
    cols = ["site_no", tcol] + [c for c, _ in out]
    if "tz_cd" in df.columns:
        cols.append("tz_cd")
    keep = df[cols].copy()
    keep = keep.rename(columns=dict(out)).rename(columns={tcol: "time_local"})
    for _, name in out:
        keep[name] = pd.to_numeric(keep[name], errors="coerce")
    naive = pd.to_datetime(keep["time_local"], errors="coerce", format="mixed")
    keep = keep.assign(time_local=naive).dropna(subset=["time_local"])

    if "tz_cd" in keep.columns:
        off = keep["tz_cd"].map(TZ_OFFSET_HOURS)
        bad = off.isna()
        if bad.any():
            raise ValueError(f"unmapped NWIS tz codes: "
                             f"{sorted(keep.loc[bad, 'tz_cd'].unique())}")
        keep["time"] = (keep["time_local"]
                        - pd.to_timedelta(off, unit="h")).dt.tz_localize("UTC")
    else:
        # daily values carry no clock time; stamp them at local midnight UTC-9
        keep["time"] = (keep["time_local"]
                        + pd.Timedelta(hours=9)).dt.tz_localize("UTC")
    return keep


def main():
    os.makedirs(OUT, exist_ok=True)
    sites = ",".join(SITES)

    dv = rdb("https://waterservices.usgs.gov/nwis/dv/",
             dict(format="rdb", sites=sites, startDT="1976-01-01", endDT="2026-09-20",
                  parameterCd="00060,00065", statCd="00003", siteStatus="all"))
    dvt = tidy(dv, "datetime")
    dvt.to_parquet(f"{OUT}/usgs_daily.parquet", index=False)
    print("daily:", dvt.shape, dvt.time.min(), "->", dvt.time.max())
    print(dvt.groupby("site_no").size())

    # instantaneous values only go back to ~1994 and are only needed for the
    # SWOT era, where sub-daily timing matters for celerity.
    iv = rdb("https://nwis.waterservices.usgs.gov/nwis/iv/",
             dict(format="rdb", sites=sites, startDT="2023-01-01", endDT="2026-09-20",
                  parameterCd="00060,00065", siteStatus="all"))
    ivt = tidy(iv, "datetime")
    ivt.to_parquet(f"{OUT}/usgs_instantaneous.parquet", index=False)
    print("instantaneous:", ivt.shape, ivt.time.min(), "->", ivt.time.max())
    print(ivt.groupby("site_no").size())

    pd.DataFrame({"site_no": list(SITES), "name": list(SITES.values())}).to_csv(
        f"{OUT}/sites.csv", index=False)


if __name__ == "__main__":
    main()
