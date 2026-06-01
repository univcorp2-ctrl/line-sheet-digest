#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from line_property_automation.config import LineConfig
from line_property_automation.line_client import LineMessagingClient
from line_property_automation.property_ingest import load_properties, write_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize property data and prepare LINE messages.")
    parser.add_argument("--input", required=True, type=Path, help="CSV/JSON/JSONL property file")
    parser.add_argument("--output", default=Path("out"), type=Path, help="Output directory")
    parser.add_argument("--format", choices=["all"], default="all")
    parser.add_argument("--send", action="store_true", help="Send first generated Flex messages to LINE")
    parser.add_argument("--to", default=os.getenv("LINE_DEFAULT_TO", ""), help="LINE userId/groupId/roomId recipient")
    parser.add_argument("--execute", action="store_true", help="Actually call LINE API. Without this, dry-run is forced.")
    args = parser.parse_args()

    properties = load_properties(args.input)
    outputs = write_outputs(properties, args.output)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))

    if args.send:
        if not args.to:
            print("--send requires --to or LINE_DEFAULT_TO", file=sys.stderr)
            return 2
        config = LineConfig.from_env()
        if not args.execute:
            config = LineConfig(
                channel_access_token=config.channel_access_token,
                channel_secret=config.channel_secret,
                default_to=config.default_to,
                dry_run=True,
            )
        client = LineMessagingClient(config)
        messages = [item.to_flex_message() for item in properties[:5]]
        result = client.push_messages(args.to, messages)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
        if not result.ok:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
