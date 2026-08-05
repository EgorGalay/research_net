from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


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


@dataclass(slots=True)
class ResearchState:
    request: ResearchRequest
    tasks: List[ResearchTask] = field(default_factory=list)
    sources: List[SourceDocument] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    verification: Optional[VerificationNote] = None
    report: str = ""
