#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from line_property_automation.config import LineConfig
from line_property_automation.line_client import LineMessagingClient
from line_property_automation.openchat_policy import explain_openchat_limit


def main() -> int:
    parser = argparse.ArgumentParser(description="LINE Official Account API helper.")
    parser.add_argument("--execute", action="store_true", help="Actually call LINE API. Default is dry-run.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("bot-info")
    sub.add_parser("quota")
    sub.add_parser("openchat-policy")

    push = sub.add_parser("push-text")
    push.add_argument("--to", required=True)
    push.add_argument("--text", required=True)

    broadcast = sub.add_parser("broadcast-text")
    broadcast.add_argument("--text", required=True)

    args = parser.parse_args()

    if args.command == "openchat-policy":
        print(explain_openchat_limit())
        return 0

    base_config = LineConfig.from_env()
    config = LineConfig(
        channel_access_token=base_config.channel_access_token,
        channel_secret=base_config.channel_secret,
        default_to=base_config.default_to,
        dry_run=not args.execute or base_config.dry_run,
    )
    client = LineMessagingClient(config)

    if args.command == "bot-info":
        result = client.get_bot_info()
    elif args.command == "quota":
        result = client.get_quota()
    elif args.command == "push-text":
        result = client.push_text(args.to, args.text)
    elif args.command == "broadcast-text":
        result = client.broadcast_text(args.text)
    else:
        parser.error("unknown command")

    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
