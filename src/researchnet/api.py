from __future__ import annotations

from pathlib import Path
from typing import Literal

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover - optional web deps fallback for local test environments
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class BaseModel:
        def __init__(self, **data: object) -> None:
            annotations = getattr(self.__class__, "__annotations__", {})
            for name in annotations:
                default = getattr(self.__class__, name, None)
                value = data.get(name, default)
                if value is Ellipsis:
                    value = None
                setattr(self, name, value)

    def Field(default: object, **_: object) -> object:
        return default

    class _Route:
        def __init__(self, path: str, endpoint):
            self.path = path
            self.endpoint = endpoint

    class _Router:
        def __init__(self) -> None:
            self.routes: list[_Route] = []

    class FastAPI:
        def __init__(self, title: str, version: str) -> None:
            self.title = title
            self.version = version
            self.router = _Router()

        def get(self, path: str):
            return self._register(path)

        def post(self, path: str):
            return self._register(path)

        def _register(self, path: str):
            def decorator(endpoint):
                self.router.routes.append(_Route(path, endpoint))
                return endpoint

            return decorator

from .workflow import ResearchNet


class ResearchRequestPayload(BaseModel):
    topic: str = Field(..., min_length=1)
    audience: str = "portfolio reviewers"
    depth: Literal["quick", "standard", "deep"] = "standard"


def create_app(db_path: str | Path | None = None) -> FastAPI:
    runner = ResearchNet(db_path=db_path)
    app = FastAPI(title="ResearchNet API", version="0.3.0")

    @app.get("/")
    def index() -> dict[str, object]:
        return {
            "name": "ResearchNet API",
            "status": "ready",
            "version": "0.3.0",
            "docs_url": "/docs",
            "endpoints": {
                "health": "/health",
                "research": "POST /research",
            },
        }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/research")
    def research(payload: ResearchRequestPayload) -> dict[str, object]:
        return runner.run_topic(topic=payload.topic, audience=payload.audience, depth=payload.depth)

    @app.get("/runs")
    def list_runs(limit: int = 20) -> dict[str, object]:
        runs = runner.run_store.list_runs(limit=limit)
        return {"count": len(runs), "runs": [run.to_dict() for run in runs]}

    @app.get("/runs/latest")
    def latest_run() -> dict[str, object]:
        run = runner.run_store.get_latest_run()
        if run is None:
            raise HTTPException(status_code=404, detail="No runs have been recorded yet.")
        return run.to_dict()

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, object]:
        run = runner.run_store.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found.")
        return run.to_dict()

    return app


app = create_app()
