from __future__ import annotations

from typing import List

from .models import (
    Finding,
    ResearchRequest,
    ResearchState,
    ResearchTask,
    SourceDocument,
    VerificationNote,
)
from .source_store import SourceStore


class PlannerAgent:
    def run(self, request: ResearchRequest) -> List[ResearchTask]:
        topic = request.topic.strip()
        tasks = [
            ResearchTask(
                title=f"Define scope for {topic}",
                rationale="Clarify the exact problem, audience, and success criteria.",
            ),
            ResearchTask(
                title=f"Collect evidence about {topic}",
                rationale="Find supporting material that explains the core idea and practical value.",
            ),
            ResearchTask(
                title=f"Check reliability and risks for {topic}",
                rationale="Look for tradeoffs, weak spots, and missing evidence.",
            ),
        ]
        if request.depth == "deep":
            tasks.append(
                ResearchTask(
                    title=f"Identify implementation opportunities for {topic}",
                    rationale="Translate research into a concrete product direction for a stronger portfolio story.",
                )
            )
        elif request.depth == "quick":
            tasks = tasks[:2]
        return tasks


class SearcherAgent:
    def __init__(self, store: SourceStore) -> None:
        self.store = store

    def run(self, state: ResearchState) -> List[Finding]:
        terms = self._extract_terms(state)
        sources = self.store.search(terms, limit=4)
        findings = []
        for source in sources:
            relevance = self._relevance_score(state.request.topic, source)
            findings.append(
                Finding(
                    source_id=source.source_id,
                    evidence=source.summary,
                    relevance=relevance,
                )
            )
        state.sources = sources
        return findings

    def _extract_terms(self, state: ResearchState) -> List[str]:
        base = state.request.topic.lower().split()
        extra = [task.title for task in state.tasks]
        return base + " ".join(extra).lower().split()

    def _relevance_score(self, topic: str, source: SourceDocument) -> float:
        topic_terms = {token for token in topic.lower().split() if len(token) > 2}
        source_terms = set(source.tags) | set(source.title.lower().split()) | set(source.summary.lower().split())
        overlap = len(topic_terms & source_terms)
        return round(min(1.0, 0.35 + overlap * 0.18 + source.credibility * 0.35), 2)


class VerifierAgent:
    def run(self, state: ResearchState) -> VerificationNote:
        if not state.findings:
            return VerificationNote(status="weak", note="No evidence was collected, so the result is too thin.")

        avg_relevance = sum(f.relevance for f in state.findings) / len(state.findings)
        avg_credibility = sum(s.credibility for s in state.sources) / len(state.sources)
        confidence = round((avg_relevance * 0.6) + (avg_credibility * 0.4), 2)

        if confidence >= 0.75:
            note = "Evidence quality looks solid and the result is defensible."
            status = "strong"
        elif confidence >= 0.55:
            note = "Evidence is usable, but the final report should mention assumptions and caveats."
            status = "moderate"
        else:
            note = "The evidence base is weak. The topic needs better sources before a strong conclusion."
            status = "weak"

        return VerificationNote(status=status, note=f"{note} Confidence score: {confidence}.")


class SynthesizerAgent:
    def run(self, state: ResearchState) -> str:
        lines = []
        lines.append(f"# Research Brief: {state.request.topic}")
        lines.append("")
        lines.append(f"Audience: {state.request.audience}")
        lines.append(f"Depth: {state.request.depth}")
        lines.append("")
        lines.append("## Plan")
        for index, task in enumerate(state.tasks, start=1):
            lines.append(f"{index}. **{task.title}** - {task.rationale}")
        lines.append("")
        lines.append("## Key Findings")
        for finding, source in self._match_findings_to_sources(state):
            lines.append(f"- **{source.title}**")
            lines.append(f"  - Relevance: `{finding.relevance}`")
            lines.append(f"  - Evidence: {finding.evidence}")
            lines.append(f"  - Source: {source.url}")
        lines.append("")
        lines.append("## Verification")
        if state.verification:
            lines.append(f"- Status: `{state.verification.status}`")
            lines.append(f"- Note: {state.verification.note}")
        else:
            lines.append("- Verification not available.")
        lines.append("")
        lines.append("## Portfolio Angle")
        lines.append(
            "- This project demonstrates multi-agent orchestration, shared state, deterministic reasoning steps, and a clear path to real tool integration."
        )
        return "\n".join(lines)

    def _match_findings_to_sources(self, state: ResearchState):
        source_by_id = {source.source_id: source for source in state.sources}
        for finding in state.findings:
            source = source_by_id.get(finding.source_id)
            if source:
                yield finding, source


class QualityAgent:
    def run(self, state: ResearchState) -> ResearchState:
        if state.verification and state.verification.status == "weak":
            state.report += "\n\n> Note: The workflow flagged weak evidence. Add more sources before using this as a final answer."
        return state
