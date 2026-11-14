"""No model bytes required: shape and fail-closed contract tests."""
import unittest
import numpy as np
from scripts.p85_korean_real_onnx import (
    MODEL_DIMENSION, mean_pool_and_normalize, prefixed, verify_local_assets,
)
from pathlib import Path


class KoreanOnnxContracts(unittest.TestCase):
    def test_e5_query_passage_prefixes(self):
        self.assertEqual(prefixed("query", " 반품 문의 "), "query: 반품 문의")
        self.assertEqual(prefixed("passage", " 규정 "), "passage: 규정")
        for kind, value in (("other", "text"), ("query", ""), ("passage", "x"*501)):
            with self.assertRaises(ValueError):
                prefixed(kind, value)

    def test_attention_mask_excludes_padding(self):
        x = np.zeros((2, 3, MODEL_DIMENSION), dtype=np.float32)
        x[0, 0, 0] = 2
        x[0, 1, 1] = 2
        x[0, 2, 2] = 1000  # must not influence first embedding
        x[1, 0, 2] = 4
        mask = np.array([[1, 1, 0], [1, 0, 0]], dtype=np.int64)
        result = mean_pool_and_normalize(x, mask)
        self.assertEqual(result.shape, (2, MODEL_DIMENSION))
        self.assertAlmostEqual(float(result[0, 0]), 2**-0.5, places=5)
        self.assertAlmostEqual(float(result[0, 1]), 2**-0.5, places=5)
        self.assertEqual(float(result[0, 2]), 0.0)
        self.assertAlmostEqual(float(result[1, 2]), 1.0, places=5)

    def test_invalid_masks_or_dimensions_refused(self):
        with self.assertRaises(ValueError):
            mean_pool_and_normalize(np.ones((1, 2, 384)), np.zeros((1, 2)))
        with self.assertRaises(ValueError):
            mean_pool_and_normalize(np.ones((1, 2, 12)), np.ones((1, 2)))

    def test_missing_verified_model_never_accepted(self):
        with self.assertRaises(ValueError):
            verify_local_assets(Path("relative/model"))
        with self.assertRaises(RuntimeError):
            verify_local_assets((Path.home() / "not-existing-citevault-model-dir-test-20261114").resolve())


if __name__ == "__main__":
    unittest.main()
