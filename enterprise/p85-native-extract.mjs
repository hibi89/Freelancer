/** P85 local bytes-only PDF/DOCX evidence adapter. Not original pinned RAG Studio. */
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const script = fileURLToPath(new URL('./p85-native-extract.py', import.meta.url));
const deny = () => { throw Object.assign(new Error('CITEVAULT_NATIVE_HOLD'), {code: 'NATIVE_HOLD'}); };

/** Run only after the caller has checked tenant/role ACL and source SHA-256. */
export function extractVerifiedNativeBytes(bytes, kind, {python = 'python'} = {}) {
  if (!Buffer.isBuffer(bytes) || bytes.length < 8 || bytes.length > 2*1024*1024 ||
      !['pdf', 'docx'].includes(kind) || typeof python !== 'string' ||
      !/^(python(?:3(?:\.\d+)?)?|py)$/u.test(python)) deny();
  let result;
  try {
    result = spawnSync(python, ['-I', '-B', script, kind], {
      input: bytes, timeout: 8000, maxBuffer: 512*1024, windowsHide: true,
      env: {PATH: process.env.PATH ?? '', PYTHONIOENCODING: 'utf-8'},
      encoding: 'utf8'
    });
  } catch { deny(); }
  if (result.error || result.status !== 0 || result.signal || !result.stdout || result.stdout.length > 512*1024) deny();
  let parsed;
  try { parsed = JSON.parse(result.stdout); } catch { deny(); }
  const unit = kind === 'pdf' ? 'page' : 'paragraph';
  if (parsed?.status !== 'OK' || parsed.unit !== unit || !Array.isArray(parsed.rows) ||
      parsed.rows.length < 1 || parsed.rows.length > 64) deny();
  const positions = new Set();
  return parsed.rows.map(entry => {
    if (!Number.isSafeInteger(entry?.position) || entry.position < 1 || entry.position > 64 ||
        positions.has(entry.position) || typeof entry.quote !== 'string' ||
        entry.quote.length < 1 || entry.quote.length > 4096) deny();
    positions.add(entry.position);
    return {source_unit:unit, position:entry.position, quote:entry.quote};
  });
}
