# AIエージェント完全委任プロンプト集

このドキュメントは、Claude Code / Codex / GitHub Copilot Agentなどに、LINE公式アカウント連携・物件情報自動化の準備作業をできるだけ委任するためのプロンプト集です。

人間がやる必要があるのは、原則として以下だけです。

- LINE公式アカウントの作成
- Messaging APIの有効化
- Channel secret / Channel access tokenの取得
- Cloudflare / Google / GitHubにSecret値を保存
- LINE Developers ConsoleにWebhook URLを登録
- 最終的な実送信判断

AIエージェントには、リポジトリ内の調査、実装、設定ファイル作成、テスト、CI確認、物件データ整形、dry-run、手順書更新を任せます。

---

## 0. 最初にAIエージェントへ渡す共通指示

Claude Code / Codexを起動したら、最初に以下を貼ります。

```text
このリポジトリはLINE公式アカウントのMessaging APIと物件情報自動化のためのプロジェクトです。

まず以下のファイルを読んで、ルールを把握してください。

- README.md
- AGENTS.md
- CODEX.md
- CLAUDE.md
- docs/LINE_API_RESEARCH_ja.md
- docs/SETUP_LINE_ja.md
- docs/PROPERTY_AUTOMATION_ja.md
- docs/architecture.md

重要ルール:
- Secret値を読まない、表示しない、コミットしない。
- .env / .env.* / secrets/** / credentials*.json は読まない。
- LINE個人アカウントの自動操作は実装しない。
- OpenChatの非公式クロールや自動投稿は実装しない。
- 実送信は --execute が明示されたときだけにする。
- 変更後は必ずテストとサンプル物件成果物生成を実行する。
- READMEとdocsも必要に応じて更新する。

まず現在のリポジトリ構成を確認し、初期導入に不足しているファイル、手順、テスト、CI、サンプルデータを洗い出してください。その後、Secret値なしでできる作業をすべて進めてください。
```

---

## 1. 初期導入を全部整えてもらうプロンプト

```text
LINE公式アカウントのMessaging APIを使って、Webhook受信、Google Sheets保存、物件情報CSV/JSONのLINE配信用メッセージ生成、dry-run送信確認までできる初期導入状態にしてください。

やってほしいこと:
1. README.mdを、初めて開いた人がそのまま導入できる内容に更新する。
2. docs/SETUP_LINE_ja.mdに、LINE Official Account Manager、Messaging API、Developers Console、Webhook、Cloudflare、GAS、GitHub Secretsの手順を細かく書く。
3. Secretの実値は書かず、必要なSecret名だけ列挙する。
4. .env.exampleを最新化する。
5. scripts/validate_env.pyで必要な環境変数を検証できるようにする。
6. scripts/property_pipeline.pyでサンプルCSVから以下を生成できるようにする。
   - out/line_messages.txt
   - out/line_flex_messages.json
   - out/properties.normalized.csv
   - out/summary.txt
7. scripts/line_oa.pyでLINE公式アカウントAPIのdry-runと実行を分離する。
8. 実送信は --execute と LINE_DRY_RUN=false が揃ったときだけにする。
9. OpenChatの非公式自動操作は実装しない。代替案をdocsに書く。
10. GitHub Actionsでテストとサンプル成果物生成を行う。
11. 変更後に以下を実行して結果を報告する。

検証コマンド:
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
cd cloudflare-worker && npm test

Secretがないため実行できない箇所は、dry-runまたは手順書更新に切り替えてください。
```

---

## 2. LINE側の設定後にAIエージェントへ渡すプロンプト

人間が以下を完了した後に使います。

- LINE公式アカウント作成
- Messaging API有効化
- Channel secret取得
- Channel access token発行
- Webhook URL登録
- GitHub / Cloudflare / GASにSecret保存

```text
LINE公式アカウント側の初期設定とSecret保存は完了しました。

ただし、Secret値は見ないでください。リポジトリ内のコード、README、docs、CIを確認し、Secret値を出力せずに以下を検証してください。

1. 必要なSecret名がREADMEとdocsにすべて書かれているか。
2. .env.exampleが実運用に必要な項目を網羅しているか。
3. scripts/validate_env.pyで本番に必要な環境変数不足を検出できるか。
4. Cloudflare WorkerのWebhook署名検証がLINE_CHANNEL_SECRETを使う設計になっているか。
5. 空イベントのWebhook検証POSTにも200を返せるか。
6. Google Apps Scriptへ転送する時にFORWARD_SHARED_TOKENを使う設計になっているか。
7. LINE送信CLIはデフォルトdry-runになっているか。
8. 実送信には --execute が必要になっているか。
9. 物件CSVからLINE配信用成果物を生成できるか。
10. テストとCIが通るか。

検証後、問題があれば修正し、READMEとdocsも更新してください。
```

---

## 3. 物件情報の運用開始プロンプト

```text
物件情報配信の運用を開始したいです。

以下を行ってください。

1. data/sample_properties.csvを参考に、投入予定CSVの列名を確認する。
2. 必須列が足りない場合は、どの列が不足しているか分かるようにエラーを改善する。
3. CSV/JSON/JSONLを読み込み、物件情報を正規化する。
4. LINE配信用テキストを生成する。
5. LINE Flex Message JSONを生成する。
6. 正規化CSVを生成する。
7. summary.txtに件数、対象駅、注意点を出す。
8. dry-runで送信payloadを確認する。
9. 実送信はしない。
10. テストを追加・更新する。
11. GitHub Actions artifactに生成物が残るようにする。

実行コマンド例:
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --send --to <dummy_user_or_group_id>

最後に、生成ファイルの場所と確認ポイントを報告してください。
```

