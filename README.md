# ResearchNet

ResearchNet is a portfolio-ready multi-agent research network MVP.

It demonstrates a simple but realistic agent pipeline:

- `PlannerAgent` breaks a topic into research tasks
- `SearcherAgent` retrieves and ranks supporting sources
- `VerifierAgent` checks confidence and flags weak evidence
- `SynthesizerAgent` turns the result into a clean markdown report

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

## What This Project Shows

- multi-agent orchestration
- shared state between agents
- deterministic workflow steps
- structured outputs
- a clean path to add LLMs, web search, vector search, and persistence later

## Next Up

Planned upgrades:

- plug in a real search provider
- add OpenAI/LLM-backed reasoning
- expose a FastAPI endpoint
- store run history in SQLite or Postgres
- add a small web UI for traces and source inspection
