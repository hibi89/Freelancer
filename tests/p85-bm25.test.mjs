import test from 'node:test';
import assert from 'node:assert/strict';
import {rankAuthorizedBM25} from '../enterprise/p85-bm25.mjs';
const cite=(id,quote,line=1)=>({document_id:id,source_unit:'line',line,quote});
test('BM25 ranks matching Korean native evidence above unrelated content',()=>{
 const c=[cite('unrelated','서버 보안 정책과 암호화 업데이트를 실시한다.'),
  cite('returns','반품 신청 가능 기간은 7일 이내입니다.'),
  cite('shipping','배송 준비 시작은 2 영업일 이내입니다.')];
 const r=rankAuthorizedBM25(c,'반품 신청 가능 기간은 언제인가요?',3);
 assert.equal(r[0].document_id,'returns');assert.ok(r.every(x=>c.includes(x)));
});
test('BM25 respects explicit limit and preserves exact SHA/citation metadata',()=>{
 const c=[{...cite('a','배송 준비는 2 영업일 이내입니다.'),source_sha256:'a'.repeat(64),page:2,source_unit:'page'},
  cite('b','배송 준비는 3 영업일 이내입니다.')];
 const r=rankAuthorizedBM25(c,'배송 준비',1);assert.equal(r.length,1);
 assert.equal(r[0],c[0]);assert.equal(r[0].page,2);
});
test('BM25 on no tokens/no evidence returns no invented answer',()=>{
 assert.deepEqual(rankAuthorizedBM25([cite('doc','매출 1000원')],'?',5),[]);
 assert.deepEqual(rankAuthorizedBM25([],'반품 기간',5),[]);
});
test('BM25 ties use deterministic document ID and source order',()=>{
 const c=[cite('z','반품 정책은 7일',2),cite('a','반품 정책은 7일',3),cite('a','반품 정책은 7일',1)];
 assert.deepEqual(rankAuthorizedBM25(c,'반품 정책',3).map(x=>[x.document_id,x.line]),[['a',1],['a',3],['z',2]]);
});
test('BM25 never retrieves citations not present in the caller ACL scope',()=>{
 const visible=[cite('visible','반품 신청 기간은 7일')];
 const returned=rankAuthorizedBM25(visible,'반품 기간 7일',10);
 assert.ok(returned.every(x=>visible.includes(x)));
 assert.doesNotMatch(JSON.stringify(returned),/secret|private/);
});
test('invalid limits, chunk schema or oversized corpus fail closed',()=>{
 assert.throws(()=>rankAuthorizedBM25(null,'반품',5),{code:'QUERY_INVALID'});
 assert.throws(()=>rankAuthorizedBM25([cite('a','반품')],'반품',11),{code:'QUERY_INVALID'});
 assert.throws(()=>rankAuthorizedBM25([{document_id:'x',quote:42}],'반품',5),{code:'QUERY_INVALID'});
});