---

## 4. 実送信前レビューをさせるプロンプト

```text
LINE公式アカウントで物件情報を実送信する前のレビューをしてください。

絶対に実送信しないでください。

確認してほしいこと:
1. LINE_DRY_RUNがtrueまたは未設定ならdry-runになるか。
2. --executeなしでは送信されないか。
3. 送信対象のuserId/groupId/roomIdをログやdocsに漏らしていないか。
4. Channel access tokenやChannel secretを表示していないか。
5. out/line_messages.txtの文面に誤字や不自然な表現がないか。
6. out/line_flex_messages.jsonがLINE Flex Message形式として破綻していないか。
7. URLが空でないか。
8. 賃料、住所、最寄駅が抜けていないか。
9. 同じ物件が重複していないか。
10. OpenChatへ自動投稿するコードが混入していないか。
11. CIが成功しているか。

問題があれば修正し、問題がなければ「実送信準備OK。ただし送信は人間の最終確認後」と報告してください。
```

---

## 5. 実送信コマンドを作ってもらうプロンプト

このプロンプトは、AIにSecret値を見せず、コマンドだけ作らせる用途です。

```text
物件情報をLINE公式アカウントで実送信するためのコマンドを作ってください。

条件:
- Secret値は表示しない。
- 送信先IDは <userId_or_groupId> のプレースホルダーにする。
- 実送信には LINE_DRY_RUN=false と --execute が必要な形にする。
- 実行前チェックコマンドも一緒に出す。
- OpenChat自動投稿コマンドは出さない。

対象ファイル:
- data/sample_properties.csv

出力してほしいもの:
1. 環境変数検証コマンド
2. テストコマンド
3. 物件成果物生成コマンド
4. dry-runコマンド
5. 実送信コマンド
6. 送信後に確認するログや成果物
```

期待される実送信コマンド例:

```bash
LINE_DRY_RUN=false python scripts/property_pipeline.py --input data/sample_properties.csv --output out --send --to <userId_or_groupId> --execute
```

---

## 6. OpenChat要望が出たときの安全プロンプト

```text
OpenChatに物件情報を流したいという要望があります。

このリポジトリでは、OpenChatの非公式クロール、個人LINEアカウントの自動操作、ブラウザ自動化による投稿は実装しないでください。

代わりに以下を整備してください。
1. out/line_messages.txtに、人間がOpenChatへ手動投稿しやすい文面を生成する。
2. OpenChatへ投稿する前のチェックリストをdocsに書く。
3. 公式アカウントへの誘導文を作る。
4. 通常のLINEグループに公式アカウントBotを招待する代替手順を書く。
5. OpenChat自動投稿コードがないことをテストまたはレビュー観点に入れる。

最後に、なぜOpenChatを直接自動操作しないのかをREADMEに短く説明してください。
```

---

## 7. Cloudflare Worker確認プロンプト

```text
Cloudflare WorkerのLINE Webhook処理を確認・改善してください。

確認項目:
1. POST /line-webhook を受けられるか。
2. x-line-signatureをLINE_CHANNEL_SECRETで検証しているか。
3. 検証失敗時にイベントを処理しないか。
4. LINEのWebhook URL検証用の空イベントPOSTに200を返すか。
5. TARGET_SOURCE_IDSで許可対象を絞れるか。
6. GAS_WEB_APP_URLへ転送できるか。
7. FORWARD_SHARED_TOKENをGAS転送時に付与しているか。
8. エラー時にもSecretをログに出さないか。
9. npm testが通るか。
10. READMEとdocsに設定手順があるか。

変更後は以下を実行してください。
cd cloudflare-worker && npm test
```

---

## 8. GitHub Actions / artifact確認プロンプト

```text
GitHub Actionsを確認・改善してください。

やってほしいこと:
1. push / pull_request / workflow_dispatchで動くvalidate workflowを確認する。
2. Node 20でCloudflare Workerテストを実行する。
3. Python 3.12でcompileallとunittestを実行する。
4. data/sample_properties.csvからout配下に成果物を生成する。
5. out配下をproperty-automation-outputs artifactとしてアップロードする。
6. READMEにActionsとartifactの見方を書く。
7. CIが失敗したらログを読み、修正して再実行する。

変更後にGitHub Actionsの結果を確認し、成功/失敗とrun URLを報告してください。
```

---

## 9. AIエージェントに完了報告させるテンプレート

```text
作業完了報告は以下の形式でお願いします。

- 実施内容:
- 変更ファイル:
- 実行したテスト:
- テスト結果:
- 生成された成果物:
- Secret設定が必要な場所:
- 人間がまだ操作する必要がある項目:
- 実送信前の注意点:
- OpenChatに関する制限:
- 次に見るべきファイル:
```

---

## 10. 人間だけがやる最小作業

AIエージェントに任せても、以下は人間が実施または最終確認してください。

1. LINE公式アカウントの作成
2. Messaging APIの有効化
3. Channel secret / access tokenの取得
4. Cloudflare WorkerのSecret登録
5. Google Apps Scriptのデプロイ許可
6. GitHub Actions Secrets登録
7. Webhook URLの登録と検証
8. 送信先userId/groupIdの確認
9. 実送信前の文面確認
10. 実送信の最終判断
