# CLAUDE.md

Claude Codeはこのファイルをプロジェクトメモリとして扱う。

## プロジェクト概要

LINE公式アカウントのMessaging APIでWebhook受信、Google Sheets保存、要約通知、物件情報のLINE配信用整形を行うテンプレート。OpenChatは公式APIでできる範囲だけ扱い、非公式な自動操作は実装しない。

## Claudeへの指示

- 変更時は `AGENTS.md` のルールを優先する。
- Secretや`.env`を読まない。
- 実送信につながる変更はdry-runをデフォルトにする。
- 物件データの必須項目は `title/rent/station/address/url`。
- LINE API実行コードは `LineMessagingClient` に集約する。
- ドキュメントは日本語で、初心者向け手順を維持する。

## 検証コマンド

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
cd cloudflare-worker && npm test
```
