/** Native evidence charts for the current submission, from saved results only. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const ROOT="/Users/lele/Desktop/MergeTreeMaps/RG-MTM/paper";
const STAGE=process.env.RGMTM_FRONTIER_STAGE||ROOT+'/.build/annual-frontier';
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

