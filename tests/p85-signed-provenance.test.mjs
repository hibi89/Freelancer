import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createSyntheticProvenance,verifySyntheticProvenance} from '../enterprise/p85-signed-provenance.mjs';
const SHA=x=>crypto.createHash('sha256').update(x).digest('hex');
const keys=crypto.generateKeyPairSync('ed25519'),wrong=crypto.generateKeyPairSync('ed25519');
const doc1={id:'pdf-manual',kind:'pdf',sha256:SHA('synthetic pdf bytes')};
const doc2={id:'sales-policy',kind:'docx',sha256:SHA('synthetic docx bytes')};
const params={tenantId:'orgA',keyId:'producerA',sourceSha256:SHA('synthetic sales csv'),
  mappingSha256:SHA('synthetic prep mapping'),version:5,issuedAtMs:1000,
  expiresAtMs:8000,documents:[doc1,doc2],privateKey:keys.privateKey};
const env=()=>createSyntheticProvenance(params);
const verify=(envelope=env(),extra={})=>verifySyntheticProvenance({
  envelope,trustedPublicKey:keys.publicKey,expectedTenant:params.tenantId,
  expectedKeyId:params.keyId,expectedSourceSha256:params.sourceSha256,
  expectedMappingSha256:params.mappingSha256,expectedDocuments:params.documents,
  lastSeenVersion:4,nowMs:5000,...extra});
const alter=(callback)=>{const e=env();const p=JSON.parse(JSON.stringify(e));callback(p);return p;};

test('valid Ed25519 binds two source hashes and exact ordered documents but stays HOLD',()=>{
  const r=verify();assert.equal(r.status,'REVIEW_HOLD');
  assert.equal(r.signature_verified,true);assert.equal(r.documents_verified,2);
  assert.equal(r.source_rights_verified,false);assert.equal(r.customer_approval,false);
  assert.equal(r.ax_package_created,false);assert.equal(r.answer,null);assert.equal(r.network_calls,0);
});
test('source SHA tampering invalidates signature',()=>{
  assert.throws(()=>verify(alter(x=>x.payload.source_sha256=SHA('tampered'))),{code:'BOUNDARY_MISMATCH'});
});
test('mapping SHA tampering is forbidden',()=>{
  assert.throws(()=>verify(alter(x=>x.payload.mapping_sha256=SHA('tampered'))),{code:'BOUNDARY_MISMATCH'});
});
test('switching tenant or key ID fails',()=>{
  for(const change of [x=>x.payload.tenant_id='orgB',x=>x.payload.key_id='producerB'])
    assert.throws(()=>verify(alter(change)),{code:'BOUNDARY_MISMATCH'});
});
test('changing review status to approved cannot be signed or verified',()=>{
  assert.throws(()=>verify(alter(x=>x.payload.review_state='ACCEPTED')),{code:'CONTRACT_INVALID'});
});
test('forging source rights true cannot be verified',()=>{
  assert.throws(()=>verify(alter(x=>x.payload.rights_verified=true)),{code:'CONTRACT_INVALID'});
});
test('wrong trusted Ed25519 public key rejects valid signature',()=>{
  assert.throws(()=>verify(env(),{trustedPublicKey:wrong.publicKey}),{code:'SIGNATURE_INVALID'});
});
test('tamper document digest after signing fails',()=>{
  assert.throws(()=>verify(alter(x=>x.payload.documents[0].sha256=SHA('changed'))),{code:'DOCUMENT_MISMATCH'});
});
test('caller-provided expected document SHA mismatch fails',()=>{
  assert.throws(()=>verify(env(),{expectedDocuments:[doc1,{...doc2,sha256:SHA('wrong')}] }),{code:'DOCUMENT_MISMATCH'});
});
test('pinned key identity cannot come from envelope',()=>{
  assert.throws(()=>verify(env(),{expectedKeyId:'untrustedIssuer'}),{code:'BOUNDARY_MISMATCH'});
});
test('signature needs correct ed25519 bytes and format',()=>{
  assert.throws(()=>verify(alter(x=>x.signature='1'.repeat(86))),{code:'SIGNATURE_INVALID'});
  assert.throws(()=>verify(alter(x=>x.signature='evil')), {code:'ENVELOPE_INVALID'});
});
test('expires exactly at boundary, future creation is blocked',()=>{
  assert.throws(()=>verify(env(),{nowMs:8000}),{code:'PROOF_EXPIRED'});
  assert.throws(()=>verify(env(),{nowMs:999}),{code:'PROOF_EXPIRED'});
});
test('monotonic version counter blocks reuse or replay',()=>{
  assert.throws(()=>verify(env(),{lastSeenVersion:5}),{code:'PROOF_REPLAY'});
  assert.throws(()=>verify(env(),{lastSeenVersion:6}),{code:'PROOF_REPLAY'});
});
test('unsorted or repeated document IDs are refused',()=>{
  assert.throws(()=>createSyntheticProvenance({...params,documents:[doc1,doc1]}),{code:'DOCUMENT_INVALID'});
  assert.throws(()=>verify(alter(x=>x.payload.documents.reverse())),{code:'DOCUMENT_ORDER_INVALID'});
});
test('additional unsigned approval fields are refused',()=>{
  assert.throws(()=>verify(alter(x=>x.payload.customer_rights_approved=true)),{code:'CONTRACT_INVALID'});
  assert.throws(()=>verify(alter(x=>x.approved=true)),{code:'ENVELOPE_INVALID'});
});
test('invalid signing key (public not private) is refused',()=>{
  assert.throws(()=>createSyntheticProvenance({...params,privateKey:keys.publicKey}),{code:'KEY_INVALID'});
});
test('invalid timestamp or long-lived approval claim refused',()=>{
  assert.throws(()=>createSyntheticProvenance({...params,expiresAtMs:1000}),{code:'CONTRACT_INVALID'});
  assert.throws(()=>createSyntheticProvenance({...params,expiresAtMs:1000+86400001}),{code:'CONTRACT_INVALID'});
});
test('non Ed25519 algorithm cannot enter verifier',()=>{
  const rsa=crypto.generateKeyPairSync('rsa',{modulusLength:2048});
  assert.throws(()=>verify(env(),{trustedPublicKey:rsa.publicKey}),{code:'KEY_INVALID'});
});
