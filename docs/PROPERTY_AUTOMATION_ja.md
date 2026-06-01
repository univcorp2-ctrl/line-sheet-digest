# 物件情報自動化ガイド

## 入力フォーマット

CSV/JSON/JSONLを受け付けます。必須項目は以下です。

- `title` または `物件名`
- `rent` または `賃料`
- `station` または `最寄駅`
- `address` または `住所`
- `url` または `URL`

任意項目:

- `layout` / `間取り`
- `area` / `面積`
- `description` / `説明`

## 生成コマンド

```bash
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --format all
```

生成物:

- `out/line_messages.txt`: 人間が確認してそのまま送れるテキスト
- `out/line_flex_messages.json`: LINE Flex Message用JSON
- `out/properties.normalized.csv`: 正規化済みCSV
- `out/summary.txt`: 件数・駅一覧・確認事項

## LINEへ送信

dry-run:

```bash
python scripts/property_pipeline.py --input data/sample_properties.csv --output out --send --to <userId_or_groupId>
```

実送信:

```bash
LINE_DRY_RUN=false python scripts/property_pipeline.py --input data/sample_properties.csv --output out --send --to <userId_or_groupId> --execute
```

## GitHub Actions

`validate` workflowは、テスト後にサンプル物件データから成果物を作り、`property-automation-outputs` artifactとして保存します。

## 運用フロー

1. 物件情報をCSV/JSONで準備する。
2. pipelineをdry-runで実行する。
3. `out/line_messages.txt` と `out/line_flex_messages.json` を確認する。
4. URL、賃料、掲載可否、誤字、重複を確認する。
5. 必要ならLINEへ実送信する。
6. 送信後は使用メッセージ数とレスポンスを確認する。
