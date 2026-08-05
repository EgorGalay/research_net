from __future__ import annotations

import argparse
import json
from pathlib import Path

from .workflow import ResearchNet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ResearchNet multi-agent workflow.")
    parser.add_argument("--topic", required=True, help="Research topic to analyze.")
    parser.add_argument("--audience", default="portfolio reviewers", help="Target audience for the report.")
    parser.add_argument("--depth", default="standard", choices=["quick", "standard", "deep"], help="Research depth.")
    parser.add_argument("--output", help="Optional path to write the markdown report.")
    parser.add_argument("--export-json", help="Optional path to write the full structured result as JSON.")
    parser.add_argument("--json", action="store_true", help="Print the full structured result as JSON.")
    parser.add_argument("--serve", action="store_true", help="Run the FastAPI app with Uvicorn.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind when using --serve.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind when using --serve.")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.serve:
        try:
            from uvicorn import run
        except ImportError as exc:  # pragma: no cover - optional web dependency
            raise SystemExit("Uvicorn is not installed. Install dependencies first: pip install -e .") from exc

        run("researchnet.api:app", host=args.host, port=args.port, reload=False)
        return

    app = ResearchNet()
    result = app.run_topic(topic=args.topic, audience=args.audience, depth=args.depth)
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
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nSaved JSON result to {json_path}")


if __name__ == "__main__":
    main()
