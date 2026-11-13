import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {ScopedConversation} from '../enterprise/p85-conversation.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
import {html,js} from '../enterprise/p85-ui.mjs';
const hash=text=>crypto.createHash('sha256').update(text).digest('hex');
const passwords={user:'SYNTHETIC_CHAT_USER_123456',admin:'SYNTHETIC_CHAT_ADMIN_123456',
 other:'SYNTHETIC_CHAT_OTHER_123456'};
function fixture(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-conversation-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const texts={v1:'반품 신청 기간은 7일 이내입니다.',v2:'반품 신청 기간은 14일 이내입니다.',secret:'비밀 정책은 31일 이내입니다.'};
  for(const [tenant,id,version,text] of [['tenantA','policy','v1',texts.v1],['tenantA','policy','v2',texts.v2],['tenantB','secret','v1',texts.secret]]){
    const dest=path.join(root,tenant,id);fs.mkdirSync(dest,{recursive:true});
    fs.writeFileSync(path.join(dest,version+'.txt'),text);
  }
  const accounts=[
    createSyntheticAccount({userId:'user',tenantId:'tenantA',groups:['staff'],projects:['qa'],clearance:1,password:passwords.user}),
    createSyntheticAccount({userId:'admin',tenantId:'tenantA',groups:['staff'],projects:['qa'],clearance:3,admin:true,password:passwords.admin}),
    createSyntheticAccount({userId:'other',tenantId:'tenantB',groups:['secret'],projects:['strategy'],clearance:3,password:passwords.other})
  ];
  const documents=[
    {tenantId:'tenantA',id:'policy',version:'v1',collection:'manuals',groups:['staff'],projects:['qa'],classification:1,sha256:hash(texts.v1),active:true,reviewState:'SYNTHETIC_APPROVED'},
    {tenantId:'tenantB',id:'secret',version:'v1',collection:'secret',groups:['secret'],projects:['strategy'],classification:3,sha256:hash(texts.secret),active:true,reviewState:'SYNTHETIC_APPROVED'}
  ];
  const vault=new LocalSyntheticVault({root,accounts,documents});
  const tokens=Object.fromEntries(Object.entries(passwords).map(([id,password])=>[id,vault.login(id,password).token]));
  let now=2000000;
  const memory=new ScopedConversation(vault,{clock:()=>now,ttlMs:120000,capacity:8});
  return {root,vault,tokens,memory,texts,advance:ms=>now+=ms};
}
test('bounded first answer is exact source evidence, not generated text or network access',t=>{
  const f=fixture(t),r=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  assert.equal(r.status,'SEARCH_ONLY');assert.equal(r.answer,null);assert.equal(r.network_calls,0);
  assert.match(r.conversation.thread_id,/^[a-f0-9]{32}$/);assert.equal(r.conversation.continuation,false);
  assert.equal(r.evidence[0].document_id,'policy');assert.equal(r.evidence[0].version,'v1');
  assert.doesNotMatch(JSON.stringify(r),/SYNTHETIC_CHAT|tenantB|secret/);
});
test('follow-up is restricted to previous evidence and freshly authorized source bytes',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  const next=f.memory.ask(f.tokens.user,{question:'그 기간은?',threadId:first.conversation.thread_id});
  assert.equal(next.status,'SEARCH_ONLY');assert.equal(next.conversation.continuation,true);
  assert.deepEqual([...new Set(next.evidence.map(e=>e.document_id))],['policy']);
  assert.ok(next.evidence.every(e=>e.source_sha256===hash(f.texts.v1)));
  assert.equal(next.answer,null);assert.equal(next.network_calls,0);
});
test('another bearer cannot steal the conversation and sees no thread evidence',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  const r=f.memory.ask(f.tokens.admin,{question:'다시 보여줘',threadId:first.conversation.thread_id});
  assert.deepEqual(r,{status:'CONTEXT_INVALID',answer:null,evidence:[],model_state:'UNAVAILABLE',network_calls:0,conversation:null});
});
test('expired conversation is fail-closed without old citations',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  f.advance(120001);const r=f.memory.ask(f.tokens.user,{question:'다시?',threadId:first.conversation.thread_id});
  assert.equal(r.status,'CONTEXT_INVALID');assert.deepEqual(r.evidence,[]);
});
test('retirement invalidates old context at source authorization boundary',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  f.vault.retire(f.tokens.admin,'policy');
  const r=f.memory.ask(f.tokens.user,{question:'그 문서?',threadId:first.conversation.thread_id});
  assert.equal(r.status,'CONTEXT_INVALID');assert.equal(r.answer,null);assert.deepEqual(r.evidence,[]);
});
test('version activation and source SHA rotation invalidate previous conversation',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  f.vault.replaceVersion(f.tokens.admin,'policy','v2',hash(f.texts.v2));
  const r=f.memory.ask(f.tokens.user,{question:'다시?',threadId:first.conversation.thread_id});
  assert.equal(r.status,'CONTEXT_INVALID');assert.deepEqual(r.evidence,[]);
  const fresh=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  assert.equal(fresh.evidence[0].version,'v2');
});
test('source tampering invalidates context rather than relying on cached data',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  fs.appendFileSync(path.join(f.root,'tenantA/policy/v1.txt'),'tamper');
  const r=f.memory.ask(f.tokens.user,{question:'다시?',threadId:first.conversation.thread_id});
  assert.equal(r.status,'CONTEXT_INVALID');assert.deepEqual(r.evidence,[]);
});
test('logout forgets prior conversation; reused thread never returns old citations',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  f.memory.forgetToken(f.tokens.user);
  const r=f.memory.ask(f.tokens.user,{question:'다시?',threadId:first.conversation.thread_id});
  assert.equal(r.status,'CONTEXT_INVALID');assert.equal(r.conversation,null);
});
test('rejects scope expansion and malformed thread IDs',t=>{
  const f=fixture(t),first=f.memory.ask(f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  assert.throws(()=>f.memory.ask(f.tokens.user,{question:'다시?',threadId:first.conversation.thread_id,documentIds:['secret']}),{code:'QUERY_INVALID'});
  assert.throws(()=>f.memory.ask(f.tokens.user,{question:'다시?',threadId:'../invalid'}),{code:'QUERY_INVALID'});
  assert.throws(()=>f.memory.ask('WRONG',{question:'반품'}),{code:'UNAUTHENTICATED'});
});
test('cross-tenant first query cannot create conversation or reveal source',t=>{
  const f=fixture(t);
  assert.throws(()=>f.memory.ask(f.tokens.user,{question:'기밀',documentIds:['secret']}),{code:'NOT_FOUND'});
});
test('HTTP authenticated conversation start, next, logout revoke, and no external calls',async t=>{
  const f=fixture(t),api=await launchSyntheticLoopback(f.vault);t.after(()=>api.close());
  async function post(route,token,body){const r=await fetch(api.baseUrl+route,{method:'POST',headers:{'content-type':'application/json',...(token?{authorization:'Bearer '+token}:{})},body:JSON.stringify(body)});return {status:r.status,data:await r.json()};}
  const start=await post('/v1/conversation/ask',f.tokens.user,{question:'반품 신청 기간',documentIds:['policy']});
  assert.equal(start.status,200);assert.equal(start.data.status,'SEARCH_ONLY');
  const id=start.data.conversation.thread_id;
  const next=await post('/v1/conversation/ask',f.tokens.user,{question:'그 기간은?',threadId:id});
  assert.equal(next.status,200);assert.equal(next.data.conversation.continuation,true);
  assert.equal(next.data.answer,null);assert.equal(next.data.network_calls,0);
  const denied=await post('/v1/conversation/ask',f.tokens.other,{question:'그 정책',threadId:id});
  assert.equal(denied.status,200);assert.equal(denied.data.status,'CONTEXT_INVALID');
  const end=await post('/v1/logout',f.tokens.user,{});assert.equal(end.status,200);
  const stale=await post('/v1/conversation/ask',f.tokens.user,{question:'그 기간',threadId:id});
  assert.notEqual(stale.data.status,'SEARCH_ONLY');assert.deepEqual(stale.data.evidence??[],[]);
});
test('UI exposes explicit start/continue conversation buttons with no unsafe DOM sinks',()=>{
  assert.match(html,/id="conversation-start"/);assert.match(html,/id="conversation-next"/);
  assert.match(js,/\/v1\/conversation\/ask/);
  assert.doesNotMatch(js,/innerHTML|localStorage|sessionStorage|WebSocket|sendBeacon/);
});
