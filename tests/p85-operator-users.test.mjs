import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {SyntheticVaultStateStore} from '../enterprise/p85-state-store.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const ownerPass='synthetic-local-admin-access-2026';
const p1='operator-employee-strong-pass';
const p2='operator-newcomer-strong-pass';
function setup(t){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-operator-'));

 const dirs=[['tenantA','policy','staff','quality','반품 신청은 7일 이내 가능합니다.'],
   ['tenantA','sealed','management','audit','내부 전용 규정은 14일 이내 가능합니다.'],
   ['tenantB','foreign','staff','quality','다른 조직 비밀정보입니다.']];
 const docs=dirs.map(([tenantId,id,group,project,body])=>{
   const folder=path.join(root,tenantId,id);fs.mkdirSync(folder,{recursive:true});
   fs.writeFileSync(path.join(folder,'v1.txt'),body);
   return {tenantId,id,version:'v1',collection:'policies',groups:[group],projects:[project],
     classification:1,active:true,reviewState:'SYNTHETIC_APPROVED',sha256:digest(Buffer.from(body))};
 });
 const accounts=[
 createSyntheticAccount({userId:'adminA',tenantId:'tenantA',groups:['staff','management'],projects:['quality','audit'],clearance:3,admin:true,password:ownerPass}),
 createSyntheticAccount({userId:'employee',tenantId:'tenantA',groups:['staff'],projects:['quality'],clearance:1,password:p1}),
 createSyntheticAccount({userId:'adminB',tenantId:'tenantB',groups:['staff'],projects:['quality'],clearance:3,admin:true,password:ownerPass})];
 const stores=[];const clients=[];
 const spawn=()=>{const store=new SyntheticVaultStateStore({root});stores.push(store);
   const vault=new LocalSyntheticVault({root,accounts,documents:docs,stateStore:store});clients.push(vault);return vault;};
 t.after(()=>{for(const s of stores)s.close();fs.rmSync(root,{recursive:true,force:true});});
 return {root,spawn,accounts,docs};
}
const scope=(groups=['staff'],projects=['quality'],clearance=1)=>({groups,projects,clearance});
test('local operator user provisioning, persistence and instant role enforcement',async t=>{
 const e=setup(t),v=e.spawn(),admin=v.login('adminA',ownerPass).token;
 await t.test('provision bounded non-admin account with scrypt verifier only',()=>{
   const r=v.provisionUser(admin,{userId:'newcomer',password:p2,...scope()});
   assert.equal(r.status,'USER_CREATED');assert.equal(r.tenant_id,'tenantA');
   assert.equal(v.login('newcomer',p2).token.length,64);
   const raw=fs.readFileSync(path.join(e.root,'citevault-synthetic-state.sqlite'));
   assert.equal(raw.includes(Buffer.from(p2)),false);
 });
 await t.test('a second process can authenticate the newly provisioned account',()=>{
   const v2=e.spawn(),s=v2.login('newcomer',p2).token;
   assert.equal(v2.source(s,'policy').citations.length,1);
   assert.throws(()=>v2.source(s,'sealed'),{code:'NOT_FOUND'});
 });
 await t.test('already-issued sessions lose access immediately after owner role update, even across clients',()=>{
   const v2=e.spawn(),session=v2.login('newcomer',p2).token;
   assert.ok(v2.source(session,'policy').citations.length>0);
   assert.equal(v.changeUserAccess(admin,'newcomer',scope(['management'],['audit'])).status,'USER_ACCESS_CHANGED');
   assert.throws(()=>v2.source(session,'policy'),{code:'NOT_FOUND'});
   assert.ok(v2.source(session,'sealed').citations.length>0);
 });
 await t.test('restarted store refuses malicious reseeding to replace privileged existing user',()=>{
   const v3=e.spawn(),s=v3.login('newcomer',p2).token;
   assert.ok(v3.source(s,'sealed').citations.length>0);
   assert.throws(()=>v3.source(s,'policy'),{code:'NOT_FOUND'});
 });
 await t.test('owner revocation instantly invalidates all sessions across processes',()=>{
   const v2=e.spawn(),session=v2.login('newcomer',p2).token;
   assert.equal(v.revokeAccount(admin,'newcomer').status,'REVOKED');
   assert.throws(()=>v2.source(session,'sealed'),{code:'UNAUTHENTICATED'});
   assert.throws(()=>v2.login('newcomer',p2),{code:'ACCESS_DENIED'});
 });
 await t.test('reprovisioning a previously revoked user is forbidden',()=>{
   assert.throws(()=>v.provisionUser(admin,{userId:'newcomer',password:p2,...scope()}),{code:'USER_EXISTS'});
 });
 await t.test('audit log shows successful admin provisioning, change and revocation only inside tenant',()=>{
   const log=v.audit(admin).map(e=>e.event);
   for(const event of ['USER_CREATED','USER_ACCESS_CHANGED','USER_REVOKED'])assert.ok(log.includes(event));
   const b=v.login('adminB',ownerPass).token;
   assert.ok(v.audit(b).every(x=>!['USER_CREATED','USER_ACCESS_CHANGED','USER_REVOKED'].includes(x.event)));
 });
});
test('tenant and privilege boundaries for user administration',t=>{
 const e=setup(t),v=e.spawn(),a=v.login('adminA',ownerPass).token,
   b=v.login('adminB',ownerPass).token,member=v.login('employee',p1).token;
 assert.throws(()=>v.provisionUser(member,{userId:'rogue',password:p2,...scope()}),{code:'NOT_AUTHORIZED'});
 assert.throws(()=>v.changeUserAccess(member,'employee',scope()),{code:'NOT_AUTHORIZED'});
 assert.throws(()=>v.provisionUser(b,{userId:'employee',password:p2,...scope()}),{code:'USER_EXISTS'});
 assert.throws(()=>v.changeUserAccess(a,'adminB',scope()),{code:'NOT_FOUND'});
 assert.throws(()=>v.changeUserAccess(a,'adminA',scope()),{code:'NOT_FOUND'});
 assert.throws(()=>v.changeUserAccess(a,'employee',scope(['management','ungranted'],['quality'])),{code:'ACCOUNT_SCOPE_INVALID'});
 assert.throws(()=>v.changeUserAccess(a,'employee',scope(['staff'],['quality'],4)),{code:'ACCOUNT_SCOPE_INVALID'});
 assert.throws(()=>v.provisionUser(a,{userId:'guest',password:'short',...scope()}),{code:'ACCOUNT_INVALID'});
 assert.throws(()=>v.provisionUser(a,{userId:'guest',password:p2,...scope([],['quality'])}),{code:'ACCOUNT_SCOPE_INVALID'});
 assert.throws(()=>v.provisionUser(a,{userId:'guest',password:p2,...scope(['staff'],[])}),{code:'ACCOUNT_SCOPE_INVALID'});
 const x=v.provisionUser(a,{userId:'guest',password:p2,...scope()});assert.equal(x.status,'USER_CREATED');
 assert.throws(()=>v.provisionUser(a,{userId:'guest',password:p2,...scope()}),{code:'USER_EXISTS'});
 assert.throws(()=>v.changeUserAccess(b,'guest',scope()),{code:'NOT_FOUND'});
});
test('localhost real HTTP operator provisioning and permission change with isolation',async t=>{
 const e=setup(t),v=e.spawn(),api=await launchSyntheticLoopback(v);t.after(()=>api.close());
 const owner=v.login('adminA',ownerPass).token,member=v.login('employee',p1).token;
 async function call(route,token,request){return fetch(api.baseUrl+route,{method:'POST',headers:{authorization:'Bearer '+token,'content-type':'application/json'},body:JSON.stringify(request)});}
 let res=await call('/v1/admin/provision',member,{userId:'webuser',password:p2,...scope()});assert.equal(res.status,403);
 res=await call('/v1/admin/provision',owner,{userId:'webuser',password:p2,...scope()});
 assert.equal(res.status,201);assert.equal((await res.json()).status,'USER_CREATED');
 const user=v.login('webuser',p2).token;
 res=await call('/v1/admin/access',owner,{userId:'webuser',...scope(['management'],['audit'])});
 assert.equal(res.status,200);assert.equal((await res.json()).status,'USER_ACCESS_CHANGED');
 res=await fetch(api.baseUrl+'/v1/source/policy',{headers:{authorization:'Bearer '+user}});assert.equal(res.status,404);
 res=await fetch(api.baseUrl+'/v1/source/sealed',{headers:{authorization:'Bearer '+user}});assert.equal(res.status,200);
 res=await call('/v1/admin/provision',owner,{userId:'webuser',password:p2,...scope()});assert.equal(res.status,409);
});
