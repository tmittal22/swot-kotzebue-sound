const path = require('path');
const NP = '/home/tmittal/.npm-global/lib/node_modules';
const PptxGenJS = require(path.join(NP, 'pptxgenjs'));

const ROOT = '/media/tmittal/extradrive1/swot_kotzebue';
const F = n => path.join(ROOT, 'figs', n);

// Arctic-ocean palette: deep navy dominates, glacial teal supports,
// amber is the single sharp accent reserved for caution / late-summer.
const INK = '0B2F4A', TEAL = '2E8BA8', AMBER = 'E8A33D',
      ICE = 'F2F6F8', WHITE = 'FFFFFF', MUTED = '5A7284', RED = 'B4442E';
const HF = 'Georgia', BF = 'Calibri';

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';   // 13.33 x 7.5 in (LAYOUT_16x9 is only 10 x 5.625)
pptx.author = 'SWOT Kotzebue project';
pptx.title = 'SWOT over Kotzebue Sound';

const W = 13.33, H = 7.5;

function darkSlide() {
  const s = pptx.addSlide();
  s.background = { color: INK };
  return s;
}
function lightSlide(title, kicker) {
  const s = pptx.addSlide();
  s.background = { color: WHITE };
  if (kicker) s.addText(kicker.toUpperCase(), {
    x: 0.55, y: 0.30, w: 11, h: 0.26, fontFace: BF, fontSize: 11,
    color: TEAL, bold: true, charSpacing: 1.6, margin: 0 });
  if (title) s.addText(title, {
    x: 0.55, y: kicker ? 0.56 : 0.38, w: 12.2, h: 0.72, fontFace: HF,
    fontSize: 30, bold: true, color: INK, margin: 0 });
  return s;
}
// repeated motif: figure sits in a rounded, thin-bordered frame
function fig(s, file, x, y, w, h) {
  s.addShape(pptx.ShapeType.roundRect, {
    x: x - 0.07, y: y - 0.07, w: w + 0.14, h: h + 0.14,
    fill: { color: ICE }, line: { color: TEAL, width: 0.75 },
    rectRadius: 0.06 });
  s.addImage({ path: file, x, y, w, h, sizing: { type: 'contain', w, h } });
}
function caption(s, txt, x, y, w) {
  s.addText(txt, { x, y, w, h: 0.32, fontFace: BF, fontSize: 10,
    color: MUTED, italic: true, margin: 0 });
}
function stat(s, big, label, x, y, w, color) {
  s.addText(big, { x, y, w, h: 0.78, fontFace: HF, fontSize: 40, bold: true,
    color: color || TEAL, align: 'left', margin: 0 });
  s.addText(label, { x, y: y + 0.76, w, h: 0.62, fontFace: BF, fontSize: 11.5,
    color: MUTED, align: 'left', margin: 0, valign: 'top' });
}
function bullets(s, items, x, y, w, h, size) {
  s.addText(items.map(t => ({ text: t, options: { bullet: { code: '2022' }, breakLine: true } })),
    { x, y, w, h, fontFace: BF, fontSize: size || 14.5, color: '20303C',
      lineSpacing: 22, margin: 0, valign: 'top' });
}
function stepChip(s, n) {
  s.addShape(pptx.ShapeType.ellipse, { x: 12.12, y: 0.30, w: 0.62, h: 0.62,
    fill: { color: AMBER } });
  s.addText(String(n), { x: 12.12, y: 0.30, w: 0.62, h: 0.62, fontFace: HF,
    fontSize: 20, bold: true, color: INK, align: 'center', valign: 'middle', margin: 0 });
}

/* ---------------- 1 TITLE ---------------- */
let s = darkSlide();
s.addText('SWOT over Kotzebue Sound', { x: 0.8, y: 1.85, w: 11.6, h: 0.95,
  fontFace: HF, fontSize: 46, bold: true, color: WHITE, margin: 0 });
s.addText('River flow, transport, and the summer bloom season in northwest Alaska',
  { x: 0.8, y: 2.82, w: 11.2, h: 0.5, fontFace: BF, fontSize: 19, color: 'AECBDB', margin: 0 });
