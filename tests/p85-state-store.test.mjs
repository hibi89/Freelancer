import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {SyntheticVaultStateStore} from '../enterprise/p85-state-store.mjs';

const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const login=(vault,id,pw)=>vault.login(id,pw).token;
function fixture(t){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-durable-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const sources={
  'orgA/public/v1.txt':'반품 신청은 7일 이내 가능합니다.\n',
  'orgA/public/v2.txt':'반품 신청은 14일 이내 가능합니다.\n',
  'orgA/secret/v1.txt':'기밀 정책 외부반출 금지.\n',
  'orgB/foreign/v1.txt':'기업 B 독점 기술 외부반출 금지.\n'
 };
 for(const [name,contents] of Object.entries(sources)){const p=path.join(root,name);
   fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,contents);}
 const accounts=[
  createSyntheticAccount({userId:'alice',tenantId:'orgA',groups:['staff'],projects:['p1'],clearance:1,password:'durable_ALICE_secret123'}),
  createSyntheticAccount({userId:'adminA',tenantId:'orgA',groups:['staff','managers'],projects:['p1'],clearance:3,admin:true,password:'durable_ADM_A_secret123'}),
  createSyntheticAccount({userId:'adminB',tenantId:'orgB',groups:['directors'],projects:['p2'],clearance:3,admin:true,password:'durable_ADM_B_secret123'})
 ];
 const docs=[
  {tenantId:'orgA',id:'public',version:'v1',groups:['staff'],projects:['p1'],classification:1,collection:'policy',active:true,reviewState:'SYNTHETIC_APPROVED',sha256:sha(sources['orgA/public/v1.txt'])},
  {tenantId:'orgA',id:'secret',version:'v1',groups:['managers'],projects:['p1'],classification:3,collection:'restricted',active:true,reviewState:'SYNTHETIC_APPROVED',sha256:sha(sources['orgA/secret/v1.txt'])},
  {tenantId:'orgB',id:'foreign',version:'v1',groups:['directors'],projects:['p2'],classification:3,collection:'secret',active:true,reviewState:'SYNTHETIC_APPROVED',sha256:sha(sources['orgB/foreign/v1.txt'])}
 ];
 const stores=[];
 t.after(()=>{for(const s of stores)try{s.close();}catch{}});
 const open=(a=accounts,d=docs)=>{
   const store=new SyntheticVaultStateStore({root});stores.push(store);
   return {store,vault:new LocalSyntheticVault({root,accounts:a,documents:d,stateStore:store})};
 };
 return {root,sources,accounts,docs,open};
}
test('restart preserves durable exact source version and safe password hashes',t=>{
 const f=fixture(t),one=f.open();
 const admin=login(one.vault,'adminA','durable_ADM_A_secret123');
 one.vault.replaceVersion(admin,'public','v2',sha(f.sources['orgA/public/v2.txt']));
 one.store.close();
 const two=f.open();const a=login(two.vault,'alice','durable_ALICE_secret123');
 const r=two.vault.source(a,'public');assert.equal(r.citations[0].version,'v2');
 assert.match(r.citations[0].quote,/14일/);
 const file=fs.readFileSync(path.join(f.root,'citevault-synthetic-state.sqlite'));
 assert.equal(file.includes(Buffer.from('durable_ALICE_secret123')),false);
 assert.equal(file.includes(Buffer.from(f.sources['orgA/public/v2.txt'])),false);
});
test('retired document stays inaccessible after restart, even to admin',t=>{
 const f=fixture(t),one=f.open();
 one.vault.retire(login(one.vault,'adminA','durable_ADM_A_secret123'),'public');
 one.store.close();const two=f.open();
 assert.throws(()=>two.vault.source(login(two.vault,'adminA','durable_ADM_A_secret123'),'public'),{code:'NOT_FOUND'});
 assert.equal(fs.readFileSync(path.join(f.root,'orgA/public/v1.txt'),'utf8'),f.sources['orgA/public/v1.txt']);
});
test('reopening with malicious injected accounts and documents never reseeds privileges',t=>{
 const f=fixture(t),first=f.open();first.store.close();
 const forged=createSyntheticAccount({userId:'intruder',tenantId:'orgA',groups:['managers'],projects:['p1'],clearance:3,admin:true,password:'durable_FORGED_secret123'});
 const second=f.open([forged],[{...f.docs[0],groups:['managers'],classification:3}]);
 assert.throws(()=>second.vault.login('intruder','durable_FORGED_secret123'),{code:'ACCESS_DENIED'});
 assert.equal(second.vault.source(login(second.vault,'alice','durable_ALICE_secret123'),'public').status,'SOURCE_ONLY');
});
test('admin revocation disables live session and persists through restart',t=>{
 const f=fixture(t),one=f.open(),a=login(one.vault,'alice','durable_ALICE_secret123');
 const admin=login(one.vault,'adminA','durable_ADM_A_secret123');
 assert.equal(one.vault.revokeAccount(admin,'alice').status,'REVOKED');
 assert.throws(()=>one.vault.source(a,'public'),{code:'UNAUTHENTICATED'});
 one.store.close();const two=f.open();
 assert.throws(()=>two.vault.login('alice','durable_ALICE_secret123'),{code:'ACCESS_DENIED'});
});
test('other-tenant admin cannot revoke foreign employee',t=>{
 const f=fixture(t),one=f.open(),b=login(one.vault,'adminB','durable_ADM_B_secret123');
 assert.throws(()=>one.vault.revokeAccount(b,'alice'),{code:'NOT_FOUND'});
 assert.equal(one.vault.source(login(one.vault,'alice','durable_ALICE_secret123'),'public').status,'SOURCE_ONLY');
});
test('cross-instance account disable invalidates existing bearer before source read',t=>{
 const f=fixture(t),one=f.open(),two=f.open(),session=login(two.vault,'alice','durable_ALICE_secret123');
 one.vault.revokeAccount(login(one.vault,'adminA','durable_ADM_A_secret123'),'alice');
 assert.throws(()=>two.vault.source(session,'public'),{code:'UNAUTHENTICATED'});
});
test('cross-instance retire immediately blocks source and search',t=>{
 const f=fixture(t),one=f.open(),two=f.open(),user=login(two.vault,'alice','durable_ALICE_secret123');
 one.vault.retire(login(one.vault,'adminA','durable_ADM_A_secret123'),'public');
 assert.throws(()=>two.vault.source(user,'public'),{code:'NOT_FOUND'});
 assert.throws(()=>two.vault.search(user,'반품',{documentIds:['public']}),{code:'NOT_FOUND'});
});
test('durable generation rejects stale concurrent write rather than overwriting',t=>{
 const f=fixture(t),one=f.open(),two=f.open();
 one.vault.reindex(login(one.vault,'adminA','durable_ADM_A_secret123'));
 assert.throws(()=>two.vault.reindex(login(two.vault,'adminA','durable_ADM_A_secret123')),{code:'STALE_GENERATION'});
});
test('audit events persist after restart and isolate across tenants',t=>{
 const f=fixture(t),one=f.open(),alice=login(one.vault,'alice','durable_ALICE_secret123');
 one.vault.search(alice,'반품',{documentIds:['public']});one.store.close();
 const two=f.open(),a=login(two.vault,'adminA','durable_ADM_A_secret123');
 const b=login(two.vault,'adminB','durable_ADM_B_secret123');
 assert.match(JSON.stringify(two.vault.audit(a)),/SEARCH/);
 assert.doesNotMatch(JSON.stringify(two.vault.audit(b)),/SEARCH|orgA|public/);
 assert.doesNotMatch(JSON.stringify(two.vault.audit(a)),/durable_ALICE|citevault-durable-|반품/);
});
test('store refuses symlink database rather than following it',t=>{
 const f=fixture(t),outside=path.join(f.root,'outside.txt'),db=path.join(f.root,'citevault-synthetic-state.sqlite');
 fs.writeFileSync(outside,'do not use');
 try{fs.symlinkSync(outside,db);}catch(e){return t.skip(e.code);}
 assert.throws(()=>new SyntheticVaultStateStore({root:f.root}),{code:'DATABASE_UNSAFE'});
});
test('duplicate seed is transactional and does not create half-registered vault',t=>{
 const f=fixture(t),store=new SyntheticVaultStateStore({root:f.root});
 assert.throws(()=>store.loadOrInitialize({accounts:[f.accounts[0],f.accounts[0]],documents:f.docs}),{code:'TRANSACTION_FAILED'});
 const out=store.loadOrInitialize({accounts:f.accounts,documents:f.docs});
 assert.equal(out.accounts.length,3);store.close();
});
test('read after persistence store close fails rather than silently falling back',t=>{
 const f=fixture(t),one=f.open(),user=login(one.vault,'alice','durable_ALICE_secret123');
 one.store.close();
 assert.throws(()=>one.vault.source(user,'public'));
});
