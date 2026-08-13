from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .workflow import ResearchNet


COMMANDS = {"research", "export", "serve"}
RESEARCH_FLAGS_WITH_VALUES = {"--topic", "--audience", "--depth", "--output", "--export-json"}
RESEARCH_FLAGS_WITHOUT_VALUES = {"--json"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ResearchNet multi-agent workflow.")
    subparsers = parser.add_subparsers(dest="command")

    research = subparsers.add_parser("research", help="Run a research brief and print it to the terminal.")
    _add_research_arguments(research)
    research.add_argument("--output", help="Optional path to write the markdown report.")
    research.add_argument("--export-json", help="Optional path to write the full structured result as JSON.")
    research.add_argument("--json", action="store_true", help="Print the full structured result as JSON.")

    export = subparsers.add_parser("export", help="Export the research result to a file.")
    _add_research_arguments(export)
    export.add_argument("--output", required=True, help="Path to write the exported file.")
    export.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Export format for the output file.",
    )

    serve = subparsers.add_parser("serve", help="Run the FastAPI app with Uvicorn.")
    serve.add_argument("--host", default="127.0.0.1", help="Host to bind when serving the API.")
    serve.add_argument("--port", type=int, default=8000, help="Port to bind when serving the API.")

    return parser


def _add_research_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--topic", required=True, help="Research topic to analyze.")
    parser.add_argument("--audience", default="portfolio reviewers", help="Target audience for the report.")
    parser.add_argument("--depth", default="standard", choices=["quick", "standard", "deep"], help="Research depth.")


def _normalize_argv(argv: Sequence[str] | None) -> list[str]:
    values = list(sys.argv[1:] if argv is None else argv)
    if not values:
        return values
    if values[0] in {"-h", "--help"}:
        return values
    if "--serve" in values:
        filtered: list[str] = []
        skip_next = False
        for value in values:
            if skip_next:
                skip_next = False
                continue
            if value == "--serve":
                continue
            if value in RESEARCH_FLAGS_WITH_VALUES:
                skip_next = True
                continue
            if value in RESEARCH_FLAGS_WITHOUT_VALUES:
                continue
            filtered.append(value)
        return ["serve", *filtered]
    if values[0] not in COMMANDS and not values[0].startswith("-"):
        return ["research", *values]
    if values[0].startswith("-"):
        return ["research", *values]
    return values


def _run_research(args: argparse.Namespace) -> dict[str, object]:
    app = ResearchNet()
    return app.run_topic(topic=args.topic, audience=args.audience, depth=args.depth)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(_normalize_argv(argv))

    if args.command == "serve":
        try:
            from uvicorn import run
        except ImportError as exc:  # pragma: no cover - optional web dependency
            raise SystemExit("Uvicorn is not installed. Install dependencies first: pip install -e .") from exc

        run("researchnet.api:app", host=args.host, port=args.port, reload=False)
        return

    if args.command == "export":
        result = _run_research(args)
        output_path = Path(args.output)
        if args.format == "json":
            _write_json(output_path, result)
        else:
            output_path.write_text(result["report"], encoding="utf-8")
        print(f"Saved {args.format} export to {output_path}")
        return

    if args.command != "research":
        parser.print_help()
        raise SystemExit(1)

    result = _run_research(args)
    report = result["report"]

    if args.json or args.export_json:
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if args.json:
            print(payload)
        else:
            print(report)
    else:
        print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nSaved report to {output_path}")

    if args.export_json:
        json_path = Path(args.export_json)
        _write_json(json_path, result)
        print(f"\nSaved JSON result to {json_path}")


if __name__ == "__main__":
    main()
