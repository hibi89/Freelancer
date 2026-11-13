/**
 * Synthetic-only cryptographic producer provenance contract. Ed25519 is used to
 * authenticate the *review facts* and exact source digests. It NEVER grants
 * customer rights, never creates an approved AX package, and never reads files.
 * Trusted public keys and revision watermarks must come from the host, NOT the
 * untrusted envelope. No keys, customer identities or data leave this process.
 */
import crypto from 'node:crypto';

const ID=/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u;
const SHA=/^[a-f0-9]{64}$/u;
const SIG=/^[A-Za-z0-9_-]{86}$/u; // 64 Ed25519 signature bytes, base64url
const PREFIX='CITEVAULT_SYNTHETIC_PROVENANCE_V1\n';
const fail=(code)=>{throw Object.assign(new Error('PROVENANCE_REVIEW_HOLD'),{code});};
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x)&&Object.getPrototypeOf(x)===Object.prototype;
const names=(o,expected)=>obj(o)&&Object.keys(o).sort().join('|')===expected.slice().sort().join('|');
const bound=x=>typeof x==='string'&&ID.test(x);
const sha=x=>typeof x==='string'&&SHA.test(x);
function payload(p){
  const allowed=['contract','tenant_id','key_id','source_sha256','mapping_sha256','version',
    'issued_at_ms','expires_at_ms','documents','review_state','rights_verified','data_scope'];
  if(!names(p,allowed)||p.contract!=='CITEVAULT_SYNTHETIC_PROVENANCE_V1'||
     !bound(p.tenant_id)||!bound(p.key_id)||!sha(p.source_sha256)||!sha(p.mapping_sha256)||
     !Number.isSafeInteger(p.version)||p.version<1||p.version>2147483647||
     !Number.isSafeInteger(p.issued_at_ms)||p.issued_at_ms<1||
     !Number.isSafeInteger(p.expires_at_ms)||p.expires_at_ms<=p.issued_at_ms||
     p.expires_at_ms-p.issued_at_ms>86400000||
     p.review_state!=='REVIEW_HOLD'||p.rights_verified!==false||p.data_scope!=='SYNTHETIC_ONLY'||
     !Array.isArray(p.documents)||p.documents.length>16)fail('CONTRACT_INVALID');
  const ids=new Set();
  for(const d of p.documents){
    if(!names(d,['id','sha256','kind'])||!bound(d.id)||!sha(d.sha256)||
       !['pdf','docx','txt','md'].includes(d.kind)||ids.has(d.id))fail('DOCUMENT_INVALID');
    ids.add(d.id);
  }
  const ordered=[...p.documents].sort((a,b)=>a.id.localeCompare(b.id,'en'));
  if(ordered.some((d,i)=>d.id!==p.documents[i].id))fail('DOCUMENT_ORDER_INVALID');
  return p;
}
function key(k,type){
  if(!(k instanceof crypto.KeyObject)||k.type!==type||k.asymmetricKeyType!=='ed25519')
    fail('KEY_INVALID');
  return k;
}
const bytes=p=>Buffer.from(PREFIX+JSON.stringify(payload(p)),'utf8');

export function createSyntheticProvenance({tenantId,keyId,sourceSha256,mappingSha256,
  version,issuedAtMs,expiresAtMs,documents=[],privateKey}){
  key(privateKey,'private');
  const clean=documents.map(d=>({id:d.id,sha256:d.sha256,kind:d.kind}))
    .sort((a,b)=>a.id.localeCompare(b.id,'en'));
  const p={contract:'CITEVAULT_SYNTHETIC_PROVENANCE_V1',tenant_id:tenantId,key_id:keyId,
    source_sha256:sourceSha256,mapping_sha256:mappingSha256,version,issued_at_ms:issuedAtMs,
    expires_at_ms:expiresAtMs,documents:clean,review_state:'REVIEW_HOLD',
    rights_verified:false,data_scope:'SYNTHETIC_ONLY'};
  const sig=crypto.sign(null,bytes(p),privateKey).toString('base64url');
  return Object.freeze({payload:Object.freeze({...p,documents:Object.freeze(clean.map(d=>Object.freeze(d)))}),signature:sig});
}

/** Accepts only a host-provided, pinned Ed25519 public key and expected digests. */
export function verifySyntheticProvenance({envelope,trustedPublicKey,expectedTenant,
  expectedKeyId,expectedSourceSha256,expectedMappingSha256,
  expectedDocuments=[],lastSeenVersion=0,nowMs}){
  key(trustedPublicKey,'public');
  if(!names(envelope,['payload','signature'])||typeof envelope.signature!=='string'||
     !SIG.test(envelope.signature))fail('ENVELOPE_INVALID');
  const p=payload(envelope.payload);
  if(!bound(expectedTenant)||!bound(expectedKeyId)||!sha(expectedSourceSha256)||
     !sha(expectedMappingSha256)||!Array.isArray(expectedDocuments)||
     !Number.isSafeInteger(lastSeenVersion)||lastSeenVersion<0||
     !Number.isSafeInteger(nowMs)||nowMs<1)fail('EXPECTED_INVALID');
  if(p.tenant_id!==expectedTenant||p.key_id!==expectedKeyId||
     p.source_sha256!==expectedSourceSha256||p.mapping_sha256!==expectedMappingSha256)
    fail('BOUNDARY_MISMATCH');
  if(p.issued_at_ms>nowMs||p.expires_at_ms<=nowMs)fail('PROOF_EXPIRED');
  if(p.version<=lastSeenVersion)fail('PROOF_REPLAY');
  const expected=expectedDocuments.map(d=>({id:d.id,sha256:d.sha256,kind:d.kind}))
    .sort((a,b)=>a.id.localeCompare(b.id,'en'));
  if(expected.length!==p.documents.length||
      expected.some((d,i)=>d.id!==p.documents[i].id||d.sha256!==p.documents[i].sha256||
        d.kind!==p.documents[i].kind))fail('DOCUMENT_MISMATCH');
  let proof;
  try{proof=Buffer.from(envelope.signature,'base64url');}
  catch{fail('SIGNATURE_INVALID');}
  if(proof.length!==64||!crypto.verify(null,bytes(p),trustedPublicKey,proof))
    fail('SIGNATURE_INVALID');
  return Object.freeze({status:'REVIEW_HOLD',contract:p.contract,key_id:p.key_id,
    version:p.version,tenant_id:p.tenant_id,source_sha256:p.source_sha256,
    mapping_sha256:p.mapping_sha256,documents_verified:p.documents.length,
    signature_verified:true,source_rights_verified:false,customer_approval:false,
    ax_package_created:false,network_calls:0,answer:null});
}
