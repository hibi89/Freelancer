import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import {queryPinnedRagSyntheticScope} from '../enterprise/p70-rag-bridge.mjs';

const root=process.env.RAG_STUDIO_ROOT;
const sha='a'.repeat(64);
const principal=()=>({subject_id:'employee1',tenant_id:'org1',groups:['teamA'],
  projects:['p1'],clearance:1,identity_state:'SYNTHETIC_ONLY'});
const doc=(id,overrides={})=>({
  id,tenant_id:'org1',group_grants:['teamA'],project_grants:['p1'],classification:1,
  review_state:'SYNTHETIC_APPROVED',source_sha256:sha,kind:'txt',version:'v1',
  expires_at_utc:'2027-01-01T00:00:00Z',lines:['반품 신청은 7일 이내 가능합니다.'],...overrides
});
const options=(extra={})=>({
  principal:principal(),catalog:[doc('document-returns'),
    doc('document-shipping',{group_grants:['teamB']})],
  now_utc:'2026-11-13T05:52:00Z',requested_ids:['document-returns'],
  question:'반품 신청 가능 기간',
  rag_root:root,
  package_root:root?path.join(root,'fixtures/ax_multi_doc_v0'):null,...extra
});

test('P70 pinned original RAG returns only scope-approved cited document', {
  skip:!root&&'Requires RAG_STUDIO_ROOT exact pinned checkout'
},async()=>{
  const r=await queryPinnedRagSyntheticScope(options());
  assert.equal(r.status,'SEARCH_ONLY');
  assert.equal(r.answer,null);
  assert.equal(r.model_state,'UNAVAILABLE');
  assert.equal(r.enterprise_identity_verified,false);
  assert.ok(r.evidence.length>0);
  assert.ok(r.evidence.every(x=>x.document_id==='document-returns'));
});
test('P70 one hidden document in a mixed request denies all evidence', async()=>{
  const r=await queryPinnedRagSyntheticScope(options({
    requested_ids:['document-returns','document-shipping']}));
  assert.equal(r.status,'FORBIDDEN_OR_NOT_FOUND');
  assert.deepEqual(r.evidence,[]);
});
test('P70 nonexistent document IDs share identical generic refusal',async()=>{
  const a=await queryPinnedRagSyntheticScope(options({requested_ids:['missing']}));
  const b=await queryPinnedRagSyntheticScope(options({requested_ids:['document-shipping']}));
  assert.deepEqual(a,b);
});
test('P70 forged corporate identity cannot activate synthetic scope',async()=>{
  await assert.rejects(()=>queryPinnedRagSyntheticScope(options({
    principal:{...principal(),identity_state:'ENTERPRISE_AUTHENTICATED'}}),
    {code:'IDENTITY_NOT_VERIFIED'});
});
test('P70 authorized doc cannot leak file paths when original RAG checkout is missing',async()=>{
  const r=await queryPinnedRagSyntheticScope(options({
    rag_root:'/this/path/citevault-no-such-rag'}));
  assert.equal(r.status,'REVIEW_HOLD');
  assert.deepEqual(r.evidence,[]);
  assert.doesNotMatch(JSON.stringify(r),/citevault-no-such-rag/);
});
test('P70 wrong-tenant request gives no citation even when original RAG exists',async()=>{
  const r=await queryPinnedRagSyntheticScope(options({
    catalog:[doc('document-returns',{tenant_id:'org2'})]}));
  assert.equal(r.status,'FORBIDDEN_OR_NOT_FOUND');
  assert.deepEqual(r.evidence,[]);
});
