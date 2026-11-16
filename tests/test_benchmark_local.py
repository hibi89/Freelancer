import unittest
from unittest.mock import patch
from scripts.benchmark_local import benchmark, _ollama_generate

class LocalBenchmarkTests(unittest.TestCase):
    def test_dry_run_never_invokes_any_model(self):
        def forbidden(*args):
            raise AssertionError("no inference in dry-run")
        result = benchmark("ollama/qwen3:4b-instruct", sender=forbidden)
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse(result["model_e2e_verified"])

    def test_bounded_local_result_calculation(self):
        calls = []
        def fake(model):
            calls.append(model)
            return {"done": True, "eval_duration": 500000000,
                    "eval_count": 12, "prompt_eval_count": 9}
        times = iter((2.0, 3.25))
        result = benchmark("ollama/qwen3:4b-instruct", execute=True, sender=fake,
                           clock=lambda: next(times),
                           gpu_reader=lambda: "GTX 1050 Ti, 1000, 4096")
        self.assertEqual(calls, ["qwen3:4b-instruct"])
        self.assertEqual(result["eval_tokens_per_second"], 24.0)
        self.assertEqual(result["elapsed_seconds"], 1.25)
        self.assertFalse(result["gpu_peak_vram_measured"])
        self.assertFalse(result["opencode_tool_permissions_verified"])

    def test_invalid_models_rejected(self):
        for model in ("openai/gpt", "ollama/", "ollama/model;rm -rf /",
                      "http://example.com", ""):
            with self.subTest(model=model), self.assertRaises(ValueError):
                benchmark(model, execute=False)

    def test_unfinished_local_generation_fails_closed(self):
        with self.assertRaises(RuntimeError):
            benchmark("ollama/qwen3:4b-instruct", execute=True,
                      sender=lambda _: {"done": False, "eval_duration": 1,
                                        "eval_count": 1},
                      clock=lambda: 1.0, gpu_reader=lambda: None)

if __name__ == "__main__":
    unittest.main()
