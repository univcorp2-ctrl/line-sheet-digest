# LINE公式アカウント API取得・設定 ブラウザエージェント実行手順

最終更新: 2026-07-17

## 目的

ローカルPCのブラウザエージェント（Playwright / Chrome DevTools MCP / secure-local-ai-agent等）に、LINE公式アカウントのMessaging API有効化、チャネル確認、Cloudflare Workerのテスト・デプロイ、Webhook登録・検証、E2Eテストまでを委任します。

この手順は `univcorp2-ctrl/line-sheet-digest` を対象にします。既存の `gh-automation.univcorp2.workers.dev` はX・SUZURI・GitHub連携等の既存ルートがあるため、上書き・変更しません。LINE用Webhookは、このリポジトリの既存Workerまたは独立Workerを使います。

## 重要な実行境界

`univcorp2-ctrl/secure-local-ai-agent` は、安全設計として資格情報の読取りを実装していません。そのため、最も安全な標準方式は次の役割分担です。

### エージェントが行うこと

- LINE Official Account ManagerとLINE Developersの画面遷移
- Messaging APIの状態確認
- Provider候補、チャネル名、Channel ID、BotベーシックIDの確認
- Secretの表示・発行ボタン直前までの操作
- Cloudflareの対象WorkerとSecret入力画面を開く
- Workerコード確認、テスト、デプロイ
- Webhook URLの登録・検証
- 応答設定の競合確認
- E2Eテストと完了報告

### ユーザーが行うこと

1. LINE Business IDのログイン、パスワード、QRログイン、MFA、本人確認
2. 後から変更できないProviderの最終選択
3. 規約・同意画面で本人操作が必要な場合の同意
4. Channel secretの表示・コピーとCloudflare Secret入力欄への貼付
5. Channel access tokenの発行・コピーとCloudflare Secret入力欄への貼付
6. 既存トークンを無効化する可能性がある再発行の判断
7. 実送信、公開配信、課金変更

資格情報の取扱いを明示的に許可した別のローカルエージェントを使用する場合でも、Secretをログ、スクリーンショット、録画、OCR、GitHub、チャットへ残さない保護が実装・検証されている場合だけ、4と5を自動化します。

## 秘密情報の絶対ルール

次の値を、チャット、GitHub、Issue、Pull Request、Markdown、ログ、スクリーンショット、録画、OCR結果へ残してはいけません。

- Channel secret
- Channel access token
- JWT秘密鍵
- LINEユーザーID、グループID、ルームID
- Cloudflare API Token
- その他の認証情報

Secret画面では以下を守ります。

1. スクリーンショット、画面録画、OCR、監査画面キャプチャを停止する
2. Secret値をコンソール、ターミナル、チャットへ表示しない
3. 可能ならクリップボード履歴を一時停止する
4. ユーザーがLINE画面からコピーし、CloudflareのSecret入力欄または `wrangler secret put` の非表示入力へ直接貼り付ける
5. エージェントはSecret入力後の保存ボタン操作と、Secret名が登録されたことだけを確認する
6. 登録後はクリップボードを無害な文字列で上書きする
7. GitHubコード検索、ローカル検索、ログ検索でSecretが残っていないことを確認する

## 事前確認

エージェントはブラウザを開く前に、次を実行します。

1. 対象リポジトリが `univcorp2-ctrl/line-sheet-digest` であることを確認する
2. `README.md`、`AGENTS.md`、`docs/SETUP_LINE_ja.md`、`docs/AI_AGENT_PROMPTS_ja.md`、本Runbookを読む
3. 現在のWorker名、Webhookパス、デプロイ方法をリポジトリから特定する
4. `gh-automation` Workerを変更対象から除外する
5. LINE用Workerが未確定なら、既存コードとデプロイ設定から候補を示して停止する
6. 操作するLINE Business IDに対象公式アカウントの管理者権限が必要であることを確認する
7. 既存ファイル、既存Worker、既存トークンへ影響する変更を行う前に差分を確認する

