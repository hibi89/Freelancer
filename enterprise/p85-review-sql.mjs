/** CITEVAULT: offline synthetic-only SQL cross-check. NEVER approved for export/answer. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {reviewSyntheticSalesDirectory} from './p70-local-review.mjs';

const fail=(code)=>{throw Object.assign(new Error('REVIEW_HOLD'),{code});};
const SHA=/^[a-f0-9]{64}$/;
const safe=/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/;
const MAX=BigInt(Number.MAX_SAFE_INTEGER);
const SQL_TOTALS='SELECT COUNT(*) AS orders, COALESCE(SUM(quantity),0) AS units, COALESCE(SUM(amount_krw),0) AS revenue_krw FROM sales';
const SQL_LINES='SELECT csv_line, order_id, amount_krw FROM sales ORDER BY csv_line';

function reReadBounded(dir){
  if(typeof dir!=='string'||!path.isAbsolute(dir))fail('SALES_ROOT_UNSAFE');
  const file=path.join(dir,'sales.csv');
  let fd;
  try{
    const st=fs.lstatSync(file);
    if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1||st.size<2||st.size>512*1024)
      fail('SALES_FILE_UNSAFE');
    fd=fs.openSync(file,fs.constants.O_RDONLY|(fs.constants.O_NOFOLLOW||0));
    const before=fs.fstatSync(fd);const bytes=fs.readFileSync(fd);const after=fs.fstatSync(fd);
    const latest=fs.lstatSync(file);
    if(before.dev!==st.dev||before.ino!==st.ino||before.size!==st.size||
       after.size!==st.size||latest.ino!==st.ino||latest.dev!==st.dev||
       after.mtimeMs!==before.mtimeMs||latest.mtimeMs!==before.mtimeMs||
       bytes.length!==st.size)fail('SALES_SOURCE_CHANGED');
    return bytes;
  }catch(e){if(e.message==='REVIEW_HOLD')throw e;fail('SALES_UNAVAILABLE');}
  finally{if(fd!==undefined)fs.closeSync(fd);}
}

/** Verifies P70 fixed mapping review first, then calculates independent SQLite totals. */
export function inspectSyntheticSqlEvidence(directory){
  const review=reviewSyntheticSalesDirectory(directory);
  if(review.status!=='REVIEW_HOLD'||review.approval!=='NOT_GRANTED'||
     review.source_rights_verified!==false||review.ax_package_created!==false||
     !SHA.test(review.source_sha256))fail('REVIEW_BOUNDARY_INVALID');
  const bytes=reReadBounded(directory);
  if(crypto.createHash('sha256').update(bytes).digest('hex')!==review.source_sha256)
    fail('SALES_DIGEST_CHANGED');
  let csv;
  try{csv=new TextDecoder('utf-8',{fatal:true}).decode(bytes).replace(/^\uFEFF/u,'');}
  catch{fail('SALES_UTF8_INVALID');}
  // Intentional narrow subset of P70's mapping/CSV parser; complex CSV is held, not silently reparsed.
  if(csv.includes('"')||csv.includes('\0')||csv.includes('\r'))fail('SALES_CSV_SUBSET_HOLD');
  const lines=csv.trimEnd().split('\n');
  if(lines.length!==review.source_rows+1||lines[0]!=='order_id,sku,quantity,unit_price_krw,amount_krw')
    fail('SALES_MAPPING_NOT_FIXED');
  const db=new DatabaseSync(':memory:');
  try{
    db.exec('CREATE TABLE sales (order_id TEXT PRIMARY KEY, sku TEXT NOT NULL, '+
      'quantity INTEGER NOT NULL CHECK(quantity>0), '+
      'unit_price_krw INTEGER NOT NULL CHECK(unit_price_krw>=0), '+
      'amount_krw INTEGER NOT NULL CHECK(amount_krw>=0),csv_line INTEGER NOT NULL UNIQUE)');
    const stmt=db.prepare('INSERT INTO sales (order_id,sku,quantity,unit_price_krw,amount_krw,csv_line) VALUES (?,?,?,?,?,?)');
    let exact=0n,units=0n;
    for(let index=1;index<lines.length;index++){
      const fields=lines[index].split(',');
      if(fields.length!==5||!safe.test(fields[0])||!safe.test(fields[1])||
        fields.slice(2).some(v=>!/^(?:0|[1-9][0-9]{0,12})$/.test(v)))fail('SALES_CSV_UNSUPPORTED');
      const [q,p,a]=fields.slice(2).map(v=>BigInt(v));
      if(q===0n||q>1000000n||p>1000000000n||a!==q*p||a>MAX)fail('SALES_AMOUNT_INVALID');
      units+=q;exact+=a;if(units>MAX||exact>MAX)fail('SALES_TOTAL_UNSAFE');
      stmt.run(fields[0],fields[1],Number(q),Number(p),Number(a),index+1);
    }
    db.exec('PRAGMA query_only=ON');
    const totals=db.prepare(SQL_TOTALS).get();
    if(!Number.isSafeInteger(totals.orders)||!Number.isSafeInteger(totals.units)||
       !Number.isSafeInteger(totals.revenue_krw)||totals.orders!==review.source_rows||
       BigInt(totals.units)!==units||BigInt(totals.revenue_krw)!==exact||
       units.toString()!==review.provisional_units||exact.toString()!==review.provisional_revenue_krw)
      fail('SQL_AGGREGATE_MISMATCH');
    // No arbitrary user SQL and never ship an approved AX_PACKAGE or generated answer.
    const evidence=db.prepare(SQL_LINES).all().map(row=>({csv_line:row.csv_line,
      order_id:row.order_id,amount_krw:String(row.amount_krw),source_sha256:review.source_sha256}));
    return Object.freeze({status:'REVIEW_HOLD',approval:'NOT_GRANTED',
      contract:'CITEVAULT_P85_PROVISIONAL_SQL_V1',engine:'node:sqlite :memory: fixed query_only',
      orders:totals.orders,units:units.toString(),provisional_revenue_krw:exact.toString(),
      evidence,source_sha256:review.source_sha256,row_lineage_verified:false,
      signed_producer_verified:false,source_rights_verified:false,generated_answer:null,
      network_calls:0,ax_package_created:false});
  }finally{db.close();}
}
