import test from 'node:test';
import assert from 'node:assert/strict';
import { validateAuthorizedCitations as valid } from '../enterprise/p70-citation-contract.mjs';

const ids = ['document-returns'];
const item = (extra = {}) => ({ document_id: 'document-returns', file_id: 'file-policy',
  source_title: 'Synthetic source', line: 2,
  quote: '반품 신청 7일 이내 가능합니다.', ...extra });
const found = (extra = {}) => ({ status: 'FOUND', answer: 'untrusted',
  evidence: [item()],
  scope: { mode: 'SESSION_SELECTED_DOCUMENTS', document_ids: [...ids] }, ...extra });
const conflict = (extra = {}) => ({ ...found({ status: 'POSSIBLE_CONFLICT', answer: null }),
  review_evidence: [item({period: 7, claim_kind: 'calendar_days'}),
    item({period: 14, claim_kind: 'calendar_days',line: 3})], ...extra });

test('actual expected RAG FOUND evidence with scoped citation is accepted', () => {
  assert.equal(valid(found(), ids), true);
});
test('FOUND without citations must never be accepted', () => {
  assert.equal(valid(found({evidence: []}), ids), false);
  assert.equal(valid(found({evidence: null}), ids), false);
});
test('FOUND with fake authorized document ID or unauthorized scope is rejected', () => {
  assert.equal(valid(found({evidence: [item({document_id:'other'})]}), ids), false);
  assert.equal(valid(found({scope: {mode:'SESSION_SELECTED_DOCUMENTS',document_ids:['other']}}), ids), false);
});
test('missing, zero or invalid line citation is rejected', () => {
  for (const x of [0, -1, 1.2, 999999, '2', null])
    assert.equal(valid(found({evidence:[item({line:x})]}), ids), false);
});
test('empty, unbounded or missing quote is rejected', () => {
  for (const x of ['', '  ', 'x'.repeat(4097), null])
    assert.equal(valid(found({evidence:[item({quote:x})]}), ids), false);
});
test('missing or malformed RAG file evidence ID is rejected', () => {
  for (const x of [undefined, '', '../file-policy', null])
    assert.equal(valid(found({evidence:[item({file_id:x})]}), ids), false);
});
test('a correct source conflict requires two periods and review citations', () => {
  assert.equal(valid(conflict(), ids), true);
  assert.equal(valid(conflict({review_evidence:[]}), ids), false);
  assert.equal(valid(conflict({review_evidence:[item({period:7,claim_kind:'calendar_days'})]}), ids), false);
});
test('conflict with same period is not substantiated', () => {
  assert.equal(valid(conflict({review_evidence:[item({period:7,claim_kind:'calendar_days'}),
    item({period:7,claim_kind:'calendar_days',line:3})]}), ids), false);
});
test('conflict cannot cite a document outside its authorized selection', () => {
  assert.equal(valid(conflict({review_evidence:[item({period:7,claim_kind:'calendar_days'}),
    item({period:14,claim_kind:'calendar_days',document_id:'other'})]}), ids), false);
});
test('conflict cannot contain a generated answer or unsupported claim unit', () => {
  assert.equal(valid(conflict({answer:'7 days'}), ids), false);
  assert.equal(valid(conflict({review_evidence:[item({period:7,claim_kind:'calendar_days'}),
    item({period:14,claim_kind:'business_days'})]}), ids), false);
});
test('no evidence is an allowed no-answer response', () => {
  const none = found({status:'NO_EVIDENCE',answer:null,evidence:[]});
  assert.equal(valid(none,ids), true);
  assert.equal(valid({...none,answer:'guess'},ids), false);
});
test('undefined array, duplicate IDs and unsupported result code fail closed', () => {
  assert.equal(valid(found(),undefined),false);
  assert.equal(valid(found(),['document-returns','document-returns']),false);
  assert.equal(valid(found({status:'ANSWERED'}),ids),false);
});
test('extra untrusted review evidence is not accepted as ordinary FOUND', () => {
  assert.equal(valid(found({review_evidence:[item()]}),ids),false);
});
test('cited file ids are restricted to normal basename-style identifiers', () => {
  assert.equal(valid(found({evidence:[item({file_id:'../private'})]}),ids),false);
});
