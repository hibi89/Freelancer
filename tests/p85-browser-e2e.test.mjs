/** Headless real-Chromium UI acceptance on isolated synthetic localhost only.
 * Uses Node 22 WebSocket + installed Chrome CDP, no browser npm dependency.
 * Never tests customer documents or bypasses browser/network policy.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawn,spawnSync} from 'node:child_process';
import {LocalSyntheticVault,createSyntheticAccount} from '../enterprise/p85-vault.mjs';
import {launchSyntheticLoopback} from '../enterprise/p85-loopback.mjs';

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const chromeBin=()=>{
  for(const name of [process.env.CITEVAULT_CHROME_BIN,'/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable','/usr/bin/chromium','/usr/bin/chromium-browser']){
    if(name&&fs.existsSync(name))return name;
  }
  for(const cmd of ['google-chrome','chromium','chromium-browser']){
    const r=spawnSync('which',[cmd],{encoding:'utf8',timeout:2000});
    if(r.status===0&&r.stdout.trim())return r.stdout.trim();
  }
  return null;
};
async function poll(fn,name){
  for(let i=0;i<100;i++){if(await fn())return;await sleep(100);}
  throw Error('BROWSER_WAIT_TIMEOUT_'+name);
}
function cdp(socket){
  let next=0;const pending=new Map(),events=[];
  socket.addEventListener('message',e=>{
    let m;try{m=JSON.parse(e.data);}catch{return;}
    if(m.id&&pending.has(m.id)){
      const r=pending.get(m.id);pending.delete(m.id);clearTimeout(r.timer);
      m.error?r.reject(Error('CDP_ERROR_'+JSON.stringify(m.error))):r.resolve(m.result);
    }else if(m.method)events.push(m);
  });
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    const id=++next,timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP_TIMEOUT_'+method));},10000);
    pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));
  });
  const evaluate=async expression=>{
    const v=await send('Runtime.evaluate',{expression,returnByValue:true});
    if(v.exceptionDetails)throw Error('BROWSER_JS_'+v.exceptionDetails.text);
    return v.result?.value;
  };
  return {send,evaluate,events};
}
test('real rendered desktop/mobile login, scoped library, search and logout in Chromium',async t=>{
  const executable=chromeBin();assert.ok(executable,'CHROME_NOT_INSTALLED');
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-real-browser-'));
  const profile=path.join(root,'chrome-profile');
  const password='SYNTHETIC_BROWSER_LOGIN_2026_LONG';
  const sources=[['corpA','policy','반품 신청은 7일 이내 가능합니다.','staff','quality'],
    ['corpB','foreign','경영 비밀은 99일 이내.','managers','secret']];
  for(const [tenant,id,txt] of sources){
    const folder=path.join(root,tenant,id);fs.mkdirSync(folder,{recursive:true});
    fs.writeFileSync(path.join(folder,'v1.txt'),txt);
  }
  const account=createSyntheticAccount({userId:'tester',tenantId:'corpA',
    groups:['staff'],projects:['quality'],clearance:1,password});
  const documents=sources.map(([tenantId,id,txt,group,project])=>({
    tenantId,id,version:'v1',collection:'manuals',groups:[group],projects:[project],
    classification:1,active:true,reviewState:'SYNTHETIC_APPROVED',
    sha256:crypto.createHash('sha256').update(txt).digest('hex')
  }));
  const vault=new LocalSyntheticVault({root,accounts:[account],documents});
  const server=await launchSyntheticLoopback(vault);
  let chrome,ws;
  t.after(async()=>{
    try{ws?.close();}catch{}
    if(chrome&&!chrome.killed){
      const exited=new Promise(r=>chrome.once('exit',r));chrome.kill('SIGTERM');
      await Promise.race([exited,sleep(3000)]);
    }
    await server.close();fs.rmSync(root,{recursive:true,force:true});
  });
  chrome=spawn(executable,['--headless=new','--no-sandbox','--disable-dev-shm-usage',
    '--disable-background-networking','--no-first-run','--no-default-browser-check',
    '--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',
    '--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
  chrome.on('error',()=>{});
  let port=0;
  await poll(()=>{
    const active=path.join(profile,'DevToolsActivePort');
    if(fs.existsSync(active))port=Number(fs.readFileSync(active,'utf8').split('\n')[0]);
    return port>0;
  },'CHROME_START');
  const list=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  const tab=list.find(x=>x.type==='page'&&x.webSocketDebuggerUrl);
  assert.ok(tab,'NO_CHROME_PAGE');
  ws=new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
    ws.addEventListener('open',resolve,{once:true});
    ws.addEventListener('error',reject,{once:true});
  });
  const browser=cdp(ws);
  await browser.send('Page.enable');await browser.send('Runtime.enable');
  await browser.send('Network.enable');
  const nav=await browser.send('Page.navigate',{url:server.baseUrl+'/'});
  assert.ok(!nav.errorText,'BROWSER_NAVIGATION_'+nav.errorText);
  await poll(()=>browser.evaluate('document.readyState==="complete" && Boolean(document.getElementById("login"))'),'UI_READY');
  assert.equal(await browser.evaluate('document.querySelectorAll("#library-documents article").length'),0);
  await browser.evaluate('(()=>{document.getElementById("userid").value="tester";document.getElementById("pw").value="'+password+'";document.getElementById("login").requestSubmit();return true})()');
  await poll(()=>browser.evaluate('document.querySelectorAll("#library-documents article").length===1 && document.getElementById("library-status").textContent.includes("현재 계정")'),'SIGNED_IN_LIBRARY');
  const status=await browser.evaluate('({documents:document.getElementById("library-documents").textContent,kpi:document.getElementById("library-kpis").textContent,chart:document.getElementById("library-chart").textContent})');
  assert.match(status.documents,/policy/);assert.match(status.kpi,/허용 문서1/);
  assert.match(status.chart,/manuals/);assert.doesNotMatch(JSON.stringify(status),/foreign|corpB|99일|경영 비밀/);
  assert.equal(await browser.evaluate('(()=>{document.querySelector("#library-documents button").click();return document.getElementById("docids").value})()'),'policy');
  await browser.evaluate('(()=>{document.getElementById("question").value="반품 신청 기간";document.getElementById("query").requestSubmit();return true})()');
  await poll(()=>browser.evaluate('document.getElementById("result").textContent.includes("SEARCH_ONLY")'),'SCOPED_SEARCH');
  assert.match(await browser.evaluate('document.getElementById("result").textContent'),/문서 policy/);
  assert.equal(await browser.evaluate('Boolean(document.getElementById("conversation-start"))'),true);
  await browser.evaluate('document.getElementById("conversation-start").click()');
  await poll(()=>browser.evaluate('document.getElementById("conversation-status").textContent.includes("근거 대화 활성")'),'CHAT_CONTEXT_START');
  await browser.evaluate('(()=>{document.getElementById("question").value="그 기간은?";document.getElementById("conversation-next").click();return true})()');
  await poll(()=>browser.evaluate('document.getElementById("conversation-status").textContent.includes("재검증된 후속 검색")'),'CHAT_CONTEXT_FOLLOWUP');
  assert.match(await browser.evaluate('document.getElementById("result").textContent'),/문서 policy/);

  await browser.send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  const scrollWidth=await browser.evaluate('document.documentElement.scrollWidth');
  assert.ok(scrollWidth<=396,'MOBILE_HORIZONTAL_OVERFLOW_'+scrollWidth);
  const screenshot=await browser.send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  const screenshotBytes=Buffer.from(screenshot.data,'base64');
  assert.ok(screenshotBytes.length>2500,'CHROMIUM_SCREENSHOT_EMPTY');
  await browser.evaluate('document.getElementById("logout").click()');
  await poll(()=>browser.evaluate('document.getElementById("library-documents").childElementCount===0 && document.getElementById("library-status").textContent.includes("로그인")'),'LOGOUT_CLEARED_DATA');
  const outside=browser.events.filter(e=>e.method==='Network.requestWillBeSent')
    .map(e=>e.params?.request?.url).filter(u=>/^https?:\/\//.test(u||'')&&!u.startsWith(server.baseUrl+'/'));
  const exceptions=browser.events.filter(e=>e.method==='Runtime.exceptionThrown');
  assert.deepEqual(outside,[],'EXTERNAL_HTTP_REQUEST');
  assert.equal(exceptions.length,0,'CHROME_JS_RUNTIME_EXCEPTION');
  t.diagnostic(JSON.stringify({scope:'REAL_CHROMIUM_LOCAL_SYNTHETIC',mobile_width:390,
    actual_login:true,acl_dashboard:true,search:true,logout:true,remote_requests:0,
    screenshot_sha256:crypto.createHash('sha256').update(screenshotBytes).digest('hex'),
    physical_win10_11:false,customer_data:false}));
});
