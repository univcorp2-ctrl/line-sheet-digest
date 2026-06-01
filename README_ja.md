# LINE Sheet Digest + 物件情報自動化

このリポジトリは、既存の `line-sheet-digest` を拡張し、LINE公式アカウントのWebhook受信・Google Sheets保存・要約通知に加えて、物件情報を自動整形してLINE配信できるようにするためのテンプレートです。

## 主な改善点

1. `scripts/property_pipeline.py` で物件CSV/JSONを正規化し、LINE配信用テキスト、Flex Message JSON、CSVを生成します。
2. `scripts/line_oa.py` でLINE公式アカウントAPIの疎通確認、bot info取得、push/broadcastのdry-run/実行を行えます。
3. `docs/LINE_API_RESEARCH_ja.md` に、LINE公式アカウントAPIの初期設定、OpenChatの制限、Claude Code / Codexから安全に自動化する設計を整理しました。
4. `CLAUDE.md` / `AGENTS.md` / `CODEX.md` に、AIコーディングエージェント用の作業ルールを用意しました。
5. GitHub Actionsでテストとサンプル成果物生成を実行し、`property-automation-outputs` artifactとして保存します。

## 最短コマンド

```bash
python scripts/validate_env.py --mode local
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
python scripts/line_oa.py bot-info
```

実送信するには、`.env.example` のSecretを設定した上で `--execute` を明示してください。

## 重要な制限

- LINE公式アカウント / Messaging APIで取得・送信できるのは、Botに届くWebhookイベントや、友だち・グループ・複数人トークなど公式に許可された範囲です。
- LINEオープンチャットを非公式にクロールしたり、一般ユーザーアカウントを自動操作して投稿する設計は採用しません。
- OpenChatは公式のサーバーサイドMessaging API連携先ではなく、必要な場合は手動投稿、公式アカウントへの誘導、または公開された正規APIが提供される範囲に限定します。

## 次に見るファイル

- 初期設定: `docs/SETUP_LINE_ja.md`
- 調査結果: `docs/LINE_API_RESEARCH_ja.md`
- 画像ガイド: `docs/VISUAL_SETUP_GUIDE_ja.md`
- 物件自動化: `docs/PROPERTY_AUTOMATION_ja.md`
- AIエージェント運用: `docs/AGENT_GUIDE_ja.md`
