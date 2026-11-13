import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
import {html,js,css} from '../enterprise/p85-ui.mjs';

const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const passwords={member:'SYNTHETIC_ONLY_member_supersecret',admin:'SYNTHETIC_ONLY_admin_supersecret',foreign:'SYNTHETIC_ONLY_foreign_supersecret'};
async function fixture(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'cv-library-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const sources=[
    ['corpA','public','반품은 7일 이내.','staff','quality','manuals',1],
    ['corpA','secret','비밀 정책 31일.','managers','security','restricted',3],
    ['corpB','other','타 조직 99일.','managers','security','restricted',3]
  ];
  for(const [tenant,id,txt] of sources){
    const p=path.join(root,tenant,id);fs.mkdirSync(p,{recursive:true});fs.writeFileSync(path.join(p,'v1.txt'),txt);
  }
  const docs=sources.map(([tenantId,id,txt,group,project,collection,classification])=>({
    tenantId,id,version:'v1',collection,groups:[group],projects:[project],classification,
    sha256:hash(txt),active:true,reviewState:'SYNTHETIC_APPROVED'
  }));
  const users=[
    createSyntheticAccount({userId:'member',tenantId:'corpA',groups:['staff'],projects:['quality'],clearance:1,password:passwords.member}),
    createSyntheticAccount({userId:'admin',tenantId:'corpA',groups:['staff','managers'],projects:['quality','security'],clearance:3,admin:true,password:passwords.admin}),
    createSyntheticAccount({userId:'foreign',tenantId:'corpB',groups:['managers'],projects:['security'],clearance:3,admin:true,password:passwords.foreign})
  ];
  const vault=new LocalSyntheticVault({root,accounts:users,documents:docs});
  const api=await launchSyntheticLoopback(vault);t.after(()=>api.close());
  const token=who=>vault.login(who,passwords[who]).token;
  const get=(tok,endpoint='/v1/library')=>fetch(api.baseUrl+endpoint,{headers:tok?{authorization:'Bearer '+tok}:{}});
  return {root,api,vault,token,get};
}
test('library refuses unauthenticated requests and never leaks metadata',async t=>{
  const f=await fixture(t);
  for(const tok of [null,'a'.repeat(64)]){
    const r=await f.get(tok);assert.equal(r.status,401);
    const data=await r.json();assert.equal(data.error,'UNAUTHENTICATED');
    assert.doesNotMatch(JSON.stringify(data),/corpA|corpB|secret|public/);
  }
});
test('member sees only documents authorized by tenant, group, project, clearance and active state',async t=>{
  const f=await fixture(t),tok=f.token('member'),response=await f.get(tok);
  assert.equal(response.status,200);assert.equal(response.headers.get('cache-control'),'no-store');
  const data=await response.json();
  assert.deepEqual(data.kpi,{accessible_documents:1,collections:1,generated_answers:0});
  assert.deepEqual(data.documents,[{id:'public',version:'v1',collection:'manuals',kind:'txt',classification:1}]);
  assert.deepEqual(data.collections,[{id:'manuals',count:1}]);
  assert.equal(data.status,'SCOPED_LIBRARY');
  assert.equal(data.network_calls,0);assert.equal(data.model_state,'UNAVAILABLE');
  assert.doesNotMatch(JSON.stringify(data),/secret|corpB|비밀 정책|반품은|[a-f0-9]{64}/);
});
test('admin sees only own tenant categories, never other tenant documents',async t=>{
  const f=await fixture(t),r=await f.get(f.token('admin'));assert.equal(r.status,200);
  const d=await r.json();
  assert.deepEqual(d.documents.map(v=>v.id),['public','secret']);
  assert.equal(d.kpi.collections,2);
  assert.equal(d.kpi.accessible_documents,2);
  assert.deepEqual(d.collections,[{id:'manuals',count:1},{id:'restricted',count:1}]);
  assert.doesNotMatch(JSON.stringify(d),/corpB|other|99일/);
});
test('admin cannot discover cross-tenant document count through aggregate API',async t=>{
  const f=await fixture(t),r=await f.get(f.token('foreign'));assert.equal(r.status,200);
  const d=await r.json();
  assert.deepEqual(d.documents.map(v=>v.id),['other']);assert.equal(d.kpi.accessible_documents,1);
  assert.doesNotMatch(JSON.stringify(d),/public|secret|corpA/);
});
test('revoke immediately prevents old bearer from viewing the library',async t=>{
  const f=await fixture(t),member=f.token('member'),admin=f.token('admin');
  assert.equal((await f.get(member)).status,200);
  assert.equal(f.vault.revokeAccount(admin,'member').status,'REVOKED');
  const response=await f.get(member);assert.equal(response.status,401);
  assert.deepEqual(await response.json(),{error:'UNAUTHENTICATED'});
});
test('document retirement removes its name before next catalog request',async t=>{
  const f=await fixture(t),token=f.token('admin');
  assert.equal((await (await f.get(token)).json()).kpi.accessible_documents,2);
  assert.equal(f.vault.retire(token,'secret').status,'RETIRED');
  const d=await (await f.get(token)).json();
  assert.equal(d.kpi.accessible_documents,1);assert.deepEqual(d.documents.map(x=>x.id),['public']);
});
test('scope change is applied to existing bearer on next catalog read',async t=>{
  const f=await fixture(t),member=f.token('member'),admin=f.token('admin');
  assert.equal((await (await f.get(member)).json()).kpi.accessible_documents,1);
  assert.equal(f.vault.changeUserAccess(admin,'member',{groups:['managers'],projects:['security'],clearance:3}).status,'USER_ACCESS_CHANGED');
  const d=await (await f.get(member)).json();
  assert.deepEqual(d.documents.map(x=>x.id),['secret']);
});
test('UI contains local-only visible KPI, chart, source selector and safe text rendering',()=>{
  assert.match(html,/id="library-kpis"/);assert.match(html,/id="library-chart"/);
  assert.match(html,/id="library-documents"/);assert.match(html,/id="refresh-library"/);
  assert.match(js,/readOnly\('\/v1\/library'\)/);assert.match(js,/textContent='문서 선택'/);
  assert.match(js,/replaceChildren/);assert.doesNotMatch(js,/innerHTML|localStorage|sessionStorage|sendBeacon|new WebSocket/);
  assert.doesNotThrow(()=>new vm.Script(js,{filename:'citevault-ui.js'}));
  assert.match(css,/\.meter/);
});
