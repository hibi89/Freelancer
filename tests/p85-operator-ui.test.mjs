import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
import {html,js,css} from '../enterprise/p85-ui.mjs';
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const pass='UI_TEST_SYNTHETIC_LOCAL_OWNER_2026';
async function fixture(t){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-ui-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 fs.mkdirSync(path.join(root,'tenantA','policy'),{recursive:true});
 fs.writeFileSync(path.join(root,'tenantA','policy','v1.txt'),'반품 신청 7일 이내 가능합니다.');
 const owner=createSyntheticAccount({userId:'owner',tenantId:'tenantA',groups:['staff'],projects:['quality'],clearance:3,admin:true,password:pass});
 const doc={tenantId:'tenantA',id:'policy',version:'v1',collection:'policies',groups:['staff'],projects:['quality'],classification:1,active:true,reviewState:'SYNTHETIC_APPROVED',sha256:digest(Buffer.from('반품 신청 7일 이내 가능합니다.'))};
 const vault=new LocalSyntheticVault({root,accounts:[owner],documents:[doc]});
 const api=await launchSyntheticLoopback(vault);t.after(()=>api.close());
 return {api,vault};
}
test('UI HTML document is available on IPv4 loopback with strict CSP and no cache',async t=>{
 const f=await fixture(t);const r=await fetch(f.api.baseUrl+'/');
 assert.equal(r.status,200);assert.equal(r.headers.get('cache-control'),'no-store');
 const csp=r.headers.get('content-security-policy');
 assert.match(csp,/default-src 'none'/);assert.match(csp,/script-src 'self'/);
 assert.match(csp,/frame-ancestors 'none'/);assert.equal(r.headers.get('x-frame-options'),'DENY');
 assert.match(await r.text(),/CITEVAULT AX/);
});
test('UI script and stylesheet are fetched locally with correct MIME and no external requests',async t=>{
 const f=await fixture(t);
 for(const [route,type,expected] of [['/ui.js','text/javascript','/v1/admin/provision'],['/ui.css','text/css','color-scheme:dark']]){
  const r=await fetch(f.api.baseUrl+route);assert.equal(r.status,200);
  assert.match(r.headers.get('content-type'),new RegExp(type));assert.match(await r.text(),new RegExp(expected));
 }
 assert.equal((await fetch(f.api.baseUrl+'/ui-secret')).status,404);
});
test('HTML has no external links, inline scripts, secret storage or token snippets',()=>{
 assert.ok(html.includes('<script src="/ui.js" defer></script>'));
 assert.ok(html.includes('오프라인 검증판'));
 assert.ok(!html.includes('http://')&&!html.includes('https://'));
 assert.ok(!html.includes('<script>'));
 assert.ok(!js.includes('localStorage')&&!js.includes('sessionStorage')&&!js.includes('innerHTML'));
 assert.ok(!js.includes('document.cookie')&&!js.includes('eval('));
 assert.ok(css.includes('color-scheme:dark'));
});
test('actual UI API contract issues a local account and searches cited evidence',async t=>{
 const f=await fixture(t);
 async function post(route,token,data){return fetch(f.api.baseUrl+route,{method:'POST',headers:{'content-type':'application/json',...(token?{authorization:'Bearer '+token}:{})},body:JSON.stringify(data)});}
 const auth=await post('/v1/login',null,{userId:'owner',password:pass});assert.equal(auth.status,200);
 const token=(await auth.json()).token;
 const r=await post('/v1/admin/provision',token,{userId:'newperson',password:'SYNTHETIC_NEW_PERSON_2026',groups:['staff'],projects:['quality'],clearance:1});
 assert.equal(r.status,201);
 const member=await post('/v1/login',null,{userId:'newperson',password:'SYNTHETIC_NEW_PERSON_2026'});
 const access=(await member.json()).token;
 const found=await post('/v1/search',access,{question:'반품 신청 기간',documentIds:['policy']});
 assert.equal(found.status,200);const result=await found.json();
 assert.equal(result.status,'SEARCH_ONLY');assert.equal(result.answer,null);assert.equal(result.evidence[0].document_id,'policy');
});
test('UI assets never use a remote URL for model or user data',()=>{
 assert.doesNotMatch(js,/fetch\(['"]https?:|new WebSocket|navigator\.sendBeacon/);
 assert.doesNotMatch(html,/action=|target=_blank|http:\/\//);
});
