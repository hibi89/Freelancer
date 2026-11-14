import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {CANDIDATE,hashLocalFile,preflightKoreanEmbedding} from '../enterprise/p85-korean-model-preflight.mjs';

function fixture(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-model-gate-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const dir=path.join(root,'model');fs.mkdirSync(path.join(dir,'onnx'),{recursive:true});
  return {root,dir};
}
test('asset verifier is restricted to exact candidate ONNX digest, no implicit acceptance',()=>{
  assert.match(CANDIDATE.expected_sha256,/^[a-f0-9]{64}$/);
  assert.equal(CANDIDATE.upstream,'intfloat/multilingual-e5-small');
  assert.equal(CANDIDATE.artifact,'onnx/model_int8.onnx');
  assert.notEqual(CANDIDATE.upstream_license_label,'COMMERCIAL_APPROVED');
});
test('streaming SHA verifier handles local synthetic bytes without network',async t=>{
  const {root}=fixture(t),p=path.join(root,'test.bin');
  const bytes=crypto.randomBytes(19181);fs.writeFileSync(p,bytes);
  const answer=await hashLocalFile(p);
  assert.deepEqual(answer,{sha256:crypto.createHash('sha256').update(bytes).digest('hex'),size:bytes.length});
});
test('rejects relative path, absent model and never performs an automatic download',async t=>{
  const {root}=fixture(t);
  await assert.rejects(()=>preflightKoreanEmbedding({modelDir:'.'}),{code:'ABSOLUTE_DIRECTORY_REQUIRED'});
  await assert.rejects(()=>preflightKoreanEmbedding({modelDir:path.join(root,'missing')}),{code:'MODEL_NOT_FOUND'});
});
test('rejects missing tokenizer metadata before touching any ONNX bytes',async t=>{
  const {dir}=fixture(t);
  fs.writeFileSync(path.join(dir,'onnx','model_int8.onnx'),Buffer.alloc(256));
  await assert.rejects(()=>preflightKoreanEmbedding({modelDir:dir}),{code:'MODEL_SUPPORT_MISSING'});
});
test('rejects a fake 118MB model fixture even if auxiliary metadata exists',async t=>{
  const {dir}=fixture(t);
  for(const item of ['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json'])
    fs.writeFileSync(path.join(dir,item),'{}');
  fs.writeFileSync(path.join(dir,'onnx','model_int8.onnx'),Buffer.from('not a real model'));
  await assert.rejects(()=>preflightKoreanEmbedding({modelDir:dir}),{code:'MODEL_SIZE_UNEXPECTED'});
});
test('rejects fake metadata with no readable JSON files, never counts as an accepted model',async t=>{
  const {dir}=fixture(t);
  for(const item of ['config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json'])
    fs.writeFileSync(path.join(dir,item),'');
  await assert.rejects(()=>preflightKoreanEmbedding({modelDir:dir}),{code:'MODEL_SUPPORT_UNSAFE'});
});
test('manual CLI has a bounded error path without remote activity',()=>{
  const script=fileURLToPath(new URL('../scripts/p85-korean-model-check.mjs',import.meta.url));
  const r=spawnSync(process.execPath,[script,'--model-dir','relative'],{encoding:'utf8',timeout:10000});
  assert.equal(r.status,1);assert.match(r.stderr,/ABSOLUTE_DIRECTORY_REQUIRED/);
  assert.doesNotMatch(r.stdout,/READY_FOR_CUSTOMER|COMMERCIAL_APPROVED/);
});
