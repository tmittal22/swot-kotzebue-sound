# THEORY.md -- what the code implements

Source of truth for the mathematics behind `src/`. Every symbol is defined with
units. Equation labels (T1, T2, ...) are referenced from the code.

## 1. What SWOT measures

The KaRIn interferometer returns, for each ~200 m **node** along a SWORD
centreline, a water-surface elevation

    h(x, t)   [m, orthometric, EGM2008 geoid]

with x the along-river distance to the river outlet (`dist_out`, m) and t the
overpass time (UTC). Reach products aggregate nodes over ~10 km.

`h` is an elevation of the water surface, not a stage on a local datum and not
a discharge. The gauge comparison in `fig01` therefore tests the *anomaly*
relationship, not absolute agreement (section 5).

Units used throughout:

| symbol | meaning | unit |
|---|---|---|
| `h`, `wse` | water surface elevation | m |
| `x`, `dist_out` | along-river distance to outlet | m (reported km) |
| `W`, `width` | water surface width | m |
| `S`, `slope` | water surface slope | m m^-1 |
| `eta` | WSE anomaly about the reference profile | m |
| `Q` | discharge | m^3 s^-1 |
| `U` | cross-sectionally averaged velocity | m s^-1 |
| `c` | flow-wave celerity | m s^-1 |
| `A` | flow cross-sectional area | m^2 |

## 2. Reference long profile (T1)

For node i with revisits t_1..t_N, the reference elevation is the temporal
median after robust outlier rejection:

    (T1a)  h_ref_raw,i = median_j { h_i(t_j) : |h_i(t_j) - m_i| <= k * 1.4826 * MAD_i }

with m_i the node median, MAD_i the median absolute deviation, and k = 4.
The factor 1.4826 converts MAD to a Gaussian-equivalent standard deviation.

The raw reference is then smoothed along-river with a running median over a
fixed **distance** window (5 km), not a fixed node count, so behaviour is
identical across gaps and variable node spacing:

    (T1b)  h_ref(x) = median { h_ref_raw(x') : |x' - x| <= L_w / 2 },  L_w = 5 km

Implemented in `spatial_hydrograph.reference_profile`. **The smoothing is
applied per river.** `dist_out` is distance to each river's own outlet, so
different rivers reuse the same numeric values; smoothing a globally sorted
array blends Kobuk, Noatak and Selawik nodes. This was a real bug, caught by
the check in section 7.

## 3. Spatial hydrograph (T2)

For a single (cycle, pass) overpass:

    (T2)  eta(x) = h(x, t_overpass) - h_ref(x)

smoothed by the same running median. `eta` is the departure of the water
surface from its long-term shape: a flow wave appears as a positive bulge that
translates downstream between overpasses. This is the Thurman et al. (2025)
"spatial hydrograph", a space series standing in for a time series.

Departure from the paper: Thurman apply a Bayes reconstruction that infills
poor-quality nodes using the SWOT river processor height covariance model. That
model is not distributed with the public vector product, so this implementation
**leaves gaps as gaps**. Consequence: noisier profiles, no interpolation across
long gaps, and no invented measurements.

## 4. Quality control

Filters, and the artefact each one removes:

| filter | value | justification |
|---|---|---|
| `reach_q` / `node_q` | <= 1 | empirical, section 5 |
| `ice_clim_f` | == 0 | ice-covered returns are not a water surface |
| `dark_frac` | <= 0.5 | dark water biases KaRIn heights; profiles showed metre-scale spikes |
| node width | >= 80 m | SWOT is specified for rivers wider than 50-100 m |
| reach `type` | exclude 3, 5, 6 | 6 is a ghost placeholder never observed; 3 (lake-on-river) and 5 (unreliable topology) broke the Selawik profile near Selawik Lake |
| per-node residual | \|eta\| <= max(1 m, 4 * 1.4826 * MAD_i) | rejects surviving outliers without clipping real floods |

`ice_clim_f` is a **fixed climatology**: first/last ice-free day-of-year is
140-143 / 288-292 in every year of the record. It defines a seasonal window and
carries no interannual information, so it cannot be used to date break-up.

## 5. Validation against stage (T3)

SWOT WSE `h` and gauge stage `g` measure the same physical water surface on
different datums, so they must differ by a constant:

    (T3)  h(t) = g(t) + c_0,   dh/dg = 1 exactly

The regression slope is therefore a **parameter-free physical test**: any value
other than 1.0 indicates a measurement or matching error, not a fitted
coefficient. Measured: 1.002 (n = 84, within 1 h coincidence).

## 6. Flow-wave celerity (T4)

For a wide channel with Manning friction the kinematic (monoclinal) wave
celerity is

    (T4a)  c = (5/3) U,   U = Q / A,  A ~ W * d

giving the physical prior used in `fig04` panel (e). With Q_90 = 2401 m^3 s^-1,
W = 410 m and d in 3-7 m, c = 1.4-3.3 m s^-1.

Two-gauge estimate from lagged cross-correlation of discharge at separation L:

    (T4b)  c = L / tau_peak

with tau_peak refined sub-daily by a parabolic fit through the three
cross-correlation samples bracketing the maximum.

Thurman's SWOT estimator pairs a spatial-hydrograph peak at x_p with the
arrival of the same wave at a downstream gauge at x_g:

    (T4c)  c = (x_p - x_g) / (t_gauge_peak - t_overpass)

**This does not work here** -- see WALKTHROUGH section 7.

## 7. Physical checks the code must pass

Implemented in `spatial_hydrograph.check_monotonic`, logged to
`docs/check_monotonic.csv`.

**Monotonicity.** Water flows downhill, so the reference profile must rise
monotonically upstream:

    (T5)  d h_ref / dx >= 0   for x increasing upstream

Measured (total reversed drop vs total rise):

| river | reversed | total rise | worst single reversal |
|---|---|---|---|
| Kobuk | 3.10 m | 166.4 m | 0.40 m |
| Noatak | 0.17 m | 548.1 m | 0.02 m |
| Selawik | 1.79 m | 3.95 m | 0.23 m |

Residual reversals are at or below the SWOT node WSE noise level (~0.2-0.4 m).
The Selawik's higher reversed fraction is expected: it falls only 4 m over
166 km, so node noise is comparable to the true gradient.

This check is what caught the cross-river smoothing bug in section 2, where
reversals reached 107 m against a 392 m rise.

## 8. Changelog

* 2026-09-20 -- initial construction. Reference profile, spatial hydrograph,
  QC battery, celerity estimators, river-ocean coupling. Cross-river smoothing
  bug found and fixed via the T5 monotonicity check. SWOT-only and SWOT+gauge
  celerity estimators both found inadequate and reported as negative results.