s.addShape(pptx.ShapeType.rect, { x: 0.8, y: 3.55, w: 1.5, h: 0.045, fill: { color: AMBER } });
s.addText([
  { text: 'Two of the three major rivers have never been gauged.\n', options: { color: WHITE, bold: true } },
  { text: 'The SWOT record assembled here is the only stage history that exists for them.', options: { color: 'AECBDB' } },
], { x: 0.8, y: 3.85, w: 9.6, h: 1.0, fontFace: BF, fontSize: 15, lineSpacing: 24, margin: 0 });
s.addText('Selawik  ·  Kobuk  ·  Noatak  ·  Buckland  ·  Squirrel  ·  Wulik',
  { x: 0.8, y: 6.35, w: 11.6, h: 0.35, fontFace: BF, fontSize: 12.5, color: TEAL, margin: 0 });

/* ---------------- 2 WHY ---------------- */
s = lightSlide('Why this basin, and why now', 'Motivation');
bullets(s, [
  'Kotzebue Sound has become a focus of harmful algal bloom concern in the Pacific Arctic, following documented Alexandrium catenella blooms and paralytic shellfish toxin accumulation.',
  'Freshwater timing plausibly matters: it sets stratification, delivers terrestrial nutrients and organic matter, and controls flushing of the lagoon complex.',
  'But the hydrology was unmeasurable. A search of all NWIS gauges in the domain returns three active records, only one on a major river.',
], 0.6, 1.55, 7.0, 2.7, 14.5);
stat(s, '3', 'active gauges in the entire\nKotzebue Sound domain', 0.6, 4.5, 2.2);
stat(s, '1', 'of them on a major river\n(Kobuk at Kiana)', 3.1, 4.5, 2.4);
stat(s, '0', 'on the Selawik or the\nNoatak, ever', 5.7, 4.5, 2.2, AMBER);
fig(s, F('fig06_satellite_basemap.png'), 8.1, 1.55, 4.75, 3.1);
caption(s, 'Fig 6 — study area on Esri World Imagery', 8.1, 4.72, 4.75);
s.addText('Gleason et al. (2026) find Arctic, multi-channel and ungauged rivers are exactly where global river models fail. That is the case for treating this basin observationally.',
  { x: 8.1, y: 5.15, w: 4.75, h: 1.5, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 18, margin: 0 });

/* ---------------- 3 SOURCES ---------------- */
s = lightSlide('Method follows two papers', 'Provenance');
const card = (x, t1, t2, body) => {
  s.addShape(pptx.ShapeType.roundRect, { x, y: 1.6, w: 5.9, h: 3.5,
    fill: { color: ICE }, line: { color: TEAL, width: 0.75 }, rectRadius: 0.06 });
  s.addText(t1, { x: x + 0.35, y: 1.85, w: 5.2, h: 0.75, fontFace: HF,
    fontSize: 17, bold: true, color: INK, margin: 0 });
  s.addText(t2, { x: x + 0.35, y: 2.62, w: 5.2, h: 0.3, fontFace: BF,
    fontSize: 11, color: TEAL, margin: 0 });
  s.addText(body, { x: x + 0.35, y: 3.0, w: 5.2, h: 1.9, fontFace: BF,
    fontSize: 12.5, color: '20303C', lineSpacing: 18, margin: 0 });
};
card(0.6, 'SWOT Captures Hydrologic Waves Traveling Down Rivers',
  'Thurman et al. 2025, GRL 52(10) · 10.1029/2024GL113875',
  'Spatial hydrographs from node WSE, wave length from a 90th-percentile run test, celerity from a SWOT peak plus a gauge peak, and spatial baseflow separation.');
card(6.85, 'SWOT, Empiricism, and River Modeling',
  'Gleason et al. 2026, GRL 53(16) · 10.1029/2026GL124323',
  '68,347 reaches, ~38% of global discharge. Models struggle in developed, multi-channel, arid and Arctic basins. Motivates an observational treatment here.');
s.addText('Thurman full text read via Scholar Gateway (Wiley returns HTTP 403 to automated fetches). Gleason not yet in the full-text corpus — abstract and 74 references via OpenAlex, and the method notes say so.',
  { x: 0.6, y: 5.35, w: 12.15, h: 0.8, fontFace: BF, fontSize: 12, color: MUTED,
    italic: true, lineSpacing: 18, margin: 0 });

