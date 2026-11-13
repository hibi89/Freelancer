/**
 * CITEVAULT P85: isolated local synthetic tenant document vault.
 * Prototype only: no persistent IAM, no real customer rights verification, no signed
 * SMAX producer, no network listener or production permission changes.
 * Users cannot make this load a source before the tenant/group/project ACL check.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {extractVerifiedNativeBytes} from './p85-native-extract.mjs';
import {rankAuthorizedBM25} from './p85-bm25.mjs';

const ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u;
const SHA = /^[a-f0-9]{64}$/u;
const DENY = code => { throw Object.assign(new Error('CITEVAULT_VAULT_DENIED'), {code}); };
const id = x => typeof x === 'string' && ID.test(x);
const list = (x,n=32) => Array.isArray(x) && x.length<=n && x.every(id) && new Set(x).size===x.length;
const obj = x => x!==null && typeof x==='object' && !Array.isArray(x) && Object.getPrototypeOf(x)===Object.prototype;
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const same = (a,b) => crypto.timingSafeEqual(Buffer.from(a,'hex'), Buffer.from(b,'hex'));

export function createSyntheticAccount({userId,tenantId,groups=[],projects=[],clearance=0,admin=false,password}) {
  if (!id(userId)||!id(tenantId)||!list(groups)||!list(projects)||!Number.isInteger(clearance)
    || clearance<0||clearance>3||typeof admin!=='boolean'||typeof password!=='string'
    || password.length<12||password.length>128) DENY('ACCOUNT_INVALID');
  const salt=crypto.randomBytes(16).toString('hex');
  const password_scrypt=crypto.scryptSync(password,Buffer.from(salt,'hex'),32).toString('hex');
  return Object.freeze({userId,tenantId,groups:Object.freeze([...groups]),
    projects:Object.freeze([...projects]),clearance,admin,salt,password_scrypt});
}
function checkAccount(a) {
  if(!obj(a)||!id(a.userId)||!id(a.tenantId)||!list(a.groups)||!list(a.projects)
    ||!Number.isInteger(a.clearance)||a.clearance<0||a.clearance>3
    ||typeof a.admin!=='boolean'||typeof a.salt!=='string'||!(/^[a-f0-9]{32}$/u).test(a.salt)
    ||typeof a.password_scrypt!=='string'||!SHA.test(a.password_scrypt)) DENY('ACCOUNT_INVALID');
  return Object.freeze({...a,groups:Object.freeze([...a.groups]),projects:Object.freeze([...a.projects])});
}
function checkDoc(d) {
  if(!obj(d)||!id(d.id)||!id(d.tenantId)||!id(d.version)||!id(d.collection)
    ||!list(d.groups)||!list(d.projects)||(!d.groups.length&&!d.projects.length)
    ||!Number.isInteger(d.classification)||d.classification<0||d.classification>3
    ||typeof d.sha256!=='string'||!SHA.test(d.sha256)||d.reviewState!=='SYNTHETIC_APPROVED'
    ||typeof d.active!=='boolean'||(d.native_kind!==undefined&&!['txt','pdf','docx'].includes(d.native_kind))) DENY('CATALOG_INVALID');
  return Object.freeze({...d,groups:Object.freeze([...d.groups]),projects:Object.freeze([...d.projects])});
}
function checkedRoot(root) {
  if(typeof root!=='string'||!path.isAbsolute(root)) DENY('ROOT_INVALID');
  const abs=path.resolve(root);let cursor=path.parse(abs).root;
  try {for(const segment of path.relative(cursor,abs).split(path.sep)) {
    if(!segment)continue;cursor=path.join(cursor,segment);
    const st=fs.lstatSync(cursor);if(st.isSymbolicLink())DENY('UNSAFE_PATH');
  }
  if(!fs.lstatSync(abs).isDirectory())DENY('ROOT_INVALID');
  } catch(e) {if(e.code==='UNSAFE_PATH')throw e;DENY('ROOT_INVALID');}
  return abs;
}
function readDocument(root,meta) {
  const kind=meta.native_kind??'txt';
  const parent=path.join(root,meta.tenantId,meta.id), filename=path.join(parent,meta.version+'.'+kind);
  try {
    for(const dir of [path.join(root,meta.tenantId),parent]) {
      const st=fs.lstatSync(dir);if(!st.isDirectory()||st.isSymbolicLink())DENY('UNSAFE_SOURCE');
    }
    const st=fs.lstatSync(filename);
    if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1||st.size<1||st.size>(kind==='txt'?256*1024:2*1024*1024))
      DENY('UNSAFE_SOURCE');
    const fd=fs.openSync(filename,fs.constants.O_RDONLY|(fs.constants.O_NOFOLLOW||0));
    try {
      const opened=fs.fstatSync(fd);
      if(opened.dev!==st.dev||opened.ino!==st.ino||opened.size!==st.size||opened.mtimeMs!==st.mtimeMs)
        DENY('SOURCE_CHANGED');
      const bytes=fs.readFileSync(fd),after=fs.lstatSync(filename),fdafter=fs.fstatSync(fd);
      if(bytes.length!==st.size||after.dev!==st.dev||after.ino!==st.ino||
        after.size!==st.size||after.mtimeMs!==st.mtimeMs||fdafter.size!==st.size||
        fdafter.mtimeMs!==st.mtimeMs) DENY('SOURCE_CHANGED');
      if(!same(hash(bytes),meta.sha256))DENY('SOURCE_DIGEST_MISMATCH');
      if(kind!=='txt'){
        const extracted=extractVerifiedNativeBytes(bytes,kind);
        return extracted.map(c=>({document_id:meta.id,version:meta.version,
          source_sha256:meta.sha256,source_unit:c.source_unit,
          [c.source_unit]:c.position,quote:c.quote}));
      }
      const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
      if(text.includes('\0'))DENY('SOURCE_INVALID');
      const lines=text.replace(/\r\n/g,'\n').split('\n');
      if(lines.length>1000||lines.some(line=>line.length>4096))DENY('SOURCE_BUDGET');
      return lines.map((quote,i)=>({document_id:meta.id,version:meta.version,
        source_sha256:meta.sha256,source_unit:'line',line:i+1,quote:quote.trim()}))
        .filter(c=>c.quote);
    } finally {fs.closeSync(fd);}
  }catch(e){if(typeof e.code==='string'&&[
    'UNSAFE_SOURCE','SOURCE_CHANGED','SOURCE_DIGEST_MISMATCH','SOURCE_INVALID','SOURCE_BUDGET','NATIVE_HOLD'
  ].includes(e.code))throw e;DENY('SOURCE_UNAVAILABLE');}
}
const words=text=>{
  const raw=text.normalize('NFKC').toLowerCase().match(/[\p{Script=Hangul}]+|[a-z0-9]+/gu)||[];
  const output=[];for(const w of raw){if(w.length<2)continue;output.push(w);
    if(/^[\p{Script=Hangul}]+$/u.test(w))for(const n of [2,3])for(let i=0;i+n<=w.length;i++)output.push(w.slice(i,i+n));}
  return [...new Set(output)].slice(0,128);
};
function conflict(chunks,question){
  if(!/(?:반품|환불)/u.test(question))return [];
  const m=new Map();for(const c of chunks){if(!/(?:반품|환불)/u.test(c.quote)||
    !/(?:신청|가능|기간)/u.test(c.quote))continue;
    for(const v of c.quote.matchAll(/(\d{1,3})\s*일\s*이내/gu)) {
      if(!m.has(v[1]))m.set(v[1],c);
    }
  }return m.size>1?[...m.values()].slice(0,2):[];
}
export class LocalSyntheticVault {
  #root; #accounts; #docs; #sessions=new Map(); #clock; #audit=[]; #cache=new Map();
  #tries=new Map(); #generation=0; #disabled=new Set(); #stateStore=null;
  constructor({root,accounts,documents,clock=()=>Date.now(),stateStore=null}) {
    this.#root=checkedRoot(root);
    if(stateStore!==null){
      if(typeof stateStore.loadOrInitialize!=='function'||typeof stateStore.saveDocumentWithGeneration!=='function')DENY('STATE_STORE_INVALID');
      const saved=stateStore.loadOrInitialize({accounts,documents});
      accounts=saved.accounts;documents=saved.documents;
      this.#disabled=new Set(saved.disabled);this.#generation=saved.generation;
      this.#stateStore=stateStore;
    }
    if(!Array.isArray(accounts)||!accounts.length||accounts.length>100||
       !Array.isArray(documents)||!documents.length||documents.length>256||typeof clock!=='function')DENY('CONFIG_INVALID');
    this.#accounts=new Map();this.#docs=new Map();this.#clock=clock;
    for(const a0 of accounts){const a=checkAccount(a0);if(this.#accounts.has(a.userId))DENY('DUPLICATE_ACCOUNT');
      this.#accounts.set(a.userId,a);}
    for(const d0 of documents){const d=checkDoc(d0),key=d.tenantId+':'+d.id;
      if(this.#docs.has(key))DENY('DUPLICATE_DOCUMENT');this.#docs.set(key,d);}
  }
  #record(code,tenantId,alreadyPersisted=false){if(this.#stateStore&&!alreadyPersisted)this.#stateStore.auditEvent(tenantId,code,this.#clock());
    this.#audit.push(Object.freeze({event:code,epoch_ms:this.#clock(),tenantId}));
    if(this.#audit.length>1000)this.#audit.shift();}
  login(userId,password) {
    const a=this.#stateStore?this.#stateStore.loadAccount(userId):this.#accounts.get(userId),t=this.#clock(),tries=this.#tries.get(userId)||{count:0,until:0};
    if(tries.until>t)DENY('ACCESS_DENIED');
    const dummySalt='00000000000000000000000000000000';
    const salt=a?.salt||dummySalt,expected=a?.password_scrypt||'0'.repeat(64);
    const valid=typeof password==='string'&&password.length<=128&&
      same(crypto.scryptSync(password,Buffer.from(salt,'hex'),32).toString('hex'),expected);
    if(!valid||this.#disabled.has(userId)||(this.#stateStore&&!this.#stateStore.accountEnabled(userId))){const count=tries.count+1;this.#tries.set(userId,{count:count>=5?0:count,until:count>=5?t+60000:0});
      this.#record('LOGIN_DENIED',a?.tenantId??null);DENY('ACCESS_DENIED');}
    this.#tries.delete(userId);
    const token=crypto.randomBytes(32).toString('hex'),expiry=t+15*60*1000;
    this.#sessions.set(hash(token),{userId:a.userId,expires:expiry});this.#record('LOGIN_SUCCESS',a.tenantId);
    return Object.freeze({token,expires_at_ms:expiry});
  }
  #principal(token){
    if(typeof token!=='string'||!(/^[a-f0-9]{64}$/u).test(token))DENY('UNAUTHENTICATED');
    const key=hash(token),s=this.#sessions.get(key);
    if(!s||s.expires<=this.#clock()){this.#sessions.delete(key);DENY('UNAUTHENTICATED');}
    const p=this.#stateStore?this.#stateStore.loadAccount(s.userId):this.#accounts.get(s.userId);
    if(!p||this.#disabled.has(s.userId)||
      (this.#stateStore&&!this.#stateStore.accountEnabled(s.userId)))DENY('UNAUTHENTICATED');return p;
  }
  logout(token){const p=this.#principal(token);this.#sessions.delete(hash(token));this.#record('LOGOUT',p.tenantId);}
  #allow(p,d){return p.tenantId===d.tenantId&&d.active&&p.clearance>=d.classification&&
    (!d.groups.length||d.groups.some(x=>p.groups.includes(x)))&&
    (!d.projects.length||d.projects.some(x=>p.projects.includes(x)));}
  #get(p,docId){if(!id(docId))DENY('INVALID_DOCUMENT_ID');
    const loaded=this.#stateStore?this.#stateStore.documentMetadata(p.tenantId,docId):this.#docs.get(p.tenantId+':'+docId);
    const d=loaded?checkDoc(loaded):null;
    if(!d||!this.#allow(p,d))DENY('NOT_FOUND');return d;}
  source(token,docId){const p=this.#principal(token),d=this.#get(p,docId);
    const citations=readDocument(this.#root,d);this.#record('SOURCE_READ',p.tenantId);
    return Object.freeze({status:'SOURCE_ONLY',citations});}
  search(token,question,{documentIds=null,collection=null,limit=5}={}){
    const p=this.#principal(token);
    if(typeof question!=='string'||!question.trim()||question.length>300||
       !Number.isInteger(limit)||limit<1||limit>10||
       (collection!==null&&!id(collection))||
       (documentIds!==null&&(!list(documentIds,8)||documentIds.length===0)))DENY('QUERY_INVALID');
    const allDocs=this.#stateStore?this.#stateStore.listDocuments(p.tenantId).map(checkDoc):[...this.#docs.values()];
    const selection=documentIds===null?
      allDocs.filter(d=>this.#allow(p,d)&&
        (collection===null||d.collection===collection)):
      documentIds.map(x=>this.#get(p,x)); // complete ACL pass before any I/O
    if(documentIds!==null&&collection!==null&&selection.some(d=>d.collection!==collection))DENY('NOT_FOUND');
    const chunks=[];for(const d of selection){
      const source=readDocument(this.#root,d); // ACL-before-raw-read, no global loadPackage
      const key=d.tenantId+':'+d.id+':'+d.version;
      this.#cache.set(key,Object.freeze(source));chunks.push(...source);
      if(chunks.length>10000)DENY('QUERY_BUDGET');}
    const shared={answer:null,model_state:'UNAVAILABLE',network_calls:0,
      index_generation:this.#generation};
    const contradictory=conflict(chunks,question);
    if(contradictory.length){this.#record('CONFLICT_HOLD',p.tenantId);
      return Object.freeze({...shared,status:'POSSIBLE_CONFLICT',evidence:contradictory});}
    const evidence=rankAuthorizedBM25(chunks,question,limit);
    this.#record('SEARCH',p.tenantId);
    return Object.freeze({...shared,search_mode:'bm25_authorized_citations',
      status:evidence.length?'SEARCH_ONLY':'INSUFFICIENT_EVIDENCE',evidence});
  }
  /** Enforce server-side fixed synthetic dataset scope before opening CSV bytes. */
  authorizeSyntheticDataset(token,{tenantId,groups,projects,clearance},directory){
    const p=this.#principal(token);
    if(!id(tenantId)||!list(groups)||!list(projects)||groups.length===0||projects.length===0||
       !Number.isInteger(clearance)||clearance<1||clearance>3)DENY('SCOPE_INVALID');
    if(p.tenantId!==tenantId||p.clearance<clearance||
       (groups.length>0&&!groups.some(x=>p.groups.includes(x)))||
       (projects.length>0&&!projects.some(x=>p.projects.includes(x))))DENY('NOT_FOUND');
    // Bind synthetic data authorization to the exact tenant-owned source directory.
    // A caller-controlled scope label cannot authorize CSV bytes from another tenant.
    const expected=path.join(this.#root,tenantId,'sales-only');
    if(typeof directory!=='string'||!path.isAbsolute(directory)||
      path.resolve(directory)!==expected)DENY('SALES_PATH_SCOPE_MISMATCH');
    try{
      for(const part of [path.join(this.#root,tenantId),expected]){
        const st=fs.lstatSync(part);
        if(!st.isDirectory()||st.isSymbolicLink())DENY('SALES_PATH_UNSAFE');
      }
    }catch(e){if(e.code==='SALES_PATH_UNSAFE')throw e;DENY('SALES_PATH_UNSAFE');}
    return true;
  }
  #admin(token){const p=this.#principal(token);if(!p.admin)DENY('NOT_AUTHORIZED');return p;}
  reindex(token){const p=this.#admin(token),next=new Map();let count=0;
    const allDocs=this.#stateStore?this.#stateStore.listDocuments(p.tenantId).map(checkDoc):[...this.#docs.values()];
    for(const d of allDocs){if(d.tenantId!==p.tenantId||!d.active)continue;
      const key=d.tenantId+':'+d.id+':'+d.version;
      next.set(key,Object.freeze(readDocument(this.#root,d)));count++;}
    // Persist generation before in-memory mutation; no original files changed.
    if(this.#stateStore)this.#stateStore.setGeneration(this.#generation+1,p.tenantId,'REINDEX',this.#clock());
    // atomic in-memory cache generation, never mutates original files
    for(const key of this.#cache.keys())if(key.startsWith(p.tenantId+':'))this.#cache.delete(key);
    for(const [key,value] of next)this.#cache.set(key,value);
    this.#generation++;this.#record('REINDEX',p.tenantId,!!this.#stateStore);
    return Object.freeze({status:'REINDEXED',document_count:count,generation:this.#generation});
  }
  replaceVersion(token,docId,newVersion,sha256){
    const p=this.#admin(token),d=this.#get(p,docId);
    if(!id(newVersion)||newVersion===d.version||typeof sha256!=='string'||!SHA.test(sha256))DENY('VERSION_INVALID');
    const next=checkDoc({...d,version:newVersion,sha256});
    readDocument(this.#root,next); // exact source bytes checked before activating
    if(this.#stateStore)this.#stateStore.saveDocumentWithGeneration(next,this.#generation,'VERSION_CHANGED',this.#clock());
    this.#docs.set(p.tenantId+':'+docId,next);
    this.#cache.delete(p.tenantId+':'+docId+':'+d.version);
    this.#generation++;this.#record('VERSION_CHANGED',p.tenantId,!!this.#stateStore);
    return Object.freeze({status:'VERSION_ACTIVATED',version:newVersion,generation:this.#generation});
  }
  retire(token,docId){const p=this.#admin(token),d=this.#get(p,docId);
    const next=Object.freeze({...d,active:false});
    if(this.#stateStore)this.#stateStore.saveDocumentWithGeneration(next,this.#generation,'DOC_RETIRED',this.#clock());
    this.#docs.set(p.tenantId+':'+docId,next);
    for(const key of this.#cache.keys())if(key.startsWith(p.tenantId+':'+docId+':'))this.#cache.delete(key);
    this.#generation++;this.#record('DOC_RETIRED',p.tenantId,!!this.#stateStore);
    return Object.freeze({status:'RETIRED',generation:this.#generation});
  }
  /** Operator-controlled *local* employee accounts, not verified corporate IAM. */
  provisionUser(token,{userId,password,groups,projects,clearance}){
    const admin=this.#admin(token);
    if(!id(userId)||!list(groups)||!list(projects)||!groups.length||!projects.length||
       !Number.isInteger(clearance)||clearance<1||clearance>admin.clearance||
       !groups.every(x=>admin.groups.includes(x))||
       !projects.every(x=>admin.projects.includes(x)))DENY('ACCOUNT_SCOPE_INVALID');
    const account=createSyntheticAccount({userId,tenantId:admin.tenantId,
      groups,projects,clearance,admin:false,password});
    if(this.#stateStore)this.#stateStore.createUser(account,admin.tenantId,this.#clock());
    else {
      if(this.#accounts.has(userId)||this.#accounts.size>=100)DENY('ACCOUNT_EXISTS');
    }
    this.#accounts.set(userId,checkAccount(account));
    this.#record('USER_CREATED',admin.tenantId,!!this.#stateStore);
    return Object.freeze({status:'USER_CREATED',user_id:userId,tenant_id:admin.tenantId});
  }
  /** Existing sessions reread roles from SQLite on every request. */
  changeUserAccess(token,userId,{groups,projects,clearance}){
    const admin=this.#admin(token);
    if(!id(userId)||!list(groups)||!list(projects)||!groups.length||!projects.length||
       !Number.isInteger(clearance)||clearance<1||clearance>admin.clearance||
       !groups.every(x=>admin.groups.includes(x))||
       !projects.every(x=>admin.projects.includes(x)))DENY('ACCOUNT_SCOPE_INVALID');
    const old=this.#stateStore?this.#stateStore.loadAccount(userId):this.#accounts.get(userId);
    if(!old||old.tenantId!==admin.tenantId||old.admin)DENY('NOT_FOUND');
    const next=checkAccount({...old,groups:[...groups],projects:[...projects],clearance});
    if(this.#stateStore)this.#stateStore.replaceUserAccess(next,admin.tenantId,this.#clock());
    this.#accounts.set(userId,next);
    this.#record('USER_ACCESS_CHANGED',admin.tenantId,!!this.#stateStore);
    return Object.freeze({status:'USER_ACCESS_CHANGED',user_id:userId});
  }
  revokeAccount(token,userId){
    const admin=this.#admin(token),target=this.#stateStore?this.#stateStore.loadAccount(userId):this.#accounts.get(userId);
    if(!id(userId)||!target||target.tenantId!==admin.tenantId||userId===admin.userId)DENY('NOT_FOUND');
    if(this.#stateStore)this.#stateStore.disableAccount(userId,admin.tenantId,'USER_REVOKED',this.#clock());
    this.#disabled.add(userId);
    for(const [key,s] of this.#sessions)if(s.userId===userId)this.#sessions.delete(key);
    this.#record('USER_REVOKED',admin.tenantId,!!this.#stateStore);
    return Object.freeze({status:'REVOKED'});
  }
  audit(token){const p=this.#admin(token);
    if(this.#stateStore)return Object.freeze(this.#stateStore.events(p.tenantId));
    return Object.freeze(this.#audit.filter(x=>x.tenantId===p.tenantId).map(({event,epoch_ms})=>({event,epoch_ms})));} 
}
