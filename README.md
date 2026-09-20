# SWOT over Kotzebue Sound: river flow, transport, and the bloom season

Flow dynamics of the rivers draining into Kotzebue Sound, northwest Alaska --
the **Selawik**, **Kobuk** and **Noatak** -- from SWOT KaRIn water-surface
elevation, and how their freshwater delivery lines up with the summer
phytoplankton season in **Hotham Inlet** (Kobuk Lake), **Selawik Lake** and the
sound itself.

Two of the three rivers have **no active stream gauge**. For the Selawik and
the Noatak, the SWOT record assembled here is the only stage time series that
exists.

Method follows two papers:

* Thurman, H. R., Allen, G. H., Williams, B. A., Cerbelaud, A., & David, C. H.
  (2025). SWOT Captures Hydrologic Waves Traveling Down Rivers. *Geophysical
  Research Letters*, 52(10). <https://doi.org/10.1029/2024GL113875>
  -- spatial hydrographs, wave length, celerity, spatial baseflow separation.
* Gleason, C. J., et al. (2026). SWOT, Empiricism, and River Modeling.
  *Geophysical Research Letters*, 53(16).
  <https://doi.org/10.1029/2026GL124323>
  -- SWOT-vs-model skill over 68,347 reaches; Arctic rivers are among the
  hardest to model, which is the motivation for treating this basin
  observationally rather than through a model.

## What is here

| Figure | Content |
|---|---|
| `figs/fig01_kiana_validation.png` | SWOT WSE vs USGS 15744500 (Kobuk at Kiana). r = 0.980, slope 1.002 m/m, 21 cm residual. Includes the QC falsification test. |
| `figs/fig02_domain_and_profiles.png` | Domain map, reference long profiles, revisit statistics. |
| `figs/fig03_seasonal_regime.png` | Seasonal regime; Kobuk late-summer peaks vs Selawik spring freshet. |
| `figs/fig04_flow_waves.png` | Distance-time anomaly maps, spatial hydrographs, celerity estimates. |
| `figs/fig05_river_ocean_coupling.png` | Bloom-season chlorophyll vs river forcing, with Case-2 caveats. |
| `figs/fig06_satellite_basemap.png` | Study area on Esri World Imagery: rivers, communities, gauge, Hotham Inlet and Selawik Lake labelled, plus a Kobuk-delta inset. |
| `figs/fig07_network_topology.png` | **How the three rivers were found.** Five topology steps from 292 candidate reaches to 3 mainstems, with an auditable selection table. |
| `figs/fig08_swot_swaths.png` | What SWOT actually measured: one overpass in absolute WSE and in anomaly, the 21 ground-track passes, observation density per node. |
| `figs/fig09_virtual_gauges.png` | Twelve SWOT virtual-gauge stage records, 4 per river. Eight are at locations that have never been gauged. |

### Data packet

`packet/` holds flat, quality-controlled exports for a collaborator, described
by `packet/MANIFEST.md`: reach and node time series, reference long profiles,
the virtual-gauge index, USGS daily and 15-minute records converted to UTC,
regional weekly chlorophyll, and the SWORD inventory.

Supporting documents:

* `docs/THEORY.md` -- measurement model, equations, units, assumptions.
* `docs/PRIORS.md` -- physical constraints every result must satisfy, and their pass/fail state.
* `docs/WALKTHROUGH.md` -- derivation, validation, results, what failed and why.
* `docs/PAPERS.md` -- method notes extracted from the two source papers.

## Data sources (all unauthenticated)

| Source | Use | Access |
|---|---|---|
| SWOT L2_HR_RiverSP Version D (SWORD v17b) | reach and node WSE, width, slope | PO.DAAC **Hydrocron** REST API, no Earthdata login needed |
| SWORD v17c | river network, node positions, `dist_out`, `main_path_id` | Zenodo record 22259077 |
| USGS NWIS | Kobuk at Kiana, Dahl Ck, Wulik R; historical Ambler | waterservices.usgs.gov |
| VIIRS SNPP science-quality chlorophyll, weekly 4 km | bloom season timing | NOAA CoastWatch ERDDAP |

