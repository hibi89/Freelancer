import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {buildPortable} from '../scripts/p85-portable-build.mjs';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const run=(command,args,opts={})=>{
  const result=spawnSync(command,args,{encoding:'utf8',timeout:120000,...opts});
  if(result.error)throw result.error;
  assert.equal(result.status,0,JSON.stringify({command,status:result.status,
    stdout:result.stdout?.slice(-1500),stderr:result.stderr?.slice(-1500)}));
  return result;
};

test('Windows synthetic-only portable package creates with exact digests, no secrets and no overwrite',t=>{
  if(process.platform!=='win32'){t.skip('Windows-only packaging');return;}
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'cv-zip-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const bundle=path.join(root,'bundle');
  const result=buildPortable({destination:bundle});
  assert.deepEqual({status:result.status,release_approved:result.release_approved,network_calls:result.network_calls},
    {status:'SYNTHETIC_PORTABLE_CREATED',release_approved:false,network_calls:0});
  const manifest=JSON.parse(fs.readFileSync(path.join(bundle,'manifest.json'),'utf8'));
  assert.equal(manifest.format,'CITEVAULT_P85_SYNTHETIC_PORTABLE_V1');
  assert.equal(manifest.customer_release_approved,false);
  assert.ok(manifest.files.length>=10);
  for(const record of manifest.files){
    const bytes=fs.readFileSync(path.join(bundle,...record.path.split('/')));
    assert.equal(bytes.length,record.size,record.path);
    assert.equal(sha(bytes),record.sha256,record.path);
    assert.doesNotMatch(record.path,/secret|token|\.env|customer/i);
  }
  assert.match(fs.readFileSync(path.join(bundle,'NOTICE.txt'),'utf8'),/SYNTHETIC TEST BUILD ONLY/);
  assert.throws(()=>buildPortable({destination:bundle}),{code:'DESTINATION_EXISTS'});
  const archive=path.join(root,'citevault-p85-qa.zip');
  const unpack=path.join(root,'restored');
  const quote=s=>"'"+s.replace(/'/g,"''")+"'";
  run('powershell.exe',['-NoProfile','-NonInteractive','-Command',
    'Compress-Archive -Path '+quote(path.join(bundle,'*'))+' -DestinationPath '+
      quote(archive)+' -CompressionLevel Optimal -Force']);
  assert.ok(fs.statSync(archive).size>1_000_000);
  run('powershell.exe',['-NoProfile','-NonInteractive','-Command',
    'Expand-Archive -LiteralPath '+quote(archive)+' -DestinationPath '+quote(unpack)]);
  for(const record of manifest.files){
    const bytes=fs.readFileSync(path.join(unpack,...record.path.split('/')));
    assert.equal(sha(bytes),record.sha256,'restored ZIP '+record.path);
  }
  // Execute the exact unpacked Node binary and UI+state+ACL startup self-test.
  const exec=run(path.join(unpack,'runtime','node.exe'),
    [path.join(unpack,'scripts','p85-operator-demo.mjs'),'--self-test'],{cwd:unpack});
  const output=JSON.parse(exec.stdout.trim());
  assert.equal(output.status,'PASS');assert.equal(output.offline,true);
  assert.equal(output.operator,true);assert.equal(output.user_provision,true);
  assert.equal(output.revoke,true);assert.equal(output.remote_calls,0);
  const launcher=fs.readFileSync(path.join(unpack,'Start-CITEVAULT-Synthetic.cmd'),'utf8');
  assert.match(launcher,/node\.exe/);assert.match(launcher,/p85-operator-demo\.mjs/);
  t.diagnostic(JSON.stringify({status:'WINDOWS_HOSTED_PORTABLE_QA_PASS',
    runtime_node:manifest.node_version,files:manifest.files.length,
    archive_sha256:sha(fs.readFileSync(archive)),archive_bytes:fs.statSync(archive).size,
    retail_release:false,customer_win10_11:false}));
});
test('portable builder rejects unsafe and existing root destinations',t=>{
  if(process.platform!=='win32'){t.skip('Windows-only');return;}
  assert.throws(()=>buildPortable({destination:process.cwd()}),{code:'DESTINATION_EXISTS'});
  assert.throws(()=>buildPortable({destination:path.parse(process.cwd()).root}),{code:'UNSAFE_DEST'});
});
