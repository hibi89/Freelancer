/**
 * CITEVAULT AX P70 synthetic policy prototype.
 * NON-PRODUCTION: no enterprise identity provider, permissions database, source byte
 * verification or customer data; only a fail-closed, deterministic policy contract.
 */
const ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u;
const HEX = /^[a-f0-9]{64}$/u;
const UTC = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/u;
const STOP = new Set(['the','and','please','알려줘','알려주세요','이','그','무엇','대해']);
const plain = x => x !== null && typeof x === 'object' && !Array.isArray(x)
  && (Object.getPrototypeOf(x) === Object.prototype || Object.getPrototypeOf(x) === null);
const refuse = code => { throw Object.assign(new Error('CITEVAULT_P70_POLICY_REFUSED'), {code}); };
const exact = (x, fields) => plain(x) && Object.keys(x).length === fields.length
  && fields.every(k => Object.hasOwn(x,k));
const identifier = x => typeof x === 'string' && ID.test(x);
const uniqueIds = (x, cap = 32) => Array.isArray(x) && x.length <= cap
  && x.every(identifier) && new Set(x).size === x.length;
const validTime = x => typeof x === 'string' && UTC.test(x)
  && Number.isFinite(Date.parse(x)) && new Date(x).toISOString().replace('.000','') === x;
function verifyPrincipal(p) {
  if (!exact(p,['subject_id','tenant_id','groups','projects','clearance','identity_state'])
    || !identifier(p.subject_id) || !identifier(p.tenant_id)
    || !uniqueIds(p.groups) || !uniqueIds(p.projects)
    || !Number.isInteger(p.clearance) || p.clearance < 0 || p.clearance > 3
    || p.identity_state !== 'SYNTHETIC_ONLY') refuse('IDENTITY_NOT_VERIFIED');
  return p;
}
function verifyDocument(d) {
  if (!exact(d,['id','tenant_id','group_grants','project_grants','classification',
    'review_state','source_sha256','kind','version','expires_at_utc','lines'])
    || !identifier(d.id) || !identifier(d.tenant_id)
    || !uniqueIds(d.group_grants) || !uniqueIds(d.project_grants)
    || (!d.group_grants.length && !d.project_grants.length)
    || !Number.isInteger(d.classification) || d.classification < 0 || d.classification > 3
    || d.review_state !== 'SYNTHETIC_APPROVED'
    || typeof d.source_sha256 !== 'string' || !HEX.test(d.source_sha256)
    || !['pdf','docx','txt','md'].includes(d.kind) || !identifier(d.version)
    || !validTime(d.expires_at_utc)
    || !Array.isArray(d.lines) || d.lines.length < 1 || d.lines.length > 200
    || d.lines.some(x => typeof x !== 'string' || !x.trim() || x.length > 2048
      || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/u.test(x))) refuse('CATALOG_INVALID');
  return d;
}
function policyAllows(p,d,now) {
  if (p.tenant_id !== d.tenant_id || p.clearance < d.classification
    || Date.parse(d.expires_at_utc) <= now) return false;
  const groups = d.group_grants.length === 0
    || d.group_grants.some(x => p.groups.includes(x));
  const projects = d.project_grants.length === 0
    || d.project_grants.some(x => p.projects.includes(x));
  return groups && projects;
}
function terms(input) {
  const words = input.normalize('NFKC').toLowerCase().match(/[\p{Script=Hangul}]+|[a-z0-9]+/gu) || [];
  const result = [];
  for (const w of words) {
    if (STOP.has(w) || w.length < 2) continue;
    result.push(w);
    if (/^[\p{Script=Hangul}]+$/u.test(w)) {
      for (let i=0; i+2<=w.length; i++) result.push(w.slice(i,i+2));
      for (let i=0; i+3<=w.length; i++) result.push(w.slice(i,i+3));
    }
  }
  return result.slice(0,300);
}
const citation = (d,idx,quote) => Object.freeze({
  document_id:d.id,document_version:d.version,source_sha256:d.source_sha256,
  source_kind:d.kind,source_unit:d.kind === 'pdf' ? 'page' : d.kind === 'docx' ? 'paragraph' : 'line',
  source_number:idx+1,quote
});
function conflictInCorpus(chunks,question) {
  if (!/반품|환불/u.test(question)) return [];
  const matched = new Map();
  for (const c of chunks) {
    if (!/반품|환불/u.test(c.quote) || !/신청|가능|기간/u.test(c.quote)) continue;
    for (const match of c.quote.matchAll(/(\d{1,3})\s*일\s*이내/gu)) {
      if (!matched.has(match[1])) matched.set(match[1],c);
    }
  }
  return matched.size > 1 ? [...matched.values()].slice(0,2) : [];
}
/**
 * Search only in synthetic documents *after* tenant/role/project/clearance
 * filtering. No caller can pass actual production auth as a synthetic fixture.
 * All requested IDs must be authorized or the entire request is refused.
 */
