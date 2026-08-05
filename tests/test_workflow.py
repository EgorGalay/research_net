from __future__ import annotations

import unittest

from researchnet.workflow import ResearchNet


class ResearchNetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = ResearchNet()

    def test_quick_mode_uses_two_tasks(self) -> None:
        result = self.app.run_topic("AI agents for customer support", depth="quick")
        self.assertEqual(len(result["tasks"]), 2)
        self.assertIn("Research Brief", result["report"])
        self.assertIn("confidence_score", result)
        self.assertIsNotNone(result["confidence_score"])
        self.assertGreater(len(result["traces"]), 0)
        agents = {trace["agent"] for trace in result["traces"]}
        self.assertTrue({"workflow", "planner", "searcher", "verifier", "synthesizer", "quality"}.issubset(agents))

    def test_deep_mode_adds_an_extra_task(self) -> None:
        result = self.app.run_topic("AI agents for customer support", depth="deep")
        self.assertEqual(len(result["tasks"]), 4)
        self.assertIsNotNone(result["verification"])
        self.assertIn("Confidence score", result["verification"]["note"])
        self.assertGreaterEqual(result["verification"]["confidence_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
