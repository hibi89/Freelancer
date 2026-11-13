import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {SyntheticVaultStateStore} from '../enterprise/p85-state-store.mjs';
import {extractVerifiedNativeBytes} from '../enterprise/p85-native-extract.mjs';
const hash=buf=>crypto.createHash('sha256').update(buf).digest('hex');
const maker=fileURLToPath(new URL('./p85-native-fixture.py',import.meta.url));

test('P85 actual PDF/DOCX native-bytes ACL suite',async t=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-native-'));
  t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  const f=spawnSync('python',['-I','-B',maker,root],{timeout:15000,encoding:'utf8'});
  assert.equal(f.status,0,'fixture failed: '+f.stderr?.slice(0,300));
  const paths={manualPdf:'orgA/manualPdf/v1.pdf',secretPdf:'orgA/secretPdf/v1.pdf',
    rulesDocx:'orgA/rulesDocx/v1.docx',compareDocx:'orgA/compareDocx/v1.docx'};
  const bytes={};for(const [id,rel] of Object.entries(paths))bytes[id]=fs.readFileSync(path.join(root,rel));
  const accounts=[
    createSyntheticAccount({userId:'alice',tenantId:'orgA',groups:['staff'],projects:['quality'],clearance:1,password:'P85_SYNTHETIC_ALICE_123'}),
    createSyntheticAccount({userId:'hr',tenantId:'orgA',groups:['hr'],projects:['payroll'],clearance:3,password:'P85_SYNTHETIC_HR_123'}),
    createSyntheticAccount({userId:'admin',tenantId:'orgA',groups:['staff','hr'],projects:['quality','payroll'],clearance:3,admin:true,password:'P85_SYNTHETIC_ADMIN_123'})
  ];
  const docs=Object.keys(paths).map(id=>({tenantId:'orgA',id,version:'v1',collection:id==='secretPdf'?'secret':'quality',
    native_kind:id.endsWith('Docx')?'docx':'pdf',groups:[id==='secretPdf'?'hr':'staff'],
    projects:[id==='secretPdf'?'payroll':'quality'],classification:id==='secretPdf'?3:1,
    reviewState:'SYNTHETIC_APPROVED',active:true,sha256:hash(bytes[id])}));
  const vault=()=>new LocalSyntheticVault({root,accounts,documents:docs});
  const login=(v,user='alice')=>v.login(user,user==='alice'?'P85_SYNTHETIC_ALICE_123':
    user==='admin'?'P85_SYNTHETIC_ADMIN_123':'P85_SYNTHETIC_HR_123').token;

  await t.test('PDF contains actual 2 pages with source page positions',()=>{
    const v=vault(),s=v.source(login(v),'manualPdf');
    assert.equal(s.citations.length,2);assert.deepEqual(s.citations.map(c=>c.page),[1,2]);
    assert.ok(s.citations.every(c=>c.source_unit==='page'));
    assert.match(s.citations[0].quote,/Product returns within 7 days/);
    assert.match(s.citations[1].quote,/Shipping starts within 2 business days/);
  });
  await t.test('DOCX actual OOXML yields correct Korean paragraph positions',()=>{
    const v=vault(),s=v.source(login(v),'rulesDocx');
    assert.equal(s.citations.length,2);assert.deepEqual(s.citations.map(c=>c.paragraph),[1,2]);
    assert.ok(s.citations.every(c=>c.source_unit==='paragraph'&&!Object.hasOwn(c,'page')));
    assert.match(s.citations[0].quote,/반품 신청은 14일 이내/);
  });
  await t.test('mixed PDF plus DOCX searched without generated answer',()=>{
    const v=vault(),r=v.search(login(v),'Product returns 반품 신청',{documentIds:['manualPdf','rulesDocx']});
    assert.equal(r.answer,null);assert.equal(r.network_calls,0);
    assert.equal(r.status,'SEARCH_ONLY');
    assert.ok(r.evidence.some(c=>c.document_id==='manualPdf'&&c.source_unit==='page'&&c.page===1));
    assert.ok(r.evidence.some(c=>c.document_id==='rulesDocx'&&c.source_unit==='paragraph'&&c.paragraph===1));
  });
  await t.test('two authorized native DOCX conflict causes full-source human HOLD',()=>{
    const v=vault(),r=v.search(login(v),'반품 신청 기간',{documentIds:['rulesDocx','compareDocx'],limit:1});
    assert.equal(r.status,'POSSIBLE_CONFLICT');assert.equal(r.answer,null);
    assert.deepEqual(new Set(r.evidence.map(c=>c.paragraph)),new Set([1]));
    assert.deepEqual(new Set(r.evidence.map(c=>c.document_id)),new Set(['rulesDocx','compareDocx']));
  });
  await t.test('unauthorized PDF ID forbidden with same NOT_FOUND as absent',()=>{
    const v=vault(),token=login(v);
    assert.throws(()=>v.source(token,'secretPdf'),{code:'NOT_FOUND'});
    assert.throws(()=>v.search(token,'SECRET',{documentIds:['manualPdf','secretPdf']}),{code:'NOT_FOUND'});
    assert.throws(()=>v.source(token,'missing'),{code:'NOT_FOUND'});
  });
  await t.test('confidential PDF not leaked to authorized full-corpus search',()=>{
    const v=vault(),r=v.search(login(v),'CONFIDENTIAL SECRET');
    assert.equal(r.status,'INSUFFICIENT_EVIDENCE');
    assert.doesNotMatch(JSON.stringify(r),/CONFIDENTIAL|secretPdf|ACME/);
  });
  await t.test('PDF source SHA tampering blocked before native parser',()=>{
    const original=path.join(root,paths.manualPdf),backup=fs.readFileSync(original);
    try{fs.appendFileSync(original,Buffer.from('TAMPER'));const v=vault();
      assert.throws(()=>v.source(login(v),'manualPdf'),{code:'SOURCE_DIGEST_MISMATCH'});
    }finally{fs.writeFileSync(original,backup);}
  });
  await t.test('DOCX hardlink and symlink rejected before parser',ctx=>{
    const source=path.join(root,paths.rulesDocx),alias=path.join(root,'alias.docx');
    fs.linkSync(source,alias);
    try{const v=vault();assert.throws(()=>v.source(login(v),'rulesDocx'),{code:'UNSAFE_SOURCE'});}
    finally{fs.rmSync(alias,{force:true});}
    const backup=source+'.back';fs.renameSync(source,backup);
    try{try{fs.symlinkSync(backup,source);}catch(e){ctx.diagnostic('OS symlink permission unavailable: '+e.code);return;}
      const v=vault();assert.throws(()=>v.source(login(v),'rulesDocx'),{code:'UNSAFE_SOURCE'});
    }finally{fs.rmSync(source,{force:true});fs.renameSync(backup,source);}
  });
  await t.test('corrupt PDF and DOCX bytes cannot be treated as evidence',()=>{
    for(const kind of ['pdf','docx']){
      assert.throws(()=>extractVerifiedNativeBytes(Buffer.from('not a valid '+kind+' document'),kind),{code:'NATIVE_HOLD'});
    }
  });
  await t.test('native parser never gets a filesystem path and returns no paths',()=>{
    const original=bytes.manualPdf,parsed=extractVerifiedNativeBytes(original,'pdf');
    assert.deepEqual(parsed.map(x=>x.position),[1,2]);
    assert.doesNotMatch(JSON.stringify(parsed),/citevault-native-|\/tmp\//);
    assert.throws(()=>extractVerifiedNativeBytes(original,'pdf',{python:'/bin/evil'}),{code:'NATIVE_HOLD'});
  });
  await t.test('persistent SQLite retains native-kind metadata after restart',()=>{
    const store=new SyntheticVaultStateStore({root});
    try{const first=new LocalSyntheticVault({root,accounts,documents:docs,stateStore:store});
      assert.equal(first.source(login(first),'rulesDocx').citations[0].source_unit,'paragraph');
    }finally{store.close();}
    const two=new SyntheticVaultStateStore({root});
    try{const next=new LocalSyntheticVault({root,accounts,documents:docs,stateStore:two});
      assert.equal(next.source(login(next),'manualPdf').citations[0].page,1);
    }finally{two.close();}
  });
  await t.test('native DOCX retire and version access remain permission-gated',()=>{
    const v=vault(),adm=login(v,'admin');
    assert.equal(v.retire(adm,'rulesDocx').status,'RETIRED');
    assert.throws(()=>v.source(login(v),'rulesDocx'),{code:'NOT_FOUND'});
    assert.deepEqual(fs.readFileSync(path.join(root,paths.rulesDocx)),bytes.rulesDocx);
  });
});
