# Walkthrough: SWOT river dynamics over Kotzebue Sound

Written so the theory and the results can be judged independently. Every number
below was produced by the scripts in `src/` in this session; the CSVs in
`docs/` hold the raw values.

---

## 1. The question

Kotzebue Sound receives freshwater from three large rivers. The Kobuk
(31,300 km^2) and the Selawik (11,600 km^2) both discharge into the Hotham
Inlet / Selawik Lake complex; the Noatak (62,100 km^2 at its SWORD outlet)
enters the sound directly at Kotzebue. The sound has become a focus of harmful
algal bloom concern in the Pacific Arctic, following documented *Alexandrium
catenella* blooms and paralytic shellfish toxin accumulation in the region
(Anderson et al., 2025, *Limnology and Oceanography Letters*,
<https://doi.org/10.1002/lol2.10421>).

The hydrological question is simple to state and, until SWOT, impossible to
answer: **when does each river deliver its water, and does that timing overlap
the bloom window?**

It was impossible because of gauging. A search of NWIS over the whole domain
returns exactly three active gauges with current data: Kobuk at Kiana
(15744500), Dahl Creek near Kobuk (15743850, a small tributary) and Wulik River
(15747000, a different basin north of the sound). **The Selawik has never had a
gauge. The Noatak gauge stopped decades ago.** Two of the three major rivers
have no in-situ stage record at all.

## 2. Why SWOT works unusually well here

SWOT flies a 21-day repeat orbit, which sounds poor for hydrology. At 67 N,
swath overlap changes that completely. Measured from the data
(`docs/revisit_stats.csv`, science orbit only, ice-free, quality-passed):

| river | median gap between observation days | 90th percentile | observation days |
|---|---|---|---|
| Kobuk | 1 d | 2 d | 382 |
| Noatak | 1 d | 3 d | 340 |
| Selawik | 1 d | 5 d | 206 |

A caveat on reading that table: "observation day" means at least one node
somewhere on that river was observed, not that the whole river was seen.

Coverage per overpass is also large. Pass 498 captures the **entire** 166 km
Selawik in a single snapshot (617 nodes); the best Kobuk passes span 304 km and
the best Noatak passes 383 km. That is what makes spatial hydrographs possible
here.

The data volume assembled: 50,115 reach observations on 148 reaches and
2,276,511 node observations, 2023-03 to 2026-09, pulled from PO.DAAC Hydrocron
without any authentication.

## 3. Establishing that the measurement is trustworthy (`fig01`)

Everything downstream depends on SWOT WSE being right, so this is tested first
against the only active gauge on a major river.

The test is chosen to be parameter-free. SWOT reports orthometric elevation;
the gauge reports stage on a local datum. They observe the same water surface,
so they must differ by a constant, and the regression slope dWSE/dstage must be
**exactly 1.0** (THEORY T3). Nothing is fitted to make that happen.

Matching each overpass to the nearest gauge reading within 1 hour gives 84
pairs over four years:

* Pearson r = **0.980** (p = 6e-59)
* slope = **1.002 m/m** against a physically required 1.000
* residual RMS = **20.6 cm**, bias +0.0 cm
* median reported SWOT uncertainty `wse_u` = 11.4 cm

The residual exceeds the instrument uncertainty, as it must: the SWOT reach
centre and the gauge are 3.6 km apart, with real water-surface slope between
them.

### Proving the quality control can fail

A passing test proves nothing if it cannot fail, so the whole validation was
rerun under relaxed filters (`docs/validation_qc_sensitivity.csv`):

| reach_q | ice filter | n | r | residual RMS |
|---|---|---|---|---|
| <= 1 | ice-free | 84 | **0.980** | **0.21 m** |
| <= 1 | ice kept | 112 | 0.776 | 0.70 m |
| <= 2 | ice-free | 132 | 0.617 | 1.34 m |
| <= 3 | ice kept | 163 | 0.581 | 1.36 m |

Both filters are load-bearing. The naive "use everything" choice degrades r
from 0.98 to 0.58 and inflates the residual sixfold.

The physical reason `reach_q <= 1` is correct, rather than merely convenient:
admitting `reach_q == 2` returns WSE from **-5.2 m to +11.2 m** on a reach
whose bed sits near 2 m and whose gauged seasonal stage range is ~4 m. Those
are retrieval failures, not extreme flows.

## 4. Long profiles, and a bug the physics caught (`fig02`)

The reference long profile (THEORY T1) is the backbone of every anomaly. It
must obey one constraint absolutely: **water flows downhill**, so reference WSE
must rise monotonically upstream.

The first implementation failed this badly -- 7,256 m of reversed drop on the
Kobuk against a 392 m total rise, with single reversals of 107 m. The
diagnostic that identified the cause was that the Kobuk and the Noatak showed
reversals with *identical* numerical values at identical `dist_out`. That is
impossible for two different rivers, and pointed straight at the cause: the
running-median smoother was operating on the globally sorted distance array, so
nodes from different rivers at the same distance-to-outlet were being blended.

After smoothing per river (`docs/check_monotonic.csv`):

| river | reversed drop | total rise | worst reversal | mean slope |
|---|---|---|---|---|
| Kobuk | 3.10 m | 166.4 m | 0.40 m | 31.4 cm km^-1 |
| Noatak | 0.17 m | 548.1 m | 0.02 m | 78.9 cm km^-1 |
| Selawik | 1.79 m | 3.95 m | 0.23 m | **2.4 cm km^-1** |

The Noatak result is worth pausing on: 0.17 m of reversal across 548 m of rise
over 3,468 node pairs, i.e. the SWOT long profile of a completely ungauged
Arctic river is monotone to within 0.03%.

**The Selawik falls 4.0 m over 166 km.** That is a backwater river: its
water-surface gradient is comparable to the node noise, and its flow is
controlled by the level of Selawik Lake and Hotham Inlet rather than by channel
slope. This matters directly for transport -- a backwater system flushes slowly
and responds to sound-side forcing (wind, storm surge, sea level) as much as to
its own runoff.

## 5. The seasonal regime, and where the rivers disagree (`fig03`)

The Kobuk gauge shows something striking. Over 1977-2022, the annual maximum
discharge fell in the late (post-15 July, rain-driven) window in 5 of 36 years,
14%. In the SWOT era it did so in **3 of 3** (2023: day 250, 2024: day 237,
2025: day 247). Under the historical base rate that is binomial p = 0.003.

**This is not presented as a trend, and the data do not support calling it
one.** A regression of the day-of-year of the annual maximum on year over the
40-year record gives +0.43 d/yr with **p = 0.29** -- not significant. The
late-season volume fraction trend is likewise flat (p = 0.77). What can be said
is narrower and still useful: *in the specific years 2023-2025, peak Kobuk
freshwater delivery landed in late August and September rather than in the
spring freshet.*

SWOT then answers the question the gauges cannot: do the ungauged rivers behave
the same way? Scoring each river-year by whether the SWOT stage index peaked in
the spring or late window (`docs/swot_peak_timing.csv`, 2026 censored):

| river | late-window peaks | day-of-year of maxima |
|---|---|---|
| Kobuk | 2 / 2 | 240, 250 |
| Noatak | 1 / 2 | 168, 237 |
| **Selawik** | **0 / 3** | **141, 145, 145** |

**The Selawik and the Kobuk are out of phase.** The Selawik peaks in mid-May in
every observed year, with remarkable consistency (a 4-day spread across three
years) -- a classic nival freshet. The Kobuk, draining the same coastline into
the same estuarine complex, peaked in late summer in both scored years.

This is the central hydrological result, and it exists only because SWOT
measured a river nobody gauges.

### Censoring

The 2026 season is truncated at 16 September. At that point the Kobuk stage
index was still rising (+0.89 m at day 256, its late-season maximum), and the
gauge recorded the 2026 annual peak on day 257. Scoring 2026 would have
reported a spring peak purely because the late peak had not yet been observed.
All 2026 river-years are censored (PRIORS P9).

## 6. Flow waves in space (`fig04`)

Spatial hydrographs (THEORY T2) reproduce the Thurman et al. construction. The
distance-time map for the Kobuk in 2025 (55 overpasses, 35,480 node
observations) shows coherent positive and negative anomaly bands, and the
individual profiles show the seasonal progression: deep negative anomalies
through July, a +1.5 m bulge in late August, decaying through October.

Stage variability along each river (`fig04f`) behaves as it should: the
standard deviation of `eta` falls downstream, from ~1.3 m at 200 km to ~0.3 m
near the outlet on the Kobuk, because the channel widens and the same discharge
change produces less stage change. The Selawik rises steeply upstream over its
short length.

Getting here required a second QC pass. The first profiles carried a 4 m spike,
a -5 m plunge near Selawik Lake, and 6.5 m variance peaks on the upper Noatak.
These traced to, respectively, surviving node outliers, SWORD type-3
lake-on-river reaches, and reaches narrower than SWOT's ~50-100 m
specification. After adding dark-water, width and per-node robust-residual
filters (THEORY section 4), `|eta|` 99th percentiles are 3.0 / 3.6 / 2.6 m for
Kobuk / Selawik / Noatak -- physically plausible stage anomalies.

## 7. Celerity: a negative result, reported as one

Three independent estimates of Kobuk flow-wave celerity:

1. **Kinematic wave theory** (THEORY T4a). With Q_90 = 2401 m^3 s^-1, SWOT
   width 410 m and depth 3-7 m: **1.4-3.3 m s^-1**.
2. **Two gauges.** Ambler and Kiana overlapped only in 1976-1978 -- the one
   such pair ever available on this river. Lagged cross-correlation of
   open-water daily discharge over L = 152 km, high-passed at 15 days to
   isolate event-scale waves, gives a peak lag of 0.51 d and
   **c = 3.44 m s^-1**. Daily sampling cannot resolve a sub-daily lag, so this
   is weakly constrained and sits at the top of the theoretical range.
3. **SWOT.** Two estimators were tried. Both fail.

   * *Profile-pair cross-correlation* (SWOT-only): returns 0.02-0.2 m s^-1,
     one to two orders of magnitude too slow. Diagnosis: the anomaly profiles
     are dominated by **static** along-river structure -- tributary junctions,
     channel geometry, residual reference-profile error -- which does not move
     between overpasses, so the cross-correlation locks onto zero lag and the
     reported shift is noise. Kept in the code as
     `fig04_waves.swot_only_celerity` with this note. Thurman et al. mention
     SWOT-only celerity as a future possibility but do not use it; this is why.
   * *Spatial-hydrograph peak plus gauge peak* (the Thurman estimator, T4c):
     returns a median 0.93 m s^-1 over 27 events. But the travel-time
     distribution piles up at the edge of the 48 h matching window, and the
     answer moves systematically with the window (0.93 / 0.66 / 0.59 m s^-1 for
     48 / 72 / 96 h). An estimator whose output tracks an arbitrary analysis
     choice is not measuring the physical quantity.

**No SWOT celerity is claimed for these rivers** (PRIORS P5). The honest
statement is that gauge and theory agree at order 1-3 m s^-1, and that the
Thurman method does not transfer to a 21-day-repeat Arctic basin with a single
gauge without event-level curation that four years of data do not support.

## 8. The bloom-season link (`fig05`)

### What the ocean data can and cannot do

VIIRS science-quality chlorophyll returns valid pixels over this domain only
from June to September -- 0.0-0.6% valid in October through May, peaking at 42%
in August. Polar night, sea ice and low sun angle remove the rest. No annual
statistic is computed.

More importantly, Kotzebue Sound is **Case-2 water**: shallow, turbid, and
CDOM-rich, fed by rivers carrying sediment and dissolved organic matter.
Standard ocean-colour chlorophyll algorithms read both as chlorophyll. The
evidence is in the data itself -- Jun-Sep median chlorophyll is
**8-38 mg m^-3 in Hotham Inlet** against **1.3-2.4 mg m^-3 in the outer
sound**. The inner values are not credible as phytoplankton biomass; they are
largely the Kobuk plume. Chlorophyll is therefore used for **season timing and
interannual comparison only**, never as biomass (PRIORS P7).

### The correlation test, and its result

Weekly Kobuk SWOT stage anomaly was correlated against log10 chlorophyll in
each of three regions at lags of 0-6 weeks, restricted to June-September. That
is 21 tests. Bonferroni alpha = 0.00238.

**Zero survive.** The largest individual correlations (inner sound r = +0.38 at
4 weeks, p = 0.012; Hotham Inlet r = -0.38 at 0 weeks, p = 0.012) are not
significant after correction. Four summers of weekly data is simply not enough
statistical power, and reporting the uncorrected p-values would be
cherry-picking.

**No river-to-bloom correlation is claimed** (PRIORS P8).

### What can be said

The defensible statement is about overlap rather than correlation. In
2023-2026, median Kobuk discharge through the August-September window ran above
the 1977-2022 climatological median (`fig05e`), and the SWOT-observed Kobuk and
Noatak stage maxima fell at day 237-250 -- inside the bloom window, when
inner-sound chlorophyll is elevated. The Selawik's freshwater, by contrast,
arrives around day 143, roughly 100 days earlier.

So the freshwater and terrestrial material reaching the sound *during* the
bloom season is Kobuk and Noatak water. If river-borne nutrients, organic
matter, or stratification matter for blooms here, the Kobuk and Noatak are the
relevant sources and the Selawik is not -- despite the Selawik discharging into
the same lagoon complex.

## 8b. How the rivers were identified (`fig07`)

The domain box contains **292 SWORD reaches**, and they are not one system.
`best_outlet` partitions them into **9 independent drainage systems**;
`main_path_id` splits those into **34 flow paths**. The Koyukuk, a Yukon
tributary, intrudes into the southeast corner and had to be excluded by
continent code (812 rather than 813).

Names cannot do the selection: `river_name` is **NODATA for 111 of the 292
reaches**, including most of the lower Kobuk. Topology can:

1. `best_outlet` -- which outlet the reach drains to.
2. `main_path_id` + `facc` -- rank the 34 paths by drainage area. Noatak
   (62,101 km2), Kobuk (31,315) and Selawik (11,616) separate cleanly.
3. `rch_id_dn` -- draw the actual reach graph; the mainstems are continuous
   chains fed by 24 confluences.
4. `dist_out` -- order reaches along each mainstem.
5. `type` -- decide what is usable. The Kobuk delta shows up here: its lowest
   84 km are types 5 and 6, which is why the Kobuk profile starts inland rather
   than at Hotham Inlet.

`docs/flow_path_selection.csv` carries the full ranking with a reason per path.
One judgement call is visible: path 7000383 (8,262 km2) is a **second** Hotham
Inlet channel, entirely type 5. One such channel (7001381) was carried and this
one was not. Both are type 5, so both are excluded from profile analysis
regardless, and no result depends on the inconsistency.

## 8c. Robustness to the quality-control choice

The robust per-feature outlier rejection developed for nodes was then applied
at reach level (more than 4 robust sigma from that reach's median, with a 3 m
floor set above the largest real gauged stage range). Apparent stage ranges of
13-20 m on some reaches fell to 2.8-7.0 m.

Every headline result is unchanged under the tightened filter:

* Kiana validation: r = 0.980, slope 1.002, residual 20.6 cm -- identical.
* Selawik peak timing: still 0/3 late, day-of-year 141, 145, 145.
* Kobuk peak timing: still 2/2 late, day 240 and 250.
* Chlorophyll: still 0 of 21 lagged correlations survive Bonferroni.

## 9. What would falsify or sharpen this

* **The out-of-phase result.** Falsified if the Selawik peaks in late summer in
  a subsequent year, or if the SWOT stage index at the Selawik proves to be
  tracking Selawik Lake level rather than river discharge. The latter is a real
  risk given the 2.4 cm km^-1 gradient and is the single most important next
  check: it needs the SWOT PLD lake product for Selawik Lake and Hotham Inlet,
  which Hydrocron serves as `feature=PriorLake` but which is not yet
  incorporated here.
* **The seasonality claim.** Needs more years. n = 3 with no significant
  40-year trend is a hypothesis.
* **The bloom link.** Needs in-situ chlorophyll or HAB cell counts from the
  Alaska HAB network to escape the Case-2 problem, and needs a nutrient or
  CDOM tracer to separate plume optics from biomass.
* **Celerity.** Needs event-level curation, or the SWOT discharge (SoS)
  product, which Hydrocron exposes on the Version 2.0 collection and which is
  not used here.

## 10. Reproducibility

All inputs are public and unauthenticated. No Earthdata login is required: the
SWOT vector products come through PO.DAAC Hydrocron, SWORD from Zenodo, gauges
from NWIS, ocean colour from NOAA CoastWatch ERDDAP. Hydrocron responses are
cached per feature under `data/swot/cache/`, so re-runs are free and offline.
