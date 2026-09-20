const path=require('path');
const NP='/home/tmittal/.npm-global/lib/node_modules';
const PptxGenJS=require(path.join(NP,'pptxgenjs'));
const ROOT='/media/tmittal/extradrive1/swot_kotzebue';
const F=n=>path.join(ROOT,'figs',n);
const INK='0B2F4A',TEAL='2E8BA8',AMBER='E8A33D',ICE='F2F6F8',WHITE='FFFFFF',
      MUTED='5A7284',RED='B4442E',GREEN='1B7A4B',PLUM='6D4C7D';
const HF='Georgia',BF='Calibri';
const pptx=new PptxGenJS(); pptx.layout='LAYOUT_WIDE';
pptx.title='Kotzebue Sound SWOT: full walkthrough';
let N=0;
function dark(){const s=pptx.addSlide();s.background={color:INK};N++;return s;}
function light(t,k){const s=pptx.addSlide();s.background={color:WHITE};N++;
  if(k)s.addText(k.toUpperCase(),{x:0.55,y:0.30,w:11,h:0.26,fontFace:BF,fontSize:10.5,
    color:TEAL,bold:true,charSpacing:1.6,margin:0});
  s.addText(t,{x:0.55,y:0.55,w:11.4,h:0.7,fontFace:HF,fontSize:27,bold:true,color:INK,margin:0});
  return s;}
function fig(s,f,x,y,w,h){s.addShape(pptx.ShapeType.roundRect,{x:x-0.07,y:y-0.07,
  w:w+0.14,h:h+0.14,fill:{color:ICE},line:{color:TEAL,width:0.75},rectRadius:0.06});
  s.addImage({path:f,x,y,w,h,sizing:{type:'contain',w,h}});}
function body(s,t,x,y,w,h,sz,c){s.addText(t,{x,y,w,h,fontFace:BF,fontSize:sz||12.5,
  color:c||'20303C',lineSpacing:18,margin:0,valign:'top'});}
function bul(s,it,x,y,w,h,sz,c){s.addText(it.map(t=>({text:t,options:{bullet:{code:'2022'},
  breakLine:true}})),{x,y,w,h,fontFace:BF,fontSize:sz||12,color:c||'20303C',
  lineSpacing:18,margin:0,valign:'top'});}
function stat(s,b,l,x,y,w,c){s.addText(b,{x,y,w,h:0.66,fontFace:HF,fontSize:29,bold:true,
  color:c||TEAL,margin:0});s.addText(l,{x,y:y+0.64,w,h:0.6,fontFace:BF,fontSize:10.5,
  color:MUTED,margin:0,valign:'top'});}
function card(s,x,y,w,h,fill,line,title,tc){s.addShape(pptx.ShapeType.roundRect,{x,y,w,h,
  fill:{color:fill},line:{color:line,width:0.85},rectRadius:0.06});
  s.addText(title,{x:x+0.35,y:y+0.22,w:w-0.7,h:0.38,fontFace:HF,fontSize:15,bold:true,
  color:tc||INK,margin:0});}
// standard explainer strip under a figure
function explain(s,what,means,y){
  s.addShape(pptx.ShapeType.roundRect,{x:0.55,y:y,w:6.0,h:1.25,fill:{color:ICE},
    line:{color:TEAL,width:0.7},rectRadius:0.05});
  s.addText('WHAT THIS PLOT IS',{x:0.85,y:y+0.13,w:5.4,h:0.24,fontFace:BF,fontSize:9,
    bold:true,color:TEAL,charSpacing:1.2,margin:0});
  body(s,what,0.85,y+0.4,5.4,0.8,10.5);
  s.addShape(pptx.ShapeType.roundRect,{x:6.8,y:y,w:5.95,h:1.25,fill:{color:'EAF4EE'},
    line:{color:GREEN,width:0.7},rectRadius:0.05});
  s.addText('WHAT IT MEANS',{x:7.1,y:y+0.13,w:5.35,h:0.24,fontFace:BF,fontSize:9,
    bold:true,color:GREEN,charSpacing:1.2,margin:0});
  body(s,means,7.1,y+0.4,5.35,0.8,10.5);
}

/* ============ 1 TITLE ============ */
let s=dark();
s.addText('Kotzebue Sound from orbit',{x:0.8,y:1.7,w:11.6,h:0.95,fontFace:HF,fontSize:44,
  bold:true,color:WHITE,margin:0});
s.addText('SWOT satellite altimetry over three Arctic rivers, two of which have never been gauged',
  {x:0.8,y:2.7,w:11.4,h:0.5,fontFace:BF,fontSize:17,color:'AECBDB',margin:0});
s.addShape(pptx.ShapeType.rect,{x:0.8,y:3.4,w:1.5,h:0.045,fill:{color:AMBER}});
body(s,'A complete walkthrough: how the data are named and cleaned, what every figure '+
 'shows and what it means, where the analysis succeeds, and the three places it fails.',
 0.8,3.75,10.8,1.0,14.5,'AECBDB');
s.addText('github.com/tmittal22/swot-kotzebue-sound',{x:0.8,y:6.3,w:11.6,h:0.35,
  fontFace:BF,fontSize:13,color:TEAL,margin:0});

/* ============ 2 THE QUESTION ============ */
s=light('The question, and why it was unanswerable','Motivation');
bul(s,['Kotzebue Sound has become a focus of harmful algal bloom concern in the Pacific Arctic.',
 'Freshwater timing plausibly matters: stratification, terrestrial nutrient delivery, and flushing of the lagoon complex.',
 'So: when does each river deliver its water, and does that overlap the bloom window?',
 'Until SWOT this was unanswerable, because the rivers are not gauged.'],
 0.6,1.5,7.1,2.6,14);
stat(s,'3','active NWIS gauges in the\nwhole domain',0.6,4.4,2.3);
stat(s,'1','on a major river\n(Kobuk at Kiana)',3.2,4.4,2.3);
stat(s,'0','on the Selawik or Noatak,\never',5.8,4.4,2.3,AMBER);
fig(s,F('fig06_satellite_basemap.png'),8.3,1.5,4.5,3.0);
body(s,'Gleason et al. (2026) find Arctic, multi-channel and ungauged rivers are exactly '+
 'where global river models fail. That is the argument for treating this basin '+
 'observationally rather than through a model.',8.3,4.7,4.5,1.8,12);

/* ============ 3 SOURCES ============ */
s=light('The two papers this follows','Provenance');
card(s,0.6,1.5,5.9,3.4,ICE,TEAL,'Thurman et al. 2025, GRL');
body(s,'10.1029/2024GL113875',0.95,2.0,5.2,0.3,10.5,TEAL);
bul(s,['Spatial hydrographs: subtract a reference long profile from node WSE',
 'Wave length from runs of nodes above their own 90th percentile',
 'Celerity from a SWOT peak plus a gauge peak',
 'Explicitly did NOT use discharge — it was not yet available'],0.95,2.4,5.2,2.3,11);
card(s,6.85,1.5,5.9,3.4,ICE,TEAL,'Gleason et al. 2026, GRL');
body(s,'10.1029/2026GL124323',7.2,2.0,5.2,0.3,10.5,TEAL);
bul(s,['68,347 reaches, ~38% of global discharge',
 'Uses SWOT observations as the standard for judging MODELS',
 'Models struggle in developed, multi-channel, arid and Arctic basins',
 'Neither paper claims SWOT discharge is accurate'],7.2,2.4,5.2,2.3,11);
