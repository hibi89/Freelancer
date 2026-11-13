/**
 * CITEVAULT AX P70 citation-contract guard.
 * Deterministic, source-independent assertion only. It does not authenticate a user,
 * prove source hashes, approve package rights or enforce ACL before loading data.
 */
const ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/u;

function validCitation(item, allowed) {
  return item !== null && typeof item === 'object' && !Array.isArray(item)
    && typeof item.document_id === 'string' && allowed.includes(item.document_id)
    && typeof item.file_id === 'string' && ID.test(item.file_id)
    && Number.isSafeInteger(item.line) && item.line > 0 && item.line <= 10000
    && typeof item.quote === 'string' && item.quote.trim().length > 0
    && item.quote.length <= 4096;
}

/** Verifies that an original RAG response is scoped and has nonempty evidence. */
export function validateAuthorizedCitations(result, allowed) {
  if (!Array.isArray(allowed) || allowed.length < 1 || allowed.length > 8
      || allowed.some(id => typeof id !== 'string' || !ID.test(id))
      || new Set(allowed).size !== allowed.length
      || result === null || typeof result !== 'object' || Array.isArray(result)) return false;
  if (!['FOUND', 'POSSIBLE_CONFLICT', 'NO_EVIDENCE'].includes(result.status)) return false;
  if (result.scope?.mode !== 'SESSION_SELECTED_DOCUMENTS'
      || !Array.isArray(result.scope.document_ids)
      || result.scope.document_ids.length !== allowed.length
      || !allowed.every((id, i) => id === result.scope.document_ids[i])) return false;
  if (!Array.isArray(result.evidence) || result.evidence.length > 10
      || result.evidence.some(item => !validCitation(item, allowed))) return false;
  for (const name of ['review_evidence', 'comparison']) {
    if (Object.hasOwn(result, name)
        && (!Array.isArray(result[name]) || result[name].length > 64
          || result[name].some(item => !validCitation(item, allowed)))) return false;
  }
  if (result.status === 'FOUND') {
    return result.evidence.length > 0
      && !Object.hasOwn(result, 'review_evidence')
      && !Object.hasOwn(result, 'comparison');
  }
  if (result.status === 'NO_EVIDENCE') {
    return result.evidence.length === 0 && result.answer === null
      && !Object.hasOwn(result, 'review_evidence')
      && !Object.hasOwn(result, 'comparison');
  }
  const review = result.review_evidence;
  if (!Array.isArray(review) || review.length < 2 || review.length > 32
      || result.answer !== null
      || Object.hasOwn(result, 'comparison')
      || review.some(item => item.claim_kind !== 'calendar_days'
        || !Number.isInteger(item.period) || item.period < 1 || item.period > 365)
      || new Set(review.map(item => item.period)).size < 2) return false;
  return true;
}
