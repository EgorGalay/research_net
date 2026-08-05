from __future__ import annotations

import argparse
from pathlib import Path

from .workflow import ResearchNet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ResearchNet multi-agent workflow.")
    parser.add_argument("--topic", required=True, help="Research topic to analyze.")
    parser.add_argument("--audience", default="portfolio reviewers", help="Target audience for the report.")
    parser.add_argument("--depth", default="standard", choices=["quick", "standard", "deep"], help="Research depth.")
    parser.add_argument("--output", help="Optional path to write the markdown report.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app = ResearchNet()
    result = app.run_topic(topic=args.topic, audience=args.audience, depth=args.depth)
    report = result["report"]

    print(report)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"\nSaved report to {output_path}")


if __name__ == "__main__":
    main()
