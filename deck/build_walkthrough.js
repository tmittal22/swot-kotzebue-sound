const path = require('path');
const NP = '/home/tmittal/.npm-global/lib/node_modules';
const PptxGenJS = require(path.join(NP, 'pptxgenjs'));
const ROOT = '/media/tmittal/extradrive1/swot_kotzebue';
const F = n => path.join(ROOT, 'figs', n);

const INK='0B2F4A', TEAL='2E8BA8', AMBER='E8A33D', ICE='F2F6F8',
      WHITE='FFFFFF', MUTED='5A7284', RED='B4442E', GREEN='1B7A4B';
const HF='Georgia', BF='Calibri';
const pptx = new PptxGenJS();
pptx.layout='LAYOUT_WIDE';
pptx.title='Kotzebue Sound: sequential walkthrough';

function dark(){const s=pptx.addSlide();s.background={color:INK};return s;}
function light(title,kicker,step){
  const s=pptx.addSlide(); s.background={color:WHITE};
  if(kicker) s.addText(kicker.toUpperCase(),{x:0.55,y:0.30,w:11,h:0.26,fontFace:BF,
    fontSize:11,color:TEAL,bold:true,charSpacing:1.6,margin:0});
  s.addText(title,{x:0.55,y:0.56,w:11.3,h:0.72,fontFace:HF,fontSize:28,bold:true,
    color:INK,margin:0});
  if(step!==undefined && step!==null){
    s.addShape(pptx.ShapeType.ellipse,{x:12.15,y:0.32,w:0.6,h:0.6,fill:{color:AMBER}});
    s.addText(String(step),{x:12.15,y:0.32,w:0.6,h:0.6,fontFace:HF,fontSize:19,
      bold:true,color:INK,align:'center',valign:'middle',margin:0});
  }
  return s;
}
function fig(s,f,x,y,w,h){
  s.addShape(pptx.ShapeType.roundRect,{x:x-0.07,y:y-0.07,w:w+0.14,h:h+0.14,
    fill:{color:ICE},line:{color:TEAL,width:0.75},rectRadius:0.06});
  s.addImage({path:f,x,y,w,h,sizing:{type:'contain',w,h}});
}
function body(s,t,x,y,w,h,sz,col){
  s.addText(t,{x,y,w,h,fontFace:BF,fontSize:sz||12.5,color:col||'20303C',
    lineSpacing:18,margin:0,valign:'top'});
}
function bul(s,items,x,y,w,h,sz){
  s.addText(items.map(t=>({text:t,options:{bullet:{code:'2022'},breakLine:true}})),
   {x,y,w,h,fontFace:BF,fontSize:sz||12.5,color:'20303C',lineSpacing:19,margin:0,valign:'top'});
}
function stat(s,big,lab,x,y,w,c){
  s.addText(big,{x,y,w,h:0.7,fontFace:HF,fontSize:32,bold:true,color:c||TEAL,margin:0});
  s.addText(lab,{x,y:y+0.68,w,h:0.62,fontFace:BF,fontSize:11,color:MUTED,margin:0,valign:'top'});
}

/* 1 title */
let s=dark();
s.addText('Kotzebue Sound, river by river',{x:0.8,y:1.9,w:11.6,h:0.9,fontFace:HF,
  fontSize:42,bold:true,color:WHITE,margin:0});
s.addText('A sequential walkthrough of every SWOT measurement in the basin',
  {x:0.8,y:2.85,w:11.2,h:0.5,fontFace:BF,fontSize:18,color:'AECBDB',margin:0});
s.addShape(pptx.ShapeType.rect,{x:0.8,y:3.55,w:1.5,h:0.045,fill:{color:AMBER}});
body(s,'From "what counts as a river" through gauge validation, main stem versus '+
  'delta distributaries, and on into Hotham Inlet and Selawik Lake.',
  0.8,3.9,10.5,1.0,15,'AECBDB');
s.addText('Noatak  ·  Kobuk  ·  Selawik',{x:0.8,y:6.4,w:11.6,h:0.35,fontFace:BF,
  fontSize:13,color:TEAL,margin:0});

/* 2 the area */
s=light('The area, and what drains into it','Orientation',0);
fig(s,F('fig06_satellite_basemap.png'),0.55,1.5,8.6,5.3);
body(s,'Three large rivers reach the sound. The Kobuk and Selawik empty into the '+
  'Hotham Inlet / Selawik Lake complex; the Noatak enters the sound directly at '+
  'Kotzebue.',9.4,1.6,3.4,1.6);
