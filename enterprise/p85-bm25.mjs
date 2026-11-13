/** Deterministic BM25 over caller-supplied, already-authorized SHA-verified citations. */
const STOP=new Set(['알려줘','알려주세요','설명해줘','무엇','뭐야','what','the','about','please','and','있는','관련','정책은']);
function terms(input){
 if(typeof input!=='string'||input.length>4096)throw Object.assign(Error('BM25_QUERY_INVALID'),{code:'QUERY_INVALID'});
 const words=input.normalize('NFKC').toLowerCase().match(/[\p{Script=Hangul}]+|[a-z0-9]+/gu)||[];
 const result=[];
 for(const w of words){if(w.length<2||STOP.has(w))continue;result.push(w);
  if(/^[\p{Script=Hangul}]+$/u.test(w))for(const n of [2,3])for(let i=0;i+n<=w.length;i++)result.push(w.slice(i,i+n));
 }
 return result.slice(0,2048);
}
/** No document bytes are read: all chunks must have passed ACL and source SHA checks. */
export function rankAuthorizedBM25(chunks,question,limit=5){
 if(!Array.isArray(chunks)||chunks.length>10000||!Number.isInteger(limit)||limit<1||limit>10||
   typeof question!=='string'||question.length>300)throw Object.assign(Error('BM25_INVALID'),{code:'QUERY_INVALID'});
 const q=[...new Set(terms(question))].slice(0,128);
 if(!q.length||!chunks.length)return [];
 const frequency=chunks.map(c=>{
  if(typeof c?.quote!=='string'||typeof c?.document_id!=='string')throw Object.assign(Error('BM25_CHUNK_INVALID'),{code:'QUERY_INVALID'});
  const values=terms(c.quote),counts=new Map();for(const x of values)counts.set(x,(counts.get(x)||0)+1);
  return {source:c,length:values.length,counts};
 });
 const N=frequency.length,avg=Math.max(1,frequency.reduce((n,x)=>n+x.length,0)/N);
 const docFreq=new Map();for(const x of frequency){for(const t of x.counts.keys())if(q.includes(t))docFreq.set(t,(docFreq.get(t)||0)+1);}
 const scored=[];
 for(const x of frequency){let score=0;
  for(const token of q){const tf=x.counts.get(token)||0;if(!tf)continue;
   const df=docFreq.get(token)||0,idf=Math.log(1+(N-df+.5)/(df+.5));
   const k=1.2,b=.75,den=tf+k*(1-b+b*x.length/avg);
   score+=idf*((tf*(k+1))/den);
  }
  if(score>0)scored.push({source:x.source,score});
 }
 return scored.sort((a,b)=>b.score-a.score||a.source.document_id.localeCompare(b.source.document_id)||
   (a.source.line??a.source.page??a.source.paragraph??0)-(b.source.line??b.source.page??b.source.paragraph??0))
  .slice(0,limit).map(x=>x.source);
}
