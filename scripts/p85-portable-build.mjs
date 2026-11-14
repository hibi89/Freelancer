/** CITEVAULT AX synthetic-only Windows portable acceptance bundle builder.
 * Packages installed Node22 + strictly allowlisted local source. Does not publish artifacts.
 * Must pass redistributable license review before commercial/customer delivery.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const reject=code=>{throw Object.assign(Error('PORTABLE_BUILD_REFUSED'),{code});};
const srcRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const files=[
  'scripts/p85-operator-demo.mjs',
  'enterprise/p85-vault.mjs',
  'enterprise/p85-state-store.mjs',
  'enterprise/p85-loopback.mjs',
  'enterprise/p85-ui.mjs',
  'enterprise/p85-bm25.mjs',
  'enterprise/p85-native-extract.mjs',
  'enterprise/p85-native-extract.py',
  'enterprise/p85-conversation.mjs'
];
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function safeParent(target){
  if(!path.isAbsolute(target)||path.parse(target).root===path.resolve(target))reject('UNSAFE_DEST');
  const absolute=path.resolve(target);
  if(fs.existsSync(absolute))reject('DESTINATION_EXISTS');
  const parent=path.dirname(absolute);
  if(!fs.existsSync(parent)||!fs.statSync(parent).isDirectory())reject('PARENT_NOT_FOUND');
  if(absolute.startsWith(srcRoot+path.sep)||srcRoot.startsWith(absolute+path.sep))reject('PATH_OVERLAP');
  let current=path.parse(parent).root;
  for(const segment of path.relative(current,parent).split(path.sep)){
    if(!segment)continue;
    current=path.join(current,segment);
    const st=fs.lstatSync(current);
    if(!st.isDirectory()||st.isSymbolicLink())reject('UNSAFE_PARENT');
  }
  return absolute;
}
export function buildPortable({destination,nodeExecutable=process.execPath}){
  if(process.platform!=='win32')reject('WINDOWS_ONLY');
  if(!process.versions.node.startsWith('22.'))reject('NODE22_REQUIRED');
  const target=safeParent(destination),stage=fs.mkdtempSync(path.join(path.dirname(target),'.citevault-portable-stage-'));
  let published=false;
  try{
    const installed=fs.statSync(nodeExecutable);
    if(!installed.isFile()||installed.size<1024*1024||!nodeExecutable.toLowerCase().endsWith('.exe'))
      reject('NODE_BINARY_INVALID');
    fs.mkdirSync(path.join(stage,'runtime'),{recursive:true});
    fs.copyFileSync(nodeExecutable,path.join(stage,'runtime','node.exe'));
    const manifest={format:'CITEVAULT_P85_SYNTHETIC_PORTABLE_V1',
      target:'windows-x64',node_version:process.versions.node,external_calls:0,
      customer_release_approved:false,files:[]};
    const exe=fs.readFileSync(path.join(stage,'runtime','node.exe'));
    manifest.files.push({path:'runtime/node.exe',size:exe.length,sha256:sha(exe)});
    for(const rel of files){
      const source=path.join(srcRoot,...rel.split('/'));
      const st=fs.lstatSync(source);
      if(!st.isFile()||st.isSymbolicLink()||st.nlink!==1||st.size===0||st.size>1024*1024)
        reject('SOURCE_UNSAFE');
      const bytes=fs.readFileSync(source);
      const dest=path.join(stage,...rel.split('/'));
      fs.mkdirSync(path.dirname(dest),{recursive:true});
      fs.writeFileSync(dest,bytes,{flag:'wx'});
      manifest.files.push({path:rel,size:bytes.length,sha256:sha(bytes)});
    }
    const notice=[
      'CITEVAULT AX - SYNTHETIC TEST BUILD ONLY',
      'All data in the included operator demo is made up locally and deleted at exit.',
      'This bundle has no approved customer identity provider, Korean model, or licensed document set.',
      'The embedded Node.js executable is for internal QA only. Review Node.js and third-party',
      'redistribution licenses and include proper notices before any customer distribution.',
      'Run Start-CITEVAULT-Synthetic.cmd (test: --self-test). Ctrl+C stops local service.',
      'Only binds to http://127.0.0.1:<ephemeral-port>. No cloud/API calls in the demo.',
      'Do not use customer files, accounts, secrets or payment details.',
      ''
    ].join('\r\n');
    fs.writeFileSync(path.join(stage,'NOTICE.txt'),notice,{flag:'wx'});
    const launcher=[
      '@echo off','setlocal','cd /d "%~dp0"',
      'echo CITEVAULT AX — SYNTHETIC OFFLINE EVALUATION ONLY',
      '".\\runtime\\node.exe" ".\\scripts\\p85-operator-demo.mjs" %*',
      'exit /b %ERRORLEVEL%',''
    ].join('\r\n');
    fs.writeFileSync(path.join(stage,'Start-CITEVAULT-Synthetic.cmd'),launcher,{flag:'wx'});
    for(const rel of ['NOTICE.txt','Start-CITEVAULT-Synthetic.cmd']){
      const bytes=fs.readFileSync(path.join(stage,rel));
      manifest.files.push({path:rel,size:bytes.length,sha256:sha(bytes)});
    }
    fs.writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
    fs.renameSync(stage,target);published=true;
    return {status:'SYNTHETIC_PORTABLE_CREATED',files:manifest.files.length,
      node_version:manifest.node_version,release_approved:false,network_calls:0};
  }finally{if(!published)fs.rmSync(stage,{recursive:true,force:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const args=process.argv.slice(2);
  try{
    if(args.length!==2||args[0]!=='--dest')reject('USAGE');
    process.stdout.write(JSON.stringify(buildPortable({destination:args[1]}))+'\n');
  }catch(e){process.stderr.write(JSON.stringify({ok:false,error:e?.code??'BUILD_FAILED'})+'\n');process.exitCode=1;}
}
