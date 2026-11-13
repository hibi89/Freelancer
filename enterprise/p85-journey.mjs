/** Integrated P85 test journey: authenticated docs + offline provisional SQL, always HOLD. */
import {inspectSyntheticSqlEvidence} from './p85-review-sql.mjs';
import {verifySignedSyntheticSalesReview} from './p85-signed-review-gate.mjs';
const INVALID=()=>{throw Object.assign(new Error('QUERY_NOT_SUPPORTED'),{code:'QUERY_INVALID'});};

export function createSyntheticReviewJourney({vault,salesDirectory,salesScope,signedReview=null,clock=()=>Date.now()}){
  if(!vault||typeof vault.search!=='function'||typeof vault.authorizeSyntheticDataset!=='function'||
     typeof salesDirectory!=='string'||!salesScope||typeof salesScope!=='object'||
     (signedReview!==null&&(typeof signedReview!=='object'||Array.isArray(signedReview)))||
     typeof clock!=='function')INVALID();
  const scope=Object.freeze({tenantId:salesScope.tenantId,groups:Object.freeze([...salesScope.groups]),
    projects:Object.freeze([...salesScope.projects]),clearance:salesScope.clearance});
  return Object.freeze({assess(token,question,{documentIds=null,collection=null}={}){
    if(typeof question!=='string'||question.length<1||question.length>300)INVALID();
    const doc=vault.search(token,question,{documentIds,collection,limit:8});
    const wantsSales=/(?:총\s*매출|매출\s*총액|총\s*판매\s*금액)/u.test(question);
    const wantsPolicy=/(?:반품|환불|배송)/u.test(question);
    if(!wantsSales)return Object.freeze({...doc,status:doc.status,review_status:'NOT_REQUESTED'});
    // Unsafe scope (timeframe, SKU breakdown, arbitrary business rules) is never treated as full-period revenue.
    if(/(?:이번|지난|어제|오늘|최근|전월|전년|지난해|올해|평균|순이익|마진|수수료|SKU\s*별|제품\s*별|예측)/iu.test(question))
      return Object.freeze({status:'REVIEW_HOLD',answer:null,reason:'UNSUPPORTED_SALES_SCOPE',
        document_evidence:[],sql_evidence:null,network_calls:0});
    vault.authorizeSyntheticDataset(token,scope,salesDirectory); // no sales.csv opened before this point
    const data=inspectSyntheticSqlEvidence(salesDirectory);
    let signedReviewEvidence=Object.freeze({status:'NOT_CONFIGURED',signature_verified:false,
      source_rights_verified:false,customer_approval:false});
    if(signedReview!==null){
      try{
        signedReviewEvidence=verifySignedSyntheticSalesReview({
          source:data,config:signedReview,tenantId:scope.tenantId,nowMs:clock()});
      }catch{
        // No unverified provisional totals, citations, keys or paths cross this boundary.
        return Object.freeze({status:'REVIEW_HOLD',reason:'SIGNED_PROVENANCE_FAILED',
          answer:null,document_evidence:[],sql_evidence:null,
          signed_review:Object.freeze({status:'REVIEW_HOLD',signature_verified:false}),
          source_rights_verified:false,approved_customer_data:false,
          model_state:'UNAVAILABLE',network_calls:0});
      }
    }
    const state=doc.status==='POSSIBLE_CONFLICT'?'CONFLICT_HOLD':
      wantsPolicy&&!doc.evidence.length?'INSUFFICIENT_DOCUMENT_EVIDENCE':'APPROVAL_NOT_GRANTED';
    return Object.freeze({status:'REVIEW_HOLD',reason:state,answer:null,
      document_evidence:doc.evidence,
      sql_evidence:data,signed_review:signedReviewEvidence,
      source_rights_verified:false,approved_customer_data:false,
      model_state:'UNAVAILABLE',network_calls:0});
  }});
}
