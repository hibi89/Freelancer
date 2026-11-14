"""Offline, synthetic-only multilingual-e5-small ONNX inference acceptance.
Never connects to a network, processes customer content, or grants production approval.
Dependencies (installed separately): onnxruntime, tokenizers, numpy.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

MODEL_DIMENSION = 384
MAX_INPUTS = 12
MAX_CHARS = 500
MAX_TOKENS = 256


def prefixed(kind: str, value: str) -> str:
    if kind not in ("query", "passage") or not isinstance(value, str):
        raise ValueError("INVALID_EMBEDDING_TEXT")
    if not value.strip() or len(value) > MAX_CHARS or "\x00" in value:
        raise ValueError("INVALID_EMBEDDING_TEXT")
    return kind + ": " + value.strip()


def verify_local_assets(model_dir: Path) -> dict:
    if not model_dir.is_absolute():
        raise ValueError("ABSOLUTE_MODEL_DIR_REQUIRED")
    checker = Path(__file__).resolve().with_name("p85-korean-model-check.mjs")
    result = subprocess.run(
        ["node", str(checker), "--model-dir", str(model_dir)],
        capture_output=True, text=True, check=False, timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError("PINNED_MODEL_PREFLIGHT_FAILED")
    data = json.loads(result.stdout)
    if data.get("status") != "BINARY_HASH_VERIFIED_ONLY":
        raise RuntimeError("PINNED_MODEL_PREFLIGHT_FAILED")
    return data


def mean_pool_and_normalize(hidden, masks):
    """E5 mean pooling with attention mask and L2 normalization; no padded tokens."""
    import numpy as np

    embeddings = np.asarray(hidden, dtype=np.float32)
    attention = np.asarray(masks, dtype=np.float32)
    if embeddings.ndim != 3 or embeddings.shape[-1] != MODEL_DIMENSION:
        raise ValueError("UNEXPECTED_EMBEDDING_SHAPE")
    if attention.shape != embeddings.shape[:2] or np.any(attention.sum(axis=1) < 1):
        raise ValueError("INVALID_ATTENTION_MASK")
    pooled = (embeddings * attention[:, :, None]).sum(axis=1) / attention.sum(axis=1)[:, None]
    norms = np.linalg.norm(pooled, axis=1, keepdims=True)
    if np.any(~np.isfinite(norms)) or np.any(norms < 1e-8):
        raise ValueError("INVALID_EMBEDDING_VECTOR")
    vectors = pooled / norms
    if not np.isfinite(vectors).all():
        raise ValueError("NONFINITE_EMBEDDING_VECTOR")
    return vectors


def embed(model_dir: Path, kinds_and_texts: list[tuple[str, str]]):
    """Run signed-off local assets ONLY, using CPU provider and fixed token budgets."""
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer

    if not 1 <= len(kinds_and_texts) <= MAX_INPUTS:
        raise ValueError("EMBEDDING_BATCH_LIMIT")
    texts = [prefixed(kind, value) for kind, value in kinds_and_texts]
    tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
    tokenizer.enable_truncation(max_length=MAX_TOKENS)
    encodings = tokenizer.encode_batch(texts, add_special_tokens=True)
    max_len = max(len(item.ids) for item in encodings)
    pad_id = tokenizer.token_to_id("<pad>")
    if pad_id is None or not 1 <= max_len <= MAX_TOKENS:
        raise ValueError("UNSUPPORTED_TOKENIZER")
    token_ids = np.full((len(texts), max_len), pad_id, dtype=np.int64)
    masks = np.zeros_like(token_ids)
    for i, encoding in enumerate(encodings):
        n = len(encoding.ids)
        token_ids[i, :n] = encoding.ids
        masks[i, :n] = encoding.attention_mask
    session = ort.InferenceSession(
        str(model_dir / "onnx" / "model_int8.onnx"),
        providers=["CPUExecutionProvider"],
        sess_options=ort.SessionOptions(),
    )
    available = {item.name for item in session.get_inputs()}
    if not {"input_ids", "attention_mask"}.issubset(available):
        raise ValueError("UNEXPECTED_MODEL_INPUTS")
    allowed = {"input_ids", "attention_mask", "token_type_ids"}
    if available - allowed:
        raise ValueError("UNEXPECTED_MODEL_INPUTS")
    inputs = {"input_ids": token_ids, "attention_mask": masks}
    if "token_type_ids" in available:
        inputs["token_type_ids"] = np.zeros_like(token_ids)
    outputs = session.run(None, inputs)
    hidden = next(
        (o for o in outputs if getattr(o, "ndim", 0) == 3 and o.shape[-1] == MODEL_DIMENSION),
        None,
    )
    if hidden is None:
        raise ValueError("UNEXPECTED_MODEL_OUTPUT")
    return mean_pool_and_normalize(hidden, masks)


def synthetic_korean_smoke(model_dir: Path) -> dict:
    """Three held-out-style synthetic probes; NOT customer Gold100 or a quality claim."""
    samples = [
        ("반품 신청은 며칠 이내에 하나요?",
         "구매 후 반품 접수는 7일 이내에 신청할 수 있습니다.",
         "로그인 비밀번호는 보안 설정에서 변경할 수 있습니다."),
        ("관리자 계정 비밀번호를 어디서 변경하나요?",
         "관리자 계정의 비밀번호는 계정 보안 설정 화면에서 변경합니다.",
         "배송된 물품의 파손은 입고 담당자에게 보고합니다."),
        ("장비 정기 점검 주기는 어떻게 되나요?",
         "공장 설비의 정기 안전 점검은 매월 첫째 주에 실시합니다.",
         "신용카드 결제 취소는 구매 영수증을 확인한 후 처리합니다."),
    ]
    items = [(kind, value) for question, positive, negative in samples
             for kind, value in (("query", question),
                                 ("passage", positive),
                                 ("passage", negative))]
    start = time.perf_counter()
    vectors = embed(model_dir, items)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
    if vectors.shape != (len(samples) * 3, MODEL_DIMENSION):
        raise ValueError("UNEXPECTED_EMBEDDING_SHAPE")
    passed = 0
    margins = []
    for i in range(len(samples)):
        query, positive, negative = vectors[3*i:3*i+3]
        a, b = float(query @ positive), float(query @ negative)
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError("NONFINITE_SIMILARITY")
        margins.append(round(a-b, 5))
        passed += int(a > b)
    return {
        "status": "SYNTHETIC_KOREAN_ONNX_SMOKE_PASS" if passed == 3 else "SYNTHETIC_KOREAN_ONNX_SMOKE_FAIL",
        "cases": len(samples), "positive_ranked_first": passed,
        "cosine_margins": margins, "elapsed_ms": elapsed_ms,
        "embedding_dimensions": MODEL_DIMENSION,
        "network_calls_during_inference": 0,
        "customer_gold100_verified": False,
        "commercial_license_approved": False,
        "ready_for_customer": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--self-test", action="store_true", required=True)
    args = parser.parse_args()
    try:
        directory = Path(args.model_dir)
        verified = verify_local_assets(directory)
        result = synthetic_korean_smoke(directory)
        result["model_sha256"] = verified["onnx_sha256"]
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["status"] == "SYNTHETIC_KOREAN_ONNX_SMOKE_PASS" else 1
    except Exception as exc:
        print(json.dumps({
            "status": "SYNTHETIC_KOREAN_ONNX_SMOKE_FAIL",
            "error_type": type(exc).__name__,
            "customer_gold100_verified": False,
            "ready_for_customer": False,
        }))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