stat(s,'31,000','km2  Kobuk',9.4,3.3,3.4);
stat(s,'32,000','km2  Noatak',9.4,4.5,3.4);
stat(s,'8,160','km2  Selawik',9.4,5.7,3.4);

/* 3 step 1 what is a river */
s=light('What counts as a river here?','Step 1',1);
fig(s,F('fig07_network_topology.png'),0.55,1.5,8.6,5.3);
body(s,'292 SWORD reaches sit in the box, across 9 drainage systems and 34 flow '+
  'paths. river_name is NODATA for 111 of them, including most of the lower '+
  'Kobuk, so names cannot do this.',9.4,1.55,3.4,1.7);
bul(s,['best_outlet -> drainage system',
       'main_path_id + facc -> rank paths',
       'rch_id_dn -> the reach graph',
       'dist_out -> order along the stem',
       'type -> what is usable'],9.4,3.35,3.4,2.2,11.5);
body(s,'Noatak, Kobuk and Selawik separate cleanly from everything else by '+
  'drainage area.',9.4,5.7,3.4,1.0,11.5,TEAL);

/* 4 step 2 gauge shape */
s=light('Does SWOT see it right? Elevation','Step 2',2);
fig(s,F('fig01_kiana_validation.png'),0.55,1.5,8.6,5.3);
body(s,'Only one gauge exists on a major river: Kobuk at Kiana. SWOT reports '+
  'orthometric elevation, the gauge reports stage on a local datum, so the '+
  'regression slope must be exactly 1.0. Nothing is tuned to make that happen.',
  9.4,1.55,3.4,1.9);
stat(s,'1.002','measured slope\n(1.000 required)',9.4,3.6,3.4,GREEN);
stat(s,'r = 0.980','84 coincident\noverpasses, 21 cm RMS',9.4,5.0,3.4,GREEN);

/* 5 step 3 gauge shape vs magnitude */
s=light('Does SWOT see it right? Discharge','Step 3',3);
fig(s,F('fig16_swot_only.png'),0.55,1.5,8.6,5.3);
body(s,'SWOT-derived discharge (SoS) compared with the same gauge:',
  9.4,1.55,3.4,0.5,12);
stat(s,'r = 0.99','shape, in log space —\nthe hydrograph is right',9.4,2.15,3.4,GREEN);
stat(s,'2.9x low','median bias, NSE = -2.0 —\nmagnitude is not usable',9.4,3.55,3.4,RED);
body(s,'So relative and seasonal statements are supported; absolute freshwater '+
  'flux is not. Nothing downstream computes a flux budget.',9.4,5.0,3.4,1.3,11.5,INK);
body(s,'The SoS product carries BOTH a gauge-constrained and an unconstrained '+
  'branch, and Hydrocron does not say which it serves. But a gauge-constrained '+
  'estimate at a gauged reach would not be 3x off, so this is the unconstrained '+
  'branch (or Kiana is not in its gauge set). Either way: an inversion from '+
  'global priors, so a 3x bias on an ungauged Arctic river is expected, not a '+
  'failure.',9.4,5.95,3.4,1.5,9.5,RED);

/* 5b version comparison */
s=light('Which product version, and does it matter?','Data versions');
fig(s,F('fig18_version_comparison.png'),0.55,1.5,8.6,5.3);
body(s,'Two processing versions cover the same KaRIn observations. The official '+
  'v17b-to-v16 reach translation maps all 162 domain reaches, so identical '+
  'reaches can be compared directly, matched within 30 minutes (n = 4,849).',
  9.4,1.55,3.4,1.7);
