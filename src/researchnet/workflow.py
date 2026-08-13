from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Dict
from uuid import uuid4

from .agents import PlannerAgent, QualityAgent, SearcherAgent, SynthesizerAgent, VerifierAgent
from .models import ResearchRequest, ResearchState
from .source_store import SourceStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class ResearchNet:
    def __init__(self, store: SourceStore | None = None) -> None:
        self.store = store or SourceStore()
        self.planner = PlannerAgent()
        self.searcher = SearcherAgent(self.store)
        self.verifier = VerifierAgent()
        self.synthesizer = SynthesizerAgent()
        self.quality = QualityAgent()

    def run(self, request: ResearchRequest) -> ResearchState:
        state = ResearchState(request=request, run_id=uuid4().hex, started_at=_utc_now())
        run_started = perf_counter()
        state.log_trace("workflow", "run_started", "Research workflow started.", stage="workflow", topic=request.topic, depth=request.depth)

        state.tasks = self._run_stage(
            state,
            stage="planner",
            start_message="Planning the research tasks.",
            end_message="Created the research plan.",
            action=lambda: self.planner.run(state),
        )
        state.findings = self._run_stage(
            state,
            stage="searcher",
            start_message="Searching the local source store.",
            end_message="Collected source candidates and extracted findings.",
            action=lambda: self.searcher.run(state),
        )
        state.verification = self._run_stage(
            state,
            stage="verifier",
            start_message="Evaluating evidence quality.",
            end_message="Scored the evidence base and assigned a confidence value.",
            action=lambda: self.verifier.run(state),
        )
        state.report = self._run_stage(
            state,
            stage="synthesizer",
            start_message="Assembling the markdown report.",
            end_message="Markdown report assembled.",
            action=lambda: self.synthesizer.run(state),
        )
        state = self._run_stage(
            state,
            stage="quality",
            start_message="Applying the final quality gate.",
            end_message="Quality check finished.",
            action=lambda: self.quality.run(state),
        )

        state.finished_at = _utc_now()
        state.duration_ms = int((perf_counter() - run_started) * 1000)
        state.log_trace(
            "workflow",
            "run_completed",
            "Research workflow completed.",
            stage="workflow",
            duration_ms=state.duration_ms,
            confidence_score=state.confidence_score,
        )
        return state

    def _run_stage(self, state: ResearchState, stage: str, start_message: str, end_message: str, action: Any):
        state.log_trace(stage, f"{stage}_started", start_message, stage=stage)
        stage_started = perf_counter()
        result = action()
        duration_ms = int((perf_counter() - stage_started) * 1000)
        state.log_trace(stage, f"{stage}_completed", end_message, stage=stage, duration_ms=duration_ms)
        return result

    def run_topic(self, topic: str, audience: str = "portfolio reviewers", depth: str = "standard") -> Dict[str, Any]:
        request = ResearchRequest(topic=topic, audience=audience, depth=depth)
        state = self.run(request)
        return {
            "run_id": state.run_id,
            "started_at": state.started_at,
            "finished_at": state.finished_at,
            "duration_ms": state.duration_ms,
            "request": asdict(state.request),
            "tasks": [asdict(task) for task in state.tasks],
            "sources": [asdict(source) for source in state.sources],
            "findings": [asdict(finding) for finding in state.findings],
            "verification": asdict(state.verification) if state.verification else None,
            "confidence_score": state.confidence_score,
            "traces": [asdict(trace) for trace in state.traces],
            "report": state.report,
        }
