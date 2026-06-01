# 画像付きセットアップガイド

以下のSVGは、LINE公式アカウント、Messaging API、Cloudflare Worker、Google Sheets、物件情報パイプライン、Claude Code / Codexの関係をまとめた図解です。

![LINE setup guide](./images/line-setup-guide.svg)

## 読み方

左上から順番に進めます。

1. LINE Official Account Managerで公式アカウントを作成する。
2. Messaging APIを有効化する。
3. LINE Developers ConsoleでChannel secret / access token / Webhook URLを設定する。
4. Cloudflare WorkerでWebhook署名を検証する。
5. Google Apps Script / Sheetsへ転送する。
6. 物件CSV/JSONを `scripts/property_pipeline.py` で整形する。
7. Claude Code / Codexは `CLAUDE.md` / `AGENTS.md` / `CODEX.md` を読んで、dry-run中心で改修する。