/* ---------------- 4 DATA PIPELINE ---------------- */
s = lightSlide('Everything is unauthenticated', 'Data');
const rows = [
  ['PO.DAAC Hydrocron', 'SWOT L2_HR_RiverSP Version D (SWORD v17b)', 'reach + node WSE, width, slope', 'no login'],
  ['Zenodo 22259077', 'SWORD v17c river network', 'topology, dist_out, main_path_id', 'no login'],
  ['USGS NWIS', 'Kobuk at Kiana, Dahl Ck, Wulik; historical Ambler', 'discharge + stage, 1976-2026', 'no login'],
  ['NOAA CoastWatch ERDDAP', 'VIIRS chlorophyll, nLw(671), Kd(PAR)', 'bloom season + turbidity, 2012-2026', 'no login'],
];
s.addTable([[
  { text: 'Source', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'Product', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'Used for', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'Auth', options: { bold: true, color: WHITE, fill: { color: INK } } },
], ...rows.map(r => r.map(c => ({ text: c })))], {
  x: 0.6, y: 1.55, w: 12.15, colW: [2.6, 4.3, 3.65, 1.6], fontFace: BF,
  fontSize: 11.5, color: '20303C', border: { pt: 0.5, color: 'C9D8E2' },
  rowH: 0.42, valign: 'middle' });
stat(s, '50,115', 'reach observations\non 148 reaches', 0.6, 4.2, 2.6);
stat(s, '2.28 M', 'node observations,\n2023-03 to 2026-09', 3.5, 4.2, 2.8);
stat(s, '583 MB', 'pulled from a 3.9 GB SWORD\narchive by HTTP range: 90 s, not 4 h', 6.7, 4.2, 4.0);
s.addText('SWOT L2_HR_Raster and PIXC — the true gridded imagery — do need an Earthdata Login and are not used here. README documents how to add them.',
  { x: 0.6, y: 6.15, w: 12.15, h: 0.7, fontFace: BF, fontSize: 12, color: AMBER,
    bold: true, lineSpacing: 18, margin: 0 });

/* ---------------- 5 TOPOLOGY ---------------- */
s = lightSlide('Finding three rivers in a whole sound', 'Method'); stepChip(s, 1);
fig(s, F('fig07_network_topology.png'), 0.6, 1.5, 8.3, 5.3);
s.addText('river_name is NODATA for 111 of 292 reaches, including most of the lower Kobuk. Names cannot do the selection. Topology can:',
  { x: 9.15, y: 1.5, w: 3.6, h: 1.1, fontFace: BF, fontSize: 12.5, color: '20303C',
    lineSpacing: 18, margin: 0 });
bullets(s, [
  'best_outlet → 9 drainage systems',
  'main_path_id + facc → rank 34 paths',
  'rch_id_dn → the reach graph, 24 confluences',
  'dist_out → order along each mainstem',
  'type → what is usable',
], 9.15, 2.7, 3.6, 2.6, 12);
s.addText('The Kobuk delta appears here: its lowest 84 km are types 5 and 6, which is why its profile starts inland.',
  { x: 9.15, y: 5.4, w: 3.6, h: 1.1, fontFace: BF, fontSize: 12, color: RED,
    lineSpacing: 17, margin: 0 });

/* ---------------- 6 WHAT SWOT SAW ---------------- */
s = lightSlide('What SWOT actually measured', 'Data'); stepChip(s, 2);
fig(s, F('fig08_swot_swaths.png'), 0.6, 1.5, 8.5, 5.3);
stat(s, '21', 'distinct ground-track\npasses cross the basin', 9.4, 1.6, 3.3);
stat(s, '~1 day', 'median gap between\nobservation days', 9.4, 3.1, 3.3);
stat(s, '98', 'median observations\nper 200 m node', 9.4, 4.6, 3.3);
s.addText('Swath overlap at 67°N beats the 21-day repeat badly.',
  { x: 9.4, y: 6.05, w: 3.3, h: 0.7, fontFace: BF, fontSize: 12, color: INK,
    bold: true, lineSpacing: 17, margin: 0 });

/* ---------------- 7 VALIDATION ---------------- */
s = lightSlide('Is the measurement trustworthy?', 'Validation'); stepChip(s, 3);
fig(s, F('fig01_kiana_validation.png'), 0.6, 1.5, 8.4, 5.3);
s.addText('A parameter-free test', { x: 9.25, y: 1.5, w: 3.5, h: 0.35,
  fontFace: HF, fontSize: 15, bold: true, color: INK, margin: 0 });
