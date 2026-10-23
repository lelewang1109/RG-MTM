import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const R=path.resolve(import.meta.dirname,'..'), B=R+'/.build/wildfire_geo20261023';
const S='/Users/lele/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
process.env.RUNTIME_NODE_MODULES='/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(S+'/container_tools/artifact_tool_utils.mjs'));
const combined=process.argv.includes('--combined');
const ref=B+'/before/Fig7.pptx';
await fs.mkdir(R+'/checks/wildfire_geo20261023',{recursive:true});
const stamp=Date.now(),stem=combined?'All_Figures':'Fig7',finalPath=B+'/final/'+stem+'-'+stamp+'.pptx';
await finalizePresentation({workspaceDir:R,
 candidatePath:combined?R+'/figures_ppt/All_Figures.pptx':B+'/candidates/Fig7.pptx',
 finalPath,
 pythonExecutable:'/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
 integrityValidatorPath:S+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:S+'/container_tools/inspect_presentation_layout_geometry.py',
 explicitTotalSlideCount:combined?14:1,
 requiredNativeChartOwnerSlides:combined?[5,14]:[], nativeChartTargetApplication:'powerpoint',
 fontPolicy:{basis:'reference',families:['Arial'],referencePath:ref,referenceSha256:crypto.createHash('sha256').update(await fs.readFile(ref)).digest('hex')},
 verifyArtifactToolImport:true,receiptPath:R+'/checks/wildfire_geo20261023/'+stem+'-'+stamp+'.validation.json'});
await fs.writeFile(B+'/checks/'+stem+'-selected.json',JSON.stringify({finalPath},null,2));
console.log('Validated '+(combined?'combined deck':'Figure 7'));
