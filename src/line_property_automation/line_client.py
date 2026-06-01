from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .config import LineConfig


@dataclass
class LineApiResult:
    ok: bool
    status: int
    data: Any
    dry_run: bool = False


class LineMessagingClient:
    """Small stdlib LINE Messaging API client with dry-run safety.

    The client intentionally supports only official Messaging API endpoints and
    does not automate LINE OpenChat, personal LINE clients, or browser sessions.
    """

    base_url = "https://api.line.me"

    def __init__(self, config: LineConfig):
        self.config = config

    def get_bot_info(self) -> LineApiResult:
        return self._request("GET", "/v2/bot/info")

    def push_text(self, to: str, text: str) -> LineApiResult:
        return self.push_messages(to, [{"type": "text", "text": text}])

    def push_messages(self, to: str, messages: list[dict[str, Any]]) -> LineApiResult:
        payload = {"to": to, "messages": messages[:5]}
        return self._request("POST", "/v2/bot/message/push", payload)

    def broadcast_text(self, text: str) -> LineApiResult:
        payload = {"messages": [{"type": "text", "text": text}]}
        return self._request("POST", "/v2/bot/message/broadcast", payload)

    def get_quota(self) -> LineApiResult:
        return self._request("GET", "/v2/bot/message/quota")

    def get_quota_consumption(self) -> LineApiResult:
        return self._request("GET", "/v2/bot/message/quota/consumption")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> LineApiResult:
        if self.config.dry_run:
            return LineApiResult(ok=True, status=200, data={"method": method, "path": path, "payload": payload}, dry_run=True)

        missing = self.config.missing_for_send()
        if missing:
            return LineApiResult(ok=False, status=0, data={"error": "missing_env", "missing": missing})

        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.config.channel_access_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                text = response.read().decode("utf-8")
                return LineApiResult(ok=200 <= response.status < 300, status=response.status, data=_parse_json(text))
        except urllib.error.HTTPError as error:
            text = error.read().decode("utf-8", errors="replace")
            return LineApiResult(ok=False, status=error.code, data=_parse_json(text))
        except urllib.error.URLError as error:
            return LineApiResult(ok=False, status=0, data={"error": "network_error", "detail": str(error)})


def _parse_json(text: str) -> Any:
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}
