#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

LOCAL_OPTIONAL = [
    "LINE_CHANNEL_ACCESS_TOKEN",
    "LINE_CHANNEL_SECRET",
    "LINE_DEFAULT_TO",
    "GAS_WEB_APP_URL",
    "FORWARD_SHARED_TOKEN",
    "TARGET_SOURCE_IDS",
]
PRODUCTION_REQUIRED = [
    "LINE_CHANNEL_ACCESS_TOKEN",
    "LINE_CHANNEL_SECRET",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate environment variables for LINE automation.")
    parser.add_argument("--mode", choices=["local", "production"], default="local")
    args = parser.parse_args()

    required = PRODUCTION_REQUIRED if args.mode == "production" else []
    optional = LOCAL_OPTIONAL
    missing_required = [key for key in required if not os.getenv(key)]
    present = [key for key in optional if os.getenv(key)]
    missing_optional = [key for key in optional if not os.getenv(key)]

    print(f"mode={args.mode}")
    print(f"present={','.join(present) if present else '(none)'}")
    print(f"missing_optional={','.join(missing_optional) if missing_optional else '(none)'}")
    if missing_required:
        print(f"missing_required={','.join(missing_required)}")
        return 1
    print("ok=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
