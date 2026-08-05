from __future__ import annotations

from typing import Literal

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - import guard for optional web deps
    raise RuntimeError(
        "FastAPI support is not available. Install the project dependencies first: pip install -e ."
    ) from exc

from .workflow import ResearchNet


class ResearchRequestPayload(BaseModel):
    topic: str = Field(..., min_length=1)
    audience: str = "portfolio reviewers"
    depth: Literal["quick", "standard", "deep"] = "standard"


def create_app() -> FastAPI:
    app = FastAPI(title="ResearchNet API", version="0.2.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/research")
    def research(payload: ResearchRequestPayload) -> dict[str, object]:
        app_runner = ResearchNet()
        return app_runner.run_topic(topic=payload.topic, audience=payload.audience, depth=payload.depth)

    return app


app = create_app()
