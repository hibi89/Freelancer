/**
 * CITEVAULT AX P70: synthetic-only adapter for the pinned original RAG engine.
 * Does not implement an authentication boundary. The upstream RAG loadPackage()
 * loads all source files into memory, so this MUST NOT be exposed to customers
 * as ACL enforcement; the policy is a search-scope development test only.
 */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {authorizeSyntheticDocumentScope} from './p70-policy.mjs';
import {validateAuthorizedCitations} from './p70-citation-contract.mjs';

const safeReturn=(status)=>Object.freeze({status,answer:null,evidence:[],
  model_state:'UNAVAILABLE',enterprise_identity_verified:false,
  approval:'NOT_GRANTED'});
function verifiedModuleFile(root,relative) {
  if(typeof root!=='string'||!path.isAbsolute(root))throw Error('ROOT_INVALID');
  const base=fs.realpathSync(root);
  const rootStat=fs.lstatSync(root);
  if(!rootStat.isDirectory()||rootStat.isSymbolicLink())throw Error('ROOT_INVALID');
  const selected=path.join(base,...relative.split('/'));
  const st=fs.lstatSync(selected);
  if(!st.isFile()||st.isSymbolicLink()||st.size>512*1024)throw Error('FILE_INVALID');
  return pathToFileURL(selected).href;
}
/** No raw original source data, path or exception is emitted on refusal. */
export async function queryPinnedRagSyntheticScope({
  principal,catalog,now_utc,requested_ids,question,rag_root,package_root
}) {
  const scope=authorizeSyntheticDocumentScope({principal,catalog,now_utc,requested_ids});
  if(scope.status!=='SYNTHETIC_SCOPE_ONLY')return safeReturn('FORBIDDEN_OR_NOT_FOUND');
  if(typeof question!=='string'||!question.trim()||question.length>300)
    return safeReturn('REQUEST_INVALID');
  try {
    const moduleUrl=verifiedModuleFile(rag_root,'src/knowledge-base.mjs');
    const packagePath=fs.realpathSync(package_root);
    if(!fs.lstatSync(package_root).isDirectory()||fs.lstatSync(package_root).isSymbolicLink())
      return safeReturn('SOURCE_INVALID');
    const original=await import(moduleUrl);
    if(typeof original.knowledgeSearch!=='function')
      return safeReturn('ENGINE_CONTRACT_MISMATCH');
    const answer=original.knowledgeSearch(packagePath,scope.document_ids,question,{mode:'bm25'});
    if(!validateAuthorizedCitations(answer,scope.document_ids))
      return safeReturn('ENGINE_CONTRACT_MISMATCH');
    if(answer.status==='POSSIBLE_CONFLICT')return Object.freeze({
      ...safeReturn('POSSIBLE_CONFLICT'),
      evidence:Object.freeze((answer.review_evidence||[]).slice(0,8).map(item=>({
        document_id:item.document_id,line:item.line,quote:item.quote
      })))
    });
    if(answer.status==='NO_EVIDENCE')return safeReturn('INSUFFICIENT_EVIDENCE');
    return Object.freeze({
      ...safeReturn('SEARCH_ONLY'),
      evidence:Object.freeze((answer.evidence||[]).slice(0,8).map(item=>({
        document_id:item.document_id,line:item.line,quote:item.quote
      })))
    });
  } catch {
    return safeReturn('REVIEW_HOLD');
  }
}
