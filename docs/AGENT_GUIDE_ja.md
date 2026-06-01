# Claude Code / Codex 運用ガイド

## 目的

Claude CodeやCodexに、LINE公式アカウント運用と物件情報配信の定型作業を任せるためのリポジトリ特化ルールです。

## 読ませるファイル

- Codex: `AGENTS.md` と `CODEX.md`
- Claude Code: `CLAUDE.md` と `.claude/settings.json`
- 共通: `docs/LINE_API_RESEARCH_ja.md`

## 依頼例

```text
物件CSVを取り込んでLINE配信用Flex Messageを生成して。実送信はしないで。
```

```text
LINE公式アカウントのWebhookで物件問い合わせを受けたら、Google Sheetsに保存する処理を追加して。テストも更新して。
```

```text
OpenChatに直接投稿するのではなく、手動確認用テキストを生成して。
```

## エージェントに守らせる安全ルール

- Secretを読ませない。
- `.env` をコミットしない。
- `--execute` なしでLINE API実送信しない。
- OpenChatの非公式自動操作を作らない。
- 変更後はテストとサンプル生成を実行する。

## 期待する検証

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
cd cloudflare-worker && npm test
```
