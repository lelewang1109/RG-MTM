import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const runtimeModules=process.env.RUNTIME_NODE_MODULES;
if(!runtimeModules) throw new Error('Set RUNTIME_NODE_MODULES to the bundled Node packages path.');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtimeModules,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const skill=process.env.PRESENTATIONS_SKILL_DIR;
if(!skill) throw new Error('Set PRESENTATIONS_SKILL_DIR to the installed presentations skill.');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const SRC=import.meta.dirname, ROOT=path.resolve(SRC,'../../../../..'), OUT=process.env.ANCHORMTM_FIGURE_OUTPUT_DIR || ROOT+'/output/framework_b_paper_rebuild';
const W=1600,H=800, F='Times New Roman';
const p=Presentation.create({slideSize:{width:W,height:H}}),s=p.slides.add();s.background.fill='#FFFFFF';
const C={A:'#0066CC',B:'#FF8800',C:'#009E91',D:'#9656AD'},P={A:'#BDD6EF',B:'#FFE0BA',C:'#BDE3DF',D:'#DFCBE8'};
let n=0;const scene=[];
function shape(g,x,y,w,h,fill='none',stroke='#222222',lw=1.6){const a={geometry:g,name:`object-${++n}`,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:lw,style:'solid'}};scene.push(a);return s.shapes.add(a)}
function text(t,x,y,w,h=29,size=24,bold=false,align='center',color='#111111'){let a=shape('textbox',x,y,w,h,'none','none',0);a.text=t;a.text.style={typeface:F,fontSize:size,bold,color,alignment:align,verticalAlignment:'middle',autoFit:'none',wrap:'none',insets:0};scene.push({text:t,x,y,w,h,size,bold});return a}
function line(x,y,X,Y,c='#222222',lw=1.8,dash=false){let w=Math.max(Math.abs(X-x),.1),h=Math.max(Math.abs(Y-y),.1),l=Math.min(x,X),t=Math.min(y,Y);return s.shapes.add({geometry:'custom',name:`line-${++n}`,position:{left:l,top:t,width:w,height:h},fill:'none',line:{fill:c,width:lw,style:dash?'dashed':'solid'},customPaths:[{width:w,height:h,commands:[{moveTo:{x:x-l,y:y-t}},{lineTo:{x:X-l,y:Y-t}}]}]})}
function arrow(x,y,X,Y,c='#555555',lw=2.2){line(x,y,X,Y,c,lw);let a=Math.atan2(Y-y,X-x),r=9;line(X,Y,X-r*Math.cos(a-.48),Y-r*Math.sin(a-.48),c,lw);line(X,Y,X-r*Math.cos(a+.48),Y-r*Math.sin(a+.48),c,lw)}
function dot(x,y,k,r=7,hollow=false){return shape('ellipse',x-r,y-r,r*2,r*2,hollow?'#FFFFFF':C[k]||k,'#222222',1.2)}
function diamond(x,y,fill='#B8B8B8',r=6){shape('diamond',x-r,y-r,2*r,2*r,fill,'#222222',1.2)}
function tree(x,y,w=120,h=70,relax=false,labels=false){let root=[x+w/2,y],l=[x+w*.25,y+h*.42],r=[x+w*.75,y+h*.42],pts=[.08,.4,.6,.92].map(a=>[x+w*a,y+h]);line(...root,...l);line(...root,...r);line(...l,...pts[0]);line(...l,...pts[1]);line(...r,...pts[2]);line(...r,...pts[3]);diamond(...root);diamond(...l,relax?'#FFFFFF':'#B8B8B8');diamond(...r);pts.forEach((a,i)=>{dot(...a,'ABCD'[i],6);if(labels)text('ABCD'[i],a[0]-10,a[1]+8,20,22,21)});return pts}
function chips(order,x,y,w=280,h=27){const gap=8,cw=(w-3*gap)/4;[...order].forEach((k,i)=>{shape('roundRect',x+i*(cw+gap),y,cw,h,P[k],'#333333',1.2);text(k,x+i*(cw+gap),y,cw,h,23,true)})}
function panel(x,w,title){shape('roundRect',x,8,w,H-16,'#FFFFFF','#222222',1.8);shape('roundRect',x+12,20,w-24,42,'#E5E5E5','none',0);text(title,x+15,22,w-30,36,29,true)}
const xs=[8,406,804,1202],cw=390;xs.forEach((x,i)=>panel(x,cw,['1  Extract & reference','2  Search leaf orders','3  Place anchors','4  Reconstruct & assemble'][i]));
[398,796,1194].forEach(x=>arrow(x-2,398,x+8,398,'#555555',3));
function banner(t,x,y,w=342,size=24){shape('roundRect',x,y,w,34,'#E5E5E5','none',0);text(t,x+4,y,w-8,34,size,true)}
function orderDots(order,x,y,w=140,r=11,hollow=false){[...order].forEach((k,i)=>{let xx=x+i*w/3;dot(xx,y,k,r,hollow);text(k,xx-r,y-r,r*2,r*2,20,true)})}
function pathCurve(points,color='#222222',width=2){points.slice(1).forEach((v,i)=>line(...points[i],...v,color,width))}
function curveProfile(x,y,w=290,h=75,mark=true){const pts=[[0,.05],[.06,.18],[.12,.82],[.18,.47],[.25,.06],[.32,.3],[.39,.72],[.46,.29],[.53,.02],[.60,.34],[.66,.82],[.73,.39],[.80,.10],[.88,.72],[.95,.27],[1,.12]].map(([a,b])=>[x+a*w,y+b*h]);pathCurve(pts);if(mark){[.12,.39,.66,.88].forEach((v,i)=>dot(x+v*w,y+[.82,.72,.82,.72][i]*h,'ACBD'[i],5))}return pts}
// Stage 1: retain the field, matched trees, motion, projection and formula.
text('Time-varying scalar fields',25,77,357,27,25,true);text('(2D / 3D,  t − 1, t, t + 1)',25,105,357,25,23);
for(let f=0;f<3;f++){let x=33+f*115,y=145;shape('roundRect',x,y,103,83,'#F7FAFD','#777777',1);for(let k=0;k<4;k++){shape('ellipse',x+5+k*7+f,y+8+k*5,65-k*14,40-k*9,'none',k==3?C.A:'#9ABBDD',.9);shape('ellipse',x+41+k*5-f,y+39+k*4,57-k*10,37-k*8,'none',k==3?C.C:'#93CEC8',.9)}dot(x+30+f,y+28,'A',4);dot(x+70-f,y+57,'C',4);text(['t − 1','t','t + 1'][f],x,y+87,103,25,22)}
arrow(204,266,204,285);text('Trees + track IDs',25,293,357,28,25,true);
const tr=[];for(let f=0;f<3;f++)tr.push(tree(30+f*116,339,108,75,false,true));
for(let f=0;f<2;f++)for(let i=0;i<4;i++)line(tr[f][i][0],tr[f][i][1]+5,tr[f+1][i][0],tr[f+1][i][1]+5,'#888888',.8,true);
text('t − 1',38,455,97,25,22);text('t',154,455,97,25,22);text('t + 1',270,455,97,25,22);arrow(204,489,204,507);
line(60,644,349,644,'#555555',1.4);line(60,644,60,528,'#555555',1.4);text('y',38,520,25,23,23);text('x',350,635,24,26,23);
[[90,606,'A',29,-20],[130,628,'C',29,-20],[188,578,'C',25,-19],[241,592,'A',26,-23]].forEach(([x,y,k,dx,dy])=>{dot(x,y,k,5);arrow(x,y,x+dx,y+dy,'#555555',1.5)});arrow(154,636,286,545,C.A,3);text('a*',285,521,45,30,29,true);
text('q:',29,676,30,27,24);line(66,689,356,689);'ACBD'.split('').forEach((k,i)=>dot(91+i*76,689,k,6,true));text('qᵢᵗ = ⟨a*, pᵢᵗ⟩ − o',36,711,337,30,25);banner('One fixed spatial reference',29,754,348);
// Stage 2: all three candidates, refinement, two evaluators and admission gate.
shape('roundRect',439,78,324,57,'#F2F2F2','#888888',1);text('Topology budget ε',445,80,312,27,25,true);text('η = (ε₀ + ε) ΔF',445,107,312,27,23);
tree(538,154,128,64,false,true);arrow(577,252,466,273,'#555555',1.6);arrow(602,252,609,273,'#555555',1.6);arrow(628,252,745,273,'#555555',1.6);text('Strict',430,280,95,25,23);text('Selective relaxation',548,280,226,25,23);
orderDots('ABCD',430,330,83,11);orderDots('ACBD',553,330,83,11);orderDots('ACDB',675,330,83,11);
// Local refinement cycle.
arrow(443,373,459,361,'#777777',1.6);arrow(459,361,473,375,'#777777',1.6);arrow(473,375,458,390,'#777777',1.6);arrow(458,390,443,373,'#777777',1.6);text('Width-aware refinement',478,361,290,34,23);
shape('roundRect',430,411,342,150,'#F7F7F7','#888888',1);text('Evaluate (fixed order π)',436,416,330,28,25,true);line(602,450,602,552,'#BBBBBB',1);
text('Displacement τ',438,450,157,26,23,true);text('Merge error δ*',611,450,150,26,23,true);
line(450,505,581,505,'#555555',1.5);dot(459,505,'A',5,true);dot(511,505,'C',5,true);dot(536,505,'A',5);dot(576,505,'C',5);arrow(463,492,531,492,'#555555',1.3);arrow(531,492,463,492,'#555555',1.3);text('τ(π)',441,526,149,25,23);
tree(632,486,108,46,true,false);line(626,497,745,497,'#888888',1,true);text('δ*(π)',611,535,150,24,23);
shape('roundRect',514,577,173,33,'#FFFFFF','#888888',1);text('δ*(π) ≤ η',519,578,163,31,25,true);
shape('roundRect',430,626,342,49,'#FAFAFA','#999999',1);text('✓',435,632,25,32,29,true,'center',C.C);orderDots('ACBD',474,651,103,10);text('×',600,632,26,32,29,true);orderDots('ACDB',644,651,103,10,true);arrow(600,685,600,695);
banner('Select by (τ, NROE)',431,701,340);orderDots('ACBD',526,750,150,12);text('Finite heuristic search',432,765,338,27,20);
// Stage 3: fixed-reference targets, intervals, cap, weighted QP and motion.
text('Reference targets q (fixed reference)',817,82,364,28,23,true);text('q:',822,132,34,28,24);line(862,147,1166,147);const ord='ACBD',q=[876,969,1050,1146],a=[884,962,1043,1140];q.forEach((x,i)=>{dot(x,147,ord[i],6,true);line(x,156,x,237,'#555555',1.1,true)});
text('Anchors x with fixed-width intervals',817,191,364,28,23,true);text('x:',822,244,34,28,24);a.forEach((x,i)=>{shape('rect',x-31,239,62,36,P[ord[i]],C[ord[i]],1.2);dot(x,257,ord[i],6);text(ord[i],x-15,279,30,27,22)});line(859,321,1171,321,'#555555',1.4);line(859,313,859,321,'#555555',1.4);line(1171,313,1171,321,'#555555',1.4);text('Displacement cap: τ(π) + β₀',820,334,359,29,24);
shape('roundRect',822,399,352,145,'#F7F7F7','#888888',1);text('QP (selected order only)',829,406,338,29,25,true);text('min  Σₖ λₖ Eₖ,  k ∈ {R, G, M, C}',828,446,340,29,23);
const term=['Reference','Geometry','Motion','Centering'];term.forEach((t,i)=>{shape('roundRect',828+i*86,493,82,34,'#FFFFFF','#999999',.8);text(t,831+i*86,493,76,34,20)});
arrow(1051,570,1051,547,'#555555',1.4);text('Valid history',1060,550,112,25,21);text('Matched projected motion',824,591,352,29,24,true);
line(865,702,1152,702,'#555555',1.3);line(865,702,865,632,'#555555',1.3);text('q',839,625,23,26,24);arrow(865,702,1152,702,'#555555',1.3);dot(895,654,'A',5,true);dot(1128,641,'A',5,true);line(895,654,1128,641,C.A,1.8);dot(895,682,'C',5,true);dot(1128,671,'C',5,true);line(895,682,1128,671,C.C,1.8);text('t − 1',866,708,67,25,22);text('t',1098,708,67,25,22);arrow(1000,737,1000,751);banner('Anchors x + intervals',824,758,350);
// Stage 4: the entire reconstruction chain with stack and assembly cue.
text('Reconstructed 1D scalar profile (join)',1215,80,365,29,23,true);line(1240,238,1559,238,'#555555',1.2);line(1240,238,1240,127,'#555555',1.2);text('f(u)',1208,119,49,28,23);text('u',1561,226,23,28,23);curveProfile(1250,141,292,89,true);[.12,.39,.66,.88].forEach((v,i)=>{line(1250+v*292,137,1250+v*292,229,'#777777',1,true);text(ord[i],1250+v*292-13,244,26,25,22)});
banner('Leaf / LCA filling',1218,290,176,20);banner('Barrier correction',1406,290,176,20);
for(let i=3;i>=0;i--){let x=1261+i*11,y=375-i*13;shape('roundRect',x,y,232,70,'#FFFFFF','#999999',1);curveProfile(x+8,y+10,215,48,i==0)}text('…',1510,367,35,29,26);arrow(1551,367,1571,397,'#555555',2);arrow(1571,397,1555,428,'#555555',2);
text('Temporal merge tree map',1219,448,361,28,25,true);
const bytes=await fs.readFile(SRC+'/assets/storms_map.png');s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:'Existing qualitative Storms scalar map at epsilon ten percent from the paper',position:{left:1262,top:492,width:260,height:218.4},fit:'contain'});shape('rect',1262,492,260,218.4,'none','#444444',1);arrow(1262,719,1522,719,'#555555',1.3);text('Time',1339,721,110,27,23);
const v=text('Reference coordinate u',1140,586,190,30,22);v.position.rotation=270;
// Scalar key uses the same diverging blue--white--orange family as the map.
const key=['#2166AC','#4393C3','#92C5DE','#D1E5F0','#F7F7F7','#FDDBC7','#F4A582','#D6604D'];key.forEach((c,i)=>shape('rect',1540,688-i*24,13,24,c,'none',0));text('high',1553,495,39,24,18);text('low',1553,684,39,24,18);text('f',1534,464,24,26,23);banner('Shared origin, direction & scale',1218,758,364);
s.speakerNotes.text='Only the middle construction panel (b) of the supplied independent concept is reproduced. Every internal component is retained: field thumbnails, matched trees and track IDs, motion vectors and global projection, three candidate orders, local refinement, separate tau and delta* evaluators, admission and rejection examples, selected order, reference targets and interval anchors, displacement cap, weighted four-term QP, valid history and projected motion, reconstructed profile, leaf/LCA filling, barrier correction, profile stack and assembly, and the temporal map. Style follows the current paper: Times New Roman, gray headings, black outlines and A/B/C/D colors blue/orange/teal/purple. The output map is the paper qualitative Storms archive at epsilon ten percent. All other diagrams are schematic, not measured results. Search is heuristic. Scalar image is raster; text, curves, trees, nodes, intervals and arrows are native editable PowerPoint objects. The schematic color key indicates relative scalar order, without calibrated numeric ticks. Actual rendered errors must be checked separately from continuous feasibility.';
await fs.mkdir(OUT,{recursive:true});await fs.writeFile(SRC+'/manifest.json',JSON.stringify({width:W,height:H,font:F,objects:n,scope:'middle construction panel only; all internal components retained'},null,2));
await fs.writeFile(OUT+'/framework-full-preview.png',new Uint8Array(await(await p.export({slide:s,format:'png',scale:1.5})).arrayBuffer()));
const candidate=SRC+'/.build/candidate-full.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);

await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:OUT+'/AnchorMTM_系统框架_完整b图.pptx',pythonExecutable:process.env.RUNTIME_PYTHON || 'python3',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu',`${W*9525},${H*9525}`,'--validate-heading-fit'],explicitTotalSlideCount:1,fontPolicy:{basis:'design',families:[F]},verifyArtifactToolImport:true,receiptPath:SRC+'/.build/validation-'+Date.now()+'.json'});
console.log('Saved full-panel preview and editable PPTX');
