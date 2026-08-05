from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
from typing import List

from .models import SourceDocument


class SourceStore:
    def __init__(self, sources: List[SourceDocument] | None = None) -> None:
        self._sources = sources or self._load_default_sources()

    def _load_default_sources(self) -> List[SourceDocument]:
        return [
            SourceDocument(
                source_id="src-001",
                title="Multi-agent systems in production",
                summary="A practical overview of orchestration patterns, shared state, and tool use in multi-agent applications.",
                url="https://example.com/multi-agent-systems",
                tags=["agents", "orchestration", "production", "state"],
                credibility=0.86,
            ),
            SourceDocument(
                source_id="src-002",
                title="Research workflows with planning and verification",
                summary="Describes a planner-searcher-verifier loop for higher-quality research outputs.",
                url="https://example.com/research-workflows",
                tags=["planning", "verification", "research", "quality"],
                credibility=0.83,
            ),
            SourceDocument(
                source_id="src-003",
                title="Designing reliable AI assistants",
                summary="Focuses on traceability, retries, confidence scoring, and human-in-the-loop review.",
                url="https://example.com/reliable-ai-assistants",
                tags=["reliability", "confidence", "review", "agents"],
                credibility=0.9,
            ),
            SourceDocument(
                source_id="src-004",
                title="Fast prototyping for portfolio-grade AI demos",
                summary="Suggests starting with a narrow task, deterministic scaffolding, and strong documentation.",
                url="https://example.com/portfolio-ai-demos",
                tags=["portfolio", "mvp", "docs", "demo"],
                credibility=0.79,
            ),
        ]

    def all(self) -> List[SourceDocument]:
        return list(self._sources)

    def search(self, query_terms: List[str], limit: int = 3) -> List[SourceDocument]:
        scored = []
        normalized_terms = {term.lower() for term in query_terms if term.strip()}
        for source in self._sources:
            haystack = " ".join([source.title, source.summary, " ".join(source.tags)]).lower()
            score = sum(1 for term in normalized_terms if term in haystack)
            if score:
                scored.append((score + source.credibility, source))
        scored.sort(key=lambda item: item[0], reverse=True)
        if scored:
            return [source for _, source in scored[:limit]]

        fallback = sorted(self._sources, key=lambda source: source.credibility, reverse=True)
        return fallback[:limit]

    def save_snapshot(self, path: str | Path) -> None:
        payload = [asdict(source) for source in self._sources]
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
