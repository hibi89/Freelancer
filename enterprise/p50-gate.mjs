/**
 * CITEVAULT AX P50 read-only integration evidence gate.
 * This is a developer QA harness, NOT a corporate IAM service or package approver.
 * Actual RAG_STUDIO code is loaded from a separately pinned checkout.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL } from 'node:url';

const refuse = (code) => { throw Object.assign(new Error('CITEVAULT_P50_BLOCKED'), { code }); };
const isObj = v => v && typeof v === 'object' && !Array.isArray(v);
const hex = v => typeof v === 'string' && /^[a-f0-9]{64}$/u.test(v);

function directoryRoot(input) {
  if (typeof input !== 'string' || !path.isAbsolute(input)) refuse('ABSOLUTE_ROOT_REQUIRED');
  let stat;
  try { stat = fs.lstatSync(input); } catch { refuse('ROOT_NOT_ACCESSIBLE'); }
  if (!stat.isDirectory() || stat.isSymbolicLink()) refuse('ROOT_UNSAFE');
  return fs.realpathSync(input);
}
function codeFile(root, file) {
  const candidate = path.join(root, 'src', file);
  let st;
  try { st = fs.lstatSync(candidate); } catch { refuse('RAG_MODULE_MISSING'); }
  if (!st.isFile() || st.isSymbolicLink() || st.size > 512 * 1024) refuse('RAG_MODULE_UNSAFE');
  return pathToFileURL(candidate).href;
}

/** Digest a bounded synthetic fixture tree, not a customer data directory. */
export function snapshotFixture(input) {
  const root = directoryRoot(input), entries = [];
  function visit(dir, prefix, depth) {
    if (depth > 8 || entries.length > 128) refuse('FIXTURE_LIMIT');
    for (const entry of fs.readdirSync(dir, { withFileTypes: true }).sort((a,b)=>a.name.localeCompare(b.name))) {
      if (entry.isSymbolicLink() || (!entry.isFile() && !entry.isDirectory())) refuse('FIXTURE_UNSAFE_TYPE');
      const name = prefix ? prefix + '/' + entry.name : entry.name;
      if (entry.isDirectory()) { visit(path.join(dir, entry.name), name, depth + 1); continue; }
      const full = path.join(dir, entry.name), before = fs.lstatSync(full);
      if (!before.isFile() || before.size > 2 * 1024 * 1024) refuse('FIXTURE_FILE_UNSAFE');
      const bytes = fs.readFileSync(full), after = fs.lstatSync(full);
      if (bytes.length !== before.size || after.ino !== before.ino || after.dev !== before.dev || after.size !== before.size) refuse('FIXTURE_CHANGED_DURING_READ');
      entries.push([name, crypto.createHash('sha256').update(bytes).digest('hex')]);
      if (entries.length > 128) refuse('FIXTURE_LIMIT');
    }
  }
  visit(root, '', 0);
  if (!entries.length) refuse('FIXTURE_EMPTY');
  return crypto.createHash('sha256').update(JSON.stringify(entries.sort((a,b)=>a[0].localeCompare(b[0])))).digest('hex');
}
function validateSales(v, expectedRevenue) {
  if (!isObj(v) || v.status !== 'ANSWERED' || v.kind !== 'SQL_DOCUMENT' ||
      !isObj(v.sql_evidence) || v.sql_evidence.engine !== 'node:sqlite (in-memory)' ||
      v.sql_evidence.aggregation !== 'fixed_read_only_sales_totals' ||
      v.sql_evidence.revenue_krw !== String(expectedRevenue) ||
      !Array.isArray(v.sql_evidence.row_evidence) || v.sql_evidence.row_evidence.length === 0 ||
      !v.sql_evidence.row_evidence.every(row => isObj(row) && Number.isSafeInteger(row.csv_line) && row.csv_line >= 2) ||
      !isObj(v.document_evidence) || !Number.isSafeInteger(v.document_evidence.line) ||
      v.document_evidence.line < 1 || typeof v.document_evidence.quote !== 'string' ||
      !/반품|환불/u.test(v.document_evidence.quote)) refuse('MIXED_EVIDENCE_INVALID');
}
function validateSearch(v) {
  if (!isObj(v) || v.status !== 'FOUND' || v.search_mode !== 'bm25_line_ngrams' ||
      !Array.isArray(v.evidence) || v.evidence.length === 0 ||
      !v.evidence.every(row => isObj(row) && typeof row.document_id === 'string' &&
        Number.isSafeInteger(row.line) && row.line > 0 && typeof row.quote === 'string')) {
    refuse('BM25_EVIDENCE_INVALID');
  }
}
function validateSmax(v) {
  if (!isObj(v) || v.status !== 'REVIEW_REQUIRED' ||
      v.provenance !== 'SOURCE_DIGEST_VERIFIED' ||
      v.acceptance !== 'NOT_GRANTED' || v.ax_package_created !== false ||
      !Number.isSafeInteger(v.source_rows) || v.source_rows < 1) refuse('SMAX_NOT_FAIL_CLOSED');
}

/**
 * Exact-source synthetic evidence. Does not promote the unapproved SMAX sample
 * into an approved AX package. Never exports raw rows, texts or filesystem paths.
 */
export async function auditP50({ ragRoot, axFixture, smaxJson, smaxCsv, expectedRevenue = 157000 }) {
  const root = directoryRoot(ragRoot);
  const fixture = directoryRoot(axFixture);
  const before = snapshotFixture(fixture);
  if (typeof smaxJson !== 'string' || typeof smaxCsv !== 'string') refuse('SMAX_PATH_REQUIRED');
  const [mixed, documents, smax, validator] = await Promise.all([
    import(codeFile(root, 'mixed-question.mjs')),
    import(codeFile(root, 'document-search.mjs')),
    import(codeFile(root, 'smax-intake.mjs')),
    import(codeFile(root, 'validate.mjs'))
  ]);
  if (typeof mixed.answerMixedQuestion !== 'function' || typeof documents.searchDocuments !== 'function' ||
      typeof smax.inspectSmaxFiles !== 'function' || typeof validator.loadPackage !== 'function')
    refuse('RAG_INTERFACE_MISMATCH');
  try {
    const pkg = validator.loadPackage(fixture);
    if (!isObj(pkg) || !isObj(pkg.manifest) || pkg.manifest.schema_version !== 'AX_DATA_PACKAGE_V0')
      refuse('AX_CONTRACT_MISMATCH');
    const sales = mixed.answerMixedQuestion(fixture, '총 매출과 반품 규정을 알려줘');
    validateSales(sales, expectedRevenue);
    const retrieval = documents.searchDocuments(fixture, '반품 신청 가능 기간');
    validateSearch(retrieval);
    const pending = smax.inspectSmaxFiles(smaxJson, smaxCsv);
    validateSmax(pending);
    return Object.freeze({
      status: 'P50_INTEGRATION_EVIDENCE_ONLY',
      source_mutation: false,
      network_calls_by_gate: 0,
      producer_approval: 'NOT_GRANTED',
      enterprise_acl: 'NOT_TESTED',
      signed_transfer: 'NOT_TESTED',
      synthetic_checks: ['AX_DIGEST', 'FIXED_SQL_SALES', 'TXT_CITATION', 'BM25_RETRIEVAL', 'SMAX_REVIEW_HOLD'],
      sales_krw: sales.sql_evidence.revenue_krw,
      cited_document_count: retrieval.evidence.length,
      fixture_sha256: before
    });
  } finally {
    if (snapshotFixture(fixture) !== before) refuse('SOURCE_MUTATED');
  }
}
