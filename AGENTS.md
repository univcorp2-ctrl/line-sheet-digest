# AGENTS.md

このリポジトリは、LINE公式アカウントの公式APIと物件情報配信だけを対象にする。Codexやその他のAIコーディングエージェントは、このファイルを作業前に読むこと。

## 守ること

- LINE Channel Secret、Channel Access Token、OpenAI API Key、Google認証JSONをコミットしない。
- `.env`, `.env.*`, `secrets/**`, `credentials*.json` を読まない・変更しない。
- OpenChatの非公式クロール、個人LINEクライアントの自動操作、ブラウザセッション乗っ取りを実装しない。
- 実送信は `--execute` が明示されたCLIだけで行う。デフォルトはdry-run。
- 物件情報は `PropertyListing` で正規化し、必須項目 `title/rent/station/address/url` を満たすこと。

## テスト

Pythonを変更したら:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
```

Cloudflare Workerを変更したら:

```bash
cd cloudflare-worker && npm test
```

## 主要ファイル

- `scripts/property_pipeline.py`: 物件CSV/JSONからLINE配信用成果物を生成
- `scripts/line_oa.py`: LINE公式アカウントAPI操作CLI
- `cloudflare-worker/src/index.js`: LINE Webhook署名検証とGAS転送
- `docs/LINE_API_RESEARCH_ja.md`: 公式API調査と制限
- `docs/SETUP_LINE_ja.md`: 初期設定手順