body(s,'Thurman read in full via Scholar Gateway (Wiley returns HTTP 403 to automated '+
 'fetches). Gleason is not yet in the full-text corpus, so those notes come from the '+
 'abstract and 74 references via OpenAlex, and say so.',0.6,5.2,12.2,0.8,11.5,MUTED);

/* ============ 4 DATA SOURCES ============ */
s=light('Where every number comes from','Data');
s.addTable([[
 {text:'Source',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'Product',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'Gives',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'Auth',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'PO.DAAC Hydrocron'},{text:'SWOT L2_HR_RiverSP Version D'},{text:'reach + node WSE, width, slope'},{text:'none'}],
 [{text:'PO.DAAC Hydrocron'},{text:'SWOT L2_HR_RiverSP 2.0 + L4 SoS'},{text:'discharge estimates'},{text:'none'}],
 [{text:'PO.DAAC Hydrocron'},{text:'SWOT L2_HR_LakeSP PriorLake'},{text:'lake water level'},{text:'none'}],
 [{text:'Zenodo 22259077'},{text:'SWORD v17c + v17b/v16 table'},{text:'network topology, IDs'},{text:'none'}],
 [{text:'Zenodo 14205131'},{text:'HarP intersected SWORD-PLD'},{text:'PLD lake IDs'},{text:'none'}],
 [{text:'USGS NWIS'},{text:'daily + 15-min records'},{text:'the one validation gauge'},{text:'none'}],
 [{text:'NOAA CoastWatch'},{text:'VIIRS chl, nLw(671), Kd(PAR)'},{text:'bloom season, turbidity'},{text:'none'}]],
 {x:0.6,y:1.5,w:12.2,colW:[2.6,4.1,3.9,1.6],fontFace:BF,fontSize:10.5,color:'20303C',
  border:{pt:0.5,color:'C9D8E2'},rowH:0.38,valign:'middle'});
body(s,'Not used: SWOT L2_HR_Raster and PIXC — the true gridded imagery. Those need an '+
 'Earthdata Login, which this analysis deliberately avoided so the whole pipeline runs '+
 'with no credentials.',0.6,4.75,12.2,0.8,12,AMBER);
stat(s,'50,115','reach observations',0.6,5.7,2.6);
stat(s,'2.28 M','node observations',3.3,5.7,2.6);
stat(s,'1,276','PLD lake records',6.0,5.7,2.6);
stat(s,'583 MB','range-fetched from a\n3.9 GB archive in 90 s',8.7,5.7,3.5);

/* ============ 5 NAMING ============ */
s=light('How everything is named','Conventions');
body(s,'Every identifier in this project is structured, not arbitrary. Reading them saves '+
 'a lot of lookups.',0.55,1.4,12.2,0.4,13);
card(s,0.55,1.95,6.0,2.5,ICE,TEAL,'SWORD reach and node IDs');
s.addText('reach_id = C BBBBB RRRR T',{x:0.9,y:2.45,w:5.3,h:0.3,fontFace:'Consolas',
  fontSize:12,bold:true,color:INK,margin:0});
bul(s,['C  continent (8 = Arctic North America; all our reaches start 813)',
 'BBBBB  Pfafstetter level-6 basin',
 'RRRR  reach number, increasing upstream',
 'T  type: 1 river, 3 lake-on-river, 4 dam, 5 unreliable topology, 6 ghost'],
 0.9,2.8,5.3,1.55,10);
card(s,6.8,1.95,5.95,2.5,ICE,TEAL,'Nodes, lakes, passes');
bul(s,['node_id = C BBBBB RRRR NNN T — reach ID with a 3-digit node index, ~200 m spacing',
 'PLD lake_id = C BB NNNNNN T, a different database (prior lakes, not rivers)',
 'cycle_id = which 21-day repeat; pass_id = which ground track. Together they name one overpass.',
 'dist_out = distance along the network to that river’s own outlet, in metres'],
 7.15,2.45,5.25,1.9,10);
card(s,0.55,4.65,12.2,2.15,'FBF3E8',AMBER,'Two naming traps that bit this project');
bul(s,['dist_out is measured to EACH river’s own outlet, so different rivers reuse the same values. Smoothing a globally sorted array silently blended Kobuk and Noatak nodes — caught only by a monotonicity check.',
 'Version D uses SWORD v17b IDs; Version 2.0 uses v16. The same physical reach has two different numbers, and querying the wrong collection returns "feature not found" rather than an error you can interpret.'],
 0.9,5.15,11.5,1.5,11.5);

/* ============ 6 PRODUCT TYPES ============ */
s=light('Which SWOT product answers which question','Products');
s.addTable([[
 {text:'Product',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'Geometry',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'Good for',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'Used here?',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'RiverSP Reach'},{text:'~10 km river segment'},{text:'time series, discharge, seasonality'},{text:'yes — the backbone'}],
 [{text:'RiverSP Node'},{text:'~200 m along centreline'},{text:'long profiles, spatial hydrographs, 2-D fields'},{text:'yes — 2.28 M records'}],
 [{text:'LakeSP PriorLake'},{text:'a mapped lake polygon'},{text:'lake and reservoir level'},{text:'yes — 14 delta lakes'}],
 [{text:'L4 SoS discharge'},{text:'reach, model-inverted'},{text:'discharge where no gauge exists'},{text:'yes — shape only'}],
 [{text:'L2_HR_Raster'},{text:'100 / 250 m grid'},{text:'true imagery, inundation extent'},{text:'NO — needs login'}],
 [{text:'L2_HR_PIXC'},{text:'10-60 m pixel cloud'},{text:'the underlying retrieval'},{text:'NO — needs login'}]],
 {x:0.55,y:1.5,w:12.2,colW:[2.5,2.8,4.6,2.3],fontFace:BF,fontSize:11,color:'20303C',
  border:{pt:0.5,color:'C9D8E2'},rowH:0.45,valign:'middle'});
body(s,'A reach value is a weighted aggregate of its nodes, so reach and node products are '+
 'not independent. Anything claimed at reach level should be visible at node level too, '+
 'and the 2-D figures later are the check on that.',0.55,4.7,12.2,0.9,12.5,TEAL);
fig(s,F('fig08_swot_swaths.png'),0.55,5.7,12.2,1.3);

/* ============ 7 CLEANING ============ */
s=light('How the data are cleaned','Method');
body(s,'Raw SWOT vector data are not usable as delivered. Five filters, applied in order, '+
 'each one added because a specific artefact appeared.',0.55,1.4,12.2,0.5,13);
const filt=[
 ['reach_q / node_q ≤ 1','product quality flag','Admitting 2 returns WSE from −5.2 to +11.2 m on a reach whose bed sits near 2 m.'],
 ['ice_clim_f = 0','ice-covered epochs','KaRIn returns off river ice are not a water surface. NOTE: this flag is a fixed climatology, so it is a seasonal mask, not an ice detector.'],
 ['dark_frac ≤ 0.5','dark-water fraction','Specular or vegetated returns bias heights; profiles showed metre-scale spikes.'],
 ['width ≥ 80 m','channel too narrow','SWOT is specified for rivers wider than 50-100 m. The upper Noatak narrows below that.'],
 ['|η| ≤ max(1 m, 4σ)','per-feature outliers','Robust MAD-based rejection against each feature’s own spread, with a floor so real floods survive.']];