## フェーズ1: LINE公式アカウントを開く

1. PC版ブラウザでLINE Official Account Managerを開く
2. ログイン画面で停止する
3. ユーザーがLINE Business IDへのログイン、MFA、本人確認を完了する
4. エージェントがアカウント一覧を確認する
5. 対象が一意なら対象アカウントを開く
6. 複数候補があり判別できない場合、アカウント名とベーシックIDだけを表示して停止する
7. 設定画面へ移動できることを確認する

成功条件:

- 正しいLINE公式アカウントを開いている
- 管理者権限不足の表示がない

## フェーズ2: Messaging APIを有効化する

1. `設定` → `Messaging API` を開く
2. 現在の状態を確認する
   - 利用中: フェーズ3へ進む
   - 未利用: `Messaging APIを利用する` を押す
3. 初回の開発者情報登録画面が出た場合、入力欄まで進みユーザーへ操作を渡す
4. Provider候補を読み取る
5. Providerを自動決定しない
6. 既存Provider名、関連チャネル、重複作成リスクを非秘密情報として示して停止する
7. ユーザーがProviderを選択する
8. 同意画面で本人操作が必要ならユーザーへ渡す
9. 有効化完了を確認する

成功条件:

- Messaging APIが利用中
- 選択したProvider名を記録
- Secret値は未取得・未記録

## フェーズ3: LINE Developersでチャネルを確認する

1. 同じLINE Business IDでLINE Developers Consoleを開く
2. ログイン・MFAが必要なら停止する
3. 選択したProviderを開く
4. 対象公式アカウントと同名のMessaging APIチャネルを開く
5. チャネル種類が `Messaging API` であることを確認する
6. 次の非秘密情報だけを記録する
   - チャネル名
   - Provider名
   - Channel ID
   - BotベーシックID

成功条件:

- 正しいMessaging APIチャネルを開いている
- 別アカウントや別Providerを誤操作していない

## フェーズ4: Channel secretをCloudflareへ登録する

1. LINE Developersの `チャネル基本設定` を開く
2. `Channel secret` の位置を特定する
3. Cloudflare Dashboardで対象のLINE用Workerを開く
4. `Settings` → `Variables and Secrets` を開く
5. `LINE_CHANNEL_SECRET` のSecret入力画面を用意する
6. スクリーンショット、録画、OCRを停止する
7. ユーザーへ操作を渡す
8. ユーザーがChannel secretを表示・コピーし、Cloudflare Secret入力欄へ直接貼り付ける
9. ユーザーが完了を伝えた後、エージェントが保存する
10. Secret一覧に `LINE_CHANNEL_SECRET` という名前だけが表示されることを確認する
11. クリップボードを無害な文字列で上書きする

CLI方式:

```bash
npx wrangler secret put LINE_CHANNEL_SECRET
```

CLI方式でも値の入力だけはユーザーが行い、コマンド引数、シェル履歴、ファイルへ書きません。

成功条件:

- 対象Workerに `LINE_CHANNEL_SECRET` が存在する
- Secret実値をエージェントが読取・記録していない

## フェーズ5: Channel access tokenを発行しCloudflareへ登録する

初回疎通確認では、LINE Developers Consoleの `Messaging API設定` タブから発行できる長期のChannel access tokenを使用できます。本番運用でローテーションを自動化する場合は、別途v2.1、短期、ステートレス方式を設計します。

1. `Messaging API設定` を開く
2. チャネルアクセストークンの状態を確認する
3. 既存稼働が疑われる場合、再発行せず停止する
4. 新規または未使用チャネルの場合、発行ボタン直前まで進む
5. Cloudflareで `LINE_CHANNEL_ACCESS_TOKEN` のSecret入力画面を用意する
6. スクリーンショット、録画、OCRを停止する
7. ユーザーへ操作を渡す
8. ユーザーがトークンを発行・コピーし、Cloudflare Secret入力欄へ直接貼り付ける
9. ユーザーが完了を伝えた後、エージェントが保存する
10. Secret一覧に `LINE_CHANNEL_ACCESS_TOKEN` という名前だけが表示されることを確認する
11. クリップボードを無害な文字列で上書きする

