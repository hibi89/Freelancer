import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {reviewSyntheticSalesDirectory} from '../enterprise/p70-local-review.mjs';
import {inspectSyntheticSqlEvidence} from '../enterprise/p85-review-sql.mjs';
import {createSyntheticProvenance} from '../enterprise/p85-signed-provenance.mjs';
import {createSyntheticReviewJourney} from '../enterprise/p85-journey.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const password='SYNTHETIC_REVIEW_OPERATOR_2026';
const question='총매출과 반품 신청 규정';
const CSV='order_id,sku,quantity,unit_price_krw,amount_krw\nA001,TV,2,10000,20000\nA002,BOOK,1,37000,37000\nA003,PC,4,25000,100000\n';
const mk=(t)=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-signed-integrated-'));
 t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const sales=path.join(root,'orgA','sales-only');fs.mkdirSync(sales,{recursive:true});
 const doc=path.join(root,'orgA','policy','v1.txt');fs.mkdirSync(path.dirname(doc),{recursive:true});
 const source='반품 신청은 7일 이내 가능합니다.\n';fs.writeFileSync(doc,source);
 fs.writeFileSync(path.join(sales,'sales.csv'),CSV);
 fs.writeFileSync(path.join(sales,'smax-review.json'),JSON.stringify({contract:'SMAX_SYNTHETIC_REVIEW_V1',
  source_sha256:sha(CSV),headers:['order_id','sku','quantity','unit_price_krw','amount_krw'],row_count:3,approval:'NOT_GRANTED'}));
 fs.writeFileSync(path.join(sales,'prep-mapping.json'),JSON.stringify({contract:'PREP_SYNTHETIC_MAPPING_V1',
  source_sha256:sha(CSV),roles:{order_id:'order_id',sku:'sku',quantity:'quantity',unit_price_krw:'unit_price_krw',amount_krw:'amount_krw'},
  tax_basis:'TAX_UNKNOWN',review_state:'REVIEW_HOLD'}));
 const accounts=[createSyntheticAccount({userId:'staff',tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:1,password}),
  createSyntheticAccount({userId:'other',tenantId:'orgB',groups:['sales'],projects:['quality'],clearance:1,password})];
 const docs=[{tenantId:'orgA',id:'policy',version:'v1',collection:'handbook',groups:['sales'],projects:['quality'],
  classification:1,reviewState:'SYNTHETIC_APPROVED',active:true,sha256:sha(source)}];
 const vault=new LocalSyntheticVault({root,accounts,documents:docs});
 const keys=crypto.generateKeyPairSync('ed25519');
 const reviewed=reviewSyntheticSalesDirectory(sales);
 const proof=createSyntheticProvenance({tenantId:'orgA',keyId:'smaxlocal',sourceSha256:reviewed.source_sha256,
  mappingSha256:reviewed.mapping_sha256,version:5,issuedAtMs:1000,expiresAtMs:9000,
  documents:[],privateKey:keys.privateKey});
 const signedReview={expectedTenant:'orgA',keyId:'smaxlocal',trustedPublicKey:keys.publicKey,lastSeenVersion:4,envelope:proof};
 const create=(config=signedReview,clock=()=>5000)=>createSyntheticReviewJourney({vault,salesDirectory:sales,
  salesScope:{tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:1},signedReview:config,clock});
 const token=vault.login('staff',password).token;
 return {root,sales,vault,keys,proof,reviewed,signedReview,token,create};
};
const assess=f=>f.create().assess(f.token,question,{documentIds:['policy']});
test('real CSV+PREP mapping bytes are both hashed and bind a valid Ed25519 review',t=>{
 const f=mk(t),out=assess(f);assert.equal(out.status,'REVIEW_HOLD');assert.equal(out.reason,'APPROVAL_NOT_GRANTED');
 assert.equal(out.answer,null);assert.equal(out.network_calls,0);
 assert.equal(out.sql_evidence.provisional_revenue_krw,'157000');
 assert.equal(out.sql_evidence.mapping_sha256,f.reviewed.mapping_sha256);
 assert.equal(out.signed_review.signature_verified,true);
 assert.equal(out.signed_review.source_sha256,sha(CSV));
 assert.equal(out.signed_review.mapping_sha256,f.reviewed.mapping_sha256);
 assert.equal(out.signed_review.customer_approval,false);assert.equal(out.signed_review.ax_package_created,false);
 assert.equal(out.source_rights_verified,false);assert.equal(out.approved_customer_data,false);
 assert.equal(out.document_evidence[0].document_id,'policy');
});
test('altering otherwise valid mapping metadata refuses the signed review and hides numeric totals',t=>{
 const f=mk(t),file=path.join(f.sales,'prep-mapping.json');
 const v=JSON.parse(fs.readFileSync(file,'utf8'));v.tax_basis='TAX_UNKNOWN';v.whitespace_ignored=undefined;
 fs.writeFileSync(file,JSON.stringify(v,null,2));
 const out=assess(f);assert.equal(out.reason,'SIGNED_PROVENANCE_FAILED');
 assert.equal(out.sql_evidence,null);assert.deepEqual(out.document_evidence,[]);
 assert.equal(out.signed_review.signature_verified,false);assert.equal(out.answer,null);
});
test('forged key with matching key ID is refused',t=>{
 const f=mk(t),fake=crypto.generateKeyPairSync('ed25519');
 const out=f.create({...f.signedReview,trustedPublicKey:fake.publicKey}).assess(f.token,question,{documentIds:['policy']});
 assert.equal(out.reason,'SIGNED_PROVENANCE_FAILED');assert.equal(out.sql_evidence,null);
});
test('expired or future-dated producer envelope remains fail-closed',t=>{
 const f=mk(t);
 for(const now of [500,9000]){const out=f.create(f.signedReview,()=>now).assess(f.token,question,{documentIds:['policy']});
  assert.equal(out.reason,'SIGNED_PROVENANCE_FAILED');assert.equal(out.answer,null);}
});
test('replayed or stale producer revision remains fail-closed',t=>{
 const f=mk(t),out=f.create({...f.signedReview,lastSeenVersion:5}).assess(f.token,question,{documentIds:['policy']});
 assert.equal(out.reason,'SIGNED_PROVENANCE_FAILED');assert.equal(out.sql_evidence,null);
});
test('missing producer proof remains explicitly not signature verified',t=>{
 const f=mk(t),out=f.create(null).assess(f.token,question,{documentIds:['policy']});
 assert.equal(out.signed_review.status,'NOT_CONFIGURED');assert.equal(out.signed_review.signature_verified,false);
 assert.equal(out.answer,null);assert.equal(out.sql_evidence.approval,'NOT_GRANTED');
});
test('original source changes always refuse before signed result can be returned',t=>{
 const f=mk(t),file=path.join(f.sales,'sales.csv');fs.appendFileSync(file,'A004,TV,1,100,100\n');
 assert.throws(()=>assess(f));
});
test('wrong tenant cannot read sales data even when producer attestation is valid',t=>{
 const f=mk(t),token=f.vault.login('other',password).token;
 assert.throws(()=>f.create().assess(token,question,{documentIds:['policy']}),{code:'NOT_FOUND'});
});
test('HTTP /v1/assess validates signed source review and still denies approval',async t=>{
 const f=mk(t),api=await launchSyntheticLoopback(f.vault,{journey:f.create()});t.after(()=>api.close());
 const res=await fetch(api.baseUrl+'/v1/assess',{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer '+f.token},
  body:JSON.stringify({question,documentIds:['policy']})});
 assert.equal(res.status,200);const out=await res.json();assert.equal(out.status,'REVIEW_HOLD');assert.equal(out.answer,null);
 assert.equal(out.signed_review.signature_verified,true);assert.equal(out.signed_review.customer_approval,false);
 assert.equal(res.headers.get('cache-control'),'no-store');
});
