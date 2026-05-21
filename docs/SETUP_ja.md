# セットアップ手順

## 1. LINE Developers

1. LINE Developers ConsoleでProviderを作成します。
2. Messaging APIチャネルを作成します。
3. `Channel secret` を控えます。
4. 長期の `Channel access token` を発行します。
5. Webhook利用を有効化します。
6. 応答メッセージの自動応答は必要に応じてOFFにします。
7. グループで使う場合は、Botのグループ参加を許可します。

## 2. Google Spreadsheet / Apps Script

1. 新しいGoogle Spreadsheetを作成します。
2. `拡張機能 > Apps Script` を開きます。
3. `gas/Code.gs` の内容を貼り付けます。
4. `gas/appsscript.json` の内容をマニフェストに反映します。
5. Apps Scriptの「プロジェクトの設定」からスクリプトプロパティを設定します。

必須プロパティ:

```text
FORWARD_SHARED_TOKEN=ランダムな長い文字列
LINE_CHANNEL_ACCESS_TOKEN=LINEチャネルアクセストークン
OPENAI_API_KEY=OpenAI APIキー
NOTIFY_TO_USER_ID=最初は空でも可。あとでidコマンドで取得
```

任意プロパティ:

```text
OPENAI_MODEL=gpt-4.1-mini
TARGET_SOURCE_IDS=対象sourceIdをカンマ区切り
DIGEST_WINDOW_HOURS=24
MAX_INPUT_CHARS=12000
TIMEZONE=Asia/Tokyo
```

6. Apps Scriptエディタ上で `setupSheets` を実行し、シートを初期化します。
7. `デプロイ > 新しいデプロイ > ウェブアプリ` を選びます。
8. 実行ユーザーは自分、アクセスはCloudflare Workerから呼べる設定にします。
9. Web App URLを控えます。

## 3. Cloudflare Worker

```bash
cd cloudflare-worker
cp wrangler.toml.example wrangler.toml
npm test
```

Cloudflareにログイン後、secretsを設定します。

```bash
npx wrangler secret put LINE_CHANNEL_SECRET
npx wrangler secret put GAS_WEB_APP_URL
npx wrangler secret put FORWARD_SHARED_TOKEN
npx wrangler secret put TARGET_SOURCE_IDS
```

`TARGET_SOURCE_IDS` が未確定の場合は空で開始できます。

デプロイ:

```bash
npx wrangler deploy
```

発行されたWorker URLの `/line-webhook` をLINE DevelopersのWebhook URLへ設定します。

例:

```text
https://line-sheet-digest-webhook.example.workers.dev/line-webhook
```

## 4. 自分のuserId / groupId / roomId確認

1. LINEでBotを友だち追加します。
2. Botに `id` と送ります。
3. Botから `userId` が返信されます。
4. その `userId` をApps Scriptの `NOTIFY_TO_USER_ID` に設定します。
5. グループで使う場合はBotをグループへ招待し、グループ内で `id` と送ります。
6. 返信された `groupId` を `TARGET_SOURCE_IDS` に設定します。
7. Cloudflare Worker側の `TARGET_SOURCE_IDS` も同じ値へ更新します。

## 5. 定期実行トリガー

Apps Scriptで以下を設定します。

- 実行関数: `runDigest`
- イベントのソース: 時間主導型
- 間隔: 1時間ごと、6時間ごと、毎日など

## 6. 動作確認

1. 対象トーク/グループでメッセージを送る
2. Spreadsheetの `RawMessages` に行が増えることを確認
3. Apps Scriptで `runDigest` を手動実行
4. `Digests` に要約が追加されることを確認
5. 自分のLINEに要約通知が届くことを確認

## 7. よくある詰まりどころ

### LINE側Webhook検証が失敗する

- Worker URL末尾が `/line-webhook` になっているか確認
- `LINE_CHANNEL_SECRET` が正しいか確認
- Workerのログで `invalid signature` が出ていないか確認

### GASに記録されない

- `GAS_WEB_APP_URL` が最新デプロイURLか確認
- `FORWARD_SHARED_TOKEN` がWorker/GASで一致しているか確認
- GAS側Webアプリのアクセス権限を確認

### 自分に通知されない

- `NOTIFY_TO_USER_ID` がuserIdか確認
- `LINE_CHANNEL_ACCESS_TOKEN` が有効か確認
- Botをブロックしていないか確認

### 要約されない

- `OPENAI_API_KEY` が正しいか確認
- `RawMessages` に未要約のテキスト行があるか確認
- Apps Scriptの実行ログでOpenAIエラーを確認
