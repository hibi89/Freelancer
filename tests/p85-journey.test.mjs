import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {createSyntheticReviewJourney} from '../enterprise/p85-journey.mjs';
import {inspectSyntheticSqlEvidence} from '../enterprise/p85-review-sql.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const maker=fileURLToPath(new URL('./p85-native-fixture.py',import.meta.url));
const content='order_id,sku,quantity,unit_price_krw,amount_krw\nA001,TV,2,10000,20000\nA002,BOOK,1,37000,37000\nA003,PC,4,25000,100000\n';
function make(t){
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-journey-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const p=spawnSync('python',['-I','-B',maker,root],{encoding:'utf8',timeout:12000});
  assert.equal(p.status,0,p.stderr||'fixture failed');
  const sales=path.join(root,'orgA','sales-only');fs.mkdirSync(sales,{recursive:true});
  fs.writeFileSync(path.join(sales,'sales.csv'),content);
  const digest=sha(Buffer.from(content));
  fs.writeFileSync(path.join(sales,'smax-review.json'),JSON.stringify({contract:'SMAX_SYNTHETIC_REVIEW_V1',
    source_sha256:digest,headers:['order_id','sku','quantity','unit_price_krw','amount_krw'],row_count:3,approval:'NOT_GRANTED'}));
  fs.writeFileSync(path.join(sales,'prep-mapping.json'),JSON.stringify({contract:'PREP_SYNTHETIC_MAPPING_V1',
    source_sha256:digest,roles:{order_id:'order_id',sku:'sku',quantity:'quantity',unit_price_krw:'unit_price_krw',amount_krw:'amount_krw'},
    tax_basis:'TAX_UNKNOWN',review_state:'REVIEW_HOLD'}));
  const accounts=[
    createSyntheticAccount({userId:'alice',tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:1,password:'synthetic-ALICE-only123'}),
    createSyntheticAccount({userId:'bob',tenantId:'orgA',groups:['engineering'],projects:['quality'],clearance:1,password:'synthetic-BOB-only123'}),
    createSyntheticAccount({userId:'carol',tenantId:'orgB',groups:['sales'],projects:['quality'],clearance:1,password:'synthetic-CAROL-only123'})
  ];
  const pdf=path.join(root,'orgA','manualPdf','v1.pdf');
  const docx=path.join(root,'orgA','rulesDocx','v1.docx');
  const documents=[{id:'manualPdf',native_kind:'pdf',file:pdf},{id:'rulesDocx',native_kind:'docx',file:docx}]
    .map(x=>({id:x.id,tenantId:'orgA',native_kind:x.native_kind,version:'v1',collection:'policies',
      groups:['sales','engineering'],projects:['quality'],classification:1,active:true,reviewState:'SYNTHETIC_APPROVED',
      sha256:sha(fs.readFileSync(x.file))}));
  const vault=new LocalSyntheticVault({root,accounts,documents});
  const journey=createSyntheticReviewJourney({vault,salesDirectory:sales,salesScope:{tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:1}});
  const login=(user,pw)=>vault.login(user,pw).token;
  return {root,sales,vault,journey,login,files:{pdf,docx}};
}
const ALICE='synthetic-ALICE-only123';const BOB='synthetic-BOB-only123';const CAROL='synthetic-CAROL-only123';
const QUERY='총매출과 반품 신청 규정 알려줘';
test('P85 integrated document+SQL journey is always REVIEW_HOLD without customer approval',t=>{
 const f=make(t),token=f.login('alice',ALICE),out=f.journey.assess(token,QUERY,{documentIds:['rulesDocx']});
 assert.equal(out.status,'REVIEW_HOLD');assert.equal(out.reason,'APPROVAL_NOT_GRANTED');
 assert.equal(out.answer,null);assert.equal(out.source_rights_verified,false);
 assert.equal(out.sql_evidence.provisional_revenue_krw,'157000');
 assert.equal(out.sql_evidence.units,'7');assert.equal(out.sql_evidence.orders,3);
 assert.equal(out.sql_evidence.approval,'NOT_GRANTED');assert.equal(out.sql_evidence.ax_package_created,false);
 assert.equal(out.sql_evidence.evidence.length,3);
 assert.equal(out.document_evidence[0].source_unit,'paragraph');
 assert.equal(out.network_calls,0);
});
test('actual PDF+DOCX and SQL are combined in one local request',t=>{
 const f=make(t),token=f.login('alice',ALICE),out=f.journey.assess(token,'총 매출 Product returns 반품 신청',{documentIds:['manualPdf','rulesDocx']});
 assert.equal(out.status,'REVIEW_HOLD');
 assert.ok(out.document_evidence.some(c=>c.source_unit==='page'&&c.page===1));
 assert.ok(out.document_evidence.some(c=>c.source_unit==='paragraph'&&c.paragraph===1));
 assert.equal(out.sql_evidence.provisional_revenue_krw,'157000');
});
test('dataset permission denies after document ACL but before CSV filesystem read',t=>{
 const f=make(t),bob=f.login('bob',BOB),p=path.join(f.sales,'sales.csv');
 fs.renameSync(p,p+'.bak');
 assert.throws(()=>f.journey.assess(bob,QUERY,{documentIds:['rulesDocx']}),{code:'NOT_FOUND'});
 fs.renameSync(p+'.bak',p);
});
test('cross-tenant attempted SQL query never reads or reveals tenant A data',t=>{
 const f=make(t),carol=f.login('carol',CAROL);
 assert.throws(()=>f.journey.assess(carol,QUERY,{documentIds:['rulesDocx']}),{code:'NOT_FOUND'});
});
test('source tampering causes review HOLD rather than generated numeric answer',t=>{
 const f=make(t),alice=f.login('alice',ALICE);
 fs.appendFileSync(path.join(f.sales,'sales.csv'),'A004,TV,1,100,100\n');
 assert.throws(()=>f.journey.assess(alice,QUERY,{documentIds:['rulesDocx']}));
});
test('unapproved mapping or fake approval is rejected',t=>{
 const f=make(t),alice=f.login('alice',ALICE),p=path.join(f.sales,'smax-review.json');
 const v=JSON.parse(fs.readFileSync(p,'utf8'));v.approval='GRANTED';fs.writeFileSync(p,JSON.stringify(v));
 assert.throws(()=>f.journey.assess(alice,QUERY,{documentIds:['rulesDocx']}));
});
test('arbitrary SQL injection user prompt never becomes a SQL statement',t=>{
 const f=make(t),alice=f.login('alice',ALICE),text='총매출; DROP TABLE sales --';
 const out=f.journey.assess(alice,text,{documentIds:['rulesDocx']});
 assert.equal(out.status,'REVIEW_HOLD');assert.equal(out.answer,null);
 assert.equal(inspectSyntheticSqlEvidence(f.sales).orders,3);
});
test('unsupported sales timeframe and SKU breakdown return explicit HOLD, not false full-period totals',t=>{
 const f=make(t),alice=f.login('alice',ALICE);
 for(const question of ['이번달 총매출','SKU별 총매출','평균 총 매출']){
  const out=f.journey.assess(alice,question,{documentIds:['rulesDocx']});
  assert.equal(out.reason,'UNSUPPORTED_SALES_SCOPE');assert.equal(out.sql_evidence,null);
 }
});
test('SQL review actual SHA and totals reconcile independently',t=>{
 const f=make(t),r=inspectSyntheticSqlEvidence(f.sales);
 assert.equal(r.source_sha256,sha(Buffer.from(content)));
 assert.deepEqual(r.evidence.map(x=>x.csv_line),[2,3,4]);
 assert.deepEqual(r.evidence.map(x=>x.amount_krw),['20000','37000','100000']);
 assert.equal(r.signed_producer_verified,false);assert.equal(r.generated_answer,null);
});
test('reviewed CSV symlink blocked and never followed',t=>{
 const f=make(t),file=path.join(f.sales,'sales.csv');fs.renameSync(file,file+'.real');
 try{try{fs.symlinkSync(file+'.real',file);}catch(e){t.diagnostic('OS symlink permission unavailable: '+e.code);return;}
   assert.throws(()=>inspectSyntheticSqlEvidence(f.sales));}
 finally{fs.rmSync(file,{force:true});fs.renameSync(file+'.real',file);}
});
test('reviewed CSV schema changes (even with fresh fabricated SHA) cannot bypass fixed SQL role contract',t=>{
 const f=make(t),p=path.join(f.sales,'sales.csv');
 const old=fs.readFileSync(p,'utf8'),newText=old.replace('order_id,sku,quantity,unit_price_krw,amount_krw',
  'sku,order_id,quantity,unit_price_krw,amount_krw').replace(/A00([1-3]),(TV|BOOK|PC)/g,'$2,A00$1');
 fs.writeFileSync(p,newText);
 const hash=sha(Buffer.from(newText));for(const fn of ['smax-review.json','prep-mapping.json']){
  const fp=path.join(f.sales,fn),obj=JSON.parse(fs.readFileSync(fp,'utf8'));
  obj.source_sha256=hash;if(fn.startsWith('smax'))obj.headers=['sku','order_id','quantity','unit_price_krw','amount_krw'];
  fs.writeFileSync(fp,JSON.stringify(obj));
 }
 assert.throws(()=>inspectSyntheticSqlEvidence(f.sales),{code:'SALES_MAPPING_NOT_FIXED'});
});
test('local HTTP /v1/assess is authenticated and returns review-only PDF/DOCX+SQL',async t=>{
 const f=make(t),api=await launchSyntheticLoopback(f.vault,{journey:f.journey});t.after(()=>api.close());
 const unauthorized=await fetch(api.baseUrl+'/v1/assess',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({question:QUERY})});
 assert.equal(unauthorized.status,401);
 const token=f.login('alice',ALICE);
 const response=await fetch(api.baseUrl+'/v1/assess',{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer '+token},
  body:JSON.stringify({question:'총 매출 Product returns 반품 신청',documentIds:['manualPdf','rulesDocx']})});
 assert.equal(response.status,200);
 const out=await response.json();assert.equal(out.status,'REVIEW_HOLD');assert.equal(out.answer,null);
 assert.equal(out.sql_evidence.provisional_revenue_krw,'157000');
 assert.ok(out.document_evidence.some(x=>x.source_unit==='page'));
 assert.ok(out.document_evidence.some(x=>x.source_unit==='paragraph'));
 assert.equal(response.headers.get('cache-control'),'no-store');
});
test('HTTP non-sales users are forbidden from provisional revenue',async t=>{
 const f=make(t),api=await launchSyntheticLoopback(f.vault,{journey:f.journey});t.after(()=>api.close());
 const token=f.login('bob',BOB),response=await fetch(api.baseUrl+'/v1/assess',{method:'POST',
  headers:{'content-type':'application/json',authorization:'Bearer '+token},
  body:JSON.stringify({question:QUERY,documentIds:['rulesDocx']})});
 assert.equal(response.status,404);assert.doesNotMatch(await response.text(),/157000|20,000/);
});
test('HTTP failed source review returns 409 without leaking source paths',async t=>{
 const f=make(t),api=await launchSyntheticLoopback(f.vault,{journey:f.journey});t.after(()=>api.close());
 fs.appendFileSync(path.join(f.sales,'sales.csv'),'A004,TV,1,100,100\n');
 const token=f.login('alice',ALICE),response=await fetch(api.baseUrl+'/v1/assess',{method:'POST',
  headers:{'content-type':'application/json',authorization:'Bearer '+token},
  body:JSON.stringify({question:QUERY,documentIds:['rulesDocx']})});
 assert.equal(response.status,409);assert.deepEqual(await response.json(),{error:'REVIEW_HOLD'});
});
test('fixed sales scope cannot be mutated after journey creation',t=>{
 const f=make(t),token=f.login('bob',BOB);
 const scope={tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:1};
 const j=createSyntheticReviewJourney({vault:f.vault,salesDirectory:f.sales,salesScope:scope});
 scope.groups[0]='engineering';scope.clearance=0;scope.projects[0]='quality';
 assert.throws(()=>j.assess(token,QUERY,{documentIds:['rulesDocx']}),{code:'NOT_FOUND'});
});
test('empty group or project SQL scopes fail closed',t=>{
 const f=make(t),token=f.login('alice',ALICE);
 for(const scope of [
  {tenantId:'orgA',groups:[],projects:['quality'],clearance:1},
  {tenantId:'orgA',groups:['sales'],projects:[],clearance:1},
  {tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:0}
 ]){const j=createSyntheticReviewJourney({vault:f.vault,salesDirectory:f.sales,salesScope:scope});
  assert.throws(()=>j.assess(token,QUERY,{documentIds:['rulesDocx']}),{code:'SCOPE_INVALID'});}
});
