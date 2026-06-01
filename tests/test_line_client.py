from __future__ import annotations

import unittest

from line_property_automation.config import LineConfig
from line_property_automation.line_client import LineMessagingClient
from line_property_automation.openchat_policy import explain_openchat_limit


class LineClientTest(unittest.TestCase):
    def test_dry_run_bot_info(self) -> None:
        client = LineMessagingClient(LineConfig(dry_run=True))
        result = client.get_bot_info()
        self.assertTrue(result.ok)
        self.assertTrue(result.dry_run)
        self.assertEqual(result.data["path"], "/v2/bot/info")

    def test_missing_token_when_execute(self) -> None:
        client = LineMessagingClient(LineConfig(dry_run=False, channel_access_token=""))
        result = client.push_text("Uxxx", "hello")
        self.assertFalse(result.ok)
        self.assertIn("LINE_CHANNEL_ACCESS_TOKEN", result.data["missing"])

    def test_openchat_policy(self) -> None:
        self.assertIn("OpenChat", explain_openchat_limit())
        self.assertIn("unofficial scraping", explain_openchat_limit())


if __name__ == "__main__":
    unittest.main()
