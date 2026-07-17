# LINE公式アカウント API取得・設定 ブラウザエージェント実行手順

最終更新: 2026-07-17

## 目的

ローカルPCのブラウザエージェント（Playwright / Chrome DevTools MCP / secure-local-ai-agent等）に、LINE公式アカウントのMessaging API有効化、Channel secretとChannel access tokenの取得、Cloudflare Secretsへの登録、Webhook URLの登録・検証までを可能な限り委任します。

この手順は `univcorp2-ctrl/line-sheet-digest` を対象にします。既存の `gh-automation.univcorp2.workers.dev` はX・SUZURI・GitHub連携等の既存ルートがあるため、上書きしません。LINE用Workerは、このリポジトリの既存構成または独立Workerとして扱います。

## 人間が必ず操作・判断する箇所

ブラウザエージェントは、以下の場面だけ停止してユーザーに画面操作を求めます。

1. LINE Business IDへのログイン、パスワード入力、QRログイン、MFA、本人確認
2. プロバイダーの最終選択
   - プロバイダーは後から変更できないため、既存プロバイダーの候補一覧を表示して停止する
   - 既存の会社・サービス用プロバイダーがある場合は、重複作成しない
3. 規約・同意画面で、ユーザー本人の同意が必要と明示される場合
4. 実送信、公開配信、課金プラン変更

上記以外は、非破壊的な範囲でエージェントが続行します。

## 秘密情報の絶対ルール

次の値を、チャット、GitHub、Issue、Pull Request、Markdown、ログ、スクリーンショット、録画、OCR結果へ残してはいけません。

- Channel secret
- Channel access token
- JWT秘密鍵
- LINEユーザーID、グループID、ルームID
- Cloudflare API Token
- その他の認証情報

秘密情報を取得する画面では、以下を守ります。

1. スクリーンショット・動画記録を停止する
2. 値をコンソールへ表示しない
3. クリップボード履歴を無効化できる場合は無効化する
4. 値はCloudflare Secretsの入力欄または `wrangler secret put` の非表示入力へ直接渡す
5. 登録後、クリップボードを無害な文字列で上書きする
6. GitHubコード検索、ローカル検索、ログ検索で値が残っていないことを確認する

## 事前確認

エージェントは、ブラウザを開く前に次を確認します。

1. 対象リポジトリが `univcorp2-ctrl/line-sheet-digest` である
2. `README.md`、`AGENTS.md`、`docs/SETUP_LINE_ja.md`、`docs/AI_AGENT_PROMPTS_ja.md` を読む
3. 現在のWorker名、Webhookパス、デプロイ方法をリポジトリから特定する
4. `gh-automation` Workerを変更対象から除外する
5. LINE Official Account Managerの対象アカウント名が不明な場合、アカウント一覧を表示して停止する
6. 操作するLINE Business IDに対象公式アカウントの管理者権限があることを確認する
7. Secret値を保存するCloudflare Workerを特定する
8. 既存ファイル・既存設定をバックアップまたは差分確認する

## 実行フェーズ1: LINE公式アカウントを開く

1. PC版ブラウザでLINE Official Account Managerを開く
2. ログイン画面で停止する
3. ユーザーがLINE Business IDへのログイン、MFA、本人確認を完了する
4. エージェントはアカウント一覧を読み取る
5. 対象アカウントを選択する
6. 対象が複数あり判別できない場合は、アカウント名とベーシックIDだけを表示して停止する
7. 管理画面トップが開いたことを確認する

成功条件:

- 対象のLINE公式アカウント名が確認できる
- エージェントが設定画面へ移動できる
- 管理者権限不足の表示がない

## 実行フェーズ2: Messaging APIを有効化する

1. 右上または左メニューの `設定` を開く
2. `Messaging API` を開く
3. 現在の状態を確認する
   - すでに利用中: フェーズ3へ進む
   - 未利用: `Messaging APIを利用する` を押す
4. 初回の開発者情報登録画面が表示された場合、名前・メールアドレスの入力欄まで進む
   - ユーザー本人の登録情報が必要な場合は停止する
5. プロバイダー選択画面で候補を読み取る
6. プロバイダーを自動決定しない
7. 既存プロバイダー名、関連する既存チャネル、選択理由を非秘密情報としてユーザーへ示し、最終選択で停止する
8. ユーザーが選択したプロバイダーを指定する
9. 規約・注意事項を開き、同意が必要な場合はユーザーに操作を渡す
10. 確認画面で `OK` を押し、Messaging API有効化の完了を確認する

成功条件:

- LINE Official Account ManagerでMessaging APIが利用中になっている
- 選択したプロバイダー名を記録できる
- Secret値は記録されていない

