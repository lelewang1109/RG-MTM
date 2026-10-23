import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const RUNTIME='/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/node';
const {Presentation,PresentationFile}=await import(pathToFileURL(RUNTIME+'/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const {default:sharp}=await import(pathToFileURL(RUNTIME+'/node_modules/sharp/dist/index.mjs').href);
const ROOT=path.resolve(import.meta.dirname,'..');
const B=process.env.RGMTM_SCENE_STAGE||ROOT+'/.build/case-figures-20261023';
const stems=process.argv.slice(2).length?process.argv.slice(2):['Cylinder_additions','Wildfires_additions','Supplement_OLR_Comparison','Supplement_PM25_Comparison'];
for(const stem of stems){
 const sc=JSON.parse(await fs.readFile(B+'/scenes/'+stem+'.json','utf8'));
 const p=Presentation.create({slideSize:{width:sc.width,height:sc.height}});const sl=p.slides.add();sl.background.fill='#FFFFFF';
 for(const o of sc.objects){
  const pos={left:o.x,top:o.y,width:o.w,height:o.h,rotation:o.rotation||0};
  const ln=(fill,width,dash)=>({fill:fill||'none',width:width||0,style:dash?'dashed':'solid'});
  if(o.kind==='image'){
   // Scalar rasters fill their declared axis extent. Sample-array aspect ratios
   // are unrelated to physical/time display extents. Preserve every sample.
   const original=await fs.readFile(o.path);const meta=await sharp(original).metadata();
   const displayHeight=Math.max(meta.height,Math.round(o.h*2));
   const b=await sharp(original).resize(Math.round(displayHeight*o.w/o.h),displayHeight,{fit:'fill',kernel:'nearest'}).png().toBuffer();
   sl.images.add({name:o.name,alt:o.name,blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',position:pos,fit:'contain'});
  }else if(o.kind==='text'){
   const sh=sl.shapes.add({geometry:'textbox',name:o.name,position:pos,fill:'none',line:ln('none',0)});sh.text=o.text;sh.text.style={typeface:'Arial',fontSize:o.size,bold:o.bold,color:o.color,alignment:o.align||'left',verticalAlignment:'top',autoFit:'none',wrap:'none',insets:0};
  }else if(['rect','ellipse','roundRect'].includes(o.kind)){
   sl.shapes.add({geometry:o.kind,name:o.name,position:pos,fill:o.fill,line:ln(o.stroke,o.width)});
  }else{
   const pts=o.kind==='line'?[[o.x1,o.y1],[o.x2,o.y2]]:o.points;
   const x=Math.min(...pts.map(t=>t[0])),y=Math.min(...pts.map(t=>t[1]));const w=Math.max(...pts.map(t=>t[0]))-x||.01,h=Math.max(...pts.map(t=>t[1]))-y||.01;
   sl.shapes.add({geometry:'custom',name:o.name,position:{left:x,top:y,width:w,height:h},fill:'none',line:ln(o.color,o.width,o.dash),customPaths:[{width:w,height:h,commands:pts.map((pt,i)=>({[i?'lineTo':'moveTo']:{x:pt[0]-x,y:pt[1]-y}}))}]});
  }
 }
 sl.speakerNotes.text=sc.notes;
 await(await PresentationFile.exportPptx(p)).save(B+'/candidates/'+stem+'.pptx');
 await fs.writeFile(B+'/checks/'+stem+'_layout.json',await(await sl.export({format:'layout'})).text());
 console.log('Exported native authoring layer:',stem);
}
