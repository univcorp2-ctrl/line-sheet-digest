# LINE公式アカウントAPI / OpenChat / 初期設定 調査メモ

調査日: 2026-06-01

## 結論

1. LINE公式アカウントで自動化する中心は **Messaging API**。BotサーバーはHTTPS JSONのWebhookを受け、必要に応じてreply/push/broadcastなどで返信・配信する。
2. 2024-09-04以降、Messaging APIチャネルはLINE Developers Consoleから直接作成できず、LINE Official Account Managerで公式アカウントを作り、Messaging APIを有効化して作成する。
3. WebhookはLINE Developers ConsoleでチャネルごとにWebhook URLを設定し、疎通検証を行う。検証時はイベントが空のPOSTにもHTTP 200を返す必要がある。
4. 受信Webhookは `x-line-signature` を検証してから処理する。
5. LINE公式アカウントはグループトーク・複数人トークに招待できるが、OpenChatを通常のMessaging API Botの対象として自由に投稿・履歴取得する設計にはしない。

## 初期設定で必要なもの

- LINE Business ID
- LINE公式アカウント
- Messaging APIチャネル
- Channel secret
- Channel access token
- Webhook URL
- Webhook利用: ON
- グループ利用が必要なら、Messaging API設定の「グループ・複数人トークへの参加を許可」をON
- 本リポジトリのSecrets
  - `LINE_CHANNEL_ACCESS_TOKEN`
  - `LINE_CHANNEL_SECRET`
  - `LINE_DEFAULT_TO`
  - `GAS_WEB_APP_URL`
  - `FORWARD_SHARED_TOKEN`
  - `TARGET_SOURCE_IDS`
  - `OPENAI_API_KEY`

## 公式ドキュメント参照

- Messaging API概要: https://developers.line.biz/ja/docs/messaging-api/overview/
- Messaging APIを始めよう: https://developers.line.biz/ja/docs/messaging-api/getting-started/
- Webhook受信: https://developers.line.biz/ja/docs/messaging-api/receiving-messages/
- Webhook URL検証: https://developers.line.biz/ja/docs/messaging-api/verify-webhook-url/
- Messaging APIリファレンス: https://developers.line.biz/ja/reference/messaging-api/
- グループ/複数人トーク: https://developers.line.biz/en/docs/messaging-api/group-chats/
- チャネルアクセストークン: https://developers.line.biz/ja/docs/basics/channel-access-token/
- LINE Official Account ManagerのMessaging API設定: https://www.lycbiz.com/jp/manual/OfficialAccountManager/account-settings_messaging_api/

## OpenChatについて

OpenChatは「LINE公式アカウントのBotを招待してWebhookを受ける通常のグループ」と同じ前提で扱わない。公開されているiOS SDKにはOpenChat作成UIに関するクラスがあるが、本リポジトリはサーバーサイドでOpenChatへ自動投稿・履歴収集する機能を提供しない。

推奨代替:

- 公式アカウントの1:1チャットで物件情報を配信する
- 通常のLINEグループに公式アカウントBotを招待する
- OpenChatには人間が確認して投稿する
- OpenChat参加者を公式アカウントへ誘導し、許諾された範囲で配信する

## Claude Code / Codexにやらせる範囲

できる:

- 物件CSV/JSONの整形
- LINE Flex Message JSON生成
- Webhookハンドラー改修
- dry-runでLINE送信payload確認
- テスト/CI/README更新
- GitHub Actions artifact生成

やらせない:

- Secretの読み取りや表示
- LINE個人アカウントの自動ログイン
- OpenChatの非公式スクレイピング
- 規約回避やレート制限回避
