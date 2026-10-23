import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
// Resolved through the .build/node_modules link supplied by regenerate.py.
const RUNTIME='/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/node';
const {Presentation,PresentationFile}=await import(pathToFileURL(RUNTIME+'/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href).catch(async()=>await import('@oai/artifact-tool'));
const ROOT=path.resolve(import.meta.dirname,'..');
const sc=JSON.parse(await fs.readFile(ROOT+'/evidence/fig1/scene.json','utf8'));
const p=Presentation.create({slideSize:{width:sc.width,height:sc.height}});
const sl=p.slides.add();sl.background.fill='#FFFFFF';
function draw(o){
 const position={left:o.x,top:o.y,width:o.w,height:o.h,rotation:o.rotation||0};
 const ln=(fill,width,dash)=>({fill:fill||'none',width:width||0,style:dash?'dashed':'solid'});
 if(o.kind==='text'){
  const sh=sl.shapes.add({geometry:'textbox',name:o.name,position,fill:'none',line:ln('none',0)});
  sh.text=o.text;sh.text.style={typeface:'Arial',fontSize:o.size,bold:o.bold,color:o.color,alignment:o.align||'left',verticalAlignment:o.textOrientation?'middle':'top',autoFit:'none',wrap:'none',insets:0};return;
 }
 if(['rect','ellipse'].includes(o.kind))return sl.shapes.add({geometry:o.kind,name:o.name,position,fill:o.fill,line:ln(o.stroke,o.width)});
 if(o.kind==='blockArrow')return sl.shapes.add({geometry:'downArrow',name:o.name,position,rotation:o.rotation,fill:o.fill,line:ln(o.stroke,o.width)});
 const pts=o.kind==='line'?[[o.x1,o.y1],[o.x2,o.y2]]:o.points;
 const xx=Math.min(...pts.map(t=>t[0])),yy=Math.min(...pts.map(t=>t[1]));
 const w=Math.max(...pts.map(t=>t[0]))-xx||.01,h=Math.max(...pts.map(t=>t[1]))-yy||.01;
 return sl.shapes.add({geometry:'custom',name:o.name,position:{left:xx,top:yy,width:w,height:h},fill:'none',line:ln(o.color,o.width,o.dash),customPaths:[{width:w,height:h,commands:pts.map((pt,i)=>({[i?'lineTo':'moveTo']:{x:pt[0]-xx,y:pt[1]-yy}}))}]});
}
for(const o of sc.objects){
 if(o.kind==='image'){
  const b=await fs.readFile(o.path);
  sl.images.add({name:o.name,alt:o.name,blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',position:{left:o.x,top:o.y,width:o.w,height:o.h},fit:'contain'});
 }else draw(o);
}
sl.speakerNotes.text=sc.notes;
await(await PresentationFile.exportPptx(p)).save(ROOT+'/.build/fig1/Figure1_candidate.pptx');
await fs.writeFile(ROOT+'/.build/fig1/Figure1_layout.json',await(await sl.export({format:'layout'})).text());
console.log('Native Figure 1 exported.');
