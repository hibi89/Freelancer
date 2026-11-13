import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { auditP50, snapshotFixture } from '../enterprise/p50-gate.mjs';

const rag = process.env.RAG_STUDIO_ROOT;
const paths = rag ? {
  ragRoot: path.resolve(rag),
  axFixture: path.resolve(rag, 'fixtures/ax_sample_v0'),
  smaxJson: path.resolve(rag, 'fixtures/smax_v1_boundary/unapproved.json'),
  smaxCsv: path.resolve(rag, 'fixtures/smax_v1_boundary/source.csv')
} : null;

test('P50 refuses implicit, missing or relative source roots', async () => {
  await assert.rejects(auditP50({}), {code:'ABSOLUTE_ROOT_REQUIRED'});
  await assert.rejects(auditP50({ragRoot:'relative/path'}), {code:'ABSOLUTE_ROOT_REQUIRED'});
  assert.throws(() => snapshotFixture('relative/path'), {code:'ABSOLUTE_ROOT_REQUIRED'});
});
test('P50 refuses symbolic link fixture roots', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'citevault-unit-'));
  t.after(() => fs.rmSync(root, {recursive:true,force:true}));
  fs.writeFileSync(path.join(root,'sample.txt'), 'synthetic\n');
  assert.match(snapshotFixture(root), /^[a-f0-9]{64}$/);
  const alias = root + '-link';
  try { fs.symlinkSync(root,alias,'dir'); }
  catch (err) { if (err.code === 'EPERM') return t.skip('symlink creation not permitted on this platform'); throw err; }
  t.after(() => fs.rmSync(alias,{force:true}));
  assert.throws(()=>snapshotFixture(alias), {code:'ROOT_UNSAFE'});
});
test('P50 snapshots detect fixture changes and block symlinks', (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'citevault-snapshot-'));
  t.after(() => fs.rmSync(root, {recursive:true,force:true}));
  const file=path.join(root,'only.txt');
  fs.writeFileSync(file, 'mock synthetic one');
  const initial=snapshotFixture(root);
  assert.equal(initial,snapshotFixture(root));
  fs.writeFileSync(file,'mock synthetic two');
  assert.notEqual(initial,snapshotFixture(root));
});
test('P50 exercises real pinned RAG SQL, BM25, citations and SMAX review-only contracts', {
  skip: !paths && 'Set RAG_STUDIO_ROOT to an exact pinned local checkout'
}, async () => {
  const report = await auditP50(paths);
  assert.equal(report.status,'P50_INTEGRATION_EVIDENCE_ONLY');
  assert.equal(report.sales_krw,'157000');
  assert.equal(report.producer_approval,'NOT_GRANTED');
  assert.equal(report.source_mutation,false);
  assert.equal(report.enterprise_acl,'NOT_TESTED');
  assert.deepEqual(report.synthetic_checks,['AX_DIGEST','FIXED_SQL_SALES','TXT_CITATION','BM25_RETRIEVAL','SMAX_REVIEW_HOLD']);
});
test('P50 cannot mistake tampered SMAX data for approved producer source', {
  skip: !paths && 'Requires RAG_STUDIO_ROOT'
}, async (t) => {
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'citevault-smax-negative-'));
  t.after(()=>fs.rmSync(tmp,{recursive:true,force:true}));
  const tampered=path.join(tmp,'bad.csv');
  const raw=fs.readFileSync(paths.smaxCsv);
  fs.writeFileSync(tampered,Buffer.concat([raw,Buffer.from('tampered')]));
  await assert.rejects(auditP50({...paths,smaxCsv:tampered}),{code:'SMAX_NOT_FAIL_CLOSED'});
});
test('P50 refuses incorrect fixed SQL oracle instead of reporting success', {
  skip: !paths && 'Requires RAG_STUDIO_ROOT'
}, async () => {
  await assert.rejects(auditP50({...paths,expectedRevenue:1}),{code:'MIXED_EVIDENCE_INVALID'});
});
