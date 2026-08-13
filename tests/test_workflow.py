from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from researchnet.api import ResearchRequestPayload, create_app
from researchnet.cli import _normalize_argv, build_parser
from researchnet.workflow import ResearchNet


class ResearchNetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "researchnet.sqlite3"
        self.app = ResearchNet(db_path=self.db_path)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

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
        self.tmpdir = TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "researchnet.sqlite3"
        self.app = create_app(db_path=self.db_path)
        self.routes = {route.path: route for route in self.app.router.routes if hasattr(route, "path")}

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

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

    def test_runs_endpoints(self) -> None:
        payload = ResearchRequestPayload(
            topic="AI agents for customer support",
            audience="portfolio reviewers",
            depth="standard",
        )
        created = self.routes["/research"].endpoint(payload)
        listing = self.routes["/runs"].endpoint()
        self.assertEqual(listing["count"], 1)
        self.assertEqual(listing["runs"][0]["run_id"], created["run_id"])
        latest = self.routes["/runs/latest"].endpoint()
        self.assertEqual(latest["run_id"], created["run_id"])
        fetched = self.routes["/runs/{run_id}"].endpoint(created["run_id"])
        self.assertEqual(fetched["run_id"], created["run_id"])


class PersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "researchnet.sqlite3"
        self.app = ResearchNet(db_path=self.db_path)
        self.store = self.app.run_store

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_run_is_saved_and_trace_persisted(self) -> None:
        result = self.app.run_topic("AI agents for customer support", depth="standard")
        saved = self.store.get_run(result["run_id"])
        self.assertIsNotNone(saved)
        assert saved is not None
        self.assertEqual(saved.run_id, result["run_id"])
        self.assertEqual(saved.report, result["report"])
        self.assertEqual(saved.request.topic, "AI agents for customer support")
        self.assertGreater(len(saved.traces), 0)
        self.assertEqual(saved.traces[0].agent, "workflow")
        self.assertEqual(saved.traces[0].action, "run_started")

    def test_run_lookup_and_listing(self) -> None:
        first = self.app.run_topic("AI agents for customer support", depth="quick")
        second = self.app.run_topic("AI assistants in healthcare", depth="standard")
        listing = self.store.list_runs()
        self.assertGreaterEqual(len(listing), 2)
        self.assertEqual(listing[0].run_id, second["run_id"])
        self.assertEqual(listing[1].run_id, first["run_id"])
        latest = self.store.get_latest_run()
        self.assertIsNotNone(latest)
        assert latest is not None
        self.assertEqual(latest.run_id, second["run_id"])
        fetched = self.store.get_run(first["run_id"])
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.run_id, first["run_id"])
        self.assertEqual(fetched.sources[0].source_id, "src-003")


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
