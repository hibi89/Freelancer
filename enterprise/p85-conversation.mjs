/** CITEVAULT: bounded, memory-only, evidence-grounded follow-up search.
 * No LLM, persistent chat history, raw source cache, remote calls or client data.
 */
import crypto from 'node:crypto';

const IDENT=/^[a-f0-9]{32}$/;
const TOKEN=/^[a-f0-9]{64}$/;
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const reject=code=>{throw Object.assign(Error('CONVERSATION_REJECTED'),{code});};
const invalid=()=>Object.freeze({status:'CONTEXT_INVALID',answer:null,evidence:[],
  model_state:'UNAVAILABLE',network_calls:0,conversation:null});

export class ScopedConversation {
  #vault;#clock;#threads=new Map();#ttl;#capacity;
  constructor(vault,{clock=()=>Date.now(),ttlMs=300000,capacity=64}={}){
    if(!vault||typeof vault.search!=='function'||typeof vault.source!=='function'||
       typeof clock!=='function'||!Number.isSafeInteger(ttlMs)||ttlMs<1000||ttlMs>900000||
       !Number.isInteger(capacity)||capacity<1||capacity>128)reject('CONFIG_INVALID');
    this.#vault=vault;this.#clock=clock;this.#ttl=ttlMs;this.#capacity=capacity;
  }
  forgetToken(token){
    if(typeof token!=='string'||!TOKEN.test(token))return;
    const owner=sha(token);
    for(const [id,entry] of this.#threads)if(entry.owner===owner)this.#threads.delete(id);
  }
  ask(token,{question,threadId=null,documentIds=null,collection=null,limit=5}={}){
    if(typeof token!=='string'||!TOKEN.test(token))reject('UNAUTHENTICATED');
    if(typeof question!=='string'||!question.trim()||question.length>300||
       !Number.isInteger(limit)||limit<1||limit>10)reject('QUERY_INVALID');
    const now=this.#clock(),owner=sha(token);
    for(const [id,c] of this.#threads)if(now>=c.expires)this.#threads.delete(id);
    if(threadId!==null){
      if(typeof threadId!=='string'||!IDENT.test(threadId)||documentIds!==null||collection!==null)
        reject('QUERY_INVALID');
      const entry=this.#threads.get(threadId);
      if(!entry||entry.owner!==owner)return invalid();
      // Verify ALL last-referenced sources under current token and current ACL before retrieval.
      for(const state of entry.sources){
        let read;
        try{read=this.#vault.source(token,state.id);}
        catch(e){
          this.#threads.delete(threadId);
          if(e?.code==='UNAUTHENTICATED')throw e;
          return invalid();
        }
        const citations=read?.citations;
        if(!Array.isArray(citations)||!citations.length||
           !citations.every(c=>c.version===state.version&&c.source_sha256===state.digest)){
          this.#threads.delete(threadId);return invalid();
        }
      }
      const prior=entry.lastQuestion.slice(0,Math.max(0,299-question.length));
      const contextual=[prior,question].filter(Boolean).join(' ').slice(0,300);
      const result=this.#vault.search(token,contextual,{documentIds:entry.sources.map(s=>s.id),limit});
      // Search output only carries newly verified evidence. Keep bound source digests, not raw quotes.
      entry.lastQuestion=question;entry.expires=now+this.#ttl;
      this.#threads.delete(threadId);this.#threads.set(threadId,entry);
      return Object.freeze({...result,conversation:Object.freeze({
        thread_id:threadId,continuation:true,expires_in_s:Math.ceil(this.#ttl/1000)
      })});
    }
    const result=this.#vault.search(token,question,{documentIds,collection,limit});
    if(result.status!=='SEARCH_ONLY'||!Array.isArray(result.evidence)||!result.evidence.length)
      return Object.freeze({...result,conversation:null});
    const sources=new Map();
    for(const ev of result.evidence){
      if(typeof ev.document_id!=='string'||typeof ev.version!=='string'||
         typeof ev.source_sha256!=='string')return Object.freeze({...result,conversation:null});
      const current=sources.get(ev.document_id);
      const item={id:ev.document_id,version:ev.version,digest:ev.source_sha256};
      if(current&&(current.version!==item.version||current.digest!==item.digest))
        return Object.freeze({...result,conversation:null});
      sources.set(ev.document_id,item);
    }
    if(sources.size>8)return Object.freeze({...result,conversation:null});
    // First result has already passed the vault's ACL and digest checks.
    if(this.#threads.size>=this.#capacity)this.#threads.delete(this.#threads.keys().next().value);
    const id=crypto.randomBytes(16).toString('hex');
    this.#threads.set(id,{owner,lastQuestion:question,sources:[...sources.values()],
      expires:now+this.#ttl});
    return Object.freeze({...result,conversation:Object.freeze({
      thread_id:id,continuation:false,expires_in_s:Math.ceil(this.#ttl/1000)
    })});
  }
}
