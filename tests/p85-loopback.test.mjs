import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
async function setup(t){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-http-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const records=[['org1','public1','반품 신청 7일 이내 가능합니다.'],
   ['org1','hidden1','기밀 인사정보 55일 내 처리'],
   ['org2','other1','조직2 독점 기밀 99일 내 처리']];
 for(const [tenant,id,txt] of records){const dir=path.join(root,tenant,id);
   fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(path.join(dir,'v1.txt'),txt);}
 const users=[
   createSyntheticAccount({userId:'alice',tenantId:'org1',groups:['staff'],projects:['p1'],clearance:1,password:'TEST_ONLY_PASS_ALICE_123'}),
   createSyntheticAccount({userId:'admin1',tenantId:'org1',groups:['staff','hr'],projects:['p1'],clearance:3,admin:true,password:'TEST_ONLY_PASS_ADMIN_123'}),
   createSyntheticAccount({userId:'admin2',tenantId:'org2',groups:['admin'],projects:['p2'],clearance:3,admin:true,password:'TEST_ONLY_PASS_OTHER_123'})
 ];
 const docs=records.map(([tenant,id,txt])=>({id,tenantId:tenant,
   groups:id==='hidden1'?['hr']:id==='other1'?['admin']:['staff'],
   projects:[tenant==='org1'?'p1':'p2'],classification:id==='public1'?1:3,
   collection:'synthetic',version:'v1',sha256:sha(txt),active:true,reviewState:'SYNTHETIC_APPROVED'}));
 const vault=new LocalSyntheticVault({root,accounts:users,documents:docs});
 const api=await launchSyntheticLoopback(vault);t.after(()=>api.close());
 const req=async (method,url,data,token)=>{
   const res=await fetch(api.baseUrl+url,{method,headers:{'content-type':'application/json',
     ...(token?{authorization:'Bearer '+token}:{})},body:data===undefined?undefined:JSON.stringify(data)});
   return {status:res.status,body:await res.json(),headers:res.headers};
 };
 const login=async(userId,password)=>{const r=await req('POST','/v1/login',{userId,password});
   assert.equal(r.status,200);return r.body.token;};
 return {api,req,login,root};
}
test('HTTP launch binds IPv4 loopback only',async t=>{
 const f=await setup(t);assert.match(f.api.baseUrl,/^http:\/\/127\.0\.0\.1:\d+$/);
});
test('HTTP missing bearer rejects source with 401 and no original bytes',async t=>{
 const f=await setup(t),r=await f.req('GET','/v1/source/public1');
 assert.equal(r.status,401);assert.deepEqual(r.body,{error:'UNAUTHENTICATED'});
});
test('HTTP invalid credential rejects login without hash disclosure',async t=>{
 const f=await setup(t),r=await f.req('POST','/v1/login',{userId:'alice',password:'wrong'});
 assert.equal(r.status,401);assert.doesNotMatch(JSON.stringify(r.body),/scrypt|TEST_ONLY_PASS/);
});
test('HTTP authenticated source returns valid citation with no filesystem path',async t=>{
 const f=await setup(t),token=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 const r=await f.req('GET','/v1/source/public1',undefined,token);
 assert.equal(r.status,200);assert.equal(r.body.citations[0].document_id,'public1');
 assert.doesNotMatch(JSON.stringify(r.body),/citevault-http-|\/tmp\//);
});
test('HTTP forbidden and missing source share 404 response',async t=>{
 const f=await setup(t),token=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 const one=await f.req('GET','/v1/source/hidden1',undefined,token);
 const two=await f.req('GET','/v1/source/nonexistent',undefined,token);
 const three=await f.req('GET','/v1/source/other1',undefined,token);
 assert.equal(one.status,404);assert.deepEqual(one,two);assert.deepEqual(two,three);
});
test('HTTP unauthorized mixed scope refuses entire query',async t=>{
 const f=await setup(t),token=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 const r=await f.req('POST','/v1/search',{question:'반품',documentIds:['public1','hidden1']},token);
 assert.equal(r.status,404);assert.deepEqual(r.body,{error:'NOT_FOUND'});
});
test('HTTP search no model fallback returns only cited text',async t=>{
 const f=await setup(t),token=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 const r=await f.req('POST','/v1/search',{question:'반품 신청',documentIds:['public1']},token);
 assert.equal(r.status,200);assert.equal(r.body.answer,null);
 assert.equal(r.body.model_state,'UNAVAILABLE');assert.equal(r.body.network_calls,0);
 assert.ok(r.body.evidence.every(x=>x.document_id==='public1'));
});
test('HTTP non-admin cannot reindex or retire',async t=>{
 const f=await setup(t),token=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 const r=await f.req('POST','/v1/admin/reindex',{},token);
 assert.equal(r.status,403);assert.equal(r.body.error,'NOT_AUTHORIZED');
 const z=await f.req('POST','/v1/admin/retire',{documentId:'public1'},token);
 assert.equal(z.status,403);
});
test('HTTP admin retire immediately revokes source but preserves disk bytes',async t=>{
 const f=await setup(t),token=await f.login('admin1','TEST_ONLY_PASS_ADMIN_123');
 const file=path.join(f.root,'org1/public1/v1.txt'),before=fs.readFileSync(file);
 const r=await f.req('POST','/v1/admin/retire',{documentId:'public1'},token);
 assert.equal(r.status,200);assert.equal(r.body.status,'RETIRED');
 const after=await f.req('GET','/v1/source/public1',undefined,token);
 assert.equal(after.status,404);assert.deepEqual(fs.readFileSync(file),before);
});
test('HTTP admin of other tenant cannot retire foreign document',async t=>{
 const f=await setup(t),token=await f.login('admin2','TEST_ONLY_PASS_OTHER_123');
 const r=await f.req('POST','/v1/admin/retire',{documentId:'public1'},token);
 assert.equal(r.status,404);
});
test('HTTP logout expires bearer immediately',async t=>{
 const f=await setup(t),token=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 assert.equal((await f.req('POST','/v1/logout',{},token)).status,200);
 assert.equal((await f.req('GET','/v1/source/public1',undefined,token)).status,401);
});
test('HTTP malformed JSON gets 422 no stack trace or filesystem data',async t=>{
 const f=await setup(t),r=await fetch(f.api.baseUrl+'/v1/login',{method:'POST',
   headers:{'content-type':'application/json'},body:'{"userId":'});
 assert.equal(r.status,422);const x=await r.text();
 assert.doesNotMatch(x,/Error:|node:internal|citevault-http-/);
});
test('HTTP unsupported URL 404 and no cookies/CORS headers',async t=>{
 const f=await setup(t),r=await fetch(f.api.baseUrl+'/v1/secret',{method:'GET'});
 assert.equal(r.status,404);assert.equal(r.headers.get('access-control-allow-origin'),null);
 assert.equal(r.headers.get('set-cookie'),null);assert.equal(r.headers.get('cache-control'),'no-store');
});

test('HTTP rejects text/plain JSON before attempting login or mutations',async t=>{
 const f=await setup(t),r=await fetch(f.api.baseUrl+'/v1/login',{method:'POST',
   headers:{'content-type':'text/plain'},body:JSON.stringify({userId:'alice',password:'TEST_ONLY_PASS_ALICE_123'})});
 assert.equal(r.status,415);assert.deepEqual(await r.json(),{error:'JSON_REQUIRED'});
});
test('HTTP refuses oversize bodies with 413, no parser or path leakage',async t=>{
 const f=await setup(t),r=await fetch(f.api.baseUrl+'/v1/login',{method:'POST',
   headers:{'content-type':'application/json'},body:JSON.stringify({userId:'alice',password:'X'.repeat(5000)})});
 assert.equal(r.status,413);assert.deepEqual(await r.json(),{error:'PAYLOAD_TOO_LARGE'});
});

test('HTTP admin revocation invalidates issued bearer on next request',async t=>{
 const f=await setup(t),alice=await f.login('alice','TEST_ONLY_PASS_ALICE_123');
 const admin=await f.login('admin1','TEST_ONLY_PASS_ADMIN_123');
 const r=await f.req('POST','/v1/admin/revoke',{userId:'alice'},admin);
 assert.equal(r.status,200);assert.equal(r.body.status,'REVOKED');
 assert.equal((await f.req('GET','/v1/source/public1',undefined,alice)).status,401);
 assert.equal((await f.req('POST','/v1/login',{userId:'alice',password:'TEST_ONLY_PASS_ALICE_123'})).status,401);
});
test('HTTP foreign admin cannot revoke another tenant employee',async t=>{
 const f=await setup(t),admin=await f.login('admin2','TEST_ONLY_PASS_OTHER_123');
 const r=await f.req('POST','/v1/admin/revoke',{userId:'alice'},admin);
 assert.equal(r.status,404);
});
