# Method notes from the two source papers

## Thurman et al. (2025), GRL 52(10), doi:10.1029/2024GL113875
"SWOT Captures Hydrologic Waves Traveling Down Rivers"

Read via Scholar Gateway full text (12 chunks) plus the OpenAlex record; the
Wiley HTML and PDF both return HTTP 403 to automated fetches.

**Product.** SWOT river single-pass vector product, **Version C** (this project
uses Version D, SWORD v17b, which did not exist at their time of writing).

**Pipeline, in their words.**
1. Identify high-stage periods from USGS gauges, then plot SWOT node WSE
   against downstream distance.
2. Filter with the product quality flags -- "unfiltered elevation measurements
   include artifacts that can manifest as meter-level jumps in river height."
   They removed "only the lowest quality nodes."
3. Take the full multitemporal stack per node, reject outliers, use **median**
   values for a reference stage profile, then apply an **along-river spatial
   median filter**.
4. Quality-filter and apply a **Bayes reconstruction** at the times of interest,
   minimising posterior expected error in node heights, similar to the SWOT
   river processor's reach-slope estimation (JPL D-105505). Fills missing
   poor-quality nodes.
5. Subtract the reference profile to get the WSE anomaly; plot vs distance =
   "spatial hydrograph."

**Wave length.** Consecutive nodes exceeding the **90th percentile** of that
node's WSE over the science orbit; a wave starts/ends where >= 10 consecutive
nodes cross the threshold; events shorter than 2 km ignored. After Cerbelaud
et al. (2024).

**Celerity.** Distance between the SWOT spatial-hydrograph peak and a USGS
gauge hydrograph peak belonging to the same wave, divided by travel time.
Validated by substituting a second gauge, and by lagged cross-correlation of
the full gauge records. Results: Colorado R. 1.07 m/s (SWOT+gauge) vs 1.05
(two-gauge) vs 1.30 (all-wave average); Ocmulgee R. 0.33 vs 0.43 vs 0.67 m/s.

**Baseflow separation.** Chapman & Maxwell (1996) one-parameter digital filter
applied to the spatial hydrograph as a space-for-time substitution, with k the
baseflow recession coefficient (typical range 0.93-0.995) estimated from a
semi-log plot of the recession segment. Baseflow came out at 51.1% and 51.3% of
integrated WSE for the two events, against 49.6% and 48.7% of gauged discharge
volume.

**Their stated limitations**, all of which bite harder in this project:
* 120 km swath truncates long waves.
* 21-day repeat; SWOT captures the peaks of only ~8% of USGS high-discharge
  events (Nickles et al. 2019). Their examples are "Goldilocks" cases.
* Width data not used at all -- errors are "particularly prevalent in SWOT's
  river width measurements" (Gasnier et al. 2024).
* Bayes-reconstructed nodes carry higher uncertainty and can create artefacts.
* WSE used in lieu of discharge is complicated by nonlinear wave propagation
  and stage-discharge hysteresis.

**How this project differs.** No Bayes reconstruction (the covariance model is
not public), so gaps stay gaps. Quality filtering is stricter and empirically
justified against a gauge. Celerity could not be reproduced -- see
WALKTHROUGH section 7.

## Gleason et al. (2026), GRL 53(16), doi:10.1029/2026GL124323
"SWOT, Empiricism, and River Modeling"

Obtained via OpenAlex (abstract, full author list, 74 references). Not yet in
the Scholar Gateway full-text corpus at time of writing, so the notes below are
from the abstract and metadata rather than the methods section.

**Claim.** An inductive, empirical framework that assesses global river models
against SWOT rather than against models or sparse gauges. After controlling for
SWOT data quality, they examine **68,347 river reaches representing ~38% of
global discharge**.

**Findings relevant here.** River models struggle in areas of heavy economic
development, multi-channel rivers, arid areas, and **many Arctic rivers**.
After controlling for expected errors, skill improves as rivers get wider.
Model performance is highly variable and spatially heterogeneous, "resisting
oversimplification." They conclude that assimilating SWOT will improve models
but that model structure must change to represent realistic hydraulics.

**Why it frames this project.** It is the direct justification for treating
Kotzebue Sound observationally. The basin is Arctic, the Kobuk delta is
multi-channel, and the rivers are ungauged -- the intersection of the three
regimes Gleason et al. identify as hardest to model. The SWORD `facc`
inversion through the Kobuk delta documented in PRIORS P6 is a concrete example
of the multi-channel problem they describe.
