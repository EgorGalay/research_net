from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Any

from .agents import PlannerAgent, QualityAgent, SearcherAgent, SynthesizerAgent, VerifierAgent
from .models import ResearchRequest, ResearchState
from .source_store import SourceStore


class ResearchNet:
    def __init__(self, store: SourceStore | None = None) -> None:
        self.store = store or SourceStore()
        self.planner = PlannerAgent()
        self.searcher = SearcherAgent(self.store)
        self.verifier = VerifierAgent()
        self.synthesizer = SynthesizerAgent()
        self.quality = QualityAgent()

    def run(self, request: ResearchRequest) -> ResearchState:
        state = ResearchState(request=request)
        state.log_trace("workflow", "run_started", "Research workflow started.", topic=request.topic, depth=request.depth)
        state.tasks = self.planner.run(state)
        state.findings = self.searcher.run(state)
        state.verification = self.verifier.run(state)
        state.report = self.synthesizer.run(state)
        state = self.quality.run(state)
        state.log_trace("workflow", "run_completed", "Research workflow completed.", confidence_score=state.confidence_score)
        return state

    def run_topic(self, topic: str, audience: str = "portfolio reviewers", depth: str = "standard") -> Dict[str, Any]:
        request = ResearchRequest(topic=topic, audience=audience, depth=depth)
        state = self.run(request)
        return {
            "request": asdict(state.request),
            "tasks": [asdict(task) for task in state.tasks],
            "sources": [asdict(source) for source in state.sources],
            "findings": [asdict(finding) for finding in state.findings],
            "verification": asdict(state.verification) if state.verification else None,
            "confidence_score": state.confidence_score,
            "traces": [asdict(trace) for trace in state.traces],
            "report": state.report,
        }
