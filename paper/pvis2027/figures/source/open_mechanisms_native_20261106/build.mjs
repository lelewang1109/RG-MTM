import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const modules=process.env.RUNTIME_NODE_MODULES;
const skill=process.env.PRESENTATIONS_SKILL_DIR;
const {Presentation,PresentationFile}=await import(pathToFileURL(modules+'/@oai/artifact-tool/dist/artifact_tool.mjs'));
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs'));
const SRC=import.meta.dirname, ROOT=path.resolve(SRC,'../../../../..');
const OUT=process.env.ANCHORMTM_FIGURE_OUTPUT_DIR||ROOT+'/output/native_mechanisms_20261106';
await fs.mkdir(OUT+'/.build',{recursive:true});await fs.mkdir(OUT+'/delivery',{recursive:true});
const W=1536,H=1024,FONT='Times New Roman';
const p=Presentation.create({slideSize:{width:W,height:H}});
let s,n=0;const manifest=[];
const C={A:'#007FFF',B:'#FF8500',C:'#00B9AE',D:'#A13BC6',black:'#080808',gray:'#8C8B93'};
function shape(geometry,name,x,y,w,h,fill='none',stroke='none',lw=0){
 n++;return s.shapes.add({geometry,name,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:lw,style:'solid'}});
}
function curve(name,cmd,color=C.black,width=3,fill='none',style='solid'){
 const coords=cmd.flatMap(c=>c.slice(1));
 const xx=[],yy=[];for(let i=0;i<coords.length;i+=2){xx.push(coords[i]);yy.push(coords[i+1]);}
 const l=Math.min(...xx),t=Math.min(...yy),w=Math.max(1,Math.max(...xx)-l),h=Math.max(1,Math.max(...yy)-t);
 const commands=cmd.map(c=>c[0]==='M'?{moveTo:{x:c[1]-l,y:c[2]-t}}:c[0]==='L'?{lineTo:{x:c[1]-l,y:c[2]-t}}:c[0]==='C'?{cubicBezTo:{x1:c[1]-l,y1:c[2]-t,x2:c[3]-l,y2:c[4]-t,x:c[5]-l,y:c[6]-t}}:{close:{}});
 n++;return s.shapes.add({geometry:'custom',name,position:{left:l,top:t,width:w,height:h},fill,line:{fill:color,width,style},customPaths:[{width:w,height:h,commands}]});
}
function poly(name,pts,color,width=1,fill='none',closed=false){return curve(name,[['M',...pts[0]],...pts.slice(1).map(x=>['L',...x]),...(closed?[['Z']]:[])],color,width,fill)}
function line(name,x,y,X,Y,c=C.black,w=3,style='solid'){return curve(name,[['M',x,y],['L',X,Y]],c,w,'none',style)}
function head(name,x,y,angle,c,size=19){const a=angle,pt=(u,v)=>[x+u*Math.cos(a)-v*Math.sin(a),y+u*Math.sin(a)+v*Math.cos(a)];return poly(name,[[x,y],pt(-size,-size*.44),pt(-size*.70,0),pt(-size,size*.44)],'none',0,c,true)}
function arrow(name,x,y,X,Y,c=C.black,w=3,size=19,style='solid'){line(name+' shaft',x,y,X,Y,c,w,style);head(name+' arrowhead',X,Y,Math.atan2(Y-y,X-x),c,size)}
function node(name,x,y,r,fill,stroke=C.black,w=2.5){return shape('ellipse',name,x-r,y-r,2*r,2*r,fill,stroke,w)}
function diamond(name,x,y,r=19){return shape('diamond',name,x-r,y-r,2*r,2*r,'#FFFFFF',C.black,2.8)}
function label(name,text,x,y,w,h,size=48){let a=shape('textbox',name,x,y,w,h);a.text=text;a.text.style={typeface:FONT,fontSize:name.includes('annotation')?32:size,italic:!name.includes('annotation'),color:'#000000',alignment:'center',verticalAlignment:'middle',insets:0,wrap:'none',autoFit:'none'};return a}
function wash(name,cx,cy,rx,ry,base){for(let j=0;j<32;j++){const t=j/31,sc=1-t*.85;const rgb=base.map(v=>Math.round(255+(v-255)*Math.sin(t*Math.PI/2)));shape('ellipse',name+' editable tone '+j,cx-rx*sc,cy-ry*sc,rx*sc*2,ry*sc*2,'#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join(''));}}
function begin(name){s=p.slides.add();s.background.fill='#FFFFFF';n=0;s.speakerNotes.text=`${name}. Native editable reconstruction of the approved 1536 × 1024 reference. All displayed objects are native PowerPoint shapes, freeform paths, or text boxes. No image is embedded. Object names describe their role. Positions and scientific content follow the supplied conceptual schematic. Smooth native fills replace the source's fine raster texture; no pixel-identical raster fidelity is claimed.`;}
function end(name){manifest.push({slide:manifest.length+1,name,objects:n,images:0});}

// 1. Motion-derived direction. Isolines follow extracted original contour geometry.
begin('Direction and spatial reference');
Object.assign(C,{A:'#026EFB',B:'#FC7902',C:'#01B1A6',D:'#9E3DC1'});
const g=JSON.parse(await fs.readFile(SRC+'/direction_geometry.json','utf8'));
for(let i=0;i<g.fills.length;i++){const a=g.fills[i];poly(`Field ${a.name} editable wash region ${i+1}`,a.points,'none',0,a.color,true)}
for(let i=0;i<g.strokes.length;i++){const a=g.strokes[i];curve(`Scalar contour ${i+1}`,a.commands,a.color,.85)}
const tracks={A:[[186,453],[262,425],[331,400],[411,372]],B:[[1005,284],[1057,266],[1127,241],[1204,211]],C:[[406,628],[486,599],[556,573],[629,546]],D:[[735,470],[787,447],[847,422],[925,393]]};
for(const [k,pts] of Object.entries(tracks)){
 for(let j=0;j<3;j++){const [x,y]=pts[j],[X,Y]=pts[j+1],ang=Math.atan2(Y-y,X-x),tip=[X-15*Math.cos(ang),Y-15*Math.sin(ang)];arrow(`${k} matched displacement ${j+1}`,x,y,...tip,C[k],3,17)}
 pts.forEach(([x,y],i)=>node(`${k} extremum at time ${i+1}`,x,y,i===3?11.7:8.8,C[k],'#FFFFFF',1.5));
}
label('Extremum A label','A',420,309,43,59,49);label('Extremum B label','B',1211,140,50,61,49);label('Extremum C label','C',630,478,48,61,49);label('Extremum D label','D',930,324,50,62,49);
arrow('Fixed reference q axis',137,954,1471,600,'#0068FF',3.5,24);node('Reference origin',137,954,8.5,'#0068FF','none',0);label('Reference origin label','o',99,949,45,51,48);label('Reference axis label','q',1470,559,42,60,50);
const targets={A:[589,835],C:[726,800],D:[1044,717],B:[1349,635]};
for(const k of 'ACDB'){
 const [x,y]=tracks[k][3],[X,Y]=targets[k];
 // Individual round dots replicate the reference projection guides and remain editable.
 const len=Math.hypot(X-x,Y-y),cnt=Math.floor(len/9.5);
 for(let i=2;i<cnt;i++){const t=i/cnt;node(`${k} perpendicular projection dot ${i}`,x+(X-x)*t,y+(Y-y)*t,1.65,'#161616','none',0)}
 const ux=.966,uy=-.258,vx=-.36,vy=-.933;
 poly(`${k} right angle mark`,[[X+16*vx,Y+16*vy],[X+16*vx+16*ux,Y+16*vy+16*uy],[X+16*ux,Y+16*uy]],'#111111',1.9);
 node(`${k} projected reference target`,X,Y,9.6,'#FFFFFF',C[k],3);
}
// Preserve the small construction mark visible next to the C trajectory.
poly('Local projection right-angle mark',[[480,595],[477,585],[490,581],[493,590]],'#111111',1.8);
const ox=1139,oy=620;
arrow('Candidate direction gray',ox,oy,1472,550,'#A5A6AD',2.5,15,'dashed');
arrow('Candidate displacement B',ox,oy,1383,502,C.B,2.8,15);
arrow('Candidate displacement D',ox,oy,1387,523,C.D,2.8,15);
arrow('Candidate displacement C',ox,oy,1400,544,C.C,2.8,15);
arrow('Selected direction a star',ox,oy,1473,497,'#0068FF',3.5,24);
node('Direction fan origin',ox,oy,8,'#0068FF','none',0);
label('Direction a label','a',1454,434,41,61,51);label('Direction superscript star','*',1487,433,26,34,33);
label('Motion annotation','Matched motion',80,100,330,48,36);
label('Direction annotation','Selected direction',1288,389,240,45,34);
label('Projection annotation','Fixed spatial reference',765,839,375,48,34);
end('Direction');

// 2. Conflict. Coordinates and ordering are copied from the approved open layout.
begin('Topology and spatial-position conflict');
Object.assign(C,{A:'#0085FD',B:'#FE8302',C:'#00C1B1',D:'#AC5FC7'});
wash('AB subtree soft tint',561.5,316.5,182.5,68.5,[233,245,255]);
wash('CD subtree soft tint',968.5,317.5,175.5,67.5,[246,233,250]);
[[773,35,558,136],[773,35,971,136],[558,136,460,302],[558,136,654,302],[971,136,874,302],[971,136,1063,302]].forEach((a,i)=>line('Topology edge '+(i+1),...a,C.black,3));
diamond('Original root',773,35,21);diamond('AB merge',558,136,21);diamond('CD merge',971,136,21);
const lx=[460,654,874,1063],leafTint=['#5EB7FE','#FEA343','#00C3B0','#C891DF'];'ABCD'.split('').forEach((k,i)=>{node(k+' tree leaf',lx[i],302,14.4,leafTint[i],C.black,2.7);label(k+' tree label',k,lx[i]-25-[4,4,4,1][i],307,50,59,49)});
curve('AB subtree brace',[['M',396,370],['C',400,395,429,388,486,389],['C',524,389,547,388,555,405],['C',565,387,590,390,626,389],['C',687,389,711,395,717,370]],'#8B889B',2.6);
curve('CD subtree brace',[['M',812,370],['C',817,394,844,389,895,389],['C',934,389,957,390,965,406],['C',977,389,1003,389,1040,389],['C',1090,389,1114,393,1120,370]],'#8B889B',2.6);
const upperCurves=[[['M',456,369],['C',459,456,308,429,310,548]],[['M',653,369],['C',681,448,582,429,583,548]],[['M',872,369],['C',869,440,827,431,846,548]],[['M',1066,369],['C',1056,453,1158,434,1141,548]]];
upperCurves.forEach((c,i)=>curve('Tree leaf '+ 'ABCD'[i]+' to x',c,C['ABCD'[i]],2.8));
arrow('Displayed x coordinate axis',127,549,1441,549,C.black,3.2,22);
label('Displayed x label','x',67,500,48,64,62);
const ax=[310,583,846,1141];
[[227,408],[467,685],[755,964],[1033,1240]].forEach(([a,b],i)=>shape('roundRect','Fixed-width interval '+ 'ABCD'[i],a,560,b-a,12,C['ABCD'[i]]+'/32'));
'ABCD'.split('').forEach((k,i)=>{node(k+' displayed anchor',ax[i],548,17,C[k],C.black,2.5);label(k+' displayed anchor label',k,ax[i]-27-[6,3,6,1][i],560,54,60,51)});
line('A correspondence guide',310,655,310,883,C.A,1.4);
for(let y=666;y<875;y+=11)node('A guide dot '+y,310,y,1.15,C.A,'none',0);
curve('B order-conflict correspondence',[['M',580,654],['C',605,773,1183,789,1184,883]],C.B,2.9);
curve('C order-conflict correspondence',[['M',853,655],['C',847,769,620,748,627,883]],C.C,2.9);
curve('D order-conflict correspondence',[['M',1141,655],['C',1106,757,876,747,889,883]],C.D,2.9);
arrow('Reference q coordinate axis',127,883,1444,883,C.black,3.5,23);label('Reference q label','q',67,828,48,72,60);
const qx=[310,627,889,1184];'ACDB'.split('').forEach((k,i)=>{node(k+' reference target',qx[i],883,16.6,'#FFFFFF',C[k],4.5);label(k+' reference label',k,qx[i]-28-[3,5,2,3][i],889,56,62,51)});
label('Topology order annotation','Topology-compatible order',1124,405,405,48,34);
label('Spatial order annotation','Spatial reference order',125,943,370,48,34);
label('Order conflict annotation','Order conflict',620,615,240,45,34);
end('Conflict');

// 3. Relaxation. Separate native topology, height guides, profiles, markers and fills.
begin('Selective relaxation');
Object.assign(C,{A:'#015EC8',B:'#FE8103',C:'#009E9D',D:'#8458AA'});
line('Root-height guide',353,100,1220,100,'#888892',1.5,'dotted');
line('AB-height guide',211,277,1199,277,'#888892',1.5,'dotted');
line('CD-height guide',530,427,1395,427,'#888892',1.5,'dotted');
line('Extremum-height guide',604,533,956,533,'#888892',1.5,'dotted');
shape('rect','Raised saddle soft blue fill',725,429,74,103,'linear(0deg,#ECF8FF 0%,#F6FCFF 100%)');
arrow('Root lowering',832,101,832,267,'#9954B3',2.1,21);
arrow('Saddle raising',762,533,762,431,'#0071DB',2.4,20);
line('Strict root to AB',343,100,207,293,C.black,3.4);line('Strict root to CD',343,100,521,437,C.black,3.4);
line('Relaxed AB branch to A',207,293,109,535,'#909090',3.5,'dashed');line('Relaxed AB branch to B',207,293,294,535,'#909090',3.5,'dashed');
line('Strict CD branch to C',521,437,445,535,C.black,3.4);line('Strict CD branch to D',521,437,594,535,C.black,3.4);
diamond('Strict root',343,100,18);diamond('Released AB merge',207,293,18);diamond('Retained CD merge',521,437,18);
const strictX=[109,294,445,594],relaxedX=[959,1125,1275,1434];
'ABCD'.split('').forEach((k,i)=>{node(k+' strict leaf',strictX[i],535,16.5,C[k],C.black,2.5);label(k+' strict label',k,strictX[i]-23,548,44,46,34)});
curve('Relaxed root to A',[['M',1200,271],['C',1057,317,977,416,959,535]],C.black,3.4);
curve('Relaxed root to B',[['M',1200,271],['C',1330,317,1407,412,1434,535]],C.black,3.4);
line('Relaxed root to CD',1200,271,1200,426,C.black,3.4);line('Relaxed CD to C',1200,426,1125,535,C.black,3.4);line('Relaxed CD to D',1200,426,1275,535,C.black,3.4);
diamond('Relaxed root',1200,271,18);diamond('Relaxed retained CD merge',1200,426,18);
'ACDB'.split('').forEach((k,i)=>{node(k+' relaxed leaf',relaxedX[i],535,16.5,C[k],C.black,2.5);label(k+' relaxed label',k,relaxedX[i]-23,548,44,46,34)});
for(const [i,x] of [109,283,442,590,958,1119,1271,1432].entries())line('Leaf profile guide '+(i+1),x,599,x,i<4?904:902,'#8E8E93',1.5,'dashed');
const before=[['M',56,770],['C',78,783,83,890,110,904],['C',137,907,157,787,203,768],['C',245,779,253,901,280,904],['C',294,902,293,753,344,714],['C',386,731,410,901,443,902],['C',467,908,482,833,509,829],['C',539,834,561,900,589,902],['C',608,903,617,798,648,765]];
const after=[['M',899,780],['C',922,794,932,895,959,902],['C',984,907,997,787,1039,777],['C',1078,786,1092,900,1121,902],['C',1146,904,1165,819,1195,815],['C',1225,822,1242,900,1273,902],['C',1302,900,1314,788,1355,777],['C',1397,796,1402,904,1432,902],['C',1454,897,1474,791,1498,780]];
curve('Strict profile area',[...before,['L',648,919],['L',56,919],['Z']],'none',0,'linear(90deg,#FFFFFF 0%,#EFF9FE 55%,#EEF8FF 100%)');
curve('Relaxed profile area',[...after,['L',1498,919],['L',899,919],['Z']],'none',0,'linear(90deg,#FFFFFF 0%,#EFF9FE 55%,#EEF8FF 100%)');
line('Strict high barrier guide',204,769,649,769,'#A3A3AC',1.3,'dashed');line('Strict low barrier guide',440,829,649,829,'#A3A3AC',1.3,'dashed');
line('Relaxed high barrier guide',900,780,1497,780,'#A3A3AC',1.3,'dashed');line('Relaxed low barrier guide',1091,816,1399,816,'#A3A3AC',1.3,'dashed');
curve('Strict scalar profile',before,C.black,3.4);curve('Relaxed scalar profile',after,C.black,3.4);
for(const [name,x,end] of [['Strict',56,685],['Relaxed',899,1526]]){arrow(name+' profile ordinate',x,920,x,684,C.black,3.1,17);arrow(name+' profile abscissa',x,920,end,920,C.black,3.1,18);arrow(name+' extra direction cue',x-20,698,x-20,665,C.black,1.6,14)}
[[110,904,'A'],[280,904,'B'],[443,902,'C'],[589,902,'D'],[959,902,'A'],[1121,902,'C'],[1273,902,'D'],[1432,902,'B']].forEach(([x,y,k])=>node(k+' profile extremum '+x,x,y,9.5,C[k],C.black,1.6));
[[203,768],[344,714],[509,829],[1039,777],[1195,815],[1355,777]].forEach(([x,y])=>diamond('Profile saddle '+x,x,y,11.5));
curve('Relaxation transformation arrow',[['M',695,821],['C',737,799,772,796,819,807]],'#666666',4.5);head('Relaxation transformation arrowhead',832,809,.13,'#666666',32);
shape('ellipse','Highlight relaxed AB node',165,251,84,84,'none','#A75C32',2.7);
label('Relaxed node annotation','Relaxed',36,218,135,45,35);
line('Relaxed annotation leader',151,253,174,268,'#A75C32',2);
label('Strict tree annotation','Original topology',80,22,270,44,35);
label('Relaxed tree annotation','Relaxed topology',1085,181,285,44,35);
label('Strict profile annotation','Before relaxation',177,950,300,44,34);
label('Relaxed profile annotation','After relaxation',1075,950,300,44,34);
end('Relaxation');

await fs.writeFile(SRC+'/manifest.json',JSON.stringify({width:W,height:H,font:FONT,slides:manifest,scope:'Native shapes only. Raster source texture is approximated with editable smooth fills.'},null,2));
for(let i=0;i<p.slides.items.length;i++){const slide=p.slides.items[i];const b=await p.export({slide,format:'png',scale:1});await fs.writeFile(OUT+'/.build/slide-'+(i+1)+'.png',new Uint8Array(await b.arrayBuffer()));}
const candidate=OUT+'/.build/native-candidate.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
if(process.env.PREVIEW_ONLY!=='1')await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:OUT+'/delivery/Fig4-6_方向_冲突_放松_原生可编辑.pptx',pythonExecutable:process.env.RUNTIME_PYTHON||'python3',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu',`${W*9525},${H*9525}`],explicitTotalSlideCount:3,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:OUT+'/.build/validation-'+Date.now()+'.json'});
console.log(JSON.stringify(manifest));
