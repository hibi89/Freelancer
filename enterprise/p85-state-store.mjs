/**
 * CITEVAULT P85+ local synthetic-state durability prototype.
 * No raw document bodies, session tokens, live identities, or customer approvals.
 * Synchronous SQLite transactional metadata, not enterprise IAM production storage.
 */
import fs from 'node:fs';
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';

const ID=/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u;
const fail=code=>{throw Object.assign(new Error('CITEVAULT_STATE_REFUSED'),{code});};
const stringId=x=>typeof x==='string'&&ID.test(x);
function rootChecked(root){
  if(typeof root!=='string'||!path.isAbsolute(root))fail('ROOT_INVALID');
  const absolute=path.resolve(root),parts=path.relative(path.parse(absolute).root,absolute).split(path.sep);
  let cur=path.parse(absolute).root;
  try{
    for(const part of parts){if(!part)continue;cur=path.join(cur,part);
      if(fs.lstatSync(cur).isSymbolicLink())fail('SYMLINK_ROOT');}
    if(!fs.lstatSync(absolute).isDirectory())fail('ROOT_INVALID');
  }catch(e){if(e.code==='SYMLINK_ROOT'||e.code==='ROOT_INVALID')throw e;fail('ROOT_INVALID');}
  return absolute;
}
const parseRecord=v=>{try{const x=JSON.parse(v);if(!x||typeof x!=='object'||Array.isArray(x))fail('RECORD_INVALID');return x;}catch{fail('RECORD_INVALID');}};
export class SyntheticVaultStateStore {
  #db;
  constructor({root}){
    const dir=rootChecked(root),file=path.join(dir,'citevault-synthetic-state.sqlite');
    try{
      let stat;
      try{stat=fs.lstatSync(file);}catch(e){if(e.code!=='ENOENT')throw e;}
      if(stat&&(!stat.isFile()||stat.isSymbolicLink()||stat.nlink!==1||stat.size>10*1024*1024))fail('DATABASE_UNSAFE');
      if(!stat){const fd=fs.openSync(file,fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|(fs.constants.O_NOFOLLOW||0),0o600);fs.closeSync(fd);}
      const current=fs.lstatSync(file);
      if(!current.isFile()||current.isSymbolicLink()||current.nlink!==1)fail('DATABASE_UNSAFE');
      this.#db=new DatabaseSync(file);
      this.#db.exec('PRAGMA foreign_keys=ON; PRAGMA journal_mode=DELETE; PRAGMA busy_timeout=2000;');
      this.#db.exec(`CREATE TABLE IF NOT EXISTS header (id INTEGER PRIMARY KEY CHECK(id=1), format INTEGER NOT NULL, generation INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, record TEXT NOT NULL, disabled INTEGER NOT NULL CHECK(disabled IN (0,1)));
        CREATE TABLE IF NOT EXISTS docs (tenant_id TEXT NOT NULL, doc_id TEXT NOT NULL, record TEXT NOT NULL, PRIMARY KEY(tenant_id,doc_id));
        CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL, event TEXT NOT NULL, stamp_ms INTEGER NOT NULL);`);
      fs.chmodSync(file,0o600);
    }catch(e){if(this.#db){this.#db.close();this.#db=undefined;}
      if(e.code==='DATABASE_UNSAFE'||e.code==='ROOT_INVALID')throw e;fail('DATABASE_OPEN_FAILED');}
  }
  #transaction(fn){
    if(!this.#db)fail('DATABASE_CLOSED');
    try{this.#db.exec('BEGIN IMMEDIATE'); const result=fn();this.#db.exec('COMMIT');return result;}
    catch(e){try{this.#db.exec('ROLLBACK');}catch{}
      if(e.code&&typeof e.code==='string'&&e.code.startsWith('STATE_'))throw e;
      if(e.message==='CITEVAULT_STATE_REFUSED')throw e;
      fail('TRANSACTION_FAILED');}
  }
  /** On a restart existing entries ALWAYS take precedence over provided seeds. */
  loadOrInitialize({accounts,documents}){
    if(!Array.isArray(accounts)||!Array.isArray(documents))fail('SEED_INVALID');
    return this.#transaction(()=>{
      const meta=this.#db.prepare('SELECT format,generation FROM header WHERE id=1').get();
      if(!meta){
        if(accounts.length<1||accounts.length>100||documents.length<1||documents.length>256)fail('SEED_INVALID');
        const putAccount=this.#db.prepare('INSERT INTO users(user_id,tenant_id,record,disabled) VALUES(?,?,?,0)');
        for(const a of accounts){if(!stringId(a?.userId)||!stringId(a?.tenantId))fail('SEED_INVALID');
          putAccount.run(a.userId,a.tenantId,JSON.stringify(a));}
        const putDoc=this.#db.prepare('INSERT INTO docs(tenant_id,doc_id,record) VALUES(?,?,?)');
        for(const d of documents){if(!stringId(d?.tenantId)||!stringId(d?.id))fail('SEED_INVALID');
          putDoc.run(d.tenantId,d.id,JSON.stringify(d));}
        this.#db.prepare('INSERT INTO header(id,format,generation) VALUES(1,1,0)').run();
      }else if(meta.format!==1||meta.generation<0)fail('SCHEMA_UNSUPPORTED');
      const allAccounts=this.#db.prepare('SELECT record,disabled,user_id FROM users ORDER BY user_id').all();
      const allDocs=this.#db.prepare('SELECT record FROM docs ORDER BY tenant_id,doc_id').all();
      const generation=this.#db.prepare('SELECT generation FROM header WHERE id=1').get().generation;
      return {accounts:allAccounts.map(x=>parseRecord(x.record)),documents:allDocs.map(x=>parseRecord(x.record)),
        disabled:allAccounts.filter(x=>x.disabled===1).map(x=>x.user_id),generation};
    });
  }
  saveDocumentWithGeneration(doc,expectedGeneration,event,epoch){
    if(!stringId(doc?.tenantId)||!stringId(doc?.id)||!Number.isSafeInteger(expectedGeneration)||expectedGeneration<0)fail('DOCUMENT_INVALID');
    this.#transaction(()=>{
      const generation=this.#db.prepare('SELECT generation FROM header WHERE id=1').get()?.generation;
      if(generation!==expectedGeneration)fail('STALE_GENERATION');
      const r=this.#db.prepare('UPDATE docs SET record=? WHERE tenant_id=? AND doc_id=?')
        .run(JSON.stringify(doc),doc.tenantId,doc.id);
      if(r.changes!==1)fail('DOCUMENT_NOT_FOUND');
      this.#db.prepare('UPDATE header SET generation=? WHERE id=1').run(expectedGeneration+1);
      this.#writeAudit(doc.tenantId,event,epoch);
    });
  }
  accountEnabled(userId){
    if(!stringId(userId))return false;
    return this.#db.prepare('SELECT disabled FROM users WHERE user_id=?').get(userId)?.disabled===0;
  }
  currentGeneration(){return this.#db.prepare('SELECT generation FROM header WHERE id=1').get()?.generation;}
  documentMetadata(tenantId,docId){
    if(!stringId(tenantId)||!stringId(docId))return null;
    const result=this.#db.prepare('SELECT record FROM docs WHERE tenant_id=? AND doc_id=?').get(tenantId,docId);
    return result?parseRecord(result.record):null;
  }
  listDocuments(tenantId){
    if(!stringId(tenantId))fail('DOCUMENT_INVALID');
    return this.#db.prepare('SELECT record FROM docs WHERE tenant_id=? ORDER BY doc_id').all(tenantId).map(x=>parseRecord(x.record));
  }
  disableAccount(userId,tenantId,event,epoch){
    if(!stringId(userId)||!stringId(tenantId))fail('USER_INVALID');
    this.#transaction(()=>{
      const r=this.#db.prepare('UPDATE users SET disabled=1 WHERE user_id=? AND tenant_id=?')
        .run(userId,tenantId);
      if(r.changes!==1)fail('USER_NOT_FOUND');
      this.#writeAudit(tenantId,event,epoch);
    });
  }
  setGeneration(value,tenantId,event,epoch){
    if(!Number.isSafeInteger(value)||value<0)fail('GENERATION_INVALID');
    this.#transaction(()=>{
      const prior=this.#db.prepare('SELECT generation FROM header WHERE id=1').get();
      if(!prior||value!==prior.generation+1)fail('STALE_GENERATION');
      this.#db.prepare('UPDATE header SET generation=? WHERE id=1').run(value);
      this.#writeAudit(tenantId,event,epoch);
    });
  }
  #writeAudit(tenantId,event,epoch){
    if(!stringId(tenantId)||typeof event!=='string'||!(/^[A-Z_]{1,32}$/).test(event)
      ||!Number.isSafeInteger(epoch)||epoch<0)fail('AUDIT_INVALID');
    this.#db.prepare('INSERT INTO audit(tenant_id,event,stamp_ms) VALUES(?,?,?)').run(tenantId,event,epoch);
    this.#db.prepare('DELETE FROM audit WHERE id NOT IN (SELECT id FROM audit ORDER BY id DESC LIMIT 1000)').run();
  }
  auditEvent(tenantId,event,epoch){
    // Unknown account names never generate guessed tenant audit records.
    if(tenantId===null)return;
    this.#transaction(()=>this.#writeAudit(tenantId,event,epoch));
  }
  events(tenantId){
    if(!stringId(tenantId))fail('AUDIT_INVALID');
    return this.#db.prepare('SELECT event,stamp_ms FROM audit WHERE tenant_id=? ORDER BY id DESC LIMIT 1000')
      .all(tenantId).reverse().map(x=>Object.freeze({event:x.event,epoch_ms:x.stamp_ms}));
  }
  close(){if(this.#db){this.#db.close();this.#db=undefined;}}
}