s.addText('SWOT reports orthometric elevation; the gauge reports stage on a local datum. Same water surface, so they must differ by a constant and the slope must be exactly 1.0. Nothing is fitted to make that happen.',
  { x: 9.25, y: 1.95, w: 3.5, h: 1.8, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });
stat(s, '1.002', 'measured dWSE/dstage\n(1.000 required)', 9.25, 3.75, 3.5);
stat(s, 'r = 0.980', '84 coincident overpasses\nwithin 1 hour', 9.25, 5.2, 3.5);

/* ---------------- 8 QC ---------------- */
s = lightSlide('The quality control is load-bearing', 'Validation');
s.addText('A passing test proves nothing if it cannot fail. The whole validation was rerun under relaxed filters.',
  { x: 0.6, y: 1.5, w: 12.15, h: 0.4, fontFace: BF, fontSize: 14.5, color: '20303C', margin: 0 });
s.addTable([[
  { text: 'reach_q', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'ice filter', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'n', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'r', options: { bold: true, color: WHITE, fill: { color: INK } } },
  { text: 'residual RMS', options: { bold: true, color: WHITE, fill: { color: INK } } },
],
  [{ text: '≤ 1' }, { text: 'ice-free' }, { text: '84' },
   { text: '0.980', options: { bold: true, color: '1B7A4B' } },
   { text: '0.21 m', options: { bold: true, color: '1B7A4B' } }],
  [{ text: '≤ 1' }, { text: 'ice kept' }, { text: '112' }, { text: '0.776' }, { text: '0.70 m' }],
  [{ text: '≤ 2' }, { text: 'ice-free' }, { text: '132' }, { text: '0.617' }, { text: '1.34 m' }],
  [{ text: '≤ 3' }, { text: 'ice kept' }, { text: '163' },
   { text: '0.581', options: { color: RED } }, { text: '1.36 m', options: { color: RED } }]], {
  x: 0.6, y: 2.1, w: 7.2, colW: [1.3, 1.6, 0.8, 1.5, 2.0], fontFace: BF,
  fontSize: 13, color: '20303C', border: { pt: 0.5, color: 'C9D8E2' },
  rowH: 0.46, valign: 'middle' });
s.addText('Why reach_q ≤ 1, physically', { x: 0.6, y: 4.75, w: 7.2, h: 0.35,
  fontFace: HF, fontSize: 15, bold: true, color: INK, margin: 0 });
s.addText('Admitting reach_q = 2 returns WSE from −5.2 m to +11.2 m on a reach whose bed sits near 2 m and whose gauged seasonal range is ~4 m. Those are retrieval failures, not extreme flows.',
  { x: 0.6, y: 5.2, w: 7.2, h: 1.1, fontFace: BF, fontSize: 13, color: '20303C',
    lineSpacing: 19, margin: 0 });
fig(s, F('fig02_domain_and_profiles.png'), 8.2, 2.1, 4.55, 3.1);
caption(s, 'Fig 2 — long profiles pass a monotonicity check', 8.2, 5.28, 4.55);
s.addText('Water flows downhill, so reference WSE must rise upstream. The Noatak is monotone to 0.17 m over a 548 m rise. That check caught a real bug.',
  { x: 8.2, y: 5.65, w: 4.55, h: 1.1, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });

/* ---------------- 9 VIRTUAL GAUGES ---------------- */
s = lightSlide('Twelve virtual gauges, eight where none exist', 'Result');
fig(s, F('fig09_virtual_gauges.png'), 0.6, 1.5, 8.5, 5.3);
s.addText('Each trace is a multi-year stage record at a location on an Arctic river. For the Selawik and Noatak, no such record has ever existed.',
  { x: 9.35, y: 1.6, w: 3.4, h: 1.5, fontFace: BF, fontSize: 13, color: '20303C',
    lineSpacing: 19, margin: 0 });
s.addText('The Selawik traces are visibly flatter and smoother than the Kobuk and Noatak — consistent with backwater control.',
  { x: 9.35, y: 3.2, w: 3.4, h: 1.4, fontFace: BF, fontSize: 13, color: TEAL,
    bold: true, lineSpacing: 19, margin: 0 });
stat(s, '4.0 m', 'total Selawik fall over 166 km\n= 2.4 cm per km', 9.35, 4.75, 3.4, AMBER);

