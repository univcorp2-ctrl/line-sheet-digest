from __future__ import annotations

from dataclasses import dataclass
from typing import Any

COLUMN_ALIASES = {
    "title": ["title", "物件名", "名称", "name"],
    "rent": ["rent", "賃料", "家賃", "price"],
    "station": ["station", "最寄駅", "駅"],
    "address": ["address", "住所", "所在地"],
    "layout": ["layout", "間取り"],
    "area": ["area", "面積", "専有面積"],
    "url": ["url", "URL", "リンク", "link"],
    "description": ["description", "説明", "備考", "comment"],
}


@dataclass(frozen=True)
class PropertyListing:
    title: str
    rent: str
    station: str
    address: str
    url: str
    layout: str = ""
    area: str = ""
    description: str = ""

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "PropertyListing":
        normalized = {key: _pick(row, aliases) for key, aliases in COLUMN_ALIASES.items()}
        missing = [key for key in ["title", "rent", "station", "address", "url"] if not normalized[key]]
        if missing:
            raise ValueError(f"Missing required property fields: {', '.join(missing)}")
        return cls(**normalized)

    def to_text(self) -> str:
        lines = [
            f"🏠 {self.title}",
            f"賃料: {self.rent}",
            f"最寄駅: {self.station}",
            f"住所: {self.address}",
        ]
        if self.layout:
            lines.append(f"間取り: {self.layout}")
        if self.area:
            lines.append(f"面積: {self.area}")
        if self.description:
            lines.append(f"メモ: {self.description}")
        lines.append(self.url)
        return "\n".join(lines)

    def to_flex_message(self) -> dict[str, Any]:
        body_contents: list[dict[str, Any]] = [
            {"type": "text", "text": self.title, "weight": "bold", "size": "lg", "wrap": True},
            {"type": "text", "text": f"賃料: {self.rent}", "size": "sm", "wrap": True},
            {"type": "text", "text": f"最寄駅: {self.station}", "size": "sm", "wrap": True},
            {"type": "text", "text": f"住所: {self.address}", "size": "sm", "wrap": True},
        ]
        if self.layout or self.area:
            body_contents.append({"type": "text", "text": " / ".join([v for v in [self.layout, self.area] if v]), "size": "sm", "wrap": True})
        if self.description:
            body_contents.append({"type": "text", "text": self.description, "size": "xs", "color": "#666666", "wrap": True})
        return {
            "type": "flex",
            "altText": self.title[:400] or "物件情報",
            "contents": {
                "type": "bubble",
                "body": {"type": "box", "layout": "vertical", "spacing": "sm", "contents": body_contents},
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [{"type": "button", "style": "primary", "action": {"type": "uri", "label": "詳細を見る", "uri": self.url}}],
                },
            },
        }

    def to_csv_row(self) -> dict[str, str]:
        return {
            "title": self.title,
            "rent": self.rent,
            "station": self.station,
            "address": self.address,
            "layout": self.layout,
            "area": self.area,
            "url": self.url,
            "description": self.description,
        }


def _pick(row: dict[str, Any], aliases: list[str]) -> str:
    for alias in aliases:
        if alias in row and row[alias] is not None:
            value = str(row[alias]).strip()
            if value:
                return value
    return ""
