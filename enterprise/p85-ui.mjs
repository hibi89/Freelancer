/** Static, dependency-free loopback-only demo UI; customer data use is NOT authorized. */
export const html=`<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CITEVAULT AX — 오프라인 검증</title><link rel="stylesheet" href="/ui.css" defer></head>
<body><main><header><h1>CITEVAULT <span>AX</span></h1><p class="tag">근거 기반 문서 검색 <span class="test-pill">합성 데이터 검증판</span></p></header>
<section aria-label="로그인" class="login-panel"><h2>1. 로그인</h2><form id="login"><label>계정 <input id="userid" required autocomplete="username" maxlength="64"></label>
<label>비밀번호 <input id="pw" type="password" required autocomplete="current-password" maxlength="128"></label>
<button type="submit">로그인</button><button type="button" id="logout">로그아웃</button></form></section>
<section aria-label="근거 검색" class="search-panel"><h2>2. 문서에 질문하기</h2>
<p class="tag">질문을 입력하면 접근 가능한 문서에서 근거를 찾아 보여줍니다.</p>
<form id="query"><label class="question-field" for="question">무엇이 궁금하세요?<input id="question" required maxlength="300" placeholder="예: 반품 신청 기간은?"></label>
<button type="submit" class="primary-cta">근거 검색</button>
<details id="search-options" class="advanced"><summary>고급 검색 설정</summary>
<label for="docids">특정 문서 ID (선택)<input id="docids" maxlength="300" placeholder="비우면 허용된 모든 문서"></label>
<button type="button" id="assess">문서·SQL 검토 요청</button>
<p class="tag">검토 대상 데이터는 승인 전까지 REVIEW_HOLD 상태입니다.</p></details></form>
<div class="conversation-tools"><span class="tag">연속 질문</span>
<button type="button" id="conversation-start">대화 시작</button>
<button type="button" id="conversation-next">후속 질문</button></div>
<p id="conversation-status" class="tag" role="status" aria-live="polite">근거가 있는 대화만 5분 동안 이어집니다.</p>
<div id="result" role="status" aria-live="polite"></div></section>
<section aria-label="허용 문서 탐색" class="library-panel"><h2>내 문서</h2>
<p class="tag">현재 계정에 허용된 문서만 표시합니다.</p>
<div id="library-status" role="status" aria-live="polite">로그인이 필요합니다.</div>
<div id="library-kpis" class="kpis" aria-label="문서 지표"></div>
<details id="library-details" class="advanced"><summary>문서 목록과 상세 현황</summary>
<button id="refresh-library" type="button">목록 새로고침</button>
<div id="library-chart" aria-label="컬렉션별 허용 문서수"></div>
<div id="library-documents" aria-label="권한 있는 문서 목록"></div></details></section>
<details id="admin-panel" class="advanced"><summary>관리자 설정 (고급)</summary><section aria-label="운영자"><h2>로컬 계정 관리</h2>
<form id="operator"><label>대상 사용자 ID <input id="target" required maxlength="64"></label>
<label>초기 비밀번호 (신규 계정만 입력) <input id="newpw" type="password" autocomplete="new-password" maxlength="128"></label>
<label>그룹 (쉼표 구분) <input id="groups" required maxlength="256"></label>
<label>프로젝트 (쉼표 구분) <input id="projects" required maxlength="256"></label>
<label>등급 (1~3) <input id="clearance" type="number" min="1" max="3" value="1" required></label>
<button type="submit" id="createuser">계정 발급</button><button type="button" id="access">권한 변경</button><button type="button" id="revoke">계정 철회</button></form>
<p id="adminresult" role="status" aria-live="polite"></p></section></details>
<footer>데이터 외부 전송 없음 · 임시 로컬 데모 · 원본 자료 권리 승인 별도</footer></main><script src="/ui.js" defer></script></body></html>`;
export const css=`:root{color-scheme:dark;font-family:system-ui,'Malgun Gothic',sans-serif;background:#111827;color:#f3f4f6}body{margin:0}main{width:min(900px,92%);margin:2rem auto}header{border-bottom:1px solid #374151}h1{font-size:2rem;letter-spacing:-.04em}.tag,footer{color:#aab8ce}section{background:#1f2937;border:1px solid #374151;border-radius:12px;padding:1rem 1.4rem;margin:1rem 0}h2{font-size:1.2rem}form{display:flex;gap:.7rem;flex-wrap:wrap;align-items:end}label{display:flex;flex-direction:column;gap:.3rem;min-width:170px;flex:1}input{background:#111827;color:#fff;border:1px solid #64748b;border-radius:7px;padding:.6rem;max-width:100%;font-size:1rem}button{background:#2563eb;color:white;border:0;border-radius:8px;padding:.7rem 1rem;cursor:pointer;font-weight:bold}button:focus-visible,input:focus-visible{outline:3px solid #facc15}button:hover{background:#1d4ed8}#result{margin-top:1rem;overflow-wrap:anywhere}article{padding:.6rem;border:1px solid #4b5563;margin:.5rem 0;border-radius:7px}pre{white-space:pre-wrap;word-break:break-word}.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.6rem;margin:.8rem 0}.kpi{background:#111827;border:1px solid #475569;border-radius:8px;padding:.8rem}.kpi strong{display:block;font-size:1.5rem}.meter{height:12px;border-radius:7px;background:#111827;overflow:hidden;margin:.2rem 0 .7rem}.meter>span{display:block;background:#60a5fa;height:100%;min-width:0}.library-item{display:flex;align-items:center;justify-content:space-between;gap:.5rem;flex-wrap:wrap}.library-item button{font-size:.85rem}header{padding-bottom:1.1rem}header h1{font-size:2.3rem}header h1 span{color:#60a5fa}.test-pill{display:inline-flex;margin-left:.7rem;background:#24344f;color:#a9c8ff;border:1px solid #405575;border-radius:999px;padding:.25rem .6rem;font-size:.78rem;font-weight:600}.search-panel{border-color:#37588d;background:#172437}.search-panel h2{font-size:1.45rem}.question-field{min-width:min(100%,360px);flex:4}.question-field input{font-size:1.08rem;padding:.84rem}.primary-cta{padding:.86rem 1.4rem;background:#3b82f6}.conversation-tools{display:flex;align-items:center;gap:.55rem;flex-wrap:wrap;margin-top:1rem}.conversation-tools button{background:#324459}.advanced{margin-top:1rem;border:1px solid #40516a;border-radius:9px;padding:.7rem 1rem;background:#182335;width:100%;box-sizing:border-box}.advanced>summary{cursor:pointer;font-weight:650;color:#bbcee7}.advanced[open]>summary{margin-bottom:.8rem}.advanced label{margin:.6rem 0}.library-panel .advanced{margin-top:.5rem}.kpis{margin:1rem 0}.login-panel{background:#1a2636}#result:not(:empty){border-top:1px solid #36485e;margin-top:1.2rem;padding-top:.7rem}#result h3{margin:.4rem 0;color:#9bccff}.tag{line-height:1.5}footer{font-size:.85rem;padding:1rem}@media(max-width:640px){main{width:min(100% - 24px,900px);margin:1rem auto}section{padding:1rem;margin:.75rem 0}.question-field{min-width:100%}.primary-cta{width:100%}.test-pill{display:block;width:max-content;margin:.6rem 0 0}.advanced{padding:.65rem}.login-panel label{min-width:100%}}`;
export const js=`'use strict';
let bearer='';
let conversationId=null;
const $=id=>document.getElementById(id);
const text=(id,value)=>{$(id).textContent=String(value);};
const request=async (url,body)=>{
  const response=await fetch(url,{method:'POST',headers:{'content-type':'application/json',...(bearer?{authorization:'Bearer '+bearer}:{})},body:JSON.stringify(body)});
  const data=await response.json();
  if(!response.ok)throw Error('HTTP '+response.status+' · '+(data.error||'요청 거부'));
  return data;
};
const el=(tag,content)=>{const e=document.createElement(tag);e.textContent=String(content);return e;};
const ids=()=>{const x=$('docids').value.trim();return x?x.split(',').map(z=>z.trim()):null;};

const clearLibrary=()=>{
  $('library-kpis').replaceChildren();$('library-chart').replaceChildren();
  $('library-documents').replaceChildren();
};
const readOnly=async route=>{
  const response=await fetch(route,{method:'GET',headers:bearer?{authorization:'Bearer '+bearer}:{}});
  const data=await response.json();
  if(!response.ok)throw Error('HTTP '+response.status+' · '+(data.error||'요청 거부'));
  return data;
};
async function loadLibrary(){
  if(!bearer){clearLibrary();text('library-status','로그인이 필요합니다.');return;}
  try{
    const data=await readOnly('/v1/library');
    if(data.status!=='SCOPED_LIBRARY'||!Array.isArray(data.documents))throw Error('LIBRARY_INVALID');
    clearLibrary();
    text('library-status','현재 계정이 접근 가능한 문서만 표시합니다.');
    for(const [caption,value] of [['허용 문서',data.kpi.accessible_documents],
      ['컬렉션',data.kpi.collections],['생성된 답변',data.kpi.generated_answers]]){
      const metric=document.createElement('div');metric.className='kpi';
      metric.append(el('span',caption),el('strong',value));$('library-kpis').append(metric);
    }
    const total=Math.max(1,data.kpi.accessible_documents);
    for(const entry of data.collections){
      const label=el('p',entry.id+' · '+entry.count+'건');
      const meter=document.createElement('div');meter.className='meter';
      const fill=document.createElement('span');
      fill.style.width=(100*Math.min(entry.count,total)/total)+'%';
      meter.append(fill);$('library-chart').append(label,meter);
    }
    for(const item of data.documents){
      const card=document.createElement('article');card.className='library-item';
      card.append(el('span',item.id+' · '+item.collection+' · '+item.version+' · '+item.kind));
      const choose=document.createElement('button');choose.type='button';choose.textContent='문서 선택';
      choose.addEventListener('click',()=>{$('docids').value=item.id;$('question').focus();});
      card.append(choose);$('library-documents').append(card);
    }
  }catch(e){
    clearLibrary();text('library-status',e.message);
    if(/^HTTP 401/.test(e.message))bearer='';
  }
}
$('refresh-library').addEventListener('click',loadLibrary);

function render(out){
  const box=$('result');box.replaceChildren();
  const state=out.status||'UNKNOWN';
  const heading=state==='SEARCH_ONLY'?'문서에서 근거를 찾았습니다':state==='INSUFFICIENT_EVIDENCE'?'관련 근거가 부족합니다':state==='POSSIBLE_CONFLICT'?'서로 다른 내용이 발견되었습니다':state==='CONTEXT_INVALID'?'대화 맥락이 만료되었습니다':'검토 결과';
  const top=el('h3',heading);box.append(top);
  box.append(el('small','검증 상태: '+state));
  if(out.reason)box.append(el('p','사유: '+out.reason));
  if(out.sql_evidence)box.append(el('p','승인 전 잠정 매출 (답변 아님): '+out.sql_evidence.provisional_revenue_krw+' KRW · '+out.sql_evidence.orders+'건'));
  const items=out.document_evidence||out.evidence||[];
  for(const source of items){
    const card=document.createElement('article');
    card.append(el('strong','문서 '+source.document_id+' · '+(source.source_unit||'line')+' '+(source.page||source.paragraph||source.line||'?')));
    card.append(el('p',source.quote||'인용문 없음'));box.append(card);
  }
  if(out.answer!==null&&out.answer!==undefined)box.append(el('p','생성형 답변 사용 금지'));
  if(items.length===0)box.append(el('p','표시할 허용 증거가 없습니다.'));
}
$('login').addEventListener('submit',async ev=>{ev.preventDefault();bearer='';
 try{const out=await request('/v1/login',{userId:$('userid').value,password:$('pw').value});
   bearer=out.token;conversationId=null;text('conversation-status','새 로그인: 이전 대화는 이어지지 않습니다.');
   text('result','로그인 성공. 질문을 입력하세요.');await loadLibrary();}
 catch(e){text('result',e.message)}finally{$('pw').value='';}});
$('logout').addEventListener('click',async()=>{try{if(bearer)await request('/v1/logout',{});}catch{}
 bearer='';conversationId=null;clearLibrary();text('conversation-status','로그아웃: 대화 맥락 폐기');
 text('library-status','로그인이 필요합니다.');text('result','로그아웃되었습니다.');});
$('query').addEventListener('submit',async ev=>{ev.preventDefault();
 try{conversationId=null;render(await request('/v1/search',{question:$('question').value,documentIds:ids()}));}
 catch(e){text('result',e.message);}});
$('assess').addEventListener('click',async()=>{
 try{render(await request('/v1/assess',{question:$('question').value,documentIds:ids()}));}
 catch(e){text('result',e.message);}});

$('conversation-start').addEventListener('click',async()=>{
  conversationId=null;
  try{
    const out=await request('/v1/conversation/ask',{question:$('question').value,documentIds:ids()});
    conversationId=out.conversation?.thread_id||null;
    text('conversation-status',conversationId?'근거 대화 활성 · 5분 유효':'대화 시작 불가: 근거 부족/상충/권한 확인');
    render(out);
  }catch(e){text('result',e.message);text('conversation-status','대화 시작 거부');}
});
$('conversation-next').addEventListener('click',async()=>{
  if(!conversationId){text('conversation-status','먼저 근거 대화를 시작해야 합니다.');return;}
  try{
    const out=await request('/v1/conversation/ask',{question:$('question').value,threadId:conversationId});
    if(out.status==='CONTEXT_INVALID'){conversationId=null;text('conversation-status','문서 변경/권한 변경/만료: 처음부터 다시 검색');}
    else text('conversation-status','권한·원문 무결성 재검증된 후속 검색');
    render(out);
  }catch(e){conversationId=null;text('result',e.message);text('conversation-status','후속 대화 중단: 다시 로그인/검색');}
});
const scope=()=>({userId:$('target').value,groups:$('groups').value.split(',').map(s=>s.trim()),
 projects:$('projects').value.split(',').map(s=>s.trim()),clearance:Number($('clearance').value)});
$('operator').addEventListener('submit',async ev=>{ev.preventDefault();try{
 const out=await request('/v1/admin/provision',{...scope(),password:$('newpw').value});
 text('adminresult',out.status+' · '+out.user_id);}catch(e){text('adminresult',e.message)}finally{$('newpw').value='';}});
$('access').addEventListener('click',async()=>{try{const out=await request('/v1/admin/access',scope());
 text('adminresult',out.status+' · '+out.user_id);}catch(e){text('adminresult',e.message)}});
$('revoke').addEventListener('click',async()=>{try{const out=await request('/v1/admin/revoke',{userId:$('target').value});
 text('adminresult',out.status);}catch(e){text('adminresult',e.message)}});`;
