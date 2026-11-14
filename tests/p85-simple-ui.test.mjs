import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {html,css,js} from '../enterprise/p85-ui.mjs';

test('everyday workflow is question-first; advanced panels closed by default',()=>{
  assert.match(html,/<section aria-label="근거 검색" class="search-panel">/);
  assert.match(html,/<label class="question-field" for="question">무엇이 궁금하세요\?/);
  assert.match(html,/<button type="submit" class="primary-cta">근거 검색<\/button>/);
  for(const id of ['search-options','library-details','admin-panel']){
    assert.match(html,new RegExp('<details id="'+id+'"'));
    assert.doesNotMatch(html,new RegExp('<details id="'+id+'"[^>]*\\sopen\\b'));
  }
});
test('simple view retains all preexisting secure search and operator controls',()=>{
  for(const id of ['login','userid','pw','logout','query','question','docids','assess',
    'conversation-start','conversation-next','library-kpis','library-chart','library-documents',
    'refresh-library','operator','target','newpw','groups','projects','clearance',
    'createuser','access','revoke','result','adminresult']){
    assert.match(html,new RegExp('id="'+id+'"'),'missing '+id);
  }
  assert.match(js,/\/v1\/search/);assert.match(js,/\/v1\/conversation\/ask/);
  assert.match(js,/\/v1\/admin\/revoke/);
});
test('plain-language status accompanies preserved testable exact status codes',()=>{
  assert.match(js,/문서에서 근거를 찾았습니다/);
  assert.match(js,/관련 근거가 부족합니다/);
  assert.match(js,/서로 다른 내용이 발견되었습니다/);
  assert.match(js,/검증 상태: /);
  assert.doesNotThrow(()=>new vm.Script(js,{filename:'p85-ui.js'}));
});
test('simple UI remains strict local-only and never interpolates raw source HTML',()=>{
  assert.doesNotMatch(html,/https?:\/\/|<script>/);
  assert.doesNotMatch(js,/innerHTML|eval\(|localStorage|sessionStorage|sendBeacon|new WebSocket/);
  assert.match(css,/color-scheme:dark/);
  assert.match(css,/max-width:640px/);
  assert.match(css,/\.advanced/);
});