/* ---------------- 10 HEADLINE: OUT OF PHASE ---------------- */
s = lightSlide('The Selawik and the Kobuk are out of phase', 'Headline result');
fig(s, F('fig03_seasonal_regime.png'), 0.6, 1.5, 8.3, 5.3);
s.addText('Both drain into the same Hotham Inlet complex.',
  { x: 9.15, y: 1.55, w: 3.6, h: 0.5, fontFace: BF, fontSize: 13, color: '20303C', margin: 0 });
s.addTable([
  [{ text: 'Selawik', options: { bold: true, color: WHITE, fill: { color: RED } } },
   { text: 'day 141, 145, 145', options: { fill: { color: ICE } } }],
  [{ text: 'Kobuk', options: { bold: true, color: WHITE, fill: { color: INK } } },
   { text: 'day 240, 250', options: { fill: { color: ICE } } }],
  [{ text: 'Noatak', options: { bold: true, color: WHITE, fill: { color: '3F6B4A' } } },
   { text: 'day 168, 237', options: { fill: { color: ICE } } }],
], { x: 9.15, y: 2.15, w: 3.6, colW: [1.35, 2.25], fontFace: BF, fontSize: 12,
     color: '20303C', rowH: 0.42, valign: 'middle', border: { pt: 0.5, color: 'C9D8E2' } });
s.addText('Day-of-year of the seasonal stage maximum. The Selawik is snowmelt-driven and spikes in mid-May with a 4-day spread across three years. The Kobuk peaked in late August and September.',
  { x: 9.15, y: 3.6, w: 3.6, h: 1.6, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });
s.addText('So the freshwater arriving during the bloom window is Kobuk and Noatak water, not Selawik water.',
  { x: 9.15, y: 5.2, w: 3.6, h: 1.3, fontFace: BF, fontSize: 13, color: TEAL,
    bold: true, lineSpacing: 18, margin: 0 });

/* ---------------- 11 WAVES ---------------- */
s = lightSlide('Flow waves: length and amplitude work', 'Result');
fig(s, F('fig10_wave_propagation.png'), 0.6, 1.5, 8.4, 5.3);
bullets(s, [
  '939 wave detections by the Thurman 90th-percentile run test',
  'Median 4–8 km; 65 exceed 50 km; maximum 243 km on the Kobuk',
  'Only 1% are truncated by the observed span',
  'Amplitude grows upstream on all three rivers as the channel narrows',
  'Seasonal occurrence independently reproduces the phase split',
], 9.25, 1.65, 3.5, 4.2, 12);
s.addText('None of this needs celerity.', { x: 9.25, y: 6.0, w: 3.5, h: 0.5,
  fontFace: BF, fontSize: 13, bold: true, color: TEAL, margin: 0 });

/* ---------------- 12 RETRACTION ---------------- */
s = darkSlide();
s.addText('WHAT WE GOT WRONG', { x: 0.8, y: 0.7, w: 11, h: 0.3, fontFace: BF,
  fontSize: 12, bold: true, color: AMBER, charSpacing: 1.8, margin: 0 });
s.addText('A celerity result that looked right, and was not', { x: 0.8, y: 1.05,
  w: 11.6, h: 0.75, fontFace: HF, fontSize: 32, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: 'The apparent finding.  ', options: { bold: true, color: AMBER } },
  { text: 'Tracking the anomaly peak across consecutive overpasses gave 12 coherent events (r² > 0.7), all on the Noatak, all 12 moving downstream, median 1.53 m/s — inside the kinematic-wave prior of 1.4–3.3 m/s. Direction alone looked decisive at p = 0.5¹².', options: { color: 'CFE0EA' } },
], { x: 0.8, y: 2.1, w: 11.6, h: 1.1, fontFace: BF, fontSize: 14.5, lineSpacing: 22, margin: 0 });
s.addText([
  { text: 'The artefact.  ', options: { bold: true, color: AMBER } },
  { text: 'SWOT’s consecutive passes sweep along the river, so the centre of the observed segment marches downstream between overpasses. Regressing peak position and segment centre on time for the same events gives a median slope ratio of ', options: { color: 'CFE0EA' } },
  { text: '0.99', options: { bold: true, color: WHITE } },
  { text: '. The apparent wave speed is the ground-track speed.', options: { color: 'CFE0EA' } },
], { x: 0.8, y: 3.35, w: 11.6, h: 1.3, fontFace: BF, fontSize: 14.5, lineSpacing: 22, margin: 0 });
s.addText('Three SWOT celerity estimators, three failures — each diagnosable. No SWOT celerity is claimed for these rivers.',
  { x: 0.8, y: 4.9, w: 11.6, h: 0.6, fontFace: BF, fontSize: 15, bold: true,
    color: WHITE, margin: 0 });
