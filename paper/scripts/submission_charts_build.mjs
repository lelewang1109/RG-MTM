/** Native evidence charts for the current submission, from saved results only. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const ROOT=path.resolve(import.meta.dirname,'..');
const STAGE=ROOT+'/.build/research-charts-20261023';
const OUT=STAGE+'/output';
const RUNTIME='/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=RUNTIME+'/node/node_modules';
const SKILL='/Users/lele/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(RUNTIME+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs'));
const {applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs'));
const E=JSON.parse(await fs.readFile(STAGE+'/chart_evidence.json','utf8'));
await fs.mkdir(OUT,{recursive:true});
const C={blue:'#0072B2',green:'#009E73',orange:'#D55E00',gray:'#7B8790',black:'#263238',grid:'#D9DFE3',pink:'#CC79A7',sky:'#56B4E9'};
const methods=[['TMTM','TMTM','#777777'],['ST-MTM','ST-MTM',C.sky],['A','P',C.blue],['R 20%','R20',C.green],['Hilbert','Hilbert',C.orange],['Morton','Morton',C.pink]];
const ln=(color,width=1.5,style='solid')=>({fill:color,width,style});
function text(s,t,x,y,w,h=26,size=20,bold=false,color=C.black){
 const sh=s.shapes.add({name:t.slice(0,65),geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:ln('none',0)});
 sh.text=t;sh.text.style={typeface:'Arial',fontSize:size,bold,color,wrap:'none',autoFit:'none',insets:0};return sh;
}
function deck(w,h){const p=Presentation.create({slideSize:{width:w,height:h}});p.theme.defaultFont='Arial';const s=p.slides.add();s.background.fill='#FFFFFF';return {p,s,w,h};}
function axis(title,min,max,step,fmt='0.0',size=17){return {visible:true,title:{text:title,textStyle:{fontSize:size,fill:C.black}},min,max,majorUnit:step,numberFormatCode:fmt,textStyle:{fontSize:size-1,fill:C.black},line:ln(C.black,.8),majorGridlines:ln(C.grid,.6),minorGridlines:null};}
function chart(s,type,opts){const ch=s.charts.add(type,{chartFill:'#FFFFFF',chartLine:ln('none',0),plotAreaFill:'#FFFFFF',plotAreaLine:ln('none',0),hasLegend:false,...opts});applyPresentationChartFont(ch,{fontFamily:'Arial'});return ch;}
function series(name,xx,yy,color,marker='none',style='solid',width=1.7,filled=true){return {name,xValues:xx,values:yy,line:ln(color,width,style),marker:{symbol:marker,size:7,fill:filled?color:'#FFFFFF'},fill:color};}
function stepSeries(rows,key){let x=[],y=[];rows.forEach((r,i)=>{if(r.delta*100>70)return;if(i){x.push(r.delta*100);y.push(rows[i-1][key]*100);}x.push(r.delta*100);y.push(r[key]*100);});x.push(70);y.push(y.at(-1));return [x,y];}
async function finish(d,stem,note,requiredCharts=true){
 d.s.speakerNotes.text=note+'\nEvidence sources and SHA-256: '+JSON.stringify(E.sources);
 const candidate=STAGE+'/'+stem+'_candidate.pptx';
 await(await PresentationFile.exportPptx(d.p)).save(candidate);
 const reference=ROOT+'/figures_ppt/Fig6.pptx';
 const sha=crypto.createHash('sha256').update(await fs.readFile(reference)).digest('hex');
 await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:OUT+'/'+stem+'.pptx',
  pythonExecutable:RUNTIME+'/python/bin/python3',integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',
  layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',
  layoutArgs:['--expected-slide-size-emu',`${Math.round(d.w*9525)},${Math.round(d.h*9525)}`],
  explicitTotalSlideCount:1,requiredNativeChartOwnerSlides:requiredCharts?[1]:[],requiredNativeTableOwnerSlides:[],
  materializeLiteralChartWorkbooks:true,nativeChartTargetApplication:'powerpoint',
  fontPolicy:{basis:'reference',families:['Arial'],referencePath:reference,referenceSha256:sha},
  verifyArtifactToolImport:true,receiptPath:STAGE+'/'+stem+'_validation-'+Date.now()+'.json'});
 const png=await d.p.export({slide:d.s,format:'png',scale:1.5});
 await fs.writeFile(STAGE+'/'+stem+'_artifact_preview.png',new Uint8Array(await png.arrayBuffer()));
 console.log(stem+' complete');
}

// Figure 5. All five current two-dimensional sequences. Values remain editable.
{
 const d=deck(1500,440);const {s}=d;
 for(const [i,f] of E.frontiers.entries()){
  const left=8+i*298, rows=f.data.frontier;const yMax=Math.max(...rows.map(v=>v.F*100),...f.data.ours.map(v=>v.E_share*100))*1.12;
  const [xf,yf]=stepSeries(rows,'F'),[xp,yp]=stepSeries(rows,'Phi');
  const ser=[series('Exact frontier F',xf,yf,C.blue),series('Certified bound Φ',xp,yp,C.gray,'none','dashed',1.4)];
  for(const o of f.data.ours){ser.push(series('Same-order filling improvement',[o.D_opt_share*100,o.D_lca_share*100],[o.E_share*100,o.E_share*100],C.green,'none','solid',.8));}
  for(const o of f.data.ours)ser.push(series('Same order, optimal filling',[o.D_opt_share*100],[o.E_share*100],C.green,'circle','solid',.1,true));
  for(const o of f.data.ours)ser.push(series('Implemented LCA filling',[o.D_lca_share*100],[o.E_share*100],C.green,'circle','solid',1.4,false));
  // Equal-length scatter caches avoid synthetic origin segments in LibreOffice.
  // Repeated identical coordinates are display padding, never extra observations.
  const nPoints=Math.max(...ser.map(v=>v.values.length));
  for(const v of ser){
   v.fill='none';v.smooth=false;
   while(v.values.length<nPoints){v.xValues.push(v.xValues.at(-1));v.values.push(v.values.at(-1));}
   if(v.name.includes('filling')&&!v.name.includes('improvement'))v.line=ln('none',0);
  }
  text(s,`(${String.fromCharCode(97+i)}) ${f.label}`,left+16,5,280,28,21,true);
  chart(s,'scatter',{position:{left,top:36,width:292,height:324},series:ser,scatterOptions:{style:'lineWithMarkers'},
   xAxis:axis('d_top (% scalar range)',0,70,20,'0',16),yAxis:axis('Mean τ (% axis)',0,yMax,yMax>4?2:yMax>2?1:.5,'0.0',16)});
 }
 text(s,'Blue: exact frontier F    Gray dashed: certified bound Φ    Green: optimal / LCA working points',130,369,1300,28,19);
 text(s,'Working points: P, R2, R20, R∞. Horizontal segments show filling savings for the same order.',205,407,1130,25,17);
 await finish(d,'Fig5',E.figure5_semantics+'\nCaption: Exact small-tree attainable position–topology frontiers for all five current 2D sequences. The staircase F and certified lower bound Φ use a common scalar budget across frames. Green points show achieved orders under P, R2, R20 and R∞, with filled points for optimal filling and open points for implemented LCA filling.');
}

// Figure 7. Saved achieved settings only. Spatial and projected motion use distinct denominators.
{
 const d=deck(1344,730);const {s}=d;
 const cats=['P','R2','R20','R100'];
 const headings=['(a) Reference order error','(b) Scalar cost','(c) Motion error'];
 headings.forEach((t,i)=>text(s,t,25+i*442,4,420,30,23,true));
 for(const [r,v] of E.volume.entries()){
  const top=47+r*319;
  text(s,`${v.label} (${v.frames} frames)`,24,top,400,25,20,true);
  const make=(idx,ss,y)=>chart(s,'line',{position:{left:idx*442+10,top:top+26,width:428,height:275},categories:cats,series:ss,
   lineOptions:{smooth:false},hasLegend:idx>0,legend:{position:'bottom',textStyle:{fontSize:16,fill:C.black}},
   xAxis:{visible:true,line:ln(C.black,.8),textStyle:{fontSize:17,fill:C.black},majorGridlines:null},yAxis:y});
  const vals=k=>v.rows.map(row=>100*row[k]);
  make(0,[{name:'Mean NROE',values:vals('NROE_mean'),line:ln(C.blue,2),marker:{symbol:'circle',size:7,fill:C.blue},
    dataLabels:{showValue:true,position:'top',numberFormatCode:'0.00',textStyle:{fontSize:15,fill:C.blue}}}],axis('NROE (% axis)',0,15,5,'0',17));
  make(1,[{name:'Mean',values:vals('NMLE_mean'),line:ln(C.green,2),marker:{symbol:'circle',size:7,fill:C.green}},
    {name:'Maximum',values:vals('NMLE_max'),line:ln(C.orange,2,'dashed'),marker:{symbol:'square',size:7,fill:C.orange}}],axis('NMLE (% scalar range)',0,35,10,'0',17));
  make(2,[{name:'Spatial',values:vals('ME_3D'),line:ln(C.orange,2),marker:{symbol:'circle',size:7,fill:C.orange}},
    {name:'Projected',values:vals('ME_projected'),line:ln(C.green,2),marker:{symbol:'circle',size:7,fill:C.green}},
    {name:'Exact projection, spatial',values:cats.map(()=>100*v.exact_spatial),line:ln(C.gray,1.2,'dashed'),marker:{symbol:'none'}}],axis('ME (% clear events)',0,60,20,'0',17));
  text(s,`Clear spatial/projected events: ${v.counts.spatial}/${v.counts.projected}`,890,top+303,445,22,15,false,C.gray);
 }
 text(s,'κ = 2%, 20%, 100% controls relaxation eligibility. Curves connect achieved settings, not exact frontiers.',46,699,1250,25,18);
 await finish(d,'Fig7',E.figure7_semantics+'\nCaption: Achieved parameter settings in Tangaroa and Cylinder. P preserves the hierarchy, followed by κ=2%, 20%, 100%. The columns report mean NROE, mean and maximum NMLE, and motion error with separate spatial/projected event sets. The dashed gray motion baseline reports the spatial error of exact projection, illustrating the limitation of projection. Tangaroa R20 and R100 coincide. Cylinder R100 increases mean scalar cost without reducing NROE relative to R20.');
}

function row(rec,m,k=2){return rec.proxy.find(v=>v.method===m&&v.k===k&&v.eps===.02)||{clear:0};}
function mini(d,i,title,opts){const x=16+(i%3)*442, y=12+Math.floor(i/3)*320;text(d.s,title,x+12,y,420,26,20,true);return chart(d.s,opts.type||'scatter',{position:{left:x,top:y+30,width:425,height:282},...opts});}
function legendBlock(s,x=915,y=410){
 methods.forEach(([key,label,color],i)=>text(s,label==='P'?'P = RG-MTM-P':label==='R20'?'R20 = RG-MTM-R (κ = 20%)':label,x,y+i*32,420,27,19,false,color));
}
// Supplementary motion rates. Native stacked bars retain reversal/miss decomposition.
{
 const d=deck(1344,690);
 E.diagnostics.forEach((f,i)=>{
  const rr=methods.map(([m])=>row(f.data,m));
  mini(d,i,`(${String.fromCharCode(97+i)}) ${f.label}, n = ${rr[0].clear}`,{type:'bar',categories:methods.map(m=>m[1]),
   series:[{name:'Reversal',values:rr.map(r=>r.clear?r.reversal*100:null),points:methods.map((m,k)=>({idx:k,fill:m[2]}))},
    {name:'Miss',values:rr.map(r=>r.clear?r.miss*100:null),points:methods.map((m,k)=>({idx:k,fill:m[2]+'66'}))}],
   barOptions:{direction:'column',grouping:'stacked',gapWidth:60},xAxis:{textStyle:{fontSize:15,fill:C.black},line:ln(C.black,.8)},
   yAxis:axis('Motion error (%)',0,100,20,'0',16)});
 });
 legendBlock(d.s);text(d.s,'Solid: reversal. Pale: miss.',910,356,420,25,20,true);
 text(d.s,'k = 2, ε = 2%. Event counts describe each full sequence. PM2.5 January followed seasonal exploration.',26,658,1295,24,17);
 await finish(d,'rgmtm_motion_error_comparison','Native stacked bar chart from eval_projection.json, five retained datasets, Gaussian excluded. Total motion error equals reversal plus miss. Clear event counts are 2D spatial events, not independent samples. PM2.5 January followed seasonal exploration.');
}
// Supplementary neighbourhood preservation. Each method keeps its native anchors.
{
 const d=deck(1344,690);
 E.diagnostics.forEach((f,i)=>mini(d,i,`(${String.fromCharCode(97+i)}) ${f.label}`,{type:'scatter',
  series:methods.map(([m,label,c])=>series(label,[f.data.hidden[m].stress],[f.data.hidden[m].nn_preservation*100],c,'circle','solid',0)),
  scatterOptions:{style:'marker'},xAxis:axis('Kruskal stress-1',0,1.2,.4,'0.0',16),yAxis:axis('NN preservation (%)',0,100,20,'0',16)}));
 legendBlock(d.s);text(d.s,'Lower stress and higher',910,343,420,26,20,true);text(d.s,'NN preservation are preferable',910,370,420,26,20,true);
 text(d.s,'Frame means use native anchor geometries. Frames with fewer than three extrema are excluded.',26,658,1295,24,17);
 await finish(d,'rgmtm_neighbourhood_preservation','Native scatter chart from eval_projection.json, five retained datasets, Gaussian excluded. Frame-mean stress and nearest-neighbour preservation use saved hidden-cost evaluation. These metrics describe spatial relationships, not human performance. Frames with fewer than three extrema are excluded.');
}
// Supplementary time-window sensitivity. Null rates retain their undefined status.
{
 const d=deck(1344,690);const ks=[1,2,4,8];
 E.diagnostics.forEach((f,i)=>mini(d,i,`(${String.fromCharCode(97+i)}) ${f.label}, n = ${ks.map(k=>row(f.data,'R 20%',k).clear).join('/')}`,{type:'line',categories:ks.map(String),
  series:methods.map(([m,label,c])=>({name:label,categories:ks.filter(k=>row(f.data,m,k).clear).map(String),values:ks.filter(k=>row(f.data,m,k).clear).map(k=>row(f.data,m,k).error*100),line:ln(c,1.7),marker:{symbol:'circle',size:6,fill:c}})),
  displayBlanksAs:'gap',lineOptions:{smooth:false},xAxis:{title:{text:'Window length (time steps)',textStyle:{fontSize:16,fill:C.black}},textStyle:{fontSize:16,fill:C.black},line:ln(C.black,.8)},yAxis:axis('Motion error (%)',0,100,20,'0',16)}));
 legendBlock(d.s);text(d.s,'Counts follow k = 1/2/4/8',910,350,420,27,20,true);text(d.s,'Undefined rates remain omitted',910,378,420,27,19);
 text(d.s,'ε = 2%. Each k has its own clear-event set. Step durations differ across datasets.',26,658,1295,24,17);
 await finish(d,'rgmtm_motion_window_sensitivity','Native line charts from eval_projection.json, five retained datasets, Gaussian excluded. Each window k uses its own clear-event set. Lines connect operating settings, not physical trajectories. Step duration differs across datasets. Zero clear-event rates remain undefined and omitted.');
}
for(const stem of ['rgmtm_linked_cases','rgmtm_motion_scalar_cost','rgmtm_topology_motion_tradeoff']){
 await fs.copyFile(ROOT+'/figures_ppt/'+stem+'.pptx',OUT+'/'+stem+'.pptx');
 for(const ext of ['pdf','svg','png'])await fs.copyFile(ROOT+'/figures_export/'+stem+'.'+ext,OUT+'/'+stem+'.'+ext);
}
console.log('Unchanged three supplementary figures copied after Gaussian content audit.');
