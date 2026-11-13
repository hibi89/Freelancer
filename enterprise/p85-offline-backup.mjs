/** CITEVAULT P85: opt-in local snapshot and create-only restore for offline synthetic vaults.
 * Caller MUST stop the HTTP service and close state store before starting.
 * Never upload snapshots; no server endpoint; never write into an existing vault.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {DatabaseSync,backup as sqliteBackup} from 'node:sqlite';

const MAX_FILES=512,MAX_TOTAL=32*1024*1024,MAX_FILE=10*1024*1024;
const RESERVED=/^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const denied=code=>{throw Object.assign(Error('CITEVAULT_BACKUP_REFUSED'),{code});};
const validPart=p=>typeof p==='string'&&p.length>0&&p.length<=128&&!p.startsWith('.')&&
  !/[\x00-\x1f<>:"/\\|?*]/u.test(p)&&!/[. ]$/u.test(p)&&!RESERVED.test(p);
const allowedFile=(rel)=>rel==='citevault-synthetic-state.sqlite'||
  /\.(?:txt|md|pdf|docx|csv|json)$/iu.test(rel);
function safeBase(p){
  if(typeof p!=='string'||!path.isAbsolute(p))denied('PATH_NOT_ABSOLUTE');
  const absolute=path.resolve(p),root=path.parse(absolute).root;
  let curr=root;
  for(const part of path.relative(root,absolute).split(path.sep)){
    if(!part)continue;
    curr=path.join(curr,part);
    try {const st=fs.lstatSync(curr);if(!st.isDirectory()||st.isSymbolicLink())denied('UNSAFE_PARENT');}
    catch(e){if(e.code==='ENOENT')continue;throw e;}
  }
  return absolute;
}
function existingDir(p){
  const abs=safeBase(p);
  try{const st=fs.lstatSync(abs);if(!st.isDirectory()||st.isSymbolicLink())denied('UNSAFE_SOURCE');}
  catch(e){if(e.code==='ENOENT')denied('NOT_FOUND');throw e;}
  return abs;
}
function emptyDestination(p){
  const abs=safeBase(p);
  if(path.dirname(abs)===abs)denied('DESTINATION_ROOT');
  if(fs.existsSync(abs))denied('DESTINATION_EXISTS');
  existingDir(path.dirname(abs));
  return abs;
}
function walk(root,{excludeManifest=false}={}){
  const found=[],seen=new Set();let sum=0, dirs=0;
  function descend(relative){
    if(++dirs>MAX_FILES)denied('DIR_LIMIT');
    const folder=path.join(root,relative);
    for(const name of fs.readdirSync(folder).sort()){
      if(excludeManifest&&relative===''&&name==='manifest.json')continue;
      if(!validPart(name))denied('UNSAFE_NAME');
      const rel=relative?relative+'/'+name:name;
      const portable=rel.toLowerCase();if(seen.has(portable))denied('CASE_COLLISION');seen.add(portable);
      if(rel.split('/').length>8)denied('PATH_DEPTH');
      const file=path.join(root,...rel.split('/')),st=fs.lstatSync(file);
      if(st.isSymbolicLink())denied('SYMLINK');
      if(st.isDirectory()){descend(rel);continue;}
      if(!st.isFile()||st.nlink!==1||!allowedFile(rel)||st.size>MAX_FILE||st.size===0)
        denied('UNSAFE_FILE');
      if(++sum>MAX_FILES)denied('FILE_LIMIT');
      found.push(rel);
    }
  }
  descend('');
  if(!found.includes('citevault-synthetic-state.sqlite'))denied('SQLITE_REQUIRED');
  return found;
}
function readSecure(base,rel){
  const abs=path.join(base,...rel.split('/')),before=fs.lstatSync(abs);
  if(!before.isFile()||before.isSymbolicLink()||before.nlink!==1||before.size<1||before.size>MAX_FILE)
    denied('UNSAFE_FILE');
  const flags=fs.constants.O_RDONLY|(fs.constants.O_NOFOLLOW??0),fd=fs.openSync(abs,flags);
  try{
    const opened=fs.fstatSync(fd);
    if(opened.dev!==before.dev||opened.ino!==before.ino||opened.size!==before.size)denied('SOURCE_CHANGED');
    const data=fs.readFileSync(fd),after=fs.fstatSync(fd),pathNow=fs.lstatSync(abs);
    if(data.length!==before.size||after.size!==before.size||pathNow.ino!==before.ino||
      after.mtimeMs!==before.mtimeMs||pathNow.mtimeMs!==before.mtimeMs)denied('SOURCE_CHANGED');
    return data;
  }finally{fs.closeSync(fd);}
}
function dbVerify(dbFile){
  const db=new DatabaseSync(dbFile,{readOnly:true});
  try{
    if(db.prepare('PRAGMA quick_check').get()?.quick_check!=='ok')denied('SQLITE_CORRUPT');
    const tables=new Set(db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map(x=>x.name));
    if(!['header','users','docs','audit'].every(name=>tables.has(name)))denied('SQLITE_SCHEMA');
    const h=db.prepare('SELECT format,generation FROM header WHERE id=1').get();
    if(h?.format!==1||!Number.isSafeInteger(h.generation)||h.generation<0)denied('SQLITE_SCHEMA');
    const userCount=db.prepare('SELECT COUNT(*) AS n FROM users').get().n;
    const docs=db.prepare('SELECT tenant_id,doc_id,record FROM docs').all();
    if(userCount<1||userCount>100||docs.length<1||docs.length>256)denied('SQLITE_SCHEMA');
    return {generation:h.generation,docs};
  }catch(e){if(e?.code)throw e;denied('SQLITE_SCHEMA');}
  finally{db.close();}
}
/** Check the durable catalog against the copied files, not against mutable source paths.
 * A clean SQLite header alone must never count as a usable recovered vault.
 */