s.addText('PRIORS P5b now requires that slope ratio be reported for any future celerity claim in this basin.',
  { x: 0.8, y: 5.65, w: 11.6, h: 0.5, fontFace: BF, fontSize: 13, color: TEAL,
    italic: true, margin: 0 });

/* ---------------- 13 OCEAN TIME SERIES ---------------- */
s = lightSlide('What the receiving basins do', 'Ocean'); stepChip(s, 3);
fig(s, F('fig14_ocean_timeseries.png'), 0.6, 1.5, 8.5, 5.3);
s.addText('Chlorophyll, nLw(671) and Kd(PAR) for five basins, 2012–2026.',
  { x: 9.35, y: 1.6, w: 3.4, h: 0.8, fontFace: BF, fontSize: 12.5, color: '20303C',
    lineSpacing: 18, margin: 0 });
s.addText('All three order identically:', { x: 9.35, y: 2.5, w: 3.4, h: 0.35,
  fontFace: BF, fontSize: 12.5, bold: true, color: INK, margin: 0 });
s.addText('Selawik Lake  >  Hotham Inlet  >  Eschscholtz Bay  >  inner sound  >  outer sound',
  { x: 9.35, y: 2.9, w: 3.4, h: 1.3, fontFace: BF, fontSize: 12.5, color: TEAL,
    bold: true, lineSpacing: 19, margin: 0 });
s.addText('That is a turbidity gradient away from the river mouths. Chlorophyll following two independent turbidity proxies is the Case-2 warning restated.',
  { x: 9.35, y: 4.3, w: 3.4, h: 1.5, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });
s.addText('Valid retrievals exist only June–September here: polar night, sea ice and low sun angle remove the rest.',
  { x: 9.35, y: 5.85, w: 3.4, h: 0.95, fontFace: BF, fontSize: 11.5, color: RED,
    lineSpacing: 16, margin: 0 });

/* ---------------- 14 OPTICS VS BIOLOGY ---------------- */
s = lightSlide('Optics or productivity?', 'Ocean'); stepChip(s, 4);
fig(s, F('fig11_optics_vs_biology.png'), 0.6, 1.5, 8.4, 5.3);
s.addText('nLw(671) responds to suspended sediment and is nearly blind to chlorophyll, so it can be used as a control. Partial correlation of log Q against log chl, controlling for it:',
  { x: 9.25, y: 1.6, w: 3.5, h: 1.5, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });
s.addTable([
  [{ text: 'Outer sound', options: { bold: true } }, { text: 'optics — collapses 0.24 → 0.11' }],
  [{ text: 'Inner sound', options: { bold: true, color: '1B7A4B' } }, { text: 'survives, strengthens with lag' }],
  [{ text: 'Hotham Inlet', options: { bold: true } }, { text: 'not sediment; dilution' }],
], { x: 9.25, y: 3.2, w: 3.5, colW: [1.35, 2.15], fontFace: BF, fontSize: 11,
     color: '20303C', rowH: 0.5, valign: 'middle', border: { pt: 0.5, color: 'C9D8E2' } });
s.addText('Inner sound: sediment coupling decays 0.43 → −0.02 across 0–3 weeks while the sediment-removed chlorophyll signal rises 0.18 → 0.28. The curves cross. A signal that outlives its own forcing tracer looks like growth.',
  { x: 9.25, y: 4.85, w: 3.5, h: 1.5, fontFace: BF, fontSize: 11.5, color: TEAL,
    bold: true, lineSpacing: 16, margin: 0 });
s.addText('Caveat: nLw(671) controls sediment, not CDOM.',
  { x: 9.25, y: 6.35, w: 3.5, h: 0.4, fontFace: BF, fontSize: 11, color: RED, margin: 0 });

