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
researchnet research --topic "AI agents for customer support"
```

Legacy shortcut still works:

```bash
researchnet --topic "AI agents for customer support"
```

Print the full structured result as JSON:

```bash
researchnet research --topic "AI agents for customer support" --json
```

Export the JSON payload to disk:

```bash
researchnet research --topic "AI agents for customer support" --export-json outputs/run.json
```

Export directly with the dedicated subcommand:

```bash
researchnet export --topic "AI agents for customer support" --output outputs/run.json
```

Run the FastAPI service:

```bash
researchnet serve
```

The `serve` command does not require `--topic`.

## What This Project Shows

- multi-agent orchestration
- per-agent traceability
- shared state between agents
- deterministic workflow steps
- structured outputs
- confidence scoring for the verification step
- a CLI with `research`, `export`, and `serve` subcommands
- a REST API for remote execution
- a clean path to add LLMs, web search, vector search, and persistence later

## API

`GET /`

Returns a small welcome payload with links to the main endpoints.

`GET /health`

Returns a simple status check for orchestration or deployment probes.

`POST /research`

Example payload:

```json
{
  "topic": "AI agents for customer support",
  "audience": "portfolio reviewers",
  "depth": "standard"
}
```