filt.forEach((r,i)=>{const y=2.0+i*0.95;
 s.addShape(pptx.ShapeType.ellipse,{x:0.6,y:y+0.08,w:0.42,h:0.42,fill:{color:TEAL}});
 s.addText(String(i+1),{x:0.6,y:y+0.08,w:0.42,h:0.42,fontFace:HF,fontSize:13,bold:true,
   color:WHITE,align:'center',valign:'middle',margin:0});
 s.addText(r[0],{x:1.2,y:y+0.04,w:2.5,h:0.45,fontFace:'Consolas',fontSize:11,bold:true,
   color:INK,margin:0,valign:'top'});
 s.addText(r[1],{x:3.85,y:y+0.06,w:1.9,h:0.4,fontFace:BF,fontSize:10.5,color:MUTED,
   margin:0,valign:'top'});
 body(s,r[2],5.9,y+0.04,6.9,0.85,10.5);});

/* ============ 8 QC EVIDENCE ============ */
s=light('Why those thresholds, and not others','Method');
body(s,'A filter you cannot justify is a free parameter. So the entire validation was rerun '+
 'under relaxed settings — if the thresholds were arbitrary, skill would be insensitive to them.',
 0.55,1.4,12.2,0.55,13);
s.addTable([[
 {text:'reach_q',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'ice filter',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'n',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'r vs gauge',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'residual RMS',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'≤ 1'},{text:'ice-free'},{text:'84'},{text:'0.980',options:{bold:true,color:GREEN}},{text:'0.21 m',options:{bold:true,color:GREEN}}],
 [{text:'≤ 1'},{text:'ice kept'},{text:'112'},{text:'0.776'},{text:'0.70 m'}],
 [{text:'≤ 2'},{text:'ice-free'},{text:'132'},{text:'0.617'},{text:'1.34 m'}],
 [{text:'≤ 3'},{text:'ice kept'},{text:'163'},{text:'0.581',options:{color:RED}},{text:'1.36 m',options:{color:RED}}]],
 {x:0.55,y:2.15,w:6.6,colW:[1.2,1.5,0.8,1.6,1.5],fontFace:BF,fontSize:12,color:'20303C',
  border:{pt:0.5,color:'C9D8E2'},rowH:0.46,valign:'middle'});
body(s,'Both filters are load-bearing. The naive "use everything" choice drops r from 0.98 '+
 'to 0.58 and inflates the residual sixfold.',0.55,4.5,6.6,1.0,12.5,TEAL);
card(s,7.5,2.15,5.3,3.9,'FBEEE9',RED,'The physical argument');
body(s,'reach_q = 2 is not "slightly worse data". At the Kiana reach it returns water-surface '+
 'elevations from −5.2 m to +11.2 m. The river bed there sits near 2 m and the gauged '+
 'seasonal stage range is about 4 m. Below sea level and 11 m in the air are not extreme '+
 'flows — they are retrieval failures, and averaging them in corrupts everything downstream.',
 7.85,2.7,4.6,2.6,11.5);

/* ============ 9 VERSIONS ============ */
s=light('Two product versions, and which to trust','Data versions');
fig(s,F('fig18_version_comparison.png'),0.55,1.4,8.5,4.6);
explain(s,'Version D (SWORD v17b) matched against Version 2.0 (SWORD v16) on identical reaches within 30 minutes, n = 4,849. Panels: agreement, difference distribution, per-variable correlation, per-river bias, record length, and the trade table.',
 'Elevation is version-stable to a fraction of a centimetre, so every WSE result here is version-independent. Width is not (8.1% median difference), which is why no width-based conclusion is drawn anywhere.',6.15);
