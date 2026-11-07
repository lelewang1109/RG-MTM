import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const ROOT=import.meta.dirname;
const MOD='/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE_MODULES=MOD;
const SKILL='/Users/lele/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(MOD+'/@oai/artifact-tool/dist/artifact_tool.mjs'));
const d=JSON.parse(await fs.readFile(ROOT+'/editable_scene.json','utf8'));const p=Presentation.create({slideSize:{width:d.width,height:d.height}});const sl=p.slides.add();sl.background.fill='#FFFFFF';sl.speakerNotes.text=d.slides[0].notes;
for(const [i,s] of d.slides[0].shapes.entries()){
 const name=s.name||`${s.kind}-${i}`;
 if(s.kind==='image'){sl.images.add({blob:new Uint8Array(await fs.readFile(s.path)),contentType:'image/png',alt:name+' (scalar background only)',fit:'contain',position:{left:s.x,top:s.y,width:s.w,height:s.h}});continue;}
 if(s.kind==='text'){const a=sl.shapes.add({geometry:'textbox',name,position:{left:s.x,top:s.y,width:s.w,height:s.h,rotation:s.rotation||0},fill:'none',line:{fill:'none',width:0}});a.text=s.text;a.text.style={typeface:'Times New Roman',fontSize:s.size,bold:s.bold||false,color:'#111111',alignment:'center',verticalAlignment:'middle',insets:0,wrap:'none',autoFit:'none'};continue;}
 if(s.kind==='rect'||s.kind==='marker'){sl.shapes.add({geometry:s.kind==='rect'?'rect':s.shape,name,position:{left:s.x,top:s.y,width:s.w,height:s.h},fill:s.fill||'none',line:{fill:s.color,width:s.width||.8,style:'solid'}});continue;}
 if(s.kind==='path'){const xx=s.points.map(v=>v[0]),yy=s.points.map(v=>v[1]);const x=Math.min(...xx),y=Math.min(...yy),w=Math.max(.01,Math.max(...xx)-x),h=Math.max(.01,Math.max(...yy)-y);sl.shapes.add({geometry:'custom',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:s.color,width:s.width,style:s.style},customPaths:[{width:w,height:h,commands:s.points.map((pt,j)=>({[j?'lineTo':'moveTo']:{x:pt[0]-x,y:pt[1]-y}}))}]});}
}
const candidate=ROOT+'/.build/candidate.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
const png=await p.export({slide:sl,format:'png',scale:1.5});await fs.writeFile(ROOT+'/.build/preview.png',new Uint8Array(await png.arrayBuffer()));
const {finalizePresentation}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs'));
await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:ROOT+'/delivery/Fig6_Storms_参数与方法对比_可编辑.pptx',pythonExecutable:'/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu',`${d.width*9525},${d.height*9525}`,'--validate-heading-fit'],explicitTotalSlideCount:1,fontPolicy:{basis:'design',families:['Times New Roman']},verifyArtifactToolImport:true,receiptPath:ROOT+'/.build/validation.json'});