## 実行フェーズ3: LINE Developersでチャネルを確認する

1. LINE Official Account Managerと同じLINE Business IDでLINE Developers Consoleを開く
2. ログイン・MFAが必要なら停止する
3. フェーズ2で選択したプロバイダーを開く
4. 対象LINE公式アカウントと同名のMessaging APIチャネルを開く
5. チャネル種類が `Messaging API` であることを確認する
6. 次の非秘密情報だけを作業記録へ残す
   - チャネル名
   - Provider名
   - Channel ID
   - BotのベーシックID
7. Channel secretやaccess tokenは作業記録へ残さない

成功条件:

- 正しいMessaging APIチャネルを開いている
- 別アカウント・別プロバイダーを誤操作していない

## 実行フェーズ4: Channel secretをCloudflareへ直接登録する

1. `チャネル基本設定` を開く
2. `Channel secret` の場所を特定する
3. スクリーンショット、画面録画、OCRログを停止する
4. Secretを表示またはコピーする
5. 別タブでCloudflare Dashboardを開く
6. 対象のLINE用Workerを開く
7. `Settings` → `Variables and Secrets` を開く
8. `LINE_CHANNEL_SECRET` をSecretとして新規登録または更新する
9. 値を直接貼り付けて保存する
10. 保存後、Secret一覧に名前だけが表示され、値が再表示されないことを確認する
11. クリップボードを `CLEARED` 等で上書きする
12. ブラウザ履歴、フォーム履歴、ログに値が残っていないことを確認する

CLI方式を使う場合:

```bash
npx wrangler secret put LINE_CHANNEL_SECRET
```

値はプロンプトへ直接入力し、コマンド引数、シェル履歴、環境変数、ファイルへ書きません。

成功条件:

- Cloudflareの対象Workerに `LINE_CHANNEL_SECRET` という名前のSecretが存在する
- Secretの実値がGitHub、ログ、スクリーンショットに存在しない

## 実行フェーズ5: Channel access tokenを発行しCloudflareへ登録する

初回の疎通確認では、LINE Developers Consoleの `Messaging API設定` タブから発行できる長期のChannel access tokenを使用できます。本番運用でローテーションを自動化する場合は、別途v2.1または短期・ステートレス方式を設計します。

1. `Messaging API設定` を開く
2. `チャネルアクセストークン` のセクションへ移動する
3. 既存トークンの状態を確認する
4. 新規発行または再発行が必要かを判断する
   - 再発行すると既存トークンへ影響するため、既存運用が疑われる場合は停止する
5. 新規チャネルまたは未使用チャネルの場合、長期トークンを発行する
6. スクリーンショット、画面録画、OCRログを停止する
7. トークンをコピーする
8. Cloudflare Dashboardの対象LINE用Workerへ移動する
9. `LINE_CHANNEL_ACCESS_TOKEN` をSecretとして登録する
10. 値を保存する
11. クリップボードを無害な文字列で上書きする
12. トークンをログ、チャット、GitHubへ出力していないことを確認する

CLI方式を使う場合:

```bash
npx wrangler secret put LINE_CHANNEL_ACCESS_TOKEN
```

成功条件:

- Cloudflareの対象Workerに `LINE_CHANNEL_ACCESS_TOKEN` が存在する
- 既存の稼働トークンを意図せず無効化していない
- Secret値がどこにも平文保存されていない

## 実行フェーズ6: Webhook実装とデプロイを確認する

1. リポジトリ内でWebhookパスを確認する
2. 想定パスが `/line-webhook` か、現在の実装値かをコードから確定する
3. 次をコードレビューする
   - POSTリクエストを受信する
   - `x-line-signature` を検証する
   - JSON解析前の生の本文をHMAC-SHA256検証に使う
   - 署名不一致時にイベントを処理しない
   - `events: []` の検証POSTへHTTP 200を返す
   - Secretをログへ出さない
   - 重複Webhookへ備えてイベントIDによる冪等性を検討する
4. テストを実行する

```bash
cd cloudflare-worker
npm test
```

5. Workerをデプロイする
6. デプロイURLとWebhookパスを結合する
7. Webhook URLを非秘密情報として記録する

成功条件:

- テストが成功する
- HTTPSのWebhook URLが公開される
- 検証用POSTへHTTP 200を返せる

## 実行フェーズ7: LINE DevelopersへWebhook URLを登録する

1. LINE Developers Consoleの対象Messaging APIチャネルを開く
2. `Messaging API設定` を開く
3. `Webhook URL` に、フェーズ6で確定したHTTPS URLを入力する
4. `検証` を押す
5. 成功表示を確認する
6. 失敗した場合は、WorkerログのHTTPステータス、ルート、署名検証、空イベント処理を確認する
7. 検証成功後、`Webhookの利用` をオンにする
8. `Webhookの再送` は重複処理対策ができている場合だけオンにする
9. 画面上のURLと実際のデプロイURLが一致することを再確認する