CLI方式:

```bash
npx wrangler secret put LINE_CHANNEL_ACCESS_TOKEN
```

成功条件:

- 対象Workerに `LINE_CHANNEL_ACCESS_TOKEN` が存在する
- 既存の稼働トークンを意図せず無効化していない
- Secret実値をエージェントが読取・記録していない

## フェーズ6: Webhook実装とデプロイを確認する

1. リポジトリからWebhookパスを確定する
2. 次をコードレビューする
   - POSTを受信する
   - `x-line-signature` を検証する
   - JSON解析前の生の本文をHMAC-SHA256検証に使用する
   - 署名不一致時にイベント処理しない
   - `events: []` の検証POSTへHTTP 200を返す
   - Secretをログへ出さない
   - Webhook再送を使う場合は重複処理対策がある
3. テストを実行する

```bash
cd cloudflare-worker
npm test
```

4. テスト成功後、LINE用Workerをデプロイする
5. HTTPSのWebhook URLを確定する

成功条件:

- テスト成功
- HTTPSのWebhook URLが公開
- 検証用POSTへ200を返せる

## フェーズ7: Webhook URLを登録・検証する

1. LINE Developersの `Messaging API設定` を開く
2. Webhook URLを入力する
3. `検証` を押す
4. 成功表示を確認する
5. 失敗した場合、ルート、HTTPステータス、空イベント処理、署名検証、デプロイ先を確認する
6. 成功後、`Webhookの利用` をオンにする
7. `Webhookの再送` は冪等性・重複対策が確認できた場合だけオンにする

成功条件:

- Webhook検証成功
- Webhook利用オン
- 空イベントPOSTへ200応答

## フェーズ8: 応答設定とE2E確認

1. LINE Official Account Managerの `設定` → `応答設定` を開く
2. Webhook Botと応答メッセージ、AIチャットボットが重複返信しないよう設定する
3. テスト用に友だち追加する
4. LINEから `テスト` を送信する
5. WorkerのWebhook受信、署名検証、HTTP 200、返信または転送を確認する
6. `python scripts/line_oa.py bot-info` を実行できる場合は実行する
7. 実送信テストはdry-runを先に行う
8. 公開配信やブロードキャストはユーザーの明示承認なしに実行しない

成功条件:

- Webhook受信成功
- 署名検証成功
- HTTP 200
- 二重返信なし
- Secret漏洩なし
- 想定外の配信なし

## エラー時の確認

### Messaging APIメニューがない

- PC版Web管理画面か
- 対象アカウントの管理者権限があるか
- 別アカウントを開いていないか

### 既存Providerが表示されない

- 操作中のLINE Business IDにProviderのAdmin権限があるか
- 重複Providerを作成せず停止する

### Webhook検証が失敗する

- HTTPS URLか
- Webhookパスが正しいか
- POSTへ200を返すか
- `events: []` を処理できるか
- JSON解析前の本文で署名検証しているか
- 正しいWorkerへデプロイしたか

### 401 Unauthorized

- access tokenの登録先Workerが正しいか
- トークンが無効化・期限切れでないか
- Authorizationが `Bearer <token>` 形式か
- Secret値自体はログへ出さない

### 返信が2回届く

- LINE Official Account Managerの応答メッセージ
- AIチャットボット
- Webhook Bot

の複数機能が同時に返信していないか確認する。

## エージェントへ渡す完全委任プロンプト

