# LINE初期設定ガイド

## 1. LINE公式アカウントを作る

1. LINE Business IDでログインする。
2. LINE Official Account Managerで公式アカウントを作成する。
3. アカウント名、業種、所在地などを入力する。
4. 作成後、管理画面で対象アカウントを開く。

## 2. Messaging APIを有効化する

1. LINE Official Account Managerで対象アカウントを開く。
2. `設定` → `Messaging API` を開く。
3. `Messaging APIを利用する` を選ぶ。
4. プロバイダーを選択または作成する。
5. プロバイダーは後から変更できないため、会社/プロジェクト単位で慎重に選ぶ。
6. 有効化後、LINE Developers ConsoleにMessaging APIチャネルが作成される。

## 3. Channel Secret / Access Tokenを取得する

1. LINE Developers Consoleを開く。
2. プロバイダーを選択する。
3. 作成されたMessaging APIチャネルを開く。
4. `チャネル基本設定` で `Channel secret` をコピーする。
5. `Messaging API設定` で `Channel access token` を発行してコピーする。
6. コピーした値はSecret ManagerかGitHub Actions Secretsに保存する。

## 4. Webhook URLを設定する

Cloudflare Workerを使う場合のURL例:

```text
https://<worker-name>.<account>.workers.dev/line-webhook
```

LINE Developers Consoleの `Messaging API設定` でWebhook URLを登録し、`検証` を押す。空イベントPOSTにも200を返す必要がある。

## 5. 応答設定

LINE Official Account Manager側で、用途に応じて以下を確認する。

- Webhook: 有効
- 自動応答メッセージ: Bot側で返信するなら無効推奨
- あいさつメッセージ: 必要に応じて設定
- グループ/複数人トーク参加: グループで使う場合のみ有効

## 6. リポジトリ側Secret

GitHub ActionsやCloudflare/GASに以下を登録する。

```text
LINE_CHANNEL_ACCESS_TOKEN
LINE_CHANNEL_SECRET
LINE_DEFAULT_TO
GAS_WEB_APP_URL
FORWARD_SHARED_TOKEN
TARGET_SOURCE_IDS
OPENAI_API_KEY
```

## 7. ローカル確認

```bash
python scripts/validate_env.py --mode local
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
python scripts/line_oa.py bot-info
```

## 8. 実送信

実送信は必ず内容を確認してから行う。

```bash
LINE_DRY_RUN=false python scripts/line_oa.py --execute push-text --to <userId_or_groupId> --text "テスト送信"
LINE_DRY_RUN=false python scripts/property_pipeline.py --input data/sample_properties.csv --output out --send --to <userId_or_groupId> --execute
```

## 9. OpenChatの扱い

OpenChatは本リポジトリで自動投稿・自動収集しない。物件情報をOpenChatへ流したい場合は、生成された `out/line_messages.txt` を人間が確認して手動投稿するか、参加者を公式アカウントへ誘導する。
