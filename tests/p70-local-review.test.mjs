import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {reviewSyntheticSalesDirectory as review} from '../enterprise/p70-local-review.mjs';

const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const roles={order_id:'order_key',sku:'item',quantity:'units',unit_price_krw:'rate',amount_krw:'gross'};
const csv='order_key,item,units,rate,gross\nORD-001,N-01,2,10000,20000\nORD-002,N-02,3,5000,15000\n';
function fixture(t,raw=csv){
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-p70-review-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  fs.writeFileSync(path.join(dir,'sales.csv'),raw);
  const bytes=fs.readFileSync(path.join(dir,'sales.csv'));
  const source={contract:'SMAX_SYNTHETIC_REVIEW_V1',source_sha256:digest(bytes),
    headers:['order_key','item','units','rate','gross'],row_count:2,approval:'NOT_GRANTED'};
  const plan={contract:'PREP_SYNTHETIC_MAPPING_V1',source_sha256:digest(bytes),
    roles:{...roles},tax_basis:'TAX_UNKNOWN',review_state:'REVIEW_HOLD'};
  function save(s=source,p=plan){
    fs.writeFileSync(path.join(dir,'smax-review.json'),JSON.stringify(s));
    fs.writeFileSync(path.join(dir,'prep-mapping.json'),JSON.stringify(p));
  }
  save();
  return {dir,bytes,source,plan,save};
}
test('P70 real bytes, exact digest, role-bound row amounts produce REVIEW_HOLD only',t=>{
  const x=fixture(t),before=fs.readFileSync(path.join(x.dir,'sales.csv'));
  const r=review(x.dir);
  assert.equal(r.status,'REVIEW_HOLD');assert.equal(r.source_rows,2);
  assert.equal(r.provisional_revenue_krw,'35000');assert.equal(r.provisional_units,'5');
  assert.equal(r.source_sha256,digest(before));assert.equal(r.mapping_exactly_bound,true);
  assert.equal(r.ax_package_created,false);assert.equal(r.approval,'NOT_GRANTED');
  assert.equal(r.original_smax_verified,false);assert.equal(r.authenticated_reviewer,false);
  assert.equal(r.row_lineage_verified,false);
  assert.equal(r.network_calls,0);assert.equal(r.tax_basis,'TAX_UNKNOWN');
  assert.deepEqual(fs.readFileSync(path.join(x.dir,'sales.csv')),before);
  assert.doesNotMatch(JSON.stringify(r),/ORD-001|N-01|citevault-p70-review-/);
});
test('P70 forged SMAX approval is refused',t=>{
  const x=fixture(t);x.save({...x.source,approval:'GRANTED'},x.plan);
  assert.throws(()=>review(x.dir),{code:'SMAX_SOURCE_MISMATCH'});
});
test('P70 forged PREP approval is refused',t=>{
  const x=fixture(t);x.save(x.source,{...x.plan,review_state:'ACCEPTED'});
  assert.throws(()=>review(x.dir),{code:'PREP_MAPPING_UNAPPROVED'});
});
test('P70 stale SHA in either source or plan refuses',t=>{
  const x=fixture(t);x.save({...x.source,source_sha256:'0'.repeat(64)},x.plan);
  assert.throws(()=>review(x.dir),{code:'SMAX_SOURCE_MISMATCH'});
  x.save(x.source,{...x.plan,source_sha256:'0'.repeat(64)});
  assert.throws(()=>review(x.dir),{code:'PREP_MAPPING_UNAPPROVED'});
});
test('P70 source header order mismatch refuses',t=>{
  const x=fixture(t);x.save({...x.source,headers:[...x.source.headers].reverse()},x.plan);
  assert.throws(()=>review(x.dir),{code:'SMAX_SOURCE_MISMATCH'});
});
test('P70 incorrect mapping, duplicate roles, and tax ambiguity block',t=>{
  const x=fixture(t);
  for(const role of [{...roles,amount_krw:'units'},{...roles,order_id:'missing'}]){
    x.save(x.source,{...x.plan,roles:role});
    assert.throws(()=>review(x.dir),{code:'PREP_MAPPING_UNAPPROVED'});
  }
  x.save(x.source,{...x.plan,tax_basis:'TAX_INCLUDED'});
  assert.throws(()=>review(x.dir),{code:'PREP_MAPPING_UNAPPROVED'});
});
test('P70 row sum is not accepted when total differs from quantity times rate',t=>{
  const x=fixture(t,csv.replace('3,5000,15000','3,5000,15500'));
  assert.throws(()=>review(x.dir),{code:'CSV_AMOUNT_MISMATCH'});
});
test('P70 duplicate order IDs refuse rather than merge',t=>{
  const x=fixture(t,csv.replace('ORD-002','ORD-001'));
  assert.throws(()=>review(x.dir),{code:'CSV_ID_OR_DUPLICATE'});
});
test('P70 spreadsheet formula ID payload is refused',t=>{
  const x=fixture(t,csv.replace('ORD-002','=HYPERLINK'));
  assert.throws(()=>review(x.dir),{code:'CSV_ID_OR_DUPLICATE'});
});
test('P70 invalid UTF-8 bytes fail closed',t=>{
  const x=fixture(t);
  fs.appendFileSync(path.join(x.dir,'sales.csv'),Buffer.from([0xff]));
  assert.throws(()=>review(x.dir),{code:'INVALID_UTF8'});
});
test('P70 invalid JSON never emits contents or a local path',t=>{
  const x=fixture(t);fs.writeFileSync(path.join(x.dir,'prep-mapping.json'),'{ "secret":');
  assert.throws(()=>review(x.dir),{code:'INVALID_JSON'});
  try{review(x.dir);}catch(e){assert.doesNotMatch(e.message, /secret|citevault-p70-review-/);}
});
test('P70 unsupported relative directory refuses',()=>{
  assert.throws(()=>review('relative/input'),{code:'ABSOLUTE_DIRECTORY_REQUIRED'});
});
test('P70 source symlink cannot be read',t=>{
  const x=fixture(t),original=path.join(x.dir,'sales.csv'),target=path.join(x.dir,'source.txt');
  fs.renameSync(original,target);
  try{fs.symlinkSync(target,original);}catch(e){return t.skip(e.code);}
  assert.throws(()=>review(x.dir),{code:'INPUT_UNSAFE'});
});
test('P70 input hardlink cannot be read',t=>{
  const x=fixture(t),alias=path.join(x.dir,'alias.csv');
  try{fs.linkSync(path.join(x.dir,'sales.csv'),alias);}catch(e){return t.skip(e.code);}
  assert.throws(()=>review(x.dir),{code:'INPUT_UNSAFE'});
});
test('P70 a symlink root directory cannot be read',t=>{
  const x=fixture(t),alias=x.dir+'-linked';
  try{fs.symlinkSync(x.dir,alias,'dir');}catch(e){return t.skip(e.code);}
  t.after(()=>fs.rmSync(alias,{force:true}));
  assert.throws(()=>review(alias),{code:'SYMLINK_COMPONENT'});
});
test('P70 reject malformed/unclosed CSV quoting',t=>{
  const x=fixture(t,csv.replace('ORD-002','"ORD-002'));
  assert.throws(()=>review(x.dir),{code:'CSV_UNTERMINATED_QUOTE'});
});
test('P70 only five unique bound headers are accepted',t=>{
  const x=fixture(t,csv.replace('order_key,item,units,rate,gross','order_key,item,units,rate,rate'));
  assert.throws(()=>review(x.dir),{code:'CSV_HEADERS'});
});
