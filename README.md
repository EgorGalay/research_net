# ResearchNet

ResearchNet is a portfolio-ready multi-agent research network MVP.

It demonstrates a simple but realistic agent pipeline:

- `PlannerAgent` breaks a topic into research tasks
- `SearcherAgent` retrieves and ranks supporting sources
- `VerifierAgent` computes a confidence score and flags weak evidence
- `SynthesizerAgent` turns the result into a clean markdown report
- every agent emits a trace event so runs are easy to inspect

The current implementation runs end-to-end with local sample sources so it is easy to demo, extend, and test without API keys.

## Quick Start

```bash
python -m researchnet --topic "AI agents for customer support"
```

Or install locally:

```bash
pip install -e .
researchnet --topic "AI agents for customer support"
```

Print the full structured result as JSON:

```bash
researchnet --topic "AI agents for customer support" --json
```

Export the JSON payload to disk:

```bash
researchnet --topic "AI agents for customer support" --export-json outputs/run.json
```

Run the FastAPI service:

```bash
researchnet --serve
```

## What This Project Shows

- multi-agent orchestration
- per-agent traceability
- shared state between agents
- deterministic workflow steps
- structured outputs
- confidence scoring for the verification step
- a CLI that can emit markdown or JSON
- a REST API for remote execution
- a clean path to add LLMs, web search, vector search, and persistence later

## API

`POST /research`

Example payload:

```json
{
  "topic": "AI agents for customer support",
  "audience": "portfolio reviewers",
  "depth": "standard"
}
```

`GET /health`

Returns a simple status check for orchestration or deployment probes.
