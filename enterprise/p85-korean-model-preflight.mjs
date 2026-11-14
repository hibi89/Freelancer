/** Offline-only candidate Korean embedding asset verifier. This does NOT load a model.
 * No download, remote API, customer data, model execution, or commercial approval.
 */
import fs from 'node:fs';
import fsp from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {createReadStream} from 'node:fs';

export const CANDIDATE=Object.freeze({
  upstream:'intfloat/multilingual-e5-small',
  onnx:'Xenova/multilingual-e5-small',
  artifact:'onnx/model_int8.onnx',
  expected_sha256:'4d24e2bc01a447951524466ef533e52944bf48509e6552810bcee1a2711cb02c',
  upstream_license_label:'MIT (upstream model card; conversion/packaging review pending)',
  weight_bytes_approx:118_000_000
});
const deny=code=>{throw Object.assign(Error('OFFLINE_MODEL_PREFLIGHT_REFUSED'),{code});};
const components=p=>{const abs=path.resolve(p),root=path.parse(abs).root;
  let curr=root;
  for(const segment of path.relative(root,abs).split(path.sep)){
    if(!segment)continue;curr=path.join(curr,segment);
    const st=fs.lstatSync(curr);
    if(!st.isDirectory()||st.isSymbolicLink())deny('UNSAFE_MODEL_PATH');
  }
  return abs;
};
export async function hashLocalFile(p){
  const st=await fsp.lstat(p);
  if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1)deny('UNSAFE_MODEL_FILE');
  const sha=crypto.createHash('sha256'),stream=createReadStream(p,{flags:'r'});
  for await(const bytes of stream)sha.update(bytes);
  const after=await fsp.lstat(p);
  if(after.size!==st.size||after.mtimeMs!==st.mtimeMs||after.ino!==st.ino)
    deny('MODEL_CHANGED_DURING_HASH');
  return Object.freeze({sha256:sha.digest('hex'),size:st.size});
}
export async function preflightKoreanEmbedding({modelDir}={}){
  if(typeof modelDir!=='string'||!path.isAbsolute(modelDir))deny('ABSOLUTE_DIRECTORY_REQUIRED');
  let dir;
  try{dir=components(modelDir);}catch(e){if(e?.code==='ENOENT')deny('MODEL_NOT_FOUND');throw e;}
  // components(modelDir) already rejects symlinks at every ancestor by lstat.
  // Windows realpath may expand 8.3 names or alter case; string inequality is not a symlink test.
  const aux=['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json'];
  for(const name of aux){
    const p=path.join(dir,name);
    let st;try{st=await fsp.lstat(p);}catch(e){if(e.code==='ENOENT')deny('MODEL_SUPPORT_MISSING');throw e;}
    if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1||st.size<2||st.size>32*1024*1024)
      deny('MODEL_SUPPORT_UNSAFE');
  }
  const onnxDir=path.join(dir,'onnx');
  try{components(onnxDir);}catch(e){if(e.code==='ENOENT')deny('MODEL_NOT_FOUND');throw e;}
  const fp=path.join(onnxDir,'model_int8.onnx');
  let st;try{st=await fsp.lstat(fp);}catch(e){if(e.code==='ENOENT')deny('MODEL_NOT_FOUND');throw e;}
  if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1||
    st.size<64*1024*1024||st.size>128*1024*1024)deny('MODEL_SIZE_UNEXPECTED');
  const data=await hashLocalFile(fp);
  if(data.sha256!==CANDIDATE.expected_sha256)deny('MODEL_SHA256_MISMATCH');
  return Object.freeze({status:'BINARY_HASH_VERIFIED_ONLY',
    model_id:CANDIDATE.onnx,onnx_sha256:data.sha256,onnx_bytes:data.size,
    network_calls:0,model_inference_verified:false,commercial_license_approved:false,
    customer_gold100_verified:false,ready_for_customer:false});
}
