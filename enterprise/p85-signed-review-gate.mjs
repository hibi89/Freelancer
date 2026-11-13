/** Validates synthetic PREP+SMAX review evidence against a pinned producer key.
 * This is signature authenticity ONLY. Never grants corporate/legal approval.
 * The trusted public key, expected tenant/key and revocation epoch originate at
 * the caller's protected configuration, not from the review envelope or HTTP.
 */
import {verifySyntheticProvenance} from './p85-signed-provenance.mjs';
const fail=code=>{throw Object.assign(new Error('SIGNED_SOURCE_HOLD'),{code});};
const ID=/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/;
const sha=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
const isConfig=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);

export function verifySignedSyntheticSalesReview({source,config,tenantId,nowMs=Date.now()}){
  if(!source||source.status!=='REVIEW_HOLD'||source.approval!=='NOT_GRANTED'||
     source.source_rights_verified!==false||source.ax_package_created!==false||
     !sha(source.source_sha256)||!sha(source.mapping_sha256)||
     typeof tenantId!=='string'||!ID.test(tenantId)||
     !isConfig(config)||config.expectedTenant!==tenantId||
     typeof config.keyId!=='string'||!ID.test(config.keyId)||
     !Number.isSafeInteger(config.lastSeenVersion)||config.lastSeenVersion<0||
     !Number.isSafeInteger(nowMs)||nowMs<=0)fail('SIGNED_REVIEW_CONFIG_INVALID');
  const verified=verifySyntheticProvenance({
    envelope:config.envelope,trustedPublicKey:config.trustedPublicKey,
    expectedTenant:tenantId,expectedKeyId:config.keyId,
    expectedSourceSha256:source.source_sha256,
    expectedMappingSha256:source.mapping_sha256,expectedDocuments:[],
    lastSeenVersion:config.lastSeenVersion,nowMs
  });
  if(verified.status!=='REVIEW_HOLD'||verified.signature_verified!==true||
     verified.source_rights_verified!==false||verified.ax_package_created!==false)
    fail('SIGNED_REVIEW_STATE_INVALID');
  return Object.freeze({status:'REVIEW_HOLD',signature_verified:true,
    source_sha256:source.source_sha256,mapping_sha256:source.mapping_sha256,
    producer_key_id:verified.key_id,producer_version:verified.version,
    customer_approval:false,source_rights_verified:false,
    ax_package_created:false,network_calls:0});
}
