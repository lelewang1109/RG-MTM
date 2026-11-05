import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require(process.env.RUNTIME_NODE_MODULES ? path.join(process.env.RUNTIME_NODE_MODULES,'sharp') : '/Users/lele/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const dir=import.meta.dirname,report=[];
for(const name of ['01_direction.png','02_conflict.png','03_relaxation.png']){
 const source=path.join(dir,'original_gray_background',name),target=path.join(dir,name);
 const {data,info}=await sharp(source).removeAlpha().raw().toBuffer({resolveWithObject:true});
 const result=Buffer.from(data);let count=0;
 // Smoothly lift only the near-white substrate to avoid threshold speckles.
 // No geometry changes, interpolation, resampling or redraw.
 for(let i=0;i<data.length;i+=3){const lo=Math.min(data[i],data[i+1],data[i+2]);
  if(lo>230){const t=Math.min(1,(lo-230)/15),w=t*t*(3-2*t),lift=(255-lo)*w;
   for(let c=0;c<3;c++)result[i+c]=Math.min(255,Math.round(data[i+c]+lift));
   count++;
  }
 }
 await sharp(result,{raw:{width:info.width,height:info.height,channels:3}}).png().toFile(target);
 const decoded=await sharp(target).removeAlpha().raw().toBuffer();let alteredForeground=0;
 for(let i=0;i<data.length;i+=3){const lo=Math.min(data[i],data[i+1],data[i+2]);if(lo<=230&&(decoded[i]!==data[i]||decoded[i+1]!==data[i+1]||decoded[i+2]!==data[i+2]))alteredForeground++;}
 if(alteredForeground)throw new Error('Foreground changed: '+name);
 report.push({name,width:info.width,height:info.height,backgroundPixelsWhitened:count,changedPixelsWithMinimumChannelAtMost230:alteredForeground});
}
await fs.writeFile(path.join(dir,'BACKGROUND_VALIDATION.json'),JSON.stringify({rule:'min channel >=245 maps to pure white; smooth neutral lift over minimum channel (230,245); pixels with minimum channel <=230 remain unchanged',images:report},null,2));console.log(report);