s.addTable([
  [{text:'field',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'r',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'median diff',options:{bold:true,color:WHITE,fill:{color:INK}}}],
  [{text:'WSE'},{text:'0.999996',options:{color:GREEN,bold:true}},{text:'0.08%'}],
  [{text:'slope'},{text:'0.937'},{text:'1.6%'}],
  [{text:'width'},{text:'0.963'},{text:'8.1%',options:{color:RED,bold:true}}]],
  {x:9.4,y:3.4,w:3.4,colW:[1.0,1.2,1.2],fontFace:BF,fontSize:10.5,
   color:'20303C',rowH:0.38,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Elevation is version-stable to a fraction of a centimetre. Width is not, '+
  'which matches Thurman et al. declining to use SWOT width at all.',
  9.4,5.1,3.4,1.3,11.5,TEAL);
body(s,'The real trade is record length versus discharge: Version D runs to Sep '+
  '2026, Version 2.0 stops in 2025 but is the only one carrying SoS.',
  9.4,6.3,3.4,1.1,10.5,MUTED);

/* 6 step 4 the three rivers */
s=light('The three rivers, side by side','Step 4',4);
fig(s,F('fig12_rivers_overview.png'),0.55,1.5,8.6,5.3);
body(s,'Every river gets a multi-year stage record. For the Selawik and Noatak '+
  'this is the only stage history that has ever existed.',9.4,1.55,3.4,1.4);
body(s,'Note the shapes differ. The Selawik spikes sharply in mid-May and decays; '+
  'the Kobuk and Noatak build a broader late-summer maximum.',
  9.4,3.1,3.4,1.6,12,TEAL);
body(s,'The Squirrel is a Kobuk tributary, not an independent input. The Wulik '+
  'drains the Chukchi coast and does not reach the sound at all.',
  9.4,4.9,3.4,1.6,11.5,MUTED);

/* 7 phasing */
s=light('They are out of phase','Step 5',5);
fig(s,F('fig03_seasonal_regime.png'),0.55,1.5,8.6,5.3);
s.addTable([
  [{text:'Selawik',options:{bold:true,color:WHITE,fill:{color:RED}}},
   {text:'day 141, 145, 145',options:{fill:{color:ICE}}}],
  [{text:'Kobuk',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'day 240, 250',options:{fill:{color:ICE}}}],
  [{text:'Noatak',options:{bold:true,color:WHITE,fill:{color:'3F6B4A'}}},
   {text:'day 168, 237',options:{fill:{color:ICE}}}]],
  {x:9.4,y:1.6,w:3.4,colW:[1.3,2.1],fontFace:BF,fontSize:11.5,color:'20303C',
   rowH:0.42,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Day-of-year of the seasonal stage maximum. Both the Kobuk and Selawik '+
  'empty into the same lagoon complex, roughly 100 days apart.',
  9.4,3.1,3.4,1.5);
body(s,'Freshwater arriving during the summer bloom window is Kobuk and Noatak '+
  'water, not Selawik water.',9.4,4.7,3.4,1.4,12.5,TEAL);
body(s,'Recovered independently from SWOT discharge alone, with no gauge: '+
  'Selawik day 154, Kobuk 236, Noatak 251.',9.4,6.1,3.4,1.1,11,MUTED);

/* 7b 2-D view */
s=light('The whole record, in two dimensions','Step 5b');
fig(s,F('fig19_hovmoller.png'),0.55,1.4,8.7,5.6);
body(s,'SWOT measures a whole river at once but at sparse times. A point time '+
  'series throws away space; a long profile throws away time. This keeps both: '+
  'x is date, y is distance upstream, colour is water-surface anomaly.',
  9.5,1.5,3.3,1.8);
body(s,'Seasonal banding is visible as vertical red and blue stripes, coherent '+
  'along hundreds of kilometres at once.',9.5,3.4,3.3,1.2,12,TEAL);
s.addText('Grid filled',{x:9.5,y:4.7,w:3.3,h:0.3,fontFace:BF,fontSize:11,
  bold:true,color:INK,margin:0});
body(s,'26% Noatak, 26% Kobuk, 29% Selawik of a 10 km x 4 day grid across the '+
  'full record. The gaps are the ice-covered winters.',9.5,5.05,3.3,1.3,11);
body(s,'597,344 node observations on these three rivers alone.',
  9.5,6.4,3.3,0.7,11.5,MUTED);

/* 7c contributions and channels */
s=light('Contributions, and where 1-D breaks down','Step 5c');
body(s,'Two things control how a river reading should be interpreted: where '+
  'tributaries add drainage area, and whether the channel is single or '+
  'multi-threaded. Both come straight from SWORD and are shown beside each '+
  '2-D panel on the previous slide.',0.55,1.45,12.2,0.8,13);
s.addTable([
  [{text:'river',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'reaches',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'tributary inflows',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'multi-threaded',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'max channels',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'facc span (km2)',options:{bold:true,color:WHITE,fill:{color:INK}}}],
  [{text:'Noatak'},{text:'57'},{text:'12'},{text:'81%'},{text:'8'},{text:'953 - 61,951'}],
  [{text:'Kobuk'},{text:'40'},{text:'13'},
   {text:'100%',options:{bold:true,color:RED}},{text:'6'},{text:'1,977 - 31,315'}],
  [{text:'Selawik'},{text:'12'},{text:'3'},{text:'50%'},{text:'3'},{text:'4,029 - 11,191'}]],
  {x:0.55,y:2.5,w:12.2,colW:[1.7,1.5,2.4,2.2,2.0,2.4],fontFace:BF,fontSize:12,
   color:'20303C',rowH:0.5,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
s.addShape(pptx.ShapeType.roundRect,{x:0.55,y:4.7,w:6.0,h:2.2,fill:{color:'FBEEE9'},
  line:{color:RED,width:0.85},rectRadius:0.06});
s.addText('The Kobuk problem',{x:0.95,y:4.9,w:5.2,h:0.35,fontFace:HF,fontSize:15,
  bold:true,color:RED,margin:0});
body(s,'Every single observed Kobuk reach is multi-threaded, up to 6 channels. '+
  'So SWOT reach-averaged width and elevation aggregate across threads along '+
  'the entire river, not just in the delta. This is exactly the regime Gleason '+
  'et al. identify as hardest to model.',0.95,5.3,5.2,1.5,11.5);
s.addShape(pptx.ShapeType.roundRect,{x:6.8,y:4.7,w:5.95,h:2.2,fill:{color:ICE},
  line:{color:TEAL,width:0.85},rectRadius:0.06});
s.addText('How to compare contributions',{x:7.2,y:4.9,w:5.2,h:0.35,fontFace:HF,
  fontSize:15,bold:true,color:INK,margin:0});
bul(s,['Rank by facc step at each confluence — the only mass-based measure available',
       'Do NOT use SWOT width: 8% version-unstable and aggregated across threads',
       'Do NOT use SoS discharge for partitioning: 2.9x biased'],
  7.2,5.3,5.2,1.5,11);

/* 8 main vs channels */
s=light('Main stem versus every delta channel','Step 6',6);
fig(s,F('fig17_channels_and_lakes.png'),0.55,1.5,8.6,5.3);
body(s,'The Kobuk does not reach Hotham Inlet as one channel. It splits, and '+
  'facc DROPS downstream as it does: 31,315 km2 in the single stem, '+
  '15,162 km2 in one delta arm.',9.4,1.55,3.35,1.8);
s.addTable([
  [{text:'',options:{fill:{color:INK}}},
   {text:'median WSE',options:{bold:true,color:WHITE,fill:{color:INK}}},
   {text:'range',options:{bold:true,color:WHITE,fill:{color:INK}}}],
  [{text:'Main stem',options:{bold:true}},{text:'2.97 m'},{text:'6.18 m'}],
  [{text:'Delta arms',options:{bold:true}},{text:'0.70 m'},{text:'1.94 m'}],
  [{text:'Hotham ch. A',options:{bold:true}},{text:'0.77 m'},{text:'2.08 m'}],
  [{text:'Hotham ch. B',options:{bold:true}},{text:'0.55 m'},{text:'1.40 m'}]],
  {x:9.4,y:3.5,w:3.4,colW:[1.4,1.1,0.9],fontFace:BF,fontSize:10,color:'20303C',
   rowH:0.36,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Water level and seasonal range both collapse across the delta — the '+
  'signature of flow splitting into a backwater-controlled receiving basin.',
  9.4,5.6,3.4,1.5,11.5,TEAL);

/* 9 inlet and lake */
s=light('Hotham Inlet and Selawik Lake themselves','Step 7',7);
body(s,'These were deliberately excluded earlier. SWORD types the reaches crossing '+
  'the inlet and the lake as 3 (lake on river) and 5 (unreliable topology), which '+
  'breaks a one-dimensional long profile. But SWOT observes them perfectly well, '+
  'so here they are the subject rather than the nuisance.',0.55,1.5,12.2,1.0,13);
s.addShape(pptx.ShapeType.roundRect,{x:0.55,y:2.65,w:3.95,h:4.15,fill:{color:ICE},
  line:{color:TEAL,width:0.75},rectRadius:0.06});
s.addText('What exists',{x:0.9,y:2.9,w:3.3,h:0.4,fontFace:HF,fontSize:16,bold:true,
  color:INK,margin:0});
bul(s,['27 lake-flagged SWORD reaches across the inlet and lake',
       '1,871 quality-passed observations on the channel reaches',
       '14 PLD prior lakes in the delta with SWOT water level, 1,276 records',
       'Hydrocron serves these as feature=PriorLake'],0.9,3.4,3.3,3.2,11);
s.addShape(pptx.ShapeType.roundRect,{x:4.75,y:2.65,w:3.95,h:4.15,fill:{color:'EAF4EE'},
  line:{color:GREEN,width:0.75},rectRadius:0.06});
s.addText('What it shows',{x:5.1,y:2.9,w:3.3,h:0.4,fontFace:HF,fontSize:16,bold:true,
  color:GREEN,margin:0});
body(s,'Both basins track Kobuk stage essentially instantaneously:',5.1,3.4,3.3,0.7,11.5);
s.addTable([
  [{text:'Hotham Inlet',options:{bold:true}},{text:'r = 0.85 at lag 0'}],
  [{text:'Selawik Lake',options:{bold:true}},{text:'r = 0.87 at lag 0'}]],
  {x:5.1,y:4.2,w:3.3,colW:[1.5,1.8],fontFace:BF,fontSize:10.5,color:'20303C',
   rowH:0.4,valign:'middle',border:{pt:0.5,color:'C9D8E2'}});
body(s,'Correlation collapses by 2 weeks (0.14 and 0.26), i.e. the response is '+
  'sub-weekly. They are hydraulically connected, not storage-buffered.',
  5.1,5.15,3.3,1.5,11);
s.addShape(pptx.ShapeType.roundRect,{x:8.95,y:2.65,w:3.85,h:4.15,fill:{color:'FBEEE9'},
  line:{color:RED,width:0.75},rectRadius:0.06});
s.addText('What is still missing',{x:9.3,y:2.9,w:3.2,h:0.4,fontFace:HF,fontSize:16,
  bold:true,color:RED,margin:0});
bul(s,['Selawik Lake and Hotham Inlet are NOT in the PLD subset I obtained — the 14 lakes cap at 0.57 km2',
       'Part of that r = 0.85 is shared seasonality, not proof of forcing',
       'No bathymetry, so no volume or residence time',
       'No salinity, so the freshwater/marine boundary is unconstrained'],
  9.3,3.4,3.2,3.2,11);

/* 10 virtual gauges */
s=light('Every station, all at once','Step 8',8);
fig(s,F('fig09_virtual_gauges.png'),0.55,1.5,8.6,5.3);
body(s,'Twelve virtual gauges, four per river, spaced along each one. Eight sit '+
  'where no gauge has ever been installed.',9.4,1.6,3.4,1.4);
body(s,'The Kobuk traces follow the USGS discharge curve (grey) closely. The '+
  'Selawik traces are visibly flatter and smoother.',9.4,3.1,3.4,1.5,12,TEAL);
stat(s,'2.4 cm/km','Selawik gradient:\n4.0 m over 166 km',9.4,4.7,3.4,AMBER);
body(s,'That is why it is backwater-controlled.',9.4,6.1,3.4,0.6,11.5,MUTED);

/* 11 synthesis */
s=light('The area, end to end','Synthesis');
const steps=[
 ['Snowmelt, mid-May','The Selawik peaks at day 141-145 every observed year and drains into Selawik Lake.'],
 ['Rain, late August','The Kobuk and Noatak peak at day 236-251, roughly 100 days later.'],
 ['Through the delta','The Kobuk splits; facc falls from 31,315 to 15,162 km2 and stage drops 3.0 m to 0.7 m.'],
 ['Into the inlet','Hotham Inlet and Selawik Lake follow river stage within a week (r = 0.85, 0.87).'],
 ['Out to the sound','Kobuk discharge leads inner-sound chlorophyll by ~2 weeks, surviving a sediment control.'],
 ['The blooms: open','Two competing models, neither tested here. See next slide.']];
steps.forEach((r,i)=>{
  const y=1.5+i*0.88;
  s.addShape(pptx.ShapeType.ellipse,{x:0.6,y:y+0.06,w:0.42,h:0.42,
    fill:{color:i===5?RED:TEAL}});
  s.addText(String(i+1),{x:0.6,y:y+0.06,w:0.42,h:0.42,fontFace:HF,fontSize:13,
    bold:true,color:WHITE,align:'center',valign:'middle',margin:0});
  s.addText(r[0],{x:1.2,y:y+0.03,w:2.9,h:0.5,fontFace:BF,fontSize:13,bold:true,
    color:i===5?RED:INK,margin:0,valign:'top'});
  s.addText(r[1],{x:4.2,y:y+0.03,w:8.5,h:0.75,fontFace:BF,fontSize:11.5,
    color:'20303C',lineSpacing:15,margin:0,valign:'top'});
});

/* 11b competing models */
s=light('The blooms: two models, neither tested here','Open question');
body(s,'This project measured river hydrology. It did not measure blooms, and it '+
  'cannot arbitrate between these. Both are live, and they are not mutually '+
  'exclusive.',0.55,1.45,12.2,0.75,13);
s.addShape(pptx.ShapeType.roundRect,{x:0.55,y:2.35,w:6.0,h:3.5,fill:{color:ICE},
  line:{color:TEAL,width:0.9},rectRadius:0.06});
s.addText('Model A - advective supply',{x:0.95,y:2.6,w:5.2,h:0.4,fontFace:HF,
  fontSize:17,bold:true,color:INK,margin:0});
body(s,'Blooms form offshore in the Bering Sea and are carried north through the '+
  'Bering Strait; local cyst beds germinate when bottom water is warm enough.',
  0.95,3.1,5.2,1.0,12);
s.addText('Evidence',{x:0.95,y:4.15,w:5.2,h:0.3,fontFace:BF,fontSize:11,bold:true,
  color:TEAL,margin:0});
bul(s,['The 2022 event was tracked entering from the west and advecting north (Fachon et al. 2024)',
       'That year the Ledyard Bay cyst bed was thermally suppressed, ~1.8 C',
       'Cells were dense across a wide range of nutrient concentrations'],
  0.95,4.45,5.2,1.3,10.5);
s.addShape(pptx.ShapeType.roundRect,{x:6.8,y:2.35,w:6.0,h:3.5,fill:{color:'FBF3E8'},
  line:{color:AMBER,width:0.9},rectRadius:0.06});
s.addText('Model B - local river modulation',{x:7.2,y:2.6,w:5.2,h:0.4,fontFace:HF,
  fontSize:17,bold:true,color:INK,margin:0});
body(s,'River freshwater sets stratification, delivers terrestrial nutrients and '+
  'organic matter, and controls flushing of the inlet, modulating how a bloom '+
  'develops once cells are present.',7.2,3.1,5.2,1.0,12);
s.addText('What this project adds',{x:7.2,y:4.15,w:5.2,h:0.3,fontFace:BF,fontSize:11,
  bold:true,color:AMBER,margin:0});
bul(s,['Kobuk discharge leads inner-sound chlorophyll by ~2 weeks, surviving a sediment control (r = 0.28, n = 201)',
       'Kobuk and Noatak peak inside the bloom window; the Selawik does not',
       'But chlorophyll is not Alexandrium, and CDOM is still uncontrolled'],
  7.2,4.45,5.2,1.3,10.5);
body(s,'Separating them needs what this project does not have: HAB cell counts or '+
  'toxin data, a CDOM control, and moorings or a circulation model for the sound.',
  0.55,6.1,12.2,0.8,12.5,RED);

/* 12 close */
s=dark();
s.addText('What this can and cannot tell you',{x:0.8,y:1.3,w:11.6,h:0.7,fontFace:HF,
  fontSize:32,bold:true,color:WHITE,margin:0});
s.addText([{text:'Can.  ',options:{bold:true,color:GREEN}},
 {text:'When each river delivers water, how much water level changes and where, '+
 'how the delta splits it, and how fast the inlet and lake respond. For two of '+
 'the three rivers, nothing else on Earth provides this.',options:{color:'CFE0EA'}}],
 {x:0.8,y:2.3,w:11.6,h:1.0,fontFace:BF,fontSize:14.5,lineSpacing:22,margin:0});
s.addText([{text:'Cannot.  ',options:{bold:true,color:AMBER}},
 {text:'Absolute freshwater flux (SWOT discharge is 2.9x low), flow-wave celerity '+
 '(three estimators, three failures), attribution from SWOT alone (n = 28-39), or '+
 'or anything about what causes the harmful algal blooms.',options:{color:'CFE0EA'}}],
 {x:0.8,y:3.5,w:11.6,h:1.1,fontFace:BF,fontSize:14.5,lineSpacing:22,margin:0});
s.addShape(pptx.ShapeType.rect,{x:0.8,y:4.9,w:1.5,h:0.045,fill:{color:AMBER}});
s.addText('All data public and unauthenticated: PO.DAAC Hydrocron, SWORD v17c and '+
 'HarP on Zenodo, USGS NWIS, NOAA CoastWatch ERDDAP.',
 {x:0.8,y:5.25,w:11.6,h:0.8,fontFace:BF,fontSize:13,color:TEAL,margin:0});

pptx.writeFile({fileName:path.join(ROOT,'deck','Kotzebue_Sequential_Walkthrough.pptx')})
  .then(f=>console.log('wrote',f));
