/** Deterministic synthetic 100-query acceptance harness, NOT a customer's Gold100. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';

const sha=text=>crypto.createHash('sha256').update(text).digest('hex');
const files={
  'orgA/policy/v1.txt':'반품 신청은 7일 이내 가능합니다.\n배송 일정은 2일 이내 진행됩니다.\n',
  'orgA/compare/v1.txt':'반품 신청은 14일 이내 가능합니다.\n',
  'orgA/secretDoc/v1.txt':'비밀 규정: 외부반출을 금지합니다.\n',
  'orgB/foreign/v1.txt':'기밀: 기업 B 전용 정보.\n'
};
function setup(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-synthetic100-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  for(const [name,content] of Object.entries(files)){
    const dest=path.join(root,...name.split('/'));fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,content);
  }
  const accounts=[
    createSyntheticAccount({userId:'analyst',tenantId:'orgA',groups:['policy'],projects:['p1'],clearance:1,password:'synthetic100_ANALYST_123'}),
    createSyntheticAccount({userId:'secret',tenantId:'orgA',groups:['privileged'],projects:['p2'],clearance:3,password:'synthetic100_SECRET_123'}),
    createSyntheticAccount({userId:'external',tenantId:'orgB',groups:['privileged'],projects:['p2'],clearance:3,password:'synthetic100_EXTERNAL_123'})
  ];
  const info=[['orgA','policy','policy','p1',1],['orgA','compare','policy','p1',1],
    ['orgA','secretDoc','privileged','p2',3],['orgB','foreign','privileged','p2',3]];
  const documents=info.map(([tenantId,id,group,project,classification])=>({
    tenantId,id,version:'v1',collection:'policies',groups:[group],projects:[project],classification,
    sha256:sha(files[tenantId+'/'+id+'/v1.txt']),active:true,reviewState:'SYNTHETIC_APPROVED'
  }));
  const vault=new LocalSyntheticVault({root,accounts,documents});
  return {root,vault,token:vault.login('analyst','synthetic100_ANALYST_123').token};
}
test('100 deterministic synthetic Korean retrieval/refusal cases are scoped, grounded and measured',t=>{
  const {root,vault,token}=setup(t);const durations=[],counts={retrieval:0,insufficient:0,conflict:0,forbidden:0,mixedDenied:0};
  for(let i=0;i<100;i++){
    const start=performance.now();const ordinal=String(i).padStart(3,'0');
    if(i<20){
      const r=vault.search(token,'배송 일정은 언제인가요? 테스트 '+ordinal,{documentIds:['policy']});
      assert.equal(r.status,'SEARCH_ONLY');assert.equal(r.answer,null);
      assert.equal(r.network_calls,0);assert.ok(r.evidence.some(e=>e.document_id==='policy'&&e.quote.includes('배송')));
      counts.retrieval++;
    }else if(i<40){
      const r=vault.search(token,'zzqxnevermatch'+ordinal,{documentIds:['policy']});
      assert.equal(r.status,'INSUFFICIENT_EVIDENCE');assert.equal(r.answer,null);
      assert.deepEqual(r.evidence,[]);counts.insufficient++;
    }else if(i<60){
      const r=vault.search(token,'반품 신청 기간 확인 '+ordinal,{documentIds:['policy','compare'],limit:1});
      assert.equal(r.status,'POSSIBLE_CONFLICT');assert.equal(r.answer,null);
      assert.deepEqual(new Set(r.evidence.map(e=>e.document_id)),new Set(['policy','compare']));counts.conflict++;
    }else if(i<80){
      assert.throws(()=>vault.source(token,'secretDoc'),{code:'NOT_FOUND'});
      assert.throws(()=>vault.source(token,'missingDoc'+ordinal),{code:'NOT_FOUND'});
      counts.forbidden++;
    }else{
      assert.throws(()=>vault.search(token,'반품 신청 '+ordinal,{documentIds:['policy','secretDoc']}),{code:'NOT_FOUND'});
      counts.mixedDenied++;
    }
    durations.push(performance.now()-start);
  }
  const sorted=[...durations].sort((a,b)=>a-b),p95=sorted[Math.ceil(sorted.length*0.95)-1];
  assert.deepEqual(counts,{retrieval:20,insufficient:20,conflict:20,forbidden:20,mixedDenied:20});
  assert.equal(durations.length,100);assert.ok(Number.isFinite(p95)&&p95>=0);
  for(const [name,content] of Object.entries(files))assert.equal(sha(fs.readFileSync(path.join(root,...name.split('/')))),sha(content));
  t.diagnostic(JSON.stringify({type:'SYNTHETIC_NOT_CUSTOMER_GOLD100',cases:100,counts,p95_ms:Math.round(p95*1000)/1000,heap_used_bytes:process.memoryUsage().heapUsed}));
});
