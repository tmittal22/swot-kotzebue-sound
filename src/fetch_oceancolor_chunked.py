"""Fetch VIIRS ocean-colour bands from CoastWatch ERDDAP in yearly chunks.

The ERDDAP proxy returns 502 on a 15-year request for this box but serves a
single year in ~35 s, so each year is fetched separately and concatenated.

Bands:
  chlor_a   chlorophyll (already held; refetched only if missing)
  nLw_671   red-band normalised water-leaving radiance.  This is the
            discriminating measurement for Case-2 water: it responds to
            suspended sediment and is nearly blind to chlorophyll, so if
            apparent chlorophyll tracks nLw(671) the discharge-chlorophyll
            correlation is plume optics rather than biomass.
  kd_par    PAR diffuse attenuation, an independent turbidity proxy.
"""
import os, sys, time
from concurrent.futures import ThreadPoolExecutor

import requests
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "ocean")
TMP = os.path.join(OUT, "chunks")
ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"

LAT = (67.45, 66.10)          # descending, matching the grid
LON = (-165.60, -159.80)
YEARS = range(2012, 2027)

JOBS = [("nesdisVHNSQnLw671Weekly", "nLw_671", "nlw671_weekly"),
        ("nesdisVHNSQkdparWeekly", "kd_par", "kdpar_weekly")]


def one_year(args):
    ds, var, tag, yr = args
    path = f"{TMP}/{tag}_{yr}.nc"
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return path, "cached"
    url = (f"{ERDDAP}/{ds}.nc?{var}"
           f"[({yr}-01-01):1:({yr}-12-31)][(0.0):1:(0.0)]"
           f"[({LAT[0]}):1:({LAT[1]})][({LON[0]}):1:({LON[1]})]")
    for k in range(4):
        try:
            r = requests.get(url, timeout=600)
            if r.status_code == 200:
                open(path, "wb").write(r.content)
                return path, "ok"
            if r.status_code == 404 and "no data" in r.text.lower():
                return None, "empty"
            time.sleep(5 * (k + 1))
        except Exception:
            time.sleep(5 * (k + 1))
    return None, "fail"


def main():
    os.makedirs(TMP, exist_ok=True)
    for ds, var, tag in JOBS:
        final = f"{OUT}/{tag}.nc"
        if os.path.exists(final):
            print(f"{tag}: already assembled")
            continue
        tasks = [(ds, var, tag, y) for y in YEARS]
        paths, stats = [], {}
        with ThreadPoolExecutor(max_workers=5) as ex:
            for p, why in ex.map(one_year, tasks):
                stats[why] = stats.get(why, 0) + 1
                if p:
                    paths.append(p)
        print(f"{tag}: {stats}")
        if not paths:
            print(f"  {tag}: nothing retrieved")
            continue
        d = xr.open_mfdataset(sorted(paths), combine="by_coords")
        d = d.sortby("time").load()
        d.to_netcdf(final)
        d.close()
        print(f"  wrote {final} ({os.path.getsize(final)/1e6:.1f} MB), "
              f"{d.sizes}")


if __name__ == "__main__":
    main()
