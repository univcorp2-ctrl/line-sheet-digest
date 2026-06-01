"""Policy helpers for LINE OpenChat handling.

There is no supported server-side Messaging API workflow in this repository for
joining LINE OpenChat rooms, scraping message history, or posting as a personal
LINE user. Keep OpenChat work to manual operations or official SDK/API surfaces.
"""

from __future__ import annotations


def explain_openchat_limit() -> str:
    return (
        "LINE OpenChat is not treated as an official Messaging API Bot target in this repository. "
        "Use LINE Official Account 1:1 chat, group chat, multi-person chat, or a manual OpenChat operation instead. "
        "Do not automate personal LINE clients, browser sessions, or unofficial scraping."
    )
