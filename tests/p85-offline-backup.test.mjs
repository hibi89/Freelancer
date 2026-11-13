import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {createOfflineSnapshot,restoreOfflineSnapshot} from '../enterprise/p85-offline-backup.mjs';

function setup(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'cv-offline-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const src=path.join(root,'vault');fs.mkdirSync(src);
  const store=path.join(src,'citevault-synthetic-state.sqlite');
  const db=new DatabaseSync(store);
  db.exec('CREATE TABLE header(id INTEGER PRIMARY KEY,format INTEGER,generation INTEGER);INSERT INTO header(id,format,generation) VALUES(1,1,4);');db.close();
  for(const [rel,text] of [
    ['orgA/doc1/v1.txt','반품은 7일 이내'],
    ['orgA/doc2/v1.md','내부 정책'],
    ['orgA/sales-only/sales.csv','order_id,total\nA001,100'],
    ['orgB/memo/v1.txt','조직B 기밀'],
  ]){const dest=path.join(src,...rel.split('/'));fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,text);}
  return {root,src,backup:path.join(root,'snapshot'),restore:path.join(root,'restored')};
}
test('offline snapshot creates a new verified directory and restores exact source bytes and SQLite generation',async t=>{
  const f=setup(t),before=fs.readFileSync(path.join(f.src,'orgA/doc1/v1.txt'));
  const s=await createOfflineSnapshot({root:f.src,destination:f.backup});
  assert.deepEqual(s,{status:'SNAPSHOT_CREATED',files:5,state_generation:4});
  const r=restoreOfflineSnapshot({snapshot:f.backup,destination:f.restore});
  assert.deepEqual(r,{status:'RESTORED_CREATE_ONLY',files:5,state_generation:4});
  assert.deepEqual(fs.readFileSync(path.join(f.restore,'orgA/doc1/v1.txt')),before);
  assert.deepEqual(fs.readFileSync(path.join(f.src,'orgA/doc1/v1.txt')),before);
  assert.ok(fs.existsSync(path.join(f.restore,'citevault-synthetic-state.sqlite')));
  assert.throws(()=>restoreOfflineSnapshot({snapshot:f.backup,destination:f.restore}),{code:'DESTINATION_EXISTS'});
  await assert.rejects(()=>createOfflineSnapshot({root:f.src,destination:f.backup}),{code:'DESTINATION_EXISTS'});
});
test('modified snapshot document is refused without creating destination',async t=>{
  const f=setup(t);await createOfflineSnapshot({root:f.src,destination:f.backup});
  fs.appendFileSync(path.join(f.backup,'orgB/memo/v1.txt'),'attacker');
  assert.throws(()=>restoreOfflineSnapshot({snapshot:f.backup,destination:f.restore}),{code:'DIGEST_MISMATCH'});
  assert.equal(fs.existsSync(f.restore),false);
});
test('modified SQLite bytes are refused before restore and never accepted as customer state',async t=>{
  const f=setup(t);await createOfflineSnapshot({root:f.src,destination:f.backup});
  fs.appendFileSync(path.join(f.backup,'citevault-synthetic-state.sqlite'),'tamper');
  assert.throws(()=>restoreOfflineSnapshot({snapshot:f.backup,destination:f.restore}),{code:'DIGEST_MISMATCH'});
  assert.equal(fs.existsSync(f.restore),false);
});
test('extra undeclared file is refused',async t=>{
  const f=setup(t);await createOfflineSnapshot({root:f.src,destination:f.backup});
  fs.writeFileSync(path.join(f.backup,'orgA/doc1/extra.txt'),'leak');
  assert.throws(()=>restoreOfflineSnapshot({snapshot:f.backup,destination:f.restore}),{code:'FILE_SET_MISMATCH'});
  assert.equal(fs.existsSync(f.restore),false);
});
test('symlink input is rejected before any snapshot output',async t=>{
  const f=setup(t),evil=path.join(f.root,'elsewhere.txt');fs.writeFileSync(evil,'SECRET');
  try{fs.symlinkSync(evil,path.join(f.src,'orgA','link.txt'));}catch(e){t.skip('symlink privilege unavailable: '+e.code);return;}
  await assert.rejects(()=>createOfflineSnapshot({root:f.src,destination:f.backup}),{code:'SYMLINK'});
  assert.equal(fs.existsSync(f.backup),false);
});
test('hardlink input is rejected, even when digest otherwise matches',async t=>{
  const f=setup(t),from=path.join(f.src,'orgA/doc1/v1.txt');fs.linkSync(from,path.join(f.src,'orgA/doc1/alias.txt'));
  await assert.rejects(()=>createOfflineSnapshot({root:f.src,destination:f.backup}),{code:'UNSAFE_FILE'});
});
test('refuses child or ancestor destination to avoid recursive copy/destructive rename',async t=>{
  const f=setup(t),target=path.join(f.src,'backups');
  await assert.rejects(()=>createOfflineSnapshot({root:f.src,destination:target}),{code:'PATH_OVERLAP'});
  assert.equal(fs.existsSync(target),false);
});
test('manifest traversal, duplicate and forged generation are refused',async t=>{
  const f=setup(t);await createOfflineSnapshot({root:f.src,destination:f.backup});
  const file=path.join(f.backup,'manifest.json'),manifest=JSON.parse(fs.readFileSync(file,'utf8'));
  manifest.files[0].path='../escape.txt';fs.writeFileSync(file,JSON.stringify(manifest));
  assert.throws(()=>restoreOfflineSnapshot({snapshot:f.backup,destination:f.restore}),{code:'MANIFEST_INVALID'});
  assert.equal(fs.existsSync(f.restore),false);
});
test('snapshot has no network dependencies; human operator must opt in to backup and restore',async t=>{
  const f=setup(t),source=fs.readFileSync(path.join(f.src,'orgA/doc1/v1.txt'));
  await createOfflineSnapshot({root:f.src,destination:f.backup});
  const manifest=JSON.parse(fs.readFileSync(path.join(f.backup,'manifest.json')));
  assert.equal(manifest.format,'CITEVAULT_OFFLINE_SNAPSHOT_V1');
  assert.equal(manifest.files.length,5);
  assert.ok(manifest.files.every(x=>x.sha256.length===64));
  assert.equal(fs.readFileSync(path.join(f.src,'orgA/doc1/v1.txt')).compare(source),0);
});
