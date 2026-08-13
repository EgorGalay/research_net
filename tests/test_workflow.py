from __future__ import annotations

import unittest

from researchnet.api import ResearchRequestPayload, create_app
from researchnet.cli import _normalize_argv, build_parser
from researchnet.workflow import ResearchNet


class ResearchNetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = ResearchNet()

    def test_quick_mode_uses_two_tasks(self) -> None:
        result = self.app.run_topic("AI agents for customer support", depth="quick")
        self.assertEqual(len(result["tasks"]), 2)
        self.assertIn("Research Brief", result["report"])
        self.assertIn("run_id", result)
        self.assertTrue(result["run_id"])
        self.assertIn("started_at", result)
        self.assertIn("finished_at", result)
        self.assertGreaterEqual(result["duration_ms"], 0)
        self.assertIn("confidence_score", result)
        self.assertIsNotNone(result["confidence_score"])
        self.assertGreater(len(result["traces"]), 0)
        trace = result["traces"][0]
        self.assertIn("timestamp", trace)
        self.assertIn("stage", trace)
        self.assertIn("duration_ms", result["traces"][-1])
        agents = {trace["agent"] for trace in result["traces"]}
        self.assertTrue({"workflow", "planner", "searcher", "verifier", "synthesizer", "quality"}.issubset(agents))

    def test_deep_mode_adds_an_extra_task(self) -> None:
        result = self.app.run_topic("AI agents for customer support", depth="deep")
        self.assertEqual(len(result["tasks"]), 4)
        self.assertIsNotNone(result["verification"])
        self.assertIn("Confidence score", result["verification"]["note"])
        self.assertGreaterEqual(result["verification"]["confidence_score"], 0.0)


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.routes = {route.path: route for route in self.app.router.routes if hasattr(route, "path")}

    def test_root_and_health(self) -> None:
        root = self.routes["/"].endpoint()
        health = self.routes["/health"].endpoint()
        self.assertEqual(root["status"], "ready")
        self.assertEqual(health, {"status": "ok"})

    def test_research_endpoint(self) -> None:
        payload = ResearchRequestPayload(
            topic="AI agents for customer support",
            audience="portfolio reviewers",
            depth="standard",
        )
        response = self.routes["/research"].endpoint(payload)
        self.assertIn("run_id", response)
        self.assertIn("traces", response)
        self.assertGreater(len(response["traces"]), 0)


class CliTests(unittest.TestCase):
    def test_legacy_style_is_normalized_to_research(self) -> None:
        args = build_parser().parse_args(_normalize_argv(["--topic", "AI agents for customer support", "--json"]))
        self.assertEqual(args.command, "research")
        self.assertTrue(args.json)

    def test_export_command_is_available(self) -> None:
        args = build_parser().parse_args(["export", "--topic", "AI agents for customer support", "--output", "outputs/run.json"])
        self.assertEqual(args.command, "export")
        self.assertEqual(args.output, "outputs/run.json")


if __name__ == "__main__":
    unittest.main()
