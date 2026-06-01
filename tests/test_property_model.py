from __future__ import annotations

import unittest

from line_property_automation.property_model import PropertyListing


class PropertyModelTest(unittest.TestCase):
    def test_from_japanese_row_and_text(self) -> None:
        listing = PropertyListing.from_row(
            {
                "物件名": "青山サンプル",
                "賃料": "18万円",
                "最寄駅": "表参道",
                "住所": "東京都港区",
                "URL": "https://example.com/a",
                "間取り": "1LDK",
            }
        )
        self.assertIn("青山サンプル", listing.to_text())
        self.assertIn("1LDK", listing.to_text())

    def test_missing_required_fields(self) -> None:
        with self.assertRaises(ValueError):
            PropertyListing.from_row({"物件名": "URLなし"})

    def test_flex_message_shape(self) -> None:
        listing = PropertyListing(
            title="渋谷テスト",
            rent="13万円",
            station="渋谷",
            address="東京都渋谷区",
            url="https://example.com",
        )
        message = listing.to_flex_message()
        self.assertEqual(message["type"], "flex")
        self.assertEqual(message["contents"]["type"], "bubble")


if __name__ == "__main__":
    unittest.main()
