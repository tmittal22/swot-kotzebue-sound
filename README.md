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
| `figs/fig10_wave_propagation.png` | Wave length, amplitude and seasonality, plus the artefact test that shows why SWOT celerity is not measurable here. |
| `figs/fig11_optics_vs_biology.png` | Does the discharge-chlorophyll link survive controlling for suspended sediment? Three regions, three different answers. |
| `figs/fig12_rivers_overview.png` | **Step 1.** All six rivers: SWOT stage series, basin areas, where each one drains. |
| `figs/fig13_river_independence.png` | **Step 2.** Seasonal phasing and the inter-river correlation matrix. Are these independent forcings? Mostly not. |
| `figs/fig14_ocean_timeseries.png` | **Step 3.** Chlorophyll, nLw(671) and Kd(PAR) for five receiving basins, 2012-2026, plus climatologies. |
| `figs/fig15_attribution.png` | **Step 4.** Every river against every basin, raw and sediment-controlled. One of 70 survives. |
| `figs/fig16_swot_only.png` | **SWOT-only.** SoS discharge with no gauge in the analysis: what it can and cannot support. |

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
5. **Kobuk discharge does correlate with apparent chlorophyll -- over the full
   record.** Against 4 SWOT summers (n=46) nothing survives Bonferroni; against
   the 2012-2026 gauge record (n=178-217), **12 of 21 do**. Inner sound
   r = +0.32 at 2 weeks, Hotham Inlet r = -0.31 at 1 week. Controlling for
   suspended sediment via nLw(671) splits these three ways: the **outer sound**
   correlation collapses (optics), the **Hotham Inlet** one is untouched and
   negative (dilution), and the **inner sound** one survives and *strengthens*
   with lag (0.18 -> 0.28 at 0 -> 2 weeks) while the sediment coupling decays
   to zero. That lag structure is what a productivity response looks like. The
   control is partial: nLw(671) does not remove CDOM.
6. **SWOT flow-wave celerity is not measurable here.** Three estimators, three
   failures. The most convincing one -- peak tracking, 12 coherent Noatak
   events all moving downstream at a median 1.53 m/s -- turned out to track
   SWOT's own ground track at a slope ratio of 0.99. Wave *length* and
   *amplitude* are measured fine.

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

## Which river does what

`fig12`-`fig15` are a four-step sequence on attribution. The short answer:

* The six rivers are **collinear** (median pairwise r = 0.56, 5 of 15 pairs
  above 0.7), because they share weather. That alone limits how much can be
  attributed to any one of them.
* The receiving basins order identically in chlorophyll, nLw(671) and Kd(PAR):
  Selawik Lake > Hotham Inlet > Eschscholtz Bay > inner sound > outer sound.
  That is a turbidity gradient, and chlorophyll following it is the Case-2
  warning restated.
* Of 70 river-by-basin tests, **one survives Bonferroni**: Kobuk gauged
  discharge to inner-sound chlorophyll at a two-week lag. No SWOT-based
  forcing survives, purely for lack of power (n = 28-39 against the gauge's
  201).

SWOT tells you what each river *does*. Four summers is not yet enough to say
what each river does *to the sound*.

## Can SWOT stand on its own?

It has to, for the Selawik and Noatak. Using the SoS discharge product
(Hydrocron Version 2.0 collection, reached through the official v17b-to-v16
reach translation):

* Validated at the one gauge, SWOT-only discharge is an **excellent shape
  estimator and a poor magnitude estimator**: r = 0.991 in log space, but a
  median bias of 0.35x and NSE = -2.0. No absolute flux is computed from it.
* Used as a shape estimator, SWOT alone **recovers the phase split with no
  in-situ data**: Selawik peaks day 154, Kobuk day 236, Noatak day 251.
* SWOT alone **cannot** do the chlorophyll attribution. At n = 12 the
  correlations change sign against the n = 201 gauge analysis.

SWOT alone establishes *when* each ungauged river delivers water. It cannot yet
establish *how much*, or what that delivery does to the sound.

## On the blooms

No causal claim is made, in either direction. This project measured river
hydrology and contains no HAB cell counts, no toxin data, and no *Alexandrium*
observations; VIIRS chlorophyll is total pigment in Case-2 water, not a HAB
indicator. Advective supply through the Bering Strait is documented for the
2022 event (Fachon et al. 2024) but that is one event, and it does not exclude
a local river-modulated pathway, which this project could not have detected
either. See `docs/WALKTHROUGH.md` section 8f.

## Known limitations

* `ice_clim_f` is a fixed climatology (identical day-of-year bounds every
  year), so it is a seasonal mask, **not** an ice detector, and cannot date
  interannual break-up.
* Flow-wave celerity is **not** resolved by SWOT here, and one plausible-looking
  positive result was an artefact of the sampling geometry. See
  `docs/WALKTHROUGH.md` section 7 and `docs/wave_artefact_test.csv`.
* The inner-sound chlorophyll-discharge correlation survives controls for both
  sediment and CDOM, but ocean colour cannot confirm it is phytoplankton. That
  needs HAB cell counts or toxin data.
* Chlorophyll in Hotham Inlet reaches 8-38 mg m^-3, which is a Case-2
  retrieval artefact (sediment and CDOM read as chlorophyll), not biomass.
* The 2026 season is truncated at 16 September and is censored, not scored.
* SWORD `facc` is inflated at merged coastal outlets: Noatak reads 62,101 km2
  against a published ~32,000. Published basin areas are used for weighting.