function verifyCatalog(stage,meta){
  const ids=/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/u;
  for(const row of meta.docs){
    let doc;try{doc=JSON.parse(row.record);}catch{denied('CATALOG_INVALID');}
    if(!doc||doc.tenantId!==row.tenant_id||doc.id!==row.doc_id||
       !ids.test(doc.tenantId)||!ids.test(doc.id)||!ids.test(doc.version)||
       !['txt','pdf','docx'].includes(doc.native_kind??'txt')||
       typeof doc.active!=='boolean'||typeof doc.sha256!=='string'||
       !/^[a-f0-9]{64}$/u.test(doc.sha256))denied('CATALOG_INVALID');
    if(!doc.active)continue; // retired documents need not retain raw source bytes.
    const rel=[doc.tenantId,doc.id,doc.version+'.'+(doc.native_kind??'txt')].join('/');
    let data;try{data=readSecure(stage,rel);}catch{denied('CATALOG_SOURCE_MISSING');}
    if(sha(data)!==doc.sha256)denied('CATALOG_DIGEST_MISMATCH');
  }
}
function ensureSubdir(root,rel){
  const parent=path.dirname(rel);if(parent!=='.')fs.mkdirSync(path.join(root,...parent.split('/')),{recursive:true,mode:0o700});
}
function writeSecure(root,rel,data){
  ensureSubdir(root,rel);
  const fd=fs.openSync(path.join(root,...rel.split('/')),fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL,0o600);
  try{fs.writeFileSync(fd,data);fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
}
function validateManifest(x){
  if(!x||typeof x!=='object'||Array.isArray(x)||x.format!=='CITEVAULT_OFFLINE_SNAPSHOT_V1'||
    !Array.isArray(x.files)||x.files.length<1||x.files.length>MAX_FILES||
    !Number.isSafeInteger(x.state_generation)||x.state_generation<0)denied('MANIFEST_INVALID');
  const seen=new Set();let sum=0;
  for(const it of x.files){
    if(!it||typeof it!=='object'||typeof it.path!=='string'||!it.path.split('/').every(validPart)||
       !allowedFile(it.path)||!Number.isSafeInteger(it.size)||it.size<1||it.size>MAX_FILE||
       typeof it.sha256!=='string'||!/^[a-f0-9]{64}$/.test(it.sha256))denied('MANIFEST_INVALID');
    const folded=it.path.toLowerCase();if(seen.has(folded))denied('MANIFEST_DUPLICATE');seen.add(folded);
    sum+=it.size;if(sum>MAX_TOTAL)denied('TOTAL_LIMIT');
  }
  if(!seen.has('citevault-synthetic-state.sqlite'))denied('SQLITE_REQUIRED');
}
/** Durable snapshot in an entirely new destination folder; no overwrite. */
export async function createOfflineSnapshot({root,destination}){
  const source=existingDir(root),target=emptyDestination(destination);
  if(target===source||target.startsWith(source+path.sep)||source.startsWith(target+path.sep))denied('PATH_OVERLAP');
  const paths=walk(source),stage=fs.mkdtempSync(path.join(path.dirname(target),'.citevault-stage-'));
  let published=false;
  try{
    const contents=[],dbPath=path.join(stage,'citevault-synthetic-state.sqlite');
    const db=new DatabaseSync(path.join(source,'citevault-synthetic-state.sqlite'),{readOnly:true});
    try{await sqliteBackup(db,dbPath);}finally{db.close();}
    const state=dbVerify(dbPath);
    const stateGeneration=state.generation;
    for(const rel of paths){
      const data=rel==='citevault-synthetic-state.sqlite'?readSecure(stage,rel):readSecure(source,rel);
      if(rel!=='citevault-synthetic-state.sqlite')writeSecure(stage,rel,data);
      contents.push({path:rel,size:data.length,sha256:sha(data)});
    }
    verifyCatalog(stage,state);
    const manifest={format:'CITEVAULT_OFFLINE_SNAPSHOT_V1',state_generation:stateGeneration,files:contents};
    validateManifest(manifest);
    fs.writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx',mode:0o600});
    fs.renameSync(stage,target);published=true;
    return {status:'SNAPSHOT_CREATED',files:contents.length,state_generation:stateGeneration};
  }finally{if(!published)fs.rmSync(stage,{recursive:true,force:true});}
}
/** Restore to a NEW directory only after fully validating manifest/data; no partial target. */
export function restoreOfflineSnapshot({snapshot,destination}){
  const source=existingDir(snapshot),target=emptyDestination(destination);
  if(target===source||target.startsWith(source+path.sep)||source.startsWith(target+path.sep))denied('PATH_OVERLAP');
  let m;
  try{
    const b=readSecure(source,'manifest.json');
    if(b.length>MAX_FILE)denied('MANIFEST_INVALID');m=JSON.parse(b.toString('utf8'));
  }catch(e){if(e.code)throw e;denied('MANIFEST_INVALID');}
  validateManifest(m);
  const actual=walk(source,{excludeManifest:true}).sort(),expected=m.files.map(f=>f.path).sort();
  // Reject undeclared payload, hidden siblings, and missing data. manifest is the only extra file.
  if(JSON.stringify(actual)!==JSON.stringify(expected))denied('FILE_SET_MISMATCH');
  const stage=fs.mkdtempSync(path.join(path.dirname(target),'.citevault-restore-'));
  let published=false;
  try{
    for(const file of m.files){
      const data=readSecure(source,file.path);
      if(data.length!==file.size||sha(data)!==file.sha256)denied('DIGEST_MISMATCH');
      writeSecure(stage,file.path,data);
    }
    const state=dbVerify(path.join(stage,'citevault-synthetic-state.sqlite'));
    if(state.generation!==m.state_generation)denied('SQLITE_GENERATION_MISMATCH');
    verifyCatalog(stage,state);
    fs.renameSync(stage,target);published=true;
    return {status:'RESTORED_CREATE_ONLY',files:m.files.length,state_generation:m.state_generation};
  }finally{if(!published)fs.rmSync(stage,{recursive:true,force:true});}
}
