from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class ResearchRequest:
    topic: str
    audience: str = "portfolio reviewers"
    depth: str = "standard"


@dataclass(slots=True)
class ResearchTask:
    title: str
    rationale: str


@dataclass(slots=True)
class TraceEvent:
    timestamp: str
    stage: str
    agent: str
    action: str
    message: str
    duration_ms: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceDocument:
    source_id: str
    title: str
    summary: str
    url: str
    tags: List[str] = field(default_factory=list)
    credibility: float = 0.5


@dataclass(slots=True)
class Finding:
    source_id: str
    evidence: str
    relevance: float


@dataclass(slots=True)
class VerificationNote:
    status: str
    note: str
    confidence_score: float = 0.0


@dataclass(slots=True)
class ResearchState:
    request: ResearchRequest
    run_id: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration_ms: int = 0
    tasks: List[ResearchTask] = field(default_factory=list)
    sources: List[SourceDocument] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    verification: Optional[VerificationNote] = None
    report: str = ""
    confidence_score: Optional[float] = None
    traces: List[TraceEvent] = field(default_factory=list)

    def log_trace(
        self,
        agent: str,
        action: str,
        message: str,
        *,
        stage: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **details: Any,
    ) -> None:
        self.traces.append(
            TraceEvent(
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                stage=stage or agent,
                agent=agent,
                action=action,
                message=message,
                duration_ms=duration_ms,
                details={key: value for key, value in details.items() if value is not None},
            )
        )
