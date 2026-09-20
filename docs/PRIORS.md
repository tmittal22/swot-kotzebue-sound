# PRIORS.md -- constraints every result must satisfy

Each prior states a physical or observational constraint, how it is tested, and
its current state. A result that violates an unrelaxed prior is not reportable.

## P1 -- Water flows downhill
Reference WSE must increase monotonically upstream (THEORY T5).
**Test:** `spatial_hydrograph.check_monotonic`, `docs/check_monotonic.csv`.
**State: PASS.** Reversed drop is 1.9% (Kobuk), 0.03% (Noatak), 45% (Selawik)
of total rise; worst single reversal 0.40, 0.02 and 0.23 m, all at or below
node WSE noise. Selawik's large fraction is explained by its 2.4 cm km^-1
gradient, not by bad data.
**History: FAILED initially** at 107 m and 198 m reversals -- cross-river
smoothing bug. Fixed.

## P2 -- SWOT WSE and gauge stage differ by a constant
dh/dg = 1 exactly (THEORY T3).
**Test:** `fig01_validation.py`.
**State: PASS.** slope = 1.002 m/m, r = 0.980, n = 84, residual 21 cm.

## P3 -- Retrieval error must exceed the instrument specification, not fall below it
SWOT reach WSE is specified at ~10 cm for wide rivers; a residual much *smaller*
than the reported uncertainty would indicate circularity.
**State: PASS.** 21 cm residual vs 11 cm median reported `wse_u`; the residual
is larger, as it must be, since it also contains the 3.6 km separation between
reach and gauge, and real WSE slope between them.

## P4 -- Stage anomalies must be physically bounded
The Kobuk gauged seasonal stage range is ~4 m; anomalies of tens of metres, or
WSE below sea level on a river whose bed is near 2 m, are retrieval failures.
**Test:** `|eta|` percentiles after QC.
**State: PASS.** `|eta|` 99th percentile is 3.0 m (Kobuk), 3.6 m (Selawik),
2.6 m (Noatak).
**History: FAILED** before the QC battery of THEORY section 4: `reach_q == 2`
admitted WSE of -5.2 m to +11.2 m, and node profiles carried 4 m spikes and
6.5 m variance peaks.

## P5 -- Flow-wave celerity must be of order (5/3)U
Kinematic wave theory (THEORY T4a) gives 1.4-3.3 m s^-1 for the Kobuk at high
flow.
**State: NOT MEASURABLE FROM SWOT HERE.** Two-gauge estimate 3.44 m s^-1 sits
at the upper edge and is poorly constrained by daily data. **Three** SWOT
estimators were tried and all three fail:
1. Profile-pair cross-correlation: 0.02-0.2 m s^-1, locks onto static
   along-river structure.
2. Spatial-hydrograph peak plus gauge peak: 0.93 m s^-1 but tracks the
   matching window (0.93/0.66/0.59 for 48/72/96 h).
3. Peak tracking across consecutive overpasses: gave 12 coherent Noatak events
   at a median 1.53 m s^-1, all moving downstream, apparently inside the
   kinematic range. **This was an artefact.** `docs/wave_artefact_test.csv`
   shows the anomaly peak moves at a median 0.99x the speed of the centre of
   SWOT's observed segment: consecutive passes sweep downstream along the
   river and drag the apparent peak with them. The 12/12 downstream direction
   has the same cause.
**No SWOT celerity is claimed for these rivers.**

## P5b -- An apparent propagation speed must not equal the sampling geometry's
own speed
**Test:** regress anomaly-peak position and observed-segment-centre position on
time for the same events; compare slopes (`docs/wave_artefact_test.csv`).
**State: ENFORCED, and it caught a false positive.** Ratio 0.99. Any future
SWOT celerity claim in this basin must report this ratio.

## P6 -- Mass balance along the network
Drainage area must increase downstream on a single channel. Not true through
the Kobuk delta, where flow splits among distributaries and SWORD's main path
threads one of them: `facc` runs 15,162 -> 23,340 -> 31,315 km^2 going
*upstream* over the lowest 84 km.
**State: ACKNOWLEDGED, not violated.** The lowest 84 km of the Kobuk are
distributary channels and are excluded from mainstem profile analysis
(SWORD type 5/6).

## P7 -- Ocean colour must not be read as biomass in Case-2 water
Kotzebue Sound is shallow, turbid and CDOM-rich. Standard OC chlorophyll reads
sediment and CDOM as chlorophyll.
**Test:** magnitude sanity vs open Chukchi shelf.
**State: PRIOR ACTIVE, constrains interpretation.** Hotham Inlet Jun-Sep median
chlorophyll is 8-38 mg m^-3 against 1.3-2.4 mg m^-3 in the outer sound. The
inner values are not credible as biomass. Chlorophyll is used for season timing
and interannual comparison only.

## P8 -- Statistical claims must survive multiple-comparison correction
**Test:** Bonferroni across all lag/region combinations.
**State: ENFORCED.** Two versions of the test exist and they disagree because
of statistical power, not because of the correction:
* SWOT-era only (4 summers, n=46 weekly points): 0 of 21 survive.
* Full VIIRS era against the Kobuk gauge (2012-2026, n=178-217): **12 of 21
  survive** (`docs/chl_discharge_lag_longrecord.csv`).
The long-record result is the reportable one. Effect sizes remain modest
(|r| ~ 0.25-0.32, so ~6-10% of variance).

## P8b -- A chlorophyll-discharge correlation in Case-2 water is not evidence
of a bloom response
The surviving correlations have **opposite signs** inside and outside Hotham
Inlet (inlet r = -0.31 at 1 week; inner sound r = +0.32 at 2 weeks). That
pattern is what plume optics would produce -- flushing of the turbid inlet plus
export of sediment- and CDOM-rich water into the sound -- and equally what a
real productivity response would produce.
**State: UNRESOLVED.** Separating them needs the red-band radiance nLw(671),
which responds to suspended sediment and not to chlorophyll. That download was
still in progress at the end of this session. Until it lands, no biological
interpretation is claimed.

## P9 -- Incomplete seasons must be censored, not scored
**State: ENFORCED.** The 2026 record ends 16 September with the Kobuk stage
index still rising. Scoring it would have reported a spring peak purely from
truncation. All 2026 river-years are censored.

## P10 -- Seasonal masks must not be mistaken for measurements
`ice_clim_f` is a fixed climatology.
**State: ENFORCED.** Used as a seasonal window only. No break-up date is
derived from it.