/* ---------------- 15 ATTRIBUTION SETUP ---------------- */
s = lightSlide('Are the rivers independent forcings?', 'Attribution'); stepChip(s, 5);
fig(s, F('fig13_river_independence.png'), 0.6, 1.6, 8.5, 4.2);
s.addText('Checked before attributing anything, not after.',
  { x: 9.35, y: 1.7, w: 3.4, h: 0.5, fontFace: BF, fontSize: 13, bold: true,
    color: INK, margin: 0 });
stat(s, '0.56', 'median pairwise r\nbetween the six rivers', 9.35, 2.3, 3.4);
stat(s, '5 / 15', 'river pairs exceed r = 0.7', 9.35, 3.8, 3.4, AMBER);
s.addText('They share weather, so they are substantially collinear and cannot be cleanly separated. Kobuk–Squirrel at 0.86 is expected: the Squirrel is a Kobuk tributary, not an independent forcing.',
  { x: 9.35, y: 5.1, w: 3.4, h: 1.6, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });
caption(s, 'Fig 13 — seasonal phasing and the inter-river correlation matrix', 0.6, 5.9, 8.5);

/* ---------------- 16 ATTRIBUTION RESULT ---------------- */
s = lightSlide('Who drives what', 'Attribution'); stepChip(s, 6);
fig(s, F('fig15_attribution.png'), 0.6, 1.6, 8.6, 4.3);
s.addText('70 tests. Every river forcing against every receiving basin, at 1 and 2 week lags, raw and sediment-controlled.',
  { x: 9.45, y: 1.7, w: 3.3, h: 1.0, fontFace: BF, fontSize: 12, color: '20303C',
    lineSpacing: 17, margin: 0 });
stat(s, '1 of 70', 'survive Bonferroni', 9.45, 2.8, 3.3, '1B7A4B');
s.addText('Kobuk gauged discharge → inner-sound chlorophyll, 2-week lag, partial r = 0.28, p = 4.6e−5.',
  { x: 9.45, y: 4.2, w: 3.3, h: 1.0, fontFace: BF, fontSize: 12, color: INK,
    bold: true, lineSpacing: 17, margin: 0 });
s.addText('No SWOT forcing survives — power, not absence. n = 28–39 weekly points against the gauge’s 201.',
  { x: 9.45, y: 5.25, w: 3.3, h: 1.1, fontFace: BF, fontSize: 12, color: RED,
    lineSpacing: 17, margin: 0 });
caption(s, 'Fig 15 — rows are river forcings, columns are receiving basins', 0.6, 6.0, 8.6);

/* ---------------- 17 WHAT WE CAN SAY ---------------- */
s = lightSlide('What the data support, and what they do not', 'Summary');
s.addShape(pptx.ShapeType.roundRect, { x: 0.6, y: 1.5, w: 5.95, h: 4.35,
  fill: { color: 'EAF4EE' }, line: { color: '1B7A4B', width: 0.75 }, rectRadius: 0.06 });
s.addText('Supported', { x: 0.95, y: 1.75, w: 5.3, h: 0.4, fontFace: HF,
  fontSize: 19, bold: true, color: '1B7A4B', margin: 0 });
bullets(s, [
  'SWOT WSE is quantitatively trustworthy here: slope 1.002 where physics demands 1.0, 21 cm residual.',
  'Revisit is ~1 day, not 21, from swath overlap at 67°N.',
  'The Selawik and Kobuk deliver freshwater ~100 days apart into the same estuarine complex.',
  'The Selawik is backwater-controlled: 4.0 m of fall over 166 km.',
  'Wave length and amplitude are measurable; 939 detections.',
  'Kobuk discharge leads inner-sound chlorophyll by ~2 weeks, and survives a sediment control.',
], 0.95, 2.25, 5.3, 4.3, 12);
s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.5, w: 5.95, h: 4.35,
  fill: { color: 'FBEEE9' }, line: { color: RED, width: 0.75 }, rectRadius: 0.06 });
s.addText('Not supported', { x: 7.15, y: 1.75, w: 5.3, h: 0.4, fontFace: HF,
  fontSize: 19, bold: true, color: RED, margin: 0 });
bullets(s, [
  'No SWOT flow-wave celerity. Three estimators, three failures; the best-looking one tracked the ground track at a ratio of 0.99.',
  'No claim that the Kobuk late-summer peak is a trend. 3/3 in the SWOT era, but the 40-year regression gives p = 0.29.',
  'No biological interpretation of the outer sound: that correlation is plume optics.',
  'No attribution from SWOT alone. Four summers gives n = 28–39; nothing survives correction.',
  'ice_clim_f is a fixed climatology — a seasonal mask, not an ice detector. No break-up dates.',
], 7.15, 2.25, 5.3, 4.3, 12);

