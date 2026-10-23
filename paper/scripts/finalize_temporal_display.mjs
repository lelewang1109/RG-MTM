import fs from 'node:fs/promises';import path from 'node:path';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';
const R=path.resolve(import.meta.dirname,'..'),B=R+'/.build/temporal_display20261023';
const S='/Users/lele/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
process.env.RUNTIME_NODE_MODULES='/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(S+'/container_tools/artifact_tool_utils.mjs'));
const combined=process.argv.includes('--combined');const plans=JSON.parse(await fs.readFile(B+'/plans.json'));
const stems=combined?['All_Figures','All_Supplementary_Figures']:Object.keys(plans);
const checked={};
for(const stem of stems){
 const ref=combined?R+'/figures_ppt/Fig6.pptx':B+'/before/'+stem+'.pptx';const stamp=Date.now();const finalPath=B+'/final/'+stem+'-'+stamp+'.pptx';
 await finalizePresentation({workspaceDir:R,candidatePath:(combined?R+'/figures_ppt/':B+'/candidates/')+stem+'.pptx',finalPath,
 pythonExecutable:'/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',integrityValidatorPath:S+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:S+'/container_tools/inspect_presentation_layout_geometry.py',
 explicitTotalSlideCount:combined?(stem==='All_Figures'?14:18):1,
 requiredNativeChartOwnerSlides:combined?(stem==='All_Figures'?[5,14]:[3,4,5]):[],nativeChartTargetApplication:'powerpoint',
 fontPolicy:{basis:'reference',families:['Arial'],referencePath:ref,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(ref)).digest('hex')},verifyArtifactToolImport:true,
 receiptPath:R+'/checks/temporal_display20261023/'+stem+'-'+stamp+'.validation.json'});
 checked[stem]=finalPath;console.log('Validated',stem);
}
await fs.writeFile(B+'/checks/'+(combined?'combined':'individual')+'-selected.json',JSON.stringify(checked,null,2));
