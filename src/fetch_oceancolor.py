"""Pull VIIRS ocean-colour over Kotzebue Sound from NOAA CoastWatch ERDDAP.

Two products, chosen deliberately:

  nesdisVHNSQchlaWeekly  Science-quality VIIRS SNPP chlorophyll, ~4 km weekly,
                         2012-present, NOT gap-filled.  This is the primary
                         series: every value is a real retrieval, so the
                         seasonal cycle is not an artefact of interpolation.
                         A 14-year record also puts the 2023-2026 SWOT era in
                         climatological context.

  noaacwNPPN20S3ASCIDINEOF2kmDaily   2 km daily multi-sensor DINEOF product,
                         used only for spatial maps, where the finer grid
                         resolves Hotham Inlet.  It is gap-filled, so it is
                         never used for timing claims.

CAVEAT carried through the analysis: Kotzebue Sound is a shallow, turbid,
CDOM-rich Case-2 water body.  Standard OC chlorophyll algorithms are known to
read high there because sediment and coloured dissolved organic matter absorb
and scatter like phytoplankton.  These series are treated as a bloom-season
*timing* indicator, not as a calibrated biomass measurement.  Kd(PAR) is pulled
alongside as an independent turbidity / light-attenuation proxy so the river
plume signal can be separated from a biomass signal.
"""
import io, os, sys, time
import pandas as pd
import requests
import xarray as xr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "ocean")
ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"

LAT = (66.10, 67.45)
LON = (-165.60, -159.80)

JOBS = [
    ("nesdisVHNSQchlaWeekly", "chlor_a", "2012-01-01", "2026-08-06", "chla_weekly"),
    # nLw671 is the red water-leaving radiance band: it responds to suspended
    # sediment and is nearly blind to chlorophyll, so it separates a river
    # plume from a bloom in this Case-2 water.
    ("nesdisVHNSQnLw671Weekly", "nLw_671", "2012-01-01", "2026-08-06", "nlw671_weekly"),
    # Kd(PAR) is light attenuation: high where the water column is turbid.
    ("nesdisVHNSQkdparWeekly", "kd_par", "2012-01-01", "2026-08-06", "kdpar_weekly"),
]


def grab(ds, var, t0, t1, tag, retries=3):
    path = f"{OUT}/{tag}.nc"
    if os.path.exists(path):
        print(f"{tag}: cached ({os.path.getsize(path)/1e6:.1f} MB)")
        return path
    # griddap needs the altitude axis for these datasets; probe the axis order
    info = requests.get(f"https://coastwatch.pfeg.noaa.gov/erddap/info/{ds}/index.json",
                        timeout=60).json()["table"]["rows"]
    dims = [r[1] for r in info if r[0] == "dimension"]
    spans = {"time": f"[({t0}):1:({t1})]",
             "altitude": "[(0.0):1:(0.0)]",
             "latitude": f"[({LAT[1]}):1:({LAT[0]})]",
             "longitude": f"[({LON[0]}):1:({LON[1]})]"}
    # latitude may be stored descending or ascending; try both orders
    for latspan in (f"[({LAT[1]}):1:({LAT[0]})]", f"[({LAT[0]}):1:({LAT[1]})]"):
        spans["latitude"] = latspan
        q = var + "".join(spans[d] for d in dims)
        url = f"{ERDDAP}/{ds}.nc?{q}"
        for k in range(retries):
            r = requests.get(url, timeout=900)
            if r.status_code == 200:
                open(path, "wb").write(r.content)
                print(f"{tag}: {len(r.content)/1e6:.1f} MB")
                return path
            if r.status_code in (429, 500, 502, 503):
                time.sleep(5 * (k + 1)); continue
            break
        print(f"  {tag} lat order failed: {r.status_code} {r.text[:160]}")
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    for ds, var, t0, t1, tag in JOBS:
        try:
            p = grab(ds, var, t0, t1, tag)
            if p:
                with xr.open_dataset(p) as d:
                    v = d[var]
                    print(f"   {tag}: {dict(v.sizes)}  valid frac "
                          f"{float(v.notnull().mean()):.3f}")
        except Exception as e:
            print(f"{tag}: FAILED {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
