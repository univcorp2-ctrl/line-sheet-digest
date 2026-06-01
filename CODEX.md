# CODEX.md

Codexでこのリポジトリを扱うときの作業指示です。

## ミッション

LINE公式アカウントのMessaging APIと物件情報配信を、公式に許可されたAPI範囲で自動化する。ユーザーが「物件情報を開始」と言ったら、CSV/JSONの正規化、LINE配信用テキスト/Flex Message生成、dry-run、テスト、CI artifact確認まで進める。

## 作業手順

1. まず `AGENTS.md` と `docs/LINE_API_RESEARCH_ja.md` を読む。
2. 実装変更前に対象を特定する。
3. デフォルトではdry-runを維持し、実送信には `--execute` を要求する。
4. 変更後にPythonテストとCloudflare Workerテストを実行する。
5. README、docs、サンプルデータ、CIを同時に更新する。

## 禁止事項

- Secret値を出力しない。
- OpenChatの非公式自動投稿・スクレイピングを実装しない。
- LINEの利用規約やMessaging APIガイドラインを回避するコードを書かない。

## 便利コマンド

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
python scripts/line_oa.py openchat-policy
python scripts/line_oa.py bot-info
cd cloudflare-worker && npm test
```