`src/fetch_sword.py` pulls only the North America member out of the 3.9 GB
SWORD zip using HTTP range requests (583 MB compressed, ~90 s with 10 parallel
ranges, instead of a ~4 h full download).

## Environment

```bash
source ~/miniforge3/etc/profile.d/conda.sh && conda activate claude-science-env
```

Requires `remotezip` (`pip install remotezip`); everything else is already in
the environment.

## Reproduce

```bash
python src/fetch_sword.py --member netcdf/na_sword_v17c.nc --out data/aux/na_sword_v17c.nc
python src/build_inventory.py          # SWORD -> Kotzebue reach/node inventory
python src/hydrocron.py --what reach
python src/hydrocron.py --what node --rivers Kobuk Selawik Noatak
python src/fetch_usgs.py
python src/fetch_oceancolor.py
python src/fig01_validation.py         # ... through fig05
```

## Headline results

1. **SWOT is quantitatively trustworthy here.** Against the one active gauge,
   84 coincident overpasses give r = 0.980 and a WSE-vs-stage slope of
   1.002 m/m where physics demands exactly 1.0, with a 21 cm residual against a
   reported 11 cm uncertainty.
2. **Revisit is ~1 day, not 21.** Swath overlap at 67 N gives a median 1-day
   gap between observation days (90th percentile 2-5 days), far better than the
   21-day repeat suggests.
3. **The Selawik and the Kobuk are out of phase.** Both drain into the same
   Hotham Inlet / Selawik Lake system, but the Selawik peaks at day-of-year
   141-145 in all three scored years (snowmelt), while the Kobuk peaked at
   day 240 and 250 (late-summer rain). Freshwater arriving in the bloom window
   is Kobuk and Noatak water, not Selawik water.
4. **The Selawik is a backwater river.** It falls 4.0 m over 166 km
   (2.4 cm km^-1), so its flow is controlled by lake and sound level rather
   than channel slope -- directly relevant to residence time.
5. **No robust river-to-chlorophyll correlation.** Of 21 lagged correlations
   tested, zero survive Bonferroni correction. Four summers is not enough.

## About SWOT imagery

The figures here render the SWOT **vector** product (`L2_HR_RiverSP`): every
200 m node KaRIn returned, positioned and coloured by its measurement
(`fig08`). That is the same KaRIn retrieval, aggregated to the SWORD centreline.

SWOT also produces true raster imagery that is **not** used here:

| product | what it is | why it is absent |
|---|---|---|
| `L2_HR_Raster` | gridded 100 m / 250 m WSE and water-mask images | needs an Earthdata Login |
| `L2_HR_PIXC` | the underlying 10-60 m pixel cloud | needs an Earthdata Login |
| `L2_HR_PIXCVec` | pixel cloud tagged to SWORD reaches/nodes | needs an Earthdata Login |

Hydrocron is the exception that made this project possible without credentials.
To add raster imagery, register at <https://urs.earthdata.nasa.gov>, then:

```bash
printf 'machine urs.earthdata.nasa.gov login USER password PASS\n' >> ~/.netrc
chmod 600 ~/.netrc
python -c "import earthaccess; earthaccess.login(strategy='netrc')"
```

`earthaccess` (already installed) can then search `SWOT_L2_HR_Raster_*` by
bounding box and date. The natural targets are the Kobuk delta and Hotham Inlet
during the late-summer peaks identified in `fig03`, where the vector product is
weakest because SWORD types those reaches 5 and 6.

## Known limitations

* `ice_clim_f` is a fixed climatology (identical day-of-year bounds every
  year), so it is a seasonal mask, **not** an ice detector, and cannot date
  interannual break-up.
* Flow-wave celerity is **not** resolved by SWOT here. See
  `docs/WALKTHROUGH.md` section 7.
* Chlorophyll in Hotham Inlet reaches 8-38 mg m^-3, which is a Case-2
  retrieval artefact (sediment and CDOM read as chlorophyll), not biomass.
* The 2026 season is truncated at 16 September and is censored, not scored.
