/** Offline synthetic CITEVAULT demonstration. NOT a licensed production installation. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {createSyntheticReviewJourney} from '../enterprise/p85-journey.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const maker=fileURLToPath(new URL('../tests/p85-native-fixture.py',import.meta.url));
const review='order_id,sku,quantity,unit_price_krw,amount_krw\nA001,TV,2,10000,20000\nA002,BOOK,1,37000,37000\nA003,PC,4,25000,100000\n';
const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-offline-demo-'));
let api;
function clean(){try{fs.rmSync(root,{recursive:true,force:true});}catch{}}
async function close(){if(api){await api.close();api=null;}clean();}
try{
 const p=spawnSync('python',['-I','-B',maker,root],{timeout:15000,encoding:'utf8',windowsHide:true});
 if(p.status!==0)throw Error('SYNTHETIC_NATIVE_FIXTURE_FAILED');
 const dir=path.join(root,'orgA','sales-only');fs.mkdirSync(dir,{recursive:true});
 const sha=hash(Buffer.from(review));
 fs.writeFileSync(path.join(dir,'sales.csv'),review);
 fs.writeFileSync(path.join(dir,'smax-review.json'),JSON.stringify({contract:'SMAX_SYNTHETIC_REVIEW_V1',
   source_sha256:sha,headers:['order_id','sku','quantity','unit_price_krw','amount_krw'],row_count:3,approval:'NOT_GRANTED'}));
 fs.writeFileSync(path.join(dir,'prep-mapping.json'),JSON.stringify({contract:'PREP_SYNTHETIC_MAPPING_V1',
   source_sha256:sha,roles:{order_id:'order_id',sku:'sku',quantity:'quantity',unit_price_krw:'unit_price_krw',amount_krw:'amount_krw'},
   tax_basis:'TAX_UNKNOWN',review_state:'REVIEW_HOLD'}));
 const password=crypto.randomBytes(20).toString('base64url');
 const accounts=[createSyntheticAccount({userId:'demo',tenantId:'orgA',groups:['sales'],
   projects:['quality'],clearance:1,password})];
 const documents=[['manualPdf','pdf'],['rulesDocx','docx']].map(([id,native_kind])=>({
   id,native_kind,tenantId:'orgA',version:'v1',collection:'policies',groups:['sales'],projects:['quality'],
   classification:1,active:true,reviewState:'SYNTHETIC_APPROVED',
   sha256:hash(fs.readFileSync(path.join(root,'orgA',id,'v1.'+native_kind)))}));
 const vault=new LocalSyntheticVault({root,accounts,documents});
 const journey=createSyntheticReviewJourney({vault,salesDirectory:dir,salesScope:{tenantId:'orgA',groups:['sales'],projects:['quality'],clearance:1}});
 api=await launchSyntheticLoopback(vault,{journey});
 if(process.argv.includes('--self-test')){
   const session=vault.login('demo',password);
   const res=await fetch(api.baseUrl+'/v1/assess',{method:'POST',headers:{'content-type':'application/json',authorization:'Bearer '+session.token},
     body:JSON.stringify({question:'총매출 Product returns 반품 신청',documentIds:['manualPdf','rulesDocx']})});
   const data=await res.json();
   if(res.status!==200||data.status!=='REVIEW_HOLD'||data.answer!==null||
      data.sql_evidence?.provisional_revenue_krw!=='157000'||
      !data.document_evidence.some(x=>x.source_unit==='page')||
      !data.document_evidence.some(x=>x.source_unit==='paragraph'))throw Error('SYNTHETIC_SELF_TEST_FAILED');
   console.log(JSON.stringify({status:'PASS',offline:true,answer:null,review_state:'REVIEW_HOLD',
     sources:['pdf/page','docx/paragraph','sqlite/provisional']}));
   await close();
 }else{
   console.log('CITEVAULT synthetic-only offline demonstration; customer use NOT authorized');
   console.log('URL:',api.baseUrl,'user: demo','password:',password);
   console.log('POST /v1/login with JSON {"userId":"demo","password":"<printed password>"}');
   console.log('POST /v1/assess with Bearer token and JSON {"question":"총매출 Product returns 반품 신청","documentIds":["manualPdf","rulesDocx"]}');
   console.log('Returned status is REVIEW_HOLD by design, even when provisional totals match.');
   for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>{close().then(()=>process.exit(0)).catch(()=>process.exit(1));});
 }
}catch(e){await close();console.error('P85_SYNTHETIC_DEMO_ERROR:',e.message);process.exitCode=1;}