s.addTable([
 [{text:'WSE',options:{bold:true}},{text:'r = 0.999996'},{text:'0.08%',options:{color:GREEN,bold:true}}],
 [{text:'slope',options:{bold:true}},{text:'r = 0.937'},{text:'1.6%'}],
 [{text:'width',options:{bold:true}},{text:'r = 0.963'},{text:'8.1%',options:{color:RED,bold:true}}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.0,1.5,1.0],fontFace:BF,fontSize:11,color:'20303C',
  rowH:0.42,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'The practical trade: Version D runs to Sep 2026 and is the backbone here. Version 2.0 '+
 'stops in 2025 but is the ONLY version carrying SoS discharge, so it is used for that alone.',
 9.3,3.1,3.5,1.8,11.5);
body(s,'The official v17b→v16 reach translation table maps all 162 domain reaches, which is '+
 'what makes this comparison possible at all.',9.3,4.9,3.5,1.1,11,MUTED);


/* ============ SWORD versions and resolution ============ */
s=light('SWORD: which version, and at what resolution','Data versions');
body(s,'SWORD is the river database SWOT is defined on. Every reach and node ID in this '+
 'project comes from it, so its version and resolution set the ceiling on everything else.',
 0.55,1.35,12.2,0.5,13);
s.addText('Resolution tiers',{x:0.55,y:1.82,w:6.0,h:0.32,fontFace:HF,fontSize:14,
  bold:true,color:INK,margin:0});
s.addTable([[
 {text:'layer',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'spacing',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'count (N. America)',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'carries SWOT data?',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'centrelines'},{text:'~32 m',options:{bold:true}},{text:'10,349,756'},
  {text:'NO — geometry only',options:{color:RED}}],
 [{text:'nodes'},{text:'~199 m'},{text:'1,705,705'},{text:'yes — used here'}],
 [{text:'reaches'},{text:'~10.1 km'},{text:'38,696'},{text:'yes — used here'}]],
 {x:0.55,y:2.16,w:12.2,colW:[2.4,2.4,3.4,4.0],fontFace:BF,fontSize:11,color:'20303C',
  border:{pt:0.5,color:'C9D8E2'},rowH:0.36,valign:'middle'});
body(s,'The highest-resolution SWORD layer is the 32 m centreline — but it is geometry, not '+
 'measurement. SWOT’s vector product delivers water-surface elevation at node (200 m) and '+
 'reach (10 km) scale only. For metre-scale WSE you need L2_HR_PIXC (10-60 m pixel cloud), '+
 'which requires an Earthdata Login and is not used here.',0.55,3.65,12.2,0.85,11.5,TEAL);
s.addText('Version lineage',{x:0.55,y:4.62,w:6.0,h:0.32,fontFace:HF,fontSize:14,
  bold:true,color:INK,margin:0});
s.addTable([[
 {text:'SWORD',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'released',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'paired SWOT product',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'role here',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'v16'},{text:'Aug 2023'},{text:'RiverSP Version 2.0 + L4 SoS'},{text:'discharge only'}],
 [{text:'v17b'},{text:'2025'},{text:'RiverSP Version D (current)'},{text:'the observations'}],
 [{text:'v17c',options:{bold:true,color:GREEN}},{text:'2 Sep 2026',options:{bold:true,color:GREEN}},
  {text:'none yet — database only'},{text:'topology + IDs',options:{bold:true,color:GREEN}}]],
 {x:0.55,y:4.96,w:12.2,colW:[1.8,2.2,4.6,3.6],fontFace:BF,fontSize:11,color:'20303C',
  border:{pt:0.5,color:'C9D8E2'},rowH:0.36,valign:'middle'});
body(s,'v17c is the newest SWORD (Zenodo 22259077) and is what this project uses for network '+
 'topology. It preserves v17b structure, so its IDs match the Version D observations '+
 'directly — which is why no translation was needed there, only between v17b and v16.',
 0.55,6.4,12.2,0.8,11.5,MUTED);

/* ============ 10 TOPOLOGY ============ */
s=light('Step 1 — deciding what a river is','Analysis');
fig(s,F('fig07_network_topology.png'),0.55,1.4,8.6,4.6);
explain(s,'Six panels tracing 292 candidate SWORD reaches down to 3 mainstems: partition by best_outlet, rank flow paths by drainage area, draw the reach connectivity graph, map the survivors, show reach type along each stem, and tabulate the selection with a reason per path.',
 'river_name is NODATA for 111 of 292 reaches, so naming cannot do this. Topology can, and it is auditable: every path carries a recorded reason for inclusion or exclusion.',6.15);
body(s,'292 reaches · 9 drainage systems · 34 flow paths · 24 confluences',9.3,1.5,3.5,0.8,12,TEAL);
bul(s,['best_outlet → which sound it drains to','main_path_id + facc → rank the paths',
 'rch_id_dn → the actual reach graph','dist_out → order along the stem','type → what is observable'],
 9.3,2.4,3.5,2.2,11);
body(s,'The Kobuk delta appears here as the lowest 84 km typed 5 and 6, which is why its '+
 'profile starts inland.',9.3,4.7,3.5,1.2,11,RED);

/* ============ 11 VALIDATION ============ */
s=light('Step 2 — is the measurement trustworthy?','Analysis');
fig(s,F('fig01_kiana_validation.png'),0.55,1.4,8.6,4.6);
explain(s,'SWOT WSE against USGS 15744500 (Kobuk at Kiana), 3.6 km away. Panels: discharge with overlaid SWOT, the same data as anomalies on the gauge datum, scatter with fit, residual histogram, and the QC sensitivity test.',
 'The slope is a parameter-free physical test — two instruments on the same water surface must differ by a constant, so dWSE/dstage must be exactly 1. Measured 1.002, with nothing tuned to make it so.',6.15);
stat(s,'1.002','slope where 1.000\nis physically required',9.3,1.5,3.5,GREEN);
stat(s,'r = 0.980','84 coincident overpasses\nwithin 1 hour',9.3,2.9,3.5,GREEN);
stat(s,'21 cm','residual, against SWOT’s\nown 11 cm uncertainty',9.3,4.3,3.5);
body(s,'The residual exceeds the instrument spec, as it must: reach and gauge are 3.6 km '+
 'apart with real slope between them.',9.3,5.6,3.5,1.1,10.5,MUTED);

/* ============ 12 PROFILES ============ */
s=light('Step 3 — long profiles, and a bug the physics caught','Analysis');
fig(s,F('fig02_domain_and_profiles.png'),0.55,1.4,8.6,4.6);
explain(s,'The domain map, then the reference long profile of each river — the per-node median elevation that every later anomaly is measured against — plus the revisit-interval distribution.',
 'Water flows downhill, so these must rise monotonically upstream. That single check caught a real bug: the smoother was blending Kobuk and Noatak nodes at equal dist_out, producing 107 m reversals.',6.15);
s.addTable([
 [{text:'river',options:{bold:true,color:WHITE,fill:{color:INK}}},
  {text:'rise',options:{bold:true,color:WHITE,fill:{color:INK}}},
  {text:'gradient',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'Noatak'},{text:'548 m'},{text:'79 cm/km'}],
 [{text:'Kobuk'},{text:'167 m'},{text:'31 cm/km'}],
 [{text:'Selawik'},{text:'4.0 m'},{text:'2.4 cm/km',options:{bold:true,color:AMBER}}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.2,1.1,1.2],fontFace:BF,fontSize:11,color:'20303C',
  rowH:0.42,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'The Noatak profile is monotone to 0.17 m across a 548 m rise — an ungauged Arctic '+
 'river resolved to 0.03%.',9.3,3.3,3.5,1.2,11.5,GREEN);
body(s,'The Selawik falls 4 m in 166 km. That is not a river with a slope; it is a '+
 'backwater controlled by the level of the lake and sound it drains into.',
 9.3,4.6,3.5,1.6,11.5,AMBER);

/* ============ 13 VIRTUAL GAUGES ============ */
s=light('Step 4 — twelve virtual gauges','Analysis');
fig(s,F('fig09_virtual_gauges.png'),0.55,1.4,8.6,4.6);
explain(s,'Four reaches per river, spaced along each one, each plotted as a stage anomaly with a 4 m vertical offset. The grey curve on the Kobuk panel is the USGS discharge record.',
 'Eight of these twelve sit where no gauge has ever been installed. The Selawik traces are visibly flatter and smoother than the Kobuk and Noatak — the backwater signature again, now in the time domain.',6.15);
body(s,'Selection is not arbitrary: reaches must be type 1, at least 90 m wide, and carry '+
 '40+ quality-passed observations. Narrow headwater reaches are excluded because SWOT is '+
 'not specified below ~50-100 m width.',9.3,1.5,3.5,1.9,11.5);
stat(s,'1.3-7.0 m','observed stage range\nacross the twelve',9.3,3.6,3.5);
body(s,'Before the robust outlier filter, some of these read 13-20 m — physically impossible '+
 'and a good example of why cleaning is not optional.',9.3,5.0,3.5,1.3,11,RED);


/* ============ per-river 2-D: Kobuk ============ */
s=light('The Kobuk, on its own','One river at a time');
fig(s,F('fig21a_kobuk.png'),0.55,1.4,12.2,4.6);
explain(s,'(a) where the river sits, coloured by distance upstream so it maps directly onto the y-axis of (b); (b) every node observation as a time x distance field; (c) the same record collapsed to one number per overpass; (d) channel threading; (e) coverage in both product versions.',
 'Panel (c) is what a conventional gauge would give you. Panel (b) is what SWOT gives you instead — the same information plus 534 km of spatial structure that a point measurement discards entirely.',6.15);

/* ============ per-river 2-D: Selawik ============ */
s=light('The Selawik, on its own','One river at a time');
fig(s,F('fig21b_selawik.png'),0.55,1.4,12.2,4.6);
explain(s,'Same layout. 55,190 node observations over 166 km, 29% of the space-time grid filled — the densest of the three relative to river length, because one SWOT pass captures the entire river.',
 'The banding runs almost flat across the whole river: with a 2.4 cm/km gradient the Selawik rises and falls nearly in unison along its length, which is what backwater control looks like in 2-D.',6.15);

/* ============ per-river 2-D: Noatak ============ */
s=light('The Noatak, on its own','One river at a time');
fig(s,F('fig21c_noatak.png'),0.55,1.4,12.2,4.6);
explain(s,'Same layout. 323,183 node observations over 694 km — the largest record of the three, and the only one of the three rivers with no gauge anywhere in its history.',
 'The steepest river here at 79 cm/km, and the most clearly tilted banding: anomalies enter at the top of the panel and appear later at lower distances, which is the signature that motivated the celerity attempt.',6.15);


/* ============ season zooms ============ */
s=light('Kobuk, season by season','Seasonal zoom');
fig(s,F('fig22a_kobuk_seasons.png'),0.55,1.4,12.2,4.6);
explain(s,'One open-water season per panel on a common day-of-year axis, gridded at 10 km x 3 days. Dashed line marks the day of the seasonal anomaly maximum. The bottom row is the single gauge against its 1977-2022 median, for context.',
 'The peak falls on day 251, 241, 245 and 256 in the four years — squarely in the rain window every time, and the anomaly signal builds along the whole river at once rather than propagating up it.',6.15);

s=light('Selawik, season by season','Seasonal zoom');
fig(s,F('fig22b_selawik_seasons.png'),0.55,1.4,12.2,4.6);
explain(s,'Same layout, 166 km of river. 35-45% of the space-time grid is filled in each season — the densest coverage of the three relative to river length.',
 'Day 145, 140, 145 and 136. Four years, a 9-day spread, always in the nival window. The red freshet band spans the entire river simultaneously, then decays: backwater control seen directly.',6.15);

s=light('Noatak, season by season','Seasonal zoom');
fig(s,F('fig22c_noatak_seasons.png'),0.55,1.4,12.2,4.6);
explain(s,'Same layout, 694 km of river and the largest node record of the three. Note this river has no gauge at all — the bottom row shows the Kobuk gauge purely as regional context.',
 'Day 240, 237, 239 and 257: rain-window like the Kobuk, but with visible spring structure too. The 2026 panel is truncated on 16 September, which is why its peak sits later and its amplitude lower.',6.15);

/* ============ 14 2-D FIELDS ============ */
s=light('All three together','Everything at once');

fig(s,F('fig19_hovmoller.png'),0.55,1.4,8.7,5.0);
explain(s,'The three rivers stacked on a common time axis, each with its own distance axis. Beside each, facc marking tributary inflows (dashed) and n_chan_max marking multi-threaded reaches (red).',
 'Stacked, the phase difference is visible directly: the Selawik reddens in May while the Kobuk and Noatak are still blue, and reverses by late August. That is the headline result, read off one figure.',6.55);
stat(s,'597,344','node observations across\nthe three rivers',9.45,1.5,3.3);
stat(s,'26-29%','of the space-time grid\nfilled; gaps are winter ice',9.45,2.9,3.3);
body(s,'This is also the check that reach-level and node-level results agree — anything '+
 'claimed at reach scale should be visible here.',9.45,4.3,3.3,1.4,11,MUTED);

/* ============ 15 CONTRIBUTIONS ============ */
s=light('Step 5b — contributions and multi-threading','Analysis');
body(s,'Two SWORD attributes govern how a river reading should be interpreted: where '+
 'tributaries add drainage area, and whether the channel is single or multi-threaded.',
 0.55,1.4,12.2,0.5,13);
s.addTable([[
 {text:'river',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'reaches',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'tributary inflows',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'multi-threaded',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'max channels',options:{bold:true,color:WHITE,fill:{color:INK}}},
 {text:'facc span (km2)',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'Noatak'},{text:'57'},{text:'12'},{text:'81%'},{text:'8'},{text:'953 - 61,951'}],
 [{text:'Kobuk'},{text:'40'},{text:'13'},{text:'100%',options:{bold:true,color:RED}},{text:'6'},{text:'1,977 - 31,315'}],
 [{text:'Selawik'},{text:'12'},{text:'3'},{text:'50%'},{text:'3'},{text:'4,029 - 11,191'}]],
 {x:0.55,y:2.05,w:12.2,colW:[1.7,1.5,2.4,2.2,2.0,2.4],fontFace:BF,fontSize:12,
  color:'20303C',rowH:0.5,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
card(s,0.55,4.25,6.0,2.5,'FBEEE9',RED,'The Kobuk problem');
body(s,'Every observed Kobuk reach is multi-threaded, up to 6 channels. SWOT reach-averaged '+
 'width and elevation therefore aggregate across threads along the ENTIRE river, not just '+
 'the delta. This is exactly the regime Gleason et al. identify as hardest to model, and it '+
 'is why no width-based conclusion is drawn.',0.9,4.8,5.3,1.8,11.5);
card(s,6.8,4.25,5.95,2.5,ICE,TEAL,'How to compare contributions');
bul(s,['Rank by facc step at each confluence — the only mass-based measure available',
 'Do NOT use SWOT width: 8% version-unstable and thread-aggregated',
 'Do NOT use SoS discharge: 2.9x biased'],7.15,4.8,5.25,1.8,11.5);

/* ============ 16 CHANNEL PARTITION ============ */
s=light('Which thread actually carries the flow?','Analysis');
fig(s,F('fig20_channel_partition.png'),0.55,1.4,8.6,4.6);
explain(s,'The Kobuk distributaries and Hotham Inlet channels ranked on four independent proxies: SWORD drainage-area attribution, channel width, stage amplitude, and coupling to upstream main-stem stage.',
 'facc and width agree on roughly 60 / 19 / 19. The dynamic proxies do NOT discriminate — every channel is backwater-coupled to the same inlet at r = 0.87-0.89 — so SWOT cannot confirm the split.',6.15);
s.addTable([
 [{text:'channel',options:{bold:true,color:WHITE,fill:{color:INK}}},
  {text:'facc',options:{bold:true,color:WHITE,fill:{color:INK}}},
  {text:'width',options:{bold:true,color:WHITE,fill:{color:INK}}},
  {text:'amp',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'Kobuk main + arms'},{text:'62%'},{text:'60%'},{text:'37%'}],
 [{text:'Hotham channel A'},{text:'19%'},{text:'18%'},{text:'25%'}],
 [{text:'Hotham channel B'},{text:'19%'},{text:'15%'},{text:'18%'}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.6,0.65,0.65,0.6],fontFace:BF,fontSize:9.5,color:'20303C',
  rowH:0.42,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Honest answer: the static estimate is ~60/19/19, but it rests on SWORD’s attribution '+
 'rather than on a measurement, and the observations can neither confirm nor refute it.',
 9.3,3.5,3.5,1.6,11.5,RED);
body(s,'Resolving it needs ADCP transects at the bifurcations or a hydraulic model of the delta. A genuine limit, not a processing choice.',
 9.3,5.15,3.5,0.95,10.5,MUTED);

/* ============ 17 SEASONAL ============ */
s=light('Step 6 — the seasonal regime','Result');
fig(s,F('fig03_seasonal_regime.png'),0.55,1.4,8.6,4.6);
explain(s,'Gauge climatology with SWOT-era years overlaid; day-of-year of the annual maximum across 40 years; the SWOT stage index for all three rivers; and the seasonal composite.',
 'The Kobuk peaked in the late window in all three SWOT years against a 14% base rate — but the 40-year trend is NOT significant (p = 0.29), so this is a property of those years, not a demonstrated shift.',6.15);
s.addTable([
 [{text:'Selawik',options:{bold:true,color:WHITE,fill:{color:RED}}},{text:'day 141, 145, 145'}],
 [{text:'Kobuk',options:{bold:true,color:WHITE,fill:{color:INK}}},{text:'day 240, 250'}],
 [{text:'Noatak',options:{bold:true,color:WHITE,fill:{color:'3F6B4A'}}},{text:'day 168, 237'}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.4,2.1],fontFace:BF,fontSize:11,color:'20303C',rowH:0.42,
  valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'The Selawik and Kobuk drain into the SAME lagoon complex about 100 days apart. '+
 'Freshwater arriving during the bloom window is Kobuk and Noatak water.',
 9.3,3.1,3.5,1.7,12,TEAL);
body(s,'2026 is censored, not scored: the record ends 16 Sep with the Kobuk still rising.',
 9.3,4.9,3.5,1.2,11,MUTED);

/* ============ 18 INDEPENDENCE ============ */
s=light('Step 7 — are the rivers independent forcings?','Result');
fig(s,F('fig13_river_independence.png'),0.55,1.4,8.6,4.3);
explain(s,'Seasonal phasing of all six rivers, the pairwise correlation matrix of their weekly stage indices, and the distribution of those correlations.',
 'Checked BEFORE attributing anything, not after. Median pairwise r = 0.56 with 5 of 15 pairs above 0.7 — they share weather, so they cannot be cleanly separated as forcings.',5.85);
body(s,'Kobuk–Squirrel at 0.86 is expected: the Squirrel is a Kobuk tributary, not an '+
 'independent input. The Wulik is the most independent at r = 0.23 with the Selawik, which '+
 'fits — it drains a different coast and never reaches the sound.',9.3,1.5,3.5,2.0,11.5);
stat(s,'0.56','median pairwise r\nbetween the six rivers',9.3,3.7,3.5,AMBER);

/* ============ 19 WAVES ============ */
s=light('Step 8 — flow waves: length and amplitude','Result');
fig(s,F('fig10_wave_propagation.png'),0.55,1.4,8.6,4.6);
explain(s,'Wave length from runs of ≥10 nodes above their own 90th-percentile WSE; the artefact test; peak tracking; amplitude along river; seasonality of detections; and one example event.',
 'Length and amplitude are measured cleanly — 939 detections, median 4-8 km, 65 over 50 km, max 243 km, only 1% truncated. Amplitude grows upstream as the channel narrows. None of this needs celerity.',6.15);
body(s,'Wave occurrence independently reproduces the phase split: the Selawik’s waves are '+
 'almost entirely nival, the Kobuk’s and Noatak’s are bimodal with a rain-window peak.',
 9.3,1.5,3.5,1.7,11.5,TEAL);
stat(s,'939','wave detections',9.3,3.4,3.5);
stat(s,'243 km','longest, on the Kobuk',9.3,4.7,3.5);

/* ============ 20 RETRACTION ============ */
s=dark();
s.addText('WHERE THIS FAILED',{x:0.8,y:0.65,w:11,h:0.3,fontFace:BF,fontSize:11.5,bold:true,
  color:AMBER,charSpacing:1.8,margin:0});
s.addText('A celerity result that looked right, and was not',{x:0.8,y:1.0,w:11.6,h:0.75,
  fontFace:HF,fontSize:30,bold:true,color:WHITE,margin:0});
s.addText([{text:'The apparent finding.  ',options:{bold:true,color:AMBER}},
 {text:'Tracking the anomaly peak across consecutive overpasses gave 12 coherent events (r² > 0.7), all on the Noatak, all 12 moving downstream, median 1.53 m/s — inside the kinematic-wave prior of 1.4-3.3 m/s. Direction alone looked decisive at p = 0.5¹².',options:{color:'CFE0EA'}}],
 {x:0.8,y:2.0,w:11.6,h:1.1,fontFace:BF,fontSize:14,lineSpacing:21,margin:0});
s.addText([{text:'The artefact.  ',options:{bold:true,color:AMBER}},
 {text:'SWOT’s consecutive passes sweep ALONG the river, so the centre of the observed segment marches downstream between overpasses. Regressing peak position and segment centre on time for the same events gives a median slope ratio of ',options:{color:'CFE0EA'}},
 {text:'0.99',options:{bold:true,color:WHITE}},
 {text:'. The apparent wave speed is the ground-track speed.',options:{color:'CFE0EA'}}],
 {x:0.8,y:3.25,w:11.6,h:1.2,fontFace:BF,fontSize:14,lineSpacing:21,margin:0});
s.addText('Three SWOT celerity estimators, three failures. No SWOT celerity is claimed here.',
 {x:0.8,y:4.7,w:11.6,h:0.5,fontFace:BF,fontSize:15,bold:true,color:WHITE,margin:0});
s.addText('PRIORS P5b now requires that slope ratio be reported for any future celerity claim in this basin.',
 {x:0.8,y:5.4,w:11.6,h:0.5,fontFace:BF,fontSize:12.5,color:TEAL,italic:true,margin:0});

/* ============ 21 DELTA ============ */
s=light('Step 9 — through the delta','Result');
fig(s,F('fig17_channels_and_lakes.png'),0.55,1.4,8.6,4.6);
explain(s,'Every SWORD reach around the delta coloured by type; facc stepping DOWN through the distributaries; water level in main stem versus delta and inlet channels; inlet and lake levels; and their lagged coupling to the river.',
 'These are the type 3 and 5 reaches excluded from every earlier figure because they break a 1-D profile. Here they are the subject: water level falls 2.97 m to 0.55 m and seasonal range 6.18 m to 1.40 m across the delta.',6.15);
s.addTable([
 [{text:'',options:{fill:{color:INK}}},
  {text:'WSE',options:{bold:true,color:WHITE,fill:{color:INK}}},
  {text:'range',options:{bold:true,color:WHITE,fill:{color:INK}}}],
 [{text:'Main stem'},{text:'2.97 m'},{text:'6.18 m'}],
 [{text:'Delta arms'},{text:'0.70 m'},{text:'1.94 m'}],
 [{text:'Hotham A'},{text:'0.77 m'},{text:'2.08 m'}],
 [{text:'Hotham B'},{text:'0.55 m'},{text:'1.40 m'}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.4,1.1,1.0],fontFace:BF,fontSize:10.5,color:'20303C',
  rowH:0.38,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Flow splitting into a backwater-controlled receiving basin, measured directly.',
 9.3,3.6,3.5,1.0,11.5,TEAL);

/* ============ 22 LAKES ============ */
s=light('Step 10 — Hotham Inlet and Selawik Lake','Result');
card(s,0.55,1.4,3.95,5.2,ICE,TEAL,'What exists');
bul(s,['27 lake-flagged SWORD reaches across the inlet and lake',
 '1,871 quality-passed observations on the channel reaches',
 '14 PLD prior lakes in the delta, 1,276 records',
 'Reached via Hydrocron feature=PriorLake',
 'PLD lake IDs obtained from HarP on Zenodo, not from the authenticated PO.DAAC path'],
 0.9,1.95,3.3,4.4,11);
card(s,4.75,1.4,3.95,5.2,'EAF4EE',GREEN,'What it shows',GREEN);
body(s,'Both basins track Kobuk stage essentially instantaneously:',5.1,1.95,3.3,0.6,11.5);
s.addTable([
 [{text:'Hotham Inlet',options:{bold:true}},{text:'r = 0.85'}],
 [{text:'Selawik Lake',options:{bold:true}},{text:'r = 0.87'}]],
 {x:5.1,y:2.6,w:3.3,colW:[1.7,1.6],fontFace:BF,fontSize:10.5,color:'20303C',rowH:0.4,
  valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'at zero lag, collapsing to 0.14 and 0.26 by two weeks. The response is sub-weekly: '+
 'these basins are hydraulically connected to the river, not storage-buffered reservoirs '+
 'that integrate it.',5.1,3.5,3.3,2.0,11);
card(s,8.9,1.4,3.9,5.2,'FBEEE9',RED,'What is still missing',RED);
bul(s,['Selawik Lake and Hotham Inlet themselves are NOT in the PLD subset obtained — the 14 lakes cap at 0.57 km2',
 'Part of that r = 0.85 is shared seasonality, not proof of forcing',
 'No bathymetry, so no volume and no residence time',
 'No salinity, so the freshwater/marine boundary is unconstrained',
 'Getting the big basins as PLD lakes needs hydroweb.next, which is interactive'],
 9.25,1.95,3.2,4.4,10.5);

/* ============ 23 OCEAN DATA ============ */
s=light('Step 11 — what the ocean data actually are','Ocean');
fig(s,F('fig14_ocean_timeseries.png'),0.55,1.4,8.6,4.6);
explain(s,'Weekly VIIRS chlorophyll, nLw(671) and Kd(PAR) for five receiving basins from 2012-2026, with seasonal climatologies alongside. Lines break across the polar-night gap rather than ramping through it.',
 'All three quantities order identically — Selawik Lake > Hotham Inlet > Eschscholtz Bay > inner sound > outer sound. That is a turbidity gradient away from the river mouths, and chlorophyll following it is a warning sign.',6.15);
stat(s,'Jun-Sep','the only months with valid\nretrievals at this latitude',9.3,1.5,3.5,AMBER);
body(s,'0.0-0.6% of pixels are valid Oct-May: polar night, sea ice and low sun angle. No '+
 'annual statistic is computed anywhere.',9.3,2.9,3.5,1.4,11.5);
body(s,'Five basins, 2012-2026 — a 15-year record that long predates SWOT, which is what '+
 'gives the later correlation tests their statistical power.',9.3,4.4,3.5,1.6,11.5,TEAL);

/* ============ 24 CASE-2 ============ */
s=light('Step 12 — why chlorophyll here is not biomass','Ocean');
fig(s,F('fig11_optics_vs_biology.png'),0.55,1.4,8.6,4.6);
explain(s,'August median maps of chlorophyll, nLw(671) and Kd(PAR); apparent chlorophyll plotted against the sediment proxy; the partial-correlation test; and the lag structure for the inner sound.',
 'Kotzebue Sound is Case-2 water: shallow, turbid and CDOM-rich. Standard ocean-colour algorithms read sediment and dissolved organic matter AS chlorophyll. The three maps peak in the same plume-fed water, which is the tell.',6.15);
s.addTable([
 [{text:'Hotham Inlet',options:{bold:true}},{text:'8-38 mg m⁻³',options:{color:RED,bold:true}}],
 [{text:'Outer sound',options:{bold:true}},{text:'1.3-2.4 mg m⁻³'}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.8,1.7],fontFace:BF,fontSize:10.5,color:'20303C',rowH:0.42,
  valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Jun-Sep medians. The inner values are not credible as phytoplankton biomass — they '+
 'are largely the Kobuk plume.',9.3,2.5,3.5,1.3,11.5);
body(s,'So chlorophyll is used for SEASON TIMING and interannual comparison only, never as '+
 'a calibrated biomass measurement.',9.3,3.9,3.5,1.4,11.5,TEAL);
body(s,'nLw(671) is the discriminator: it responds to suspended sediment and is nearly blind '+
 'to chlorophyll.',9.3,5.4,3.5,1.2,11,MUTED);

/* ============ 25 CHL VS RIVER ============ */
s=light('Step 13 — does river flow track the bloom season?','Ocean');
fig(s,F('fig05_river_ocean_coupling.png'),0.55,1.4,8.6,4.6);
explain(s,'August chlorophyll map with the basins outlined; bloom season against river forcing; interannual medians; the lagged correlation on the FULL 2012-2026 gauge record; SWOT-era Kobuk flow against the bloom window; and the data-availability bar.',
 'The first version of this test used only 4 SWOT summers (n = 46) and nothing survived correction. Using the 15-year gauge record instead gives n = 178-217, and 12 of 21 correlations survive Bonferroni.',6.15);
s.addTable([
 [{text:'Inner sound',options:{bold:true}},{text:'+0.32'},{text:'2 wk'}],
 [{text:'Hotham Inlet',options:{bold:true}},{text:'−0.31'},{text:'1 wk'}],
 [{text:'Outer sound',options:{bold:true}},{text:'+0.24'},{text:'0 wk'}]],
 {x:9.3,y:1.5,w:3.5,colW:[1.7,0.9,0.9],fontFace:BF,fontSize:10.5,color:'20303C',
  rowH:0.42,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Strongest lag per basin. The OPPOSITE signs inside and outside Hotham Inlet are the '+
 'interesting part — consistent with flushing a turbid inlet while exporting plume water to '+
 'the sound.',9.3,3.0,3.5,1.8,11.5,TEAL);
body(s,'Power, not significance thresholds, was the whole story: the same test on 4 summers '+
 'versus 15 years gives 0 and 12 survivors.',9.3,4.9,3.5,1.5,11,AMBER);

/* ============ 26 OPTICS VS BIOLOGY ============ */
s=light('Step 14 — optics or productivity?','Ocean');
body(s,'Partial correlation of log discharge against log chlorophyll, controlling for '+
 'nLw(671). If the correlation collapses, it was the plume. If it survives, something else '+
 'is there. 12 tests, Bonferroni alpha = 0.00417.',0.55,1.4,12.2,0.6,13);
card(s,0.55,2.15,3.95,2.6,ICE,TEAL,'Outer sound → optics');
body(s,'Chlorophyll tracks sediment at r = 0.62, and the raw +0.24 discharge correlation '+
 'collapses to +0.11 (p = 0.10). Nothing survives. That one was the plume.',
 0.9,2.65,3.3,1.9,11);
card(s,4.75,2.15,3.95,2.6,'EAF4EE',GREEN,'Inner sound → survives',GREEN);
body(s,'Partial r rises with lag: 0.18, 0.24, 0.28, 0.26 at 0-3 weeks, while the sediment '+
 'coupling decays 0.43 → −0.02. The curves cross. Three of four lags survive.',
 5.1,2.65,3.3,1.9,11);
card(s,8.9,2.15,3.9,2.6,'FBF3E8',AMBER,'Hotham Inlet → not sediment');
body(s,'r(Q, nLw) = −0.03, so the plume is not involved, and the partial correlation '+
 '(−0.28) matches the raw one. High discharge, lower chlorophyll: dilution of a standing '+
 'stock.',9.25,2.65,3.2,1.9,11);
body(s,'The lag structure is the argument. A signal that is weakest when the plume dominates '+
 'and peaks two weeks later, after the plume tracer has decorrelated, is what growth looks '+
 'like rather than what an optical artefact looks like.',0.55,5.0,12.2,0.8,13,TEAL);
body(s,'Residual limitation: nLw(671) controls for SEDIMENT, not CDOM, which absorbs in the '+
 'blue and is a major Arctic plume constituent. The lag argument weighs against a pure-CDOM '+
 'explanation but does not exclude it. aCDOM(443) is the next control.',
 0.55,5.9,12.2,0.9,12,RED);

/* ============ 27 ATTRIBUTION ============ */
s=light('Step 15 — who drives what','Ocean');
fig(s,F('fig15_attribution.png'),0.55,1.4,8.6,4.3);
explain(s,'Every river forcing against every receiving basin at 1 and 2 week lags, raw and sediment-controlled, plus the sample size available to each forcing.',
 'One of 70 tests survives Bonferroni: Kobuk gauged discharge to inner-sound chlorophyll at a 2-week lag. No SWOT-based forcing survives, and that is power (n = 28-39) rather than absence.',5.85);
body(s,'A cautionary case is deliberately left in: Squirrel → outer sound shows raw r = 0.65 '+
 'at n = 29 with a significance star, collapsing to 0.40 once sediment is controlled. The '+
 'Squirrel is a Kobuk tributary hundreds of km from that basin.',9.3,1.5,3.5,2.2,11.5);
stat(s,'1 of 70','survive correction',9.3,3.9,3.5,GREEN);

/* ============ 28 SWOT-ONLY ============ */
s=light('Step 16 — can SWOT stand on its own?','SWOT-only');
fig(s,F('fig16_swot_only.png'),0.55,1.4,8.6,4.6);
explain(s,'SoS discharge against the one gauge (shape and magnitude), SWOT-only discharge at every river outlet, SWOT-only seasonality, the spread between discharge algorithms, and SWOT-only forcing against chlorophyll.',
 'It has to stand alone — the Selawik and Noatak have no gauge. SoS is an excellent SHAPE estimator (r = 0.99 in log space) and a poor MAGNITUDE estimator (2.9x low, NSE = −2.0).',6.15);
body(s,'Used as a shape estimator it earns its place: SWOT alone, with no in-situ data '+
 'anywhere, recovers the phase split — Selawik day 154, Kobuk 236, Noatak 251.',
 9.3,1.5,3.5,1.7,11.5,GREEN);
body(s,'It fails on attribution: substituting SoS for gauged discharge leaves n = 12, and '+
 'the correlations change sign against the n = 201 analysis.',9.3,3.3,3.5,1.6,11.5,RED);
body(s,'The SoS product carries both a gauge-constrained and an unconstrained branch and '+
 'Hydrocron does not say which it serves — but a constrained estimate could not be 3x off at '+
 'a gauged reach, so this is the unconstrained branch. An inversion from global priors, '+
 'making the bias expected rather than anomalous.',9.3,5.0,3.5,1.8,10.5,MUTED);

/* ============ 29 BLOOMS ============ */
s=light('The blooms: two models, neither tested here','Open question');
body(s,'This project measured river hydrology. It contains no HAB cell counts, no toxin '+
 'data and no Alexandrium observations, and cannot arbitrate between these. They are also '+
 'not mutually exclusive.',0.55,1.4,12.2,0.7,13);
card(s,0.55,2.25,6.0,3.4,ICE,TEAL,'Model A — advective supply');
body(s,'Blooms form offshore in the Bering Sea and are carried north through the Bering '+
 'Strait; local cyst beds germinate when bottom water is warm enough.',0.9,2.75,5.3,1.0,12);
bul(s,['The 2022 event was tracked entering from the west and advecting north (Fachon et al. 2024)',
 'That year the Ledyard Bay cyst bed was thermally suppressed at ~1.8 C',
 'Cells were dense across a wide range of nutrient concentrations'],0.9,3.8,5.3,1.6,10.5);
card(s,6.8,2.25,5.95,3.4,'FBF3E8',AMBER,'Model B — local river modulation');
body(s,'River freshwater sets stratification, delivers terrestrial nutrients and organic '+
 'matter, and controls flushing — modulating how a bloom develops once cells are present.',
 7.15,2.75,5.25,1.0,12);
bul(s,['Kobuk discharge leads inner-sound chlorophyll by ~2 weeks, surviving a sediment control',
 'Kobuk and Noatak peak inside the bloom window; the Selawik does not',
 'But chlorophyll is not Alexandrium, and CDOM is uncontrolled'],7.15,3.8,5.25,1.6,10.5);
body(s,'Separating them needs HAB cell counts or toxin data, a CDOM control, and moorings or '+
 'a circulation model for the sound. None of those are in this project.',
 0.55,5.9,12.2,0.8,12.5,RED);

/* ============ 30 SYNTHESIS ============ */
s=light('The area, end to end','Synthesis');
const st2=[['Snowmelt, mid-May','The Selawik peaks at day 141-145 every observed year and drains into Selawik Lake.'],
 ['Rain, late August','The Kobuk and Noatak peak at day 236-251, roughly 100 days later.'],
 ['Through the delta','The Kobuk splits; facc falls 31,315 → 15,162 km2 and stage drops 2.97 → 0.55 m.'],
 ['Which thread','facc and width say ~60/19/19, but the dynamic data cannot confirm it.'],
 ['Into the inlet','Hotham Inlet and Selawik Lake follow river stage within a week (r = 0.85, 0.87).'],
 ['Out to the sound','Kobuk discharge leads inner-sound chlorophyll by ~2 weeks, surviving a sediment control.'],
 ['The blooms','Open. Two models, neither tested here.']];
st2.forEach((r,i)=>{const y=1.45+i*0.78;
 s.addShape(pptx.ShapeType.ellipse,{x:0.6,y:y+0.04,w:0.4,h:0.4,fill:{color:i===6?RED:TEAL}});
 s.addText(String(i+1),{x:0.6,y:y+0.04,w:0.4,h:0.4,fontFace:HF,fontSize:12,bold:true,
   color:WHITE,align:'center',valign:'middle',margin:0});
 s.addText(r[0],{x:1.15,y:y+0.02,w:2.9,h:0.45,fontFace:BF,fontSize:12.5,bold:true,
   color:i===6?RED:INK,margin:0,valign:'top'});
 s.addText(r[1],{x:4.1,y:y+0.02,w:8.6,h:0.7,fontFace:BF,fontSize:11,color:'20303C',
   lineSpacing:14,margin:0,valign:'top'});});

/* ============ 31 CAN / CANNOT ============ */
s=light('What the data support, and what they do not','Summary');
card(s,0.55,1.4,6.0,5.3,'EAF4EE',GREEN,'Supported',GREEN);
bul(s,['SWOT WSE is trustworthy here: slope 1.002 where physics demands 1.0, 21 cm residual.',
 'Revisit is ~1 day, not 21, from swath overlap at 67°N.',
 'Selawik and Kobuk deliver freshwater ~100 days apart into the same estuarine complex.',
 'The Selawik is backwater-controlled: 4.0 m of fall over 166 km.',
 'Wave length and amplitude are measurable; 939 detections.',
 'Water level falls 2.97 → 0.55 m across the Kobuk delta as flow splits.',
 'Hotham Inlet and Selawik Lake respond to the river sub-weekly.',
 'Kobuk discharge leads inner-sound chlorophyll by ~2 weeks and survives a sediment control.'],
 0.9,1.95,5.3,4.6,11);
card(s,6.8,1.4,5.95,5.3,'FBEEE9',RED,'Not supported',RED);
bul(s,['No SWOT flow-wave celerity. Three estimators, three failures; the best-looking one tracked the ground track at a ratio of 0.99.',
 'No claim that the Kobuk late-summer peak is a trend (40-year p = 0.29).',
 'No biological reading of the outer sound: that correlation is plume optics.',
 'No attribution from SWOT alone (n = 28-39).',
 'No absolute freshwater flux: SoS discharge is 2.9x low.',
 'No confirmed flow split between delta threads.',
 'No cause for the harmful algal blooms, in either direction.'],
 7.15,1.95,5.25,4.6,11);

/* ============ 32 REPO ============ */
s=dark();
s.addText('Everything is public',{x:0.8,y:1.4,w:11.6,h:0.7,fontFace:HF,fontSize:32,
  bold:true,color:WHITE,margin:0});
s.addText('github.com/tmittal22/swot-kotzebue-sound',{x:0.8,y:2.2,w:11.6,h:0.5,
  fontFace:BF,fontSize:19,color:AMBER,margin:0});
s.addShape(pptx.ShapeType.rect,{x:0.8,y:2.95,w:1.5,h:0.045,fill:{color:AMBER}});
s.addText([
 {text:'src/',options:{bold:true,color:WHITE}},{text:'  20 scripts, each one figure or one fetch\n',options:{color:'AECBDB'}},
 {text:'figs/',options:{bold:true,color:WHITE}},{text:'  20 figures, all regenerable from scratch\n',options:{color:'AECBDB'}},
 {text:'packet/',options:{bold:true,color:WHITE}},{text:'  flat CSV exports with a manifest\n',options:{color:'AECBDB'}},
 {text:'docs/',options:{bold:true,color:WHITE}},{text:'  THEORY, PRIORS, WALKTHROUGH, PAPERS and every results table\n',options:{color:'AECBDB'}},
 {text:'deck/',options:{bold:true,color:WHITE}},{text:'  this deck and its build script',options:{color:'AECBDB'}}],
 {x:0.8,y:3.3,w:11.6,h:2.4,fontFace:BF,fontSize:14,lineSpacing:26,margin:0});
s.addText('No Earthdata Login needed for anything shown here. Hydrocron responses are cached '+
 'per feature, so re-runs are free and offline.',{x:0.8,y:6.0,w:11.6,h:0.7,fontFace:BF,
 fontSize:12.5,color:TEAL,italic:true,margin:0});

pptx.writeFile({fileName:path.join(ROOT,'deck','Kotzebue_Full_Deck.pptx')})
  .then(()=>console.log('total slides:',N));