/* ---------------- 18 NEXT ---------------- */
s = lightSlide('What would sharpen this', 'Next steps');
const nxt = [
  ['aCDOM(443) or a blue-band control', 'Closes the last gap in the optics-vs-biology test. CDOM is invisible to nLw(671) and is a major Arctic plume constituent. Same ERDDAP server, same chunked fetcher.'],
  ['SWOT PLD lake product', 'Selawik Lake and Hotham Inlet as PriorLake features. Tests whether the Selawik stage index tracks discharge or simply lake level — a real risk at 2.4 cm/km.'],
  ['Earthdata Login → L2_HR_Raster', 'True gridded imagery over the Kobuk delta and Hotham Inlet, where the vector product is weakest because SWORD types those reaches 5 and 6.'],
  ['Two to three more SWOT years', 'Roughly doubles n and would bring Buckland → Eschscholtz Bay and Kobuk → Hotham Inlet into range.'],
  ['In-situ chlorophyll or HAB cell counts', 'Alaska HAB network data would escape the Case-2 problem entirely.'],
];
nxt.forEach((r, i) => {
  const y = 1.55 + i * 1.08;
  s.addShape(pptx.ShapeType.ellipse, { x: 0.62, y: y + 0.08, w: 0.46, h: 0.46,
    fill: { color: TEAL } });
  s.addText(String(i + 1), { x: 0.62, y: y + 0.08, w: 0.46, h: 0.46, fontFace: HF,
    fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle', margin: 0 });
  s.addText(r[0], { x: 1.3, y: y + 0.05, w: 4.0, h: 0.6, fontFace: BF, fontSize: 14,
    bold: true, color: INK, margin: 0, valign: 'top' });
  s.addText(r[1], { x: 5.4, y: y + 0.05, w: 7.35, h: 0.9, fontFace: BF, fontSize: 12,
    color: '20303C', lineSpacing: 16, margin: 0, valign: 'top' });
});

/* ---------------- 19 CLOSE ---------------- */
s = darkSlide();
s.addText('Reproducibility', { x: 0.8, y: 1.5, w: 11.6, h: 0.7, fontFace: HF,
  fontSize: 34, bold: true, color: WHITE, margin: 0 });
s.addText('Every input is public and unauthenticated. No Earthdata Login is required for anything shown here.',
  { x: 0.8, y: 2.35, w: 11.6, h: 0.5, fontFace: BF, fontSize: 15, color: 'AECBDB', margin: 0 });
s.addShape(pptx.ShapeType.rect, { x: 0.8, y: 3.0, w: 1.5, h: 0.045, fill: { color: AMBER } });
s.addText([
  { text: 'README.md', options: { bold: true, color: WHITE } },
  { text: '  what it does, how to run it, environment\n', options: { color: 'AECBDB' } },
  { text: 'docs/THEORY.md', options: { bold: true, color: WHITE } },
  { text: '  equations, units, QC policy and its justification\n', options: { color: 'AECBDB' } },
  { text: 'docs/PRIORS.md', options: { bold: true, color: WHITE } },
  { text: '  physical constraints, each with a pass/fail state\n', options: { color: 'AECBDB' } },
  { text: 'docs/WALKTHROUGH.md', options: { bold: true, color: WHITE } },
  { text: '  derivation, validation, and what failed\n', options: { color: 'AECBDB' } },
  { text: 'packet/', options: { bold: true, color: WHITE } },
  { text: '  flat CSV exports with a manifest', options: { color: 'AECBDB' } },
], { x: 0.8, y: 3.35, w: 11.6, h: 2.4, fontFace: BF, fontSize: 14, lineSpacing: 26, margin: 0 });
s.addText('Hydrocron responses are cached per feature, so re-runs are free and offline.',
  { x: 0.8, y: 6.2, w: 11.6, h: 0.4, fontFace: BF, fontSize: 12.5, color: TEAL,
    italic: true, margin: 0 });

pptx.writeFile({ fileName: path.join(ROOT, 'deck', 'SWOT_Kotzebue_Sound.pptx') })
  .then(f => console.log('wrote', f));
