/** CITEVAULT P70 review-only PREP/SMAX boundary over local synthetic CSV bytes.
 * Neither a producer signature verifier nor corporate data permission service.
 * Always holds source export: not an AX_DATA_PACKAGE producer.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const fail=code=>{throw Object.assign(new Error('CITEVAULT_REVIEW_BLOCKED'),{code});};
const ID=/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u,HEX=/^[a-f0-9]{64}$/u;
const required=['order_id','sku','quantity','unit_price_krw','amount_krw'];
const plain=x=>x!==null&&typeof x==='object'&&!Array.isArray(x)
  && Object.getPrototypeOf(x)===Object.prototype;
const exact=(obj,keys)=>plain(obj)&&Object.keys(obj).length===keys.length
  && keys.every(k=>Object.hasOwn(obj,k));
function rootDir(input){
  if(typeof input!=='string'||!path.isAbsolute(input))fail('ABSOLUTE_DIRECTORY_REQUIRED');
  const full=path.resolve(input),parts=path.relative(path.parse(full).root,full).split(path.sep);
  let current=path.parse(full).root;
  try {
    for(const p of parts){if(!p)continue;current=path.join(current,p);
      if(fs.lstatSync(current).isSymbolicLink())fail('SYMLINK_COMPONENT');}
    if(!fs.lstatSync(full).isDirectory())fail('DIRECTORY_INVALID');
  }catch(e){if(e.code&&e.code.startsWith('SYMLINK'))throw e;fail('DIRECTORY_INVALID');}
  return full;
}
function readFileBounded(dir,name,max){
  const filename=path.join(dir,name);
  try {
    const before=fs.lstatSync(filename);
    if(!before.isFile()||before.isSymbolicLink()||before.nlink!==1||before.size<2||before.size>max)
      fail('INPUT_UNSAFE');
    const fd=fs.openSync(filename,fs.constants.O_RDONLY|(fs.constants.O_NOFOLLOW||0));
    try {
      const open=fs.fstatSync(fd);
      if(open.dev!==before.dev||open.ino!==before.ino||open.size!==before.size||open.mtimeMs!==before.mtimeMs)
        fail('INPUT_CHANGED');
      const bytes=fs.readFileSync(fd);
      const after=fs.lstatSync(filename),openAfter=fs.fstatSync(fd);
      if(bytes.length!==before.size||after.dev!==before.dev||after.ino!==before.ino||
        after.size!==before.size||after.mtimeMs!==before.mtimeMs||
        openAfter.size!==before.size||openAfter.mtimeMs!==before.mtimeMs)
        fail('INPUT_CHANGED');
      return bytes;
    }finally{fs.closeSync(fd);}
  }catch(e){if(typeof e.code==='string'&&['INPUT_UNSAFE','INPUT_CHANGED'].includes(e.code))throw e;
    fail('INPUT_NOT_READABLE');}
}
function utf8(bytes){
  try {return new TextDecoder('utf-8',{fatal:true}).decode(bytes).replace(/^\uFEFF/u,'');}
  catch {fail('INVALID_UTF8');}
}
function parseJson(bytes){
  try{return JSON.parse(utf8(bytes));}catch{fail('INVALID_JSON');}
}
function csvRows(bytes){
  const txt=utf8(bytes);
  if(txt.length>500000||txt.includes('\0'))fail('CSV_BUDGET');
  const rows=[];let row=[],value='',quoted=false,finishedQuote=false,started=false;
  function field(){row.push(value);value='';started=false;finishedQuote=false;
    if(row.length>32)fail('CSV_COLUMNS');}
  function line(){field();if(row.some(v=>v.length>256)||rows.length>=1001)fail('CSV_BUDGET');
    rows.push(row);row=[];}
  for(let i=0;i<txt.length;i++){
    const ch=txt[i];
    if(quoted){if(ch==='"'){if(txt[i+1]==='"'){value+='"';i++;}else{quoted=false;finishedQuote=true;}}
      else{value+=ch;}continue;}
    if(ch==='"'){if(started||finishedQuote)fail('CSV_QUOTE');quoted=true;started=true;continue;}
    if(ch===','){field();continue;}
    if(ch==='\n'||ch==='\r'){
      if(ch==='\r'&&txt[i+1]==='\n')i++;
      line();continue;
    }
    if(finishedQuote)fail('CSV_QUOTE');
    value+=ch;started=true;
    if(value.length>256)fail('CSV_CELL_BUDGET');
  }
  if(quoted)fail('CSV_UNTERMINATED_QUOTE');
  if(value.length||row.length||started||finishedQuote)line();
  if(rows.length<2)fail('CSV_EMPTY');
  const columns=rows[0];
  if(columns.length!==5||new Set(columns).size!==5||columns.some(x=>!ID.test(x)))fail('CSV_HEADERS');
  if(rows.slice(1).some(r=>r.length!==columns.length||r.some(x=>x.includes('\n')||x.includes('\r'))))
    fail('CSV_ROWS');
  return {columns,rows:rows.slice(1)};
}
function positiveInteger(s,max){
  if(typeof s!=='string'||!/^[0-9]{1,12}$/u.test(s))fail('CSV_NUMERIC');
  const v=BigInt(s);
  if(v<0n||v>max)fail('CSV_NUMERIC');
  return v;
}
/** Only fixed three files from a local synthetic fixture directory are read. */
export function reviewSyntheticSalesDirectory(dir){
  const root=rootDir(dir),csv=readFileBounded(root,'sales.csv',512*1024);
  const source=parseJson(readFileBounded(root,'smax-review.json',16*1024));
  const plan=parseJson(readFileBounded(root,'prep-mapping.json',16*1024));
  const hash=crypto.createHash('sha256').update(csv).digest('hex');
  const {columns,rows}=csvRows(csv);
  if(!exact(source,['contract','source_sha256','headers','row_count','approval'])||
      source.contract!=='SMAX_SYNTHETIC_REVIEW_V1'||source.approval!=='NOT_GRANTED'||
      typeof source.source_sha256!=='string'||!HEX.test(source.source_sha256)||
      hash!==source.source_sha256||!Array.isArray(source.headers)||
      JSON.stringify(source.headers)!==JSON.stringify(columns)||
      source.row_count!==rows.length)fail('SMAX_SOURCE_MISMATCH');
  if(!exact(plan,['contract','source_sha256','roles','tax_basis','review_state'])||
      plan.contract!=='PREP_SYNTHETIC_MAPPING_V1'||plan.source_sha256!==hash||
      plan.tax_basis!=='TAX_UNKNOWN'||plan.review_state!=='REVIEW_HOLD'||
      !exact(plan.roles,required)||Object.values(plan.roles).some(x=>!columns.includes(x))||
      new Set(Object.values(plan.roles)).size!==5)fail('PREP_MAPPING_UNAPPROVED');
  const slots=required.map(k=>columns.indexOf(plan.roles[k]));
  let revenue=0n,units=0n;const seen=new Set();
  for(const row of rows){
    const [order,sku,q,p,a]=slots.map(i=>row[i]);
    if(!ID.test(order)||!ID.test(sku)||seen.has(order))fail('CSV_ID_OR_DUPLICATE');
    seen.add(order);
    const qty=positiveInteger(q,1000000n),price=positiveInteger(p,1000000000n);
    const amount=positiveInteger(a,9007199254740991n);
    if(qty===0n||amount!==qty*price)fail('CSV_AMOUNT_MISMATCH');
    revenue+=amount;units+=qty;
    if(revenue>9007199254740991n||units>9007199254740991n)fail('CSV_TOTAL_UNSAFE');
  }
  // Snapshot the bytes after validation, without treating this as a cryptographic producer signature.
  if(!crypto.timingSafeEqual(crypto.createHash('sha256').update(readFileBounded(root,'sales.csv',512*1024)).digest(),
       crypto.createHash('sha256').update(csv).digest()))fail('SOURCE_CHANGED');
  return Object.freeze({contract:'CITEVAULT_SYNTHETIC_REVIEW_V1',status:'REVIEW_HOLD',
    source_digest_verified:true,source_sha256:hash,mapping_exactly_bound:true,
    row_lineage_verified:false,source_rows:rows.length,provisional_units:units.toString(),
    provisional_revenue_krw:revenue.toString(),tax_basis:'TAX_UNKNOWN',
    approval:'NOT_GRANTED',authenticated_reviewer:false,source_rights_verified:false,
    original_smax_verified:false,ax_package_created:false,network_calls:0});
}
