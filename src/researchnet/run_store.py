from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from .models import (
    Finding,
    ResearchRequest,
    ResearchState,
    RunDetail,
    RunSummary,
    SourceDocument,
    ResearchTask,
    TraceEvent,
    VerificationNote,
)


class RunStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or Path("work") / "researchnet.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def save(self, state: ResearchState) -> RunDetail:
        detail = RunDetail.from_state(state)
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id,
                    started_at,
                    finished_at,
                    duration_ms,
                    topic,
                    audience,
                    depth,
                    request_json,
                    report,
                    tasks_json,
                    confidence_score,
                    traces_json,
                    sources_json,
                    findings_json,
                    verification_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    detail.run_id,
                    detail.started_at,
                    detail.finished_at,
                    detail.duration_ms,
                    detail.topic,
                    detail.audience,
                    detail.depth,
                    json.dumps(detail.request.to_dict(), ensure_ascii=False),
                    detail.report,
                    json.dumps([task.to_dict() for task in detail.tasks], ensure_ascii=False),
                    detail.confidence_score,
                    json.dumps([trace.to_dict() for trace in detail.traces], ensure_ascii=False),
                    json.dumps([source.to_dict() for source in detail.sources], ensure_ascii=False),
                    json.dumps([finding.to_dict() for finding in detail.findings], ensure_ascii=False),
                    json.dumps(detail.verification.to_dict(), ensure_ascii=False) if detail.verification else None,
                ),
            )
            connection.commit()
        return detail

    def list_runs(self, limit: int = 20) -> list[RunSummary]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT run_id, started_at, finished_at, duration_ms, topic, audience, depth, confidence_score
                FROM runs
                ORDER BY started_at DESC, run_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_summary(row) for row in rows]

    def get_run(self, run_id: str) -> RunDetail | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT run_id, started_at, finished_at, duration_ms, topic, audience, depth, request_json,
                       report, tasks_json, confidence_score, traces_json, sources_json, findings_json, verification_json
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_detail(row)

    def get_latest_run(self) -> RunDetail | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT run_id, started_at, finished_at, duration_ms, topic, audience, depth, request_json,
                       report, tasks_json, confidence_score, traces_json, sources_json, findings_json, verification_json
                FROM runs
                ORDER BY started_at DESC, run_id DESC
                LIMIT 1
                """
            ).fetchone()
        if row is None:
            return None
        return self._row_to_detail(row)

    def _ensure_schema(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    audience TEXT NOT NULL,
                    depth TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    report TEXT NOT NULL,
                    tasks_json TEXT NOT NULL DEFAULT '[]',
                    confidence_score REAL,
                    traces_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    findings_json TEXT NOT NULL,
                    verification_json TEXT
                )
                """
            )
            existing_columns = {row["name"] for row in connection.execute("PRAGMA table_info(runs)").fetchall()}
            if "tasks_json" not in existing_columns:
                connection.execute("ALTER TABLE runs ADD COLUMN tasks_json TEXT NOT NULL DEFAULT '[]'")
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_runs_started_at
                ON runs(started_at DESC, run_id DESC)
                """
            )
            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_summary(self, row: sqlite3.Row) -> RunSummary:
        return RunSummary(
            run_id=row["run_id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            duration_ms=row["duration_ms"],
            topic=row["topic"],
            audience=row["audience"],
            depth=row["depth"],
            confidence_score=row["confidence_score"],
        )

    def _row_to_detail(self, row: sqlite3.Row) -> RunDetail:
        request = ResearchRequest(**json.loads(row["request_json"]))
        tasks = [ResearchTask(**item) for item in self._load_json_list(row["tasks_json"])]
        traces = [TraceEvent(**item) for item in self._load_json_list(row["traces_json"])]
        sources = [SourceDocument(**item) for item in self._load_json_list(row["sources_json"])]
        findings = [Finding(**item) for item in self._load_json_list(row["findings_json"])]
        verification_payload = self._load_json_object(row["verification_json"])
        verification = VerificationNote(**verification_payload) if verification_payload is not None else None
        return RunDetail(
            run_id=row["run_id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            duration_ms=row["duration_ms"],
            topic=row["topic"],
            audience=row["audience"],
            depth=row["depth"],
            confidence_score=row["confidence_score"],
            request=request,
            report=row["report"],
            tasks=tasks,
            traces=traces,
            sources=sources,
            findings=findings,
            verification=verification,
        )

    def _load_json_list(self, raw: str | None) -> list[dict[str, Any]]:
        if not raw:
            return []
        data = json.loads(raw)
        return list(data) if isinstance(data, list) else []

    def _load_json_object(self, raw: str | None) -> dict[str, Any] | None:
        if not raw:
            return None
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
