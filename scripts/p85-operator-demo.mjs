/** Synthetic-only user administration + browser UI demonstration. No real data. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {SyntheticVaultStateStore} from '../enterprise/p85-state-store.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-operator-demo-'));
const password=crypto.randomBytes(24).toString('base64url');
let store,api;
async function stop(){if(api){await api.close();api=null;}if(store){store.close();store=null;}
 fs.rmSync(root,{recursive:true,force:true});}
try{
 const sample='반품 신청은 7일 이내 가능합니다.\n안전 점검은 2일 이내 진행합니다.';
 const folder=path.join(root,'sandbox','policy');fs.mkdirSync(folder,{recursive:true});
 fs.writeFileSync(path.join(folder,'v1.txt'),sample);
 const accounts=[createSyntheticAccount({userId:'operator',tenantId:'sandbox',groups:['staff','admin'],
   projects:['quality'],clearance:3,admin:true,password})];
 const documents=[{tenantId:'sandbox',id:'policy',version:'v1',native_kind:'txt',collection:'manuals',
   groups:['staff'],projects:['quality'],classification:1,active:true,
   reviewState:'SYNTHETIC_APPROVED',sha256:digest(Buffer.from(sample))}];
 store=new SyntheticVaultStateStore({root});
 const vault=new LocalSyntheticVault({root,accounts,documents,stateStore:store});
 api=await launchSyntheticLoopback(vault);
 if(process.argv.includes('--self-test')){
  const req=async(p,b,token)=>fetch(api.baseUrl+p,{method:'POST',headers:{'content-type':'application/json',
   ...(token?{authorization:'Bearer '+token}:{})},body:JSON.stringify(b)});
  const ui=await fetch(api.baseUrl+'/');
  if(ui.status!==200||!(await ui.text()).includes('로컬 계정 로그인'))throw Error('UI_NOT_READY');
  const result=await req('/v1/login',{userId:'operator',password});
  if(result.status!==200)throw Error('OPERATOR_LOGIN_FAILED');
  const token=(await result.json()).token;
  const create=await req('/v1/admin/provision',{userId:'newhire',password:'SYNTHETIC_NEW_HIRE_2026',groups:['staff'],projects:['quality'],clearance:1},token);
  if(create.status!==201)throw Error('USER_CREATE_FAILED');
  const member=await req('/v1/login',{userId:'newhire',password:'SYNTHETIC_NEW_HIRE_2026'});
  if(member.status!==200)throw Error('NEW_USER_LOGIN_FAILED');
  const access=(await member.json()).token;
  const search=await req('/v1/search',{question:'반품 신청 기간',documentIds:['policy']},access);
  if(search.status!==200||(await search.json()).status!=='SEARCH_ONLY')throw Error('SEARCH_FAILED');
  const deny=await req('/v1/admin/revoke',{userId:'newhire'},token);
  if(deny.status!==200)throw Error('REVOKE_FAILED');
  const blocked=await req('/v1/search',{question:'반품',documentIds:['policy']},access);
  if(blocked.status!==401)throw Error('SESSION_NOT_REVOKED');
  console.log(JSON.stringify({status:'PASS',ui:true,offline:true,operator:true,
   user_provision:true,search:'SEARCH_ONLY',revoke:true,remote_calls:0}));
  await stop();
 }else{
  console.log('CITEVAULT AX local SYNTHETIC-ONLY operator demo. Customer use NOT APPROVED.');
  console.log('Open browser: '+api.baseUrl+'/');
  console.log('Synthetic operator: operator | one-time password: '+password);
  console.log('Do not enter customer files or credentials; Ctrl+C deletes this temporary demo.');
  for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>stop().then(()=>process.exit(0)).catch(()=>process.exit(1)));
 }
}catch(e){console.error('P85_OPERATOR_DEMO_ERROR:',e.message);await stop();process.exitCode=1;}
