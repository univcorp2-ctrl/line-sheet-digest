from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LineConfig:
    """Configuration for LINE Messaging API calls.

    Secrets must be supplied through environment variables or a secret manager.
    Never commit real token values to this repository.
    """

    channel_access_token: str = ""
    channel_secret: str = ""
    default_to: str = ""
    dry_run: bool = True

    @classmethod
    def from_env(cls) -> "LineConfig":
        return cls(
            channel_access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip(),
            channel_secret=os.getenv("LINE_CHANNEL_SECRET", "").strip(),
            default_to=os.getenv("LINE_DEFAULT_TO", "").strip(),
            dry_run=os.getenv("LINE_DRY_RUN", "true").strip().lower() not in {"0", "false", "no"},
        )

    def missing_for_send(self) -> list[str]:
        missing: list[str] = []
        if not self.channel_access_token:
            missing.append("LINE_CHANNEL_ACCESS_TOKEN")
        return missing
