from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .property_model import PropertyListing


def load_properties(path: Path) -> list[PropertyListing]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [PropertyListing.from_row(row) for row in csv.DictReader(handle)]
    if suffix in {".json", ".jsonl"}:
        return _load_json(path)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def _load_json(path: Path) -> list[PropertyListing]:
    if path.suffix.lower() == ".jsonl":
        rows: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else data.get("properties", [])
    return [PropertyListing.from_row(row) for row in rows]


def write_outputs(properties: list[PropertyListing], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / "line_messages.txt"
    flex_path = output_dir / "line_flex_messages.json"
    csv_path = output_dir / "properties.normalized.csv"
    summary_path = output_dir / "summary.txt"

    text_path.write_text("\n\n---\n\n".join(item.to_text() for item in properties), encoding="utf-8")
    flex_path.write_text(json.dumps([item.to_flex_message() for item in properties], ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["title", "rent", "station", "address", "layout", "area", "url", "description"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in properties:
            writer.writerow(item.to_csv_row())
    summary_path.write_text(_summary(properties), encoding="utf-8")
    return {"text": text_path, "flex": flex_path, "csv": csv_path, "summary": summary_path}


def _summary(properties: list[PropertyListing]) -> str:
    if not properties:
        return "物件データは0件です。"
    stations = sorted({item.station for item in properties})
    return "\n".join(
        [
            f"物件件数: {len(properties)}",
            f"対象駅: {', '.join(stations)}",
            "生成物: line_messages.txt / line_flex_messages.json / properties.normalized.csv",
            "実送信前に内容・URL・料金表記を確認してください。",
        ]
    )