export function querySyntheticEvidence({principal,catalog,question,now_utc,requested_ids=null,limit=5}) {
  const p = verifyPrincipal(principal);
  if (!Array.isArray(catalog) || catalog.length < 1 || catalog.length > 64
    || typeof question !== 'string' || !question.trim() || question.length > 300
    || !validTime(now_utc) || !Number.isInteger(limit) || limit < 1 || limit > 10
    || (requested_ids !== null && (!uniqueIds(requested_ids,8) || !requested_ids.length))) refuse('REQUEST_INVALID');
  const seen = new Set(), docs = catalog.map(d => {
    verifyDocument(d);
    const key = d.tenant_id + ':' + d.id;
    if (seen.has(key)) refuse('CATALOG_DUPLICATE');
    seen.add(key);
    return d;
  });
  const now = Date.parse(now_utc);
  const allowed = docs.filter(d => policyAllows(p,d,now));
  if (requested_ids !== null && requested_ids.some(id => !allowed.some(d => d.id === id)))
    return Object.freeze({status:'FORBIDDEN_OR_NOT_FOUND',answer:null,evidence:[],model_state:'UNAVAILABLE'});
  const visible = requested_ids === null ? allowed : allowed.filter(d => requested_ids.includes(d.id));
  if (!visible.length) return Object.freeze({status:'NO_ACCESSIBLE_EVIDENCE',answer:null,evidence:[],model_state:'UNAVAILABLE'});
  const chunks = [];
  for (const doc of visible) for(let i=0;i<doc.lines.length;i++) {
    if (chunks.length >= 1000) refuse('INDEX_BUDGET_EXCEEDED');
    chunks.push(citation(doc,i,doc.lines[i]));
  }
  const conflict = conflictInCorpus(chunks,question);
  if (conflict.length) return Object.freeze({
    status:'POSSIBLE_CONFLICT',answer:null,evidence:conflict,model_state:'UNAVAILABLE'
  });
  const q = [...new Set(terms(question))];
  if (!q.length) return Object.freeze({status:'INSUFFICIENT_EVIDENCE',answer:null,evidence:[],model_state:'UNAVAILABLE'});
  const tokenMaps = chunks.map(c => {
    const ts=terms(c.quote),m=new Map();
    for(const term of ts) m.set(term,(m.get(term)||0)+1);
    return {m,n:ts.length};
  });
  const df=new Map();
  for(const {m} of tokenMaps) for(const word of m.keys()) df.set(word,(df.get(word)||0)+1);
  const avg=tokenMaps.reduce((sum,x)=>sum+x.n,0)/tokenMaps.length || 1;
  const scored=chunks.map((c,i)=>{
    const {m,n}=tokenMaps[i];
    let s=0;
    for(const word of q) {
      const count=m.get(word)||0;
      if(!count)continue;
      const freq=df.get(word)||0;
      s+=Math.log(1+(chunks.length-freq+0.5)/(freq+0.5))
        *(count*2.2)/(count+1.2*(0.25+0.75*n/avg));
    }
    return {citation:c,score:s};
  }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score ||
    a.citation.document_id.localeCompare(b.citation.document_id) ||
    a.citation.source_number-b.citation.source_number);
  if (!scored.length) return Object.freeze({status:'INSUFFICIENT_EVIDENCE',answer:null,evidence:[],model_state:'UNAVAILABLE'});
  return Object.freeze({
    status:'SEARCH_ONLY',answer:null,
    evidence:scored.slice(0,limit).map(x=>x.citation),
    model_state:'UNAVAILABLE',network_calls:0,identity_verified:false
  });
}
/**
 * Pure PREP/SMAX *proposal* gate: an exact source digest string and column roles
 * cannot prove original bytes, reviewer identity or consent. Never promotes AX.
 */
export function assessSyntheticMapping({source,plan}) {
  if (!exact(source,['contract','sha256','headers','row_count','approval'])
    || source.contract !== 'SMAX_PREPROCESS_GENERIC_CSV_V1'
    || typeof source.sha256 !== 'string' || !HEX.test(source.sha256)
    || !uniqueIds(source.headers,32) || source.headers.length < 1
    || !Number.isSafeInteger(source.row_count) || source.row_count < 1 || source.row_count > 100000
    || source.approval !== 'NOT_GRANTED'
    || !exact(plan,['source_sha256','roles','tax_basis','review_state'])
    || plan.source_sha256 !== source.sha256
    || !plain(plan.roles) || !exact(plan.roles,['order_id','quantity','amount_krw'])
    || Object.values(plan.roles).some(x => !source.headers.includes(x))
    || new Set(Object.values(plan.roles)).size !== 3
    || !['TAX_INCLUDED','TAX_EXCLUDED','TAX_UNKNOWN'].includes(plan.tax_basis)
    || plan.review_state !== 'REVIEW_HOLD') refuse('REVIEW_INTENT_NOT_AUTHORITY');
  return Object.freeze({
    status:'REVIEW_HOLD',semantic_review:'UNVERIFIED',authenticated_reviewer:false,
    rights_verified:false,source_bytes_verified:false,ax_package_created:false,
    promotion:'BLOCKED',network_calls:0
  });
}