```text
あなたは、私が所有・管理するLINE公式アカウントのMessaging API初期設定を行うローカルPCブラウザエージェントです。

対象:
- GitHub: univcorp2-ctrl/line-sheet-digest
- 既存のgh-automation Workerは絶対に上書き・変更しない
- LINE用Webhookは、このリポジトリの既存Workerまたは独立Workerを使う

最初に読むファイル:
- README.md
- AGENTS.md
- docs/SETUP_LINE_ja.md
- docs/AI_AGENT_PROMPTS_ja.md
- docs/LINE_API_BROWSER_AGENT_RUNBOOK_ja.md

ゴール:
1. LINE公式アカウントでMessaging APIを有効化する
2. 正しいProviderとMessaging APIチャネルを確認する
3. CloudflareにLINE_CHANNEL_SECRETの入力画面を用意し、Secret値のコピー・貼付だけ人間へ渡す
4. CloudflareにLINE_CHANNEL_ACCESS_TOKENの入力画面を用意し、トークン発行・コピー・貼付だけ人間へ渡す
5. LINE用Cloudflare Workerをテスト・デプロイする
6. Webhook URLを登録して検証成功させる
7. Webhook利用をオンにする
8. 応答設定の競合を解消する
9. テストメッセージで受信、署名検証、HTTP 200、返信を確認する
10. Secretがログ、GitHub、スクリーンショット、録画、OCR、クリップボード履歴に残っていないことを確認する

必ず停止して人間へ操作を渡す場面:
- LINE Business IDログイン、パスワード、QRログイン、MFA、本人確認
- 後から変更できないProviderの最終選択
- ユーザー本人の規約同意
- Channel secretの表示、コピー、Cloudflareへの貼付
- Channel access tokenの発行、コピー、Cloudflareへの貼付
- 既存稼働トークンを無効化する可能性がある再発行
- 実送信、公開配信、課金変更

Secret取り扱い:
- Secret値を読取・表示・記録しない
- Secret画面ではスクリーンショット、録画、OCRを停止する
- Secret名だけを確認・報告する
- 人間の貼付完了後に保存操作を行う
- 登録後はクリップボードを上書きする

実行順序:
1. リポジトリと既存Worker構成を確認
2. LINE Official Account Managerへ移動
3. 対象公式アカウント確認
4. Messaging APIの状態確認と有効化
5. Provider候補を表示して停止
6. ユーザー選択後、チャネル作成完了を確認
7. LINE Developersで正しいチャネルを確認
8. Channel secretとCloudflare入力画面を並べてユーザーへ渡す
9. 保存後、Secret名だけを確認
10. Channel access tokenとCloudflare入力画面を並べてユーザーへ渡す
11. 保存後、Secret名だけを確認
12. Workerコードの署名検証と空イベント200応答を確認
13. テストを実行
14. Workerをデプロイ
15. Webhook URLを登録・検証
16. Webhook利用をオン
17. 応答設定を確認
18. LINEからテストメッセージを送信してE2E検証
19. Secret漏洩チェック
20. 完了報告

完了報告:
- 対象LINE公式アカウント名:
- Provider名:
- Channel ID:
- BotベーシックID:
- 使用したCloudflare Worker名:
- Webhook URL:
- 登録済みSecret名:
- Webhook検証結果:
- E2Eテスト結果:
- 二重返信チェック:
- Secret漏洩チェック:
- 変更ファイル:
- 実行テスト:
- 未完了項目:

Secretの実値は絶対に報告しないでください。
```

## 公式資料

- [Messaging APIを始めよう](https://developers.line.biz/ja/docs/messaging-api/getting-started/)
- [チャネルアクセストークン](https://developers.line.biz/ja/docs/basics/channel-access-token/)
- [Webhook URLを検証する](https://developers.line.biz/ja/docs/messaging-api/verify-webhook-url/)
- [Webhookの署名を検証する](https://developers.line.biz/ja/docs/messaging-api/verify-webhook-signature/)
- [LINE Official Account Manager: Messaging API](https://www.lycbiz.com/jp/manual/OfficialAccountManager/account-settings_messaging_api/)
- [LINE Official Account Manager: 応答設定](https://www.lycbiz.com/jp/manual/OfficialAccountManager/account-settings_response/)
