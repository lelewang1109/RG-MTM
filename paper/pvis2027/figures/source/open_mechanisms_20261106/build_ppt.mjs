import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const mods=process.env.RUNTIME_NODE_MODULES;if(!mods)throw new Error('Set RUNTIME_NODE_MODULES.');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(mods,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const skill=process.env.PRESENTATIONS_SKILL_DIR;if(!skill)throw new Error('Set PRESENTATIONS_SKILL_DIR.');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const src=import.meta.dirname,root=path.resolve(src,'../../../../..'),base=process.env.ANCHORMTM_FIGURE_OUTPUT_DIR||root+'/output/three_mechanisms_rebuild';await fs.mkdir(base+'/.build',{recursive:true});await fs.mkdir(base+'/delivery',{recursive:true});
const items=[['01_direction.png','Motion-derived fixed spatial reference'],['02_conflict.png','Spatial targets and exact-topology order conflict; x above q; three requested braces removed'],['03_relaxation.png','Selective relaxation of AB contiguity while CD remains grouped']];
const p=Presentation.create({slideSize:{width:1536,height:1024}});
for(let i=0;i<items.length;i++){
 const [file,desc]=items[i],s=p.slides.add();s.background.fill='#FFFFFF';const buf=await fs.readFile(src+'/'+file);
 s.images.add({blob:buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength),contentType:'image/png',alt:desc,position:{left:0,top:0,width:1536,height:1024},fit:'contain'});
 s.speakerNotes.text=`${desc}. Source: independently generated illustration refined in this chat, ${file}. Artwork is embedded at its original resolution to preserve the requested appearance. The image can be moved or replaced as a picture; its internal labels/lines are raster, not individual native objects. Scientific conceptual schematic, not experimental evidence. No mapping figure is included. Main-paper usage: single-column figure. All coordinate and height positions are schematic. Source diagrams were based on the current AnchorMTM method text.`;
 const blob=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(base+'/.build/slide-'+(i+1)+'.png',new Uint8Array(await blob.arrayBuffer()));
}
const candidate=base+'/.build/candidate.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:base+'/delivery/方向_冲突_放松_三张图.pptx',pythonExecutable:process.env.RUNTIME_PYTHON||'python3',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu',`${1536*9525},${1024*9525}`],explicitTotalSlideCount:3,verifyArtifactToolImport:true,receiptPath:base+'/.build/validation-'+Date.now()+'.json'});
console.log('Three-slide PPTX exported and validated.');
