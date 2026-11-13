/** Local-only synthetic HTTP harness for P85 vault, not a production customer API. */
import http from 'node:http';

const MAX_BODY=4096;
const send=(res,status,data)=>{
  if(res.headersSent)return;
  const out=JSON.stringify(data);
  res.writeHead(status,{'content-type':'application/json; charset=utf-8',
    'cache-control':'no-store','x-content-type-options':'nosniff',
    'content-security-policy':"default-src 'none'",'content-length':Buffer.byteLength(out)});
  res.end(out);
};
function decodeJson(bytes){
  try{const val=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
    if(val===null||typeof val!=='object'||Array.isArray(val))throw Error();
    return val;
  }catch{throw Object.assign(Error('INVALID_PAYLOAD'),{code:'INVALID_PAYLOAD'});}
}
async function body(req){
  const parts=[];let size=0;
  for await(const part of req){size+=part.length;
    if(size>MAX_BODY)throw Object.assign(Error('PAYLOAD_TOO_LARGE'),{code:'PAYLOAD_TOO_LARGE'});
    parts.push(part);
  }
  return decodeJson(Buffer.concat(parts));
}
const auth=req=>{
  const h=req.headers.authorization;
  return typeof h==='string'&&/^Bearer [a-f0-9]{64}$/u.test(h)?h.slice(7):'';
};
/** Opens an ephemeral IPv4-loopback listener only; no listener host override. */
export async function launchSyntheticLoopback(vault,{journey=null}={}){
  if(!vault||typeof vault.login!=='function'||typeof vault.search!=='function'||
    typeof vault.source!=='function'||typeof vault.retire!=='function')throw Error('VAULT_REQUIRED');
  const server=http.createServer(async(req,res)=>{
    try{
      if(req.socket.remoteAddress!=='127.0.0.1')return send(res,403,{error:'LOOPBACK_ONLY'});
      if(req.method==='POST'&&String(req.headers['content-type']||'').split(';')[0].trim().toLowerCase()!=='application/json')
        return send(res,415,{error:'JSON_REQUIRED'});
      if(req.method==='POST'&&req.url==='/v1/login'){
        const x=await body(req);
        return send(res,200,vault.login(x.userId,x.password));
      }
      const token=auth(req);
      if(req.method==='POST'&&req.url==='/v1/assess'&&journey){
        const x=await body(req);
        return send(res,200,journey.assess(token,x.question,{
          documentIds:x.documentIds??null,collection:x.collection??null}));
      }
      if(req.method==='POST'&&req.url==='/v1/search'){
        const x=await body(req);
        return send(res,200,vault.search(token,x.question,{
          documentIds:x.documentIds??null,collection:x.collection??null,
          limit:x.limit??5}));
      }
      if(req.method==='GET'&&(/^\/v1\/source\/[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u).test(req.url))
        return send(res,200,vault.source(token,req.url.slice('/v1/source/'.length)));
      if(req.method==='POST'&&req.url==='/v1/logout'){
        vault.logout(token);return send(res,200,{status:'LOGGED_OUT'});
      }
      if(req.method==='POST'&&req.url==='/v1/admin/reindex')
        return send(res,200,vault.reindex(token));
      if(req.method==='POST'&&req.url==='/v1/admin/revoke'){
        const x=await body(req);return send(res,200,vault.revokeAccount(token,x.userId));
      }
      if(req.method==='POST'&&req.url==='/v1/admin/retire'){
        const x=await body(req);return send(res,200,vault.retire(token,x.documentId));
      }
      if(req.method==='POST'&&req.url==='/v1/admin/version'){
        const x=await body(req);
        return send(res,200,vault.replaceVersion(token,x.documentId,x.version,x.sha256));
      }
      return send(res,404,{error:'NOT_FOUND'});
    }catch(e){
      const code=e?.code;
      const status=code==='UNAUTHENTICATED'||code==='ACCESS_DENIED'?401:
        code==='NOT_AUTHORIZED'?403:code==='NOT_FOUND'||code==='INVALID_DOCUMENT_ID'?404:
        code==='PAYLOAD_TOO_LARGE'?413:code==='SOURCE_DIGEST_MISMATCH'||
        code==='SOURCE_CHANGED'||code==='SOURCE_UNAVAILABLE'||code==='UNSAFE_SOURCE'?409:
        code==='INVALID_PAYLOAD'||code==='QUERY_INVALID'||code==='VERSION_INVALID'?422:500;
      if(status===500&&typeof code==='string'&&
        /^(?:SALES_|CSV_|SMAX_|PREP_|INPUT_|REVIEW_|SQL_)/.test(code))
        return send(res,409,{error:'REVIEW_HOLD'});
      send(res,status,{error:status===500?'INTERNAL_ERROR':code});
    }
  });
  server.requestTimeout=5000;server.headersTimeout=5000;
  await new Promise((resolve,reject)=>{
    server.once('error',reject);server.listen(0,'127.0.0.1',()=>{
      server.removeListener('error',reject);resolve();
    });
  });
  return Object.freeze({baseUrl:'http://127.0.0.1:'+server.address().port,
    close:()=>new Promise((resolve,reject)=>server.close(err=>err?reject(err):resolve()))});
}