成功条件:

- Webhook URL検証が成功する
- Webhookの利用がオンである
- 空イベントPOSTに200を返している

## 実行フェーズ8: LINE Official Account Managerの応答設定

1. LINE Official Account Managerへ戻る
2. `設定` → `応答設定` を開く
3. Bot側で自動返信する場合、応答メッセージによる二重返信が起きない設定にする
4. あいさつメッセージは要件に応じて維持する
5. AIチャットボット等の別自動応答が有効な場合、重複返信の有無をテストする
6. 設定変更前後を、Secretを含まない範囲で記録する

成功条件:

- 1回のユーザーメッセージに対して意図した返信だけが返る
- 公式アカウント側の応答機能とWebhook Botが競合しない

## 実行フェーズ9: 疎通確認

1. LINE Developers ConsoleのQRコードからテスト用に友だち追加する
2. `テスト` と送信する
3. WorkerがWebhookを受信したことを確認する
4. 署名検証成功を確認する
5. 返信または転送処理が設計どおり動作することを確認する
6. `python scripts/line_oa.py bot-info` を実行できる場合は実行する
7. 実送信が必要なテストは、dry-runを先に行う
8. 実送信はユーザーが明示した場合だけ行う

成功条件:

- Webhook受信成功
- HTTP 200
- 署名検証成功
- Secret漏洩なし
- 二重返信なし
- 想定外のブロードキャストなし

## エラー時の対応

### Messaging APIメニューがない

- PC版Web管理画面を使用しているか確認
- 対象アカウントの管理者権限を確認
- 別アカウントを開いていないか確認

### 既存プロバイダーが表示されない

- 操作中のLINE Business IDに、そのプロバイダーのAdmin権限があるか確認
- 重複プロバイダーを作成せず停止する

### Webhook検証が失敗する

- HTTPS URLか確認
- パスの末尾、ルート名を確認
- POSTへ200を返すか確認
- `events: []` を正常処理できるか確認
- JSON解析前の本文を署名検証しているか確認
- Cloudflareデプロイ先が正しいか確認

### 401 Unauthorized

- access tokenの登録先Workerが正しいか確認
- トークンが無効化・期限切れでないか確認
- Authorizationヘッダーが `Bearer <token>` 形式か確認
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
3. Channel secretを取得し、値を表示・記録せずCloudflare Secret `LINE_CHANNEL_SECRET` へ直接保存する
4. Channel access tokenを発行し、値を表示・記録せずCloudflare Secret `LINE_CHANNEL_ACCESS_TOKEN` へ直接保存する
5. LINE用Cloudflare Workerをテスト・デプロイする
6. Webhook URLをLINE Developersへ登録し、検証成功させる
7. Webhookの利用をオンにする
8. 応答設定の競合を解消する
9. テストメッセージで受信、署名検証、HTTP 200、返信を確認する
10. Secretがログ、GitHub、スクリーンショット、録画、クリップボード履歴に残っていないことを確認する

停止して人間へ操作を渡すのは次の場合だけ:
- LINE Business IDログイン、パスワード、QRログイン、MFA、本人確認
- 後から変更できないProviderの最終選択
- ユーザー本人による規約同意が必要な画面
- 既存稼働トークンを無効化する可能性がある再発行
- 実送信、公開配信、課金変更

Secret取り扱い:
- Secret値をチャット、ログ、端末出力、Markdown、GitHub、Issue、PRへ書かない
- Secret表示中はスクリーンショット・録画・OCRを停止する
- Cloudflare Secretsまたは `wrangler secret put` の非表示入力へ直接渡す
- 登録後はクリップボードを上書きする
- Secret名だけを完了報告する

実行順序:
1. リポジトリと既存Worker構成を確認
2. LINE Official Account Managerへ移動
3. 対象公式アカウント確認
4. Messaging APIの状態確認と有効化
5. Provider候補を表示して停止
6. ユーザー選択後、チャネル作成完了を確認
7. LINE Developersで正しいチャネルを確認
8. Channel secretをCloudflareへ直接登録
9. Channel access tokenをCloudflareへ直接登録
10. Workerコードの署名検証と空イベント200応答を確認
11. テストを実行
12. Workerをデプロイ
13. Webhook URLを登録して検証
14. Webhook利用をオン
15. 応答設定を確認
16. LINEからテストメッセージを送信してE2E検証
17. Secret漏洩チェック
18. 完了報告

完了報告は次の形式にする:
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
