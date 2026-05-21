# Google Sheets スキーマ

## RawMessages

Webhookから受け取ったイベントのうち、処理対象になったものを保存します。

| 列 | 内容 |
|---|---|
| received_at | GASが受信した日時 |
| event_timestamp | LINEイベントのtimestamp |
| source_type | user / group / room |
| source_id | userId / groupId / roomId |
| user_id | 発言者のuserId |
| message_id | LINE messageId |
| message_type | text / image / sticker など |
| text | テキスト本文。非テキストは空 |
| raw_json | イベント全体のJSON |
| digest_batch_id | 要約済みならdigest_id |

## Digests

`runDigest` によって作成された要約を保存します。

| 列 | 内容 |
|---|---|
| digest_id | 一意な要約ID |
| created_at | 要約作成日時 |
| period_start | 対象メッセージ最古日時 |
| period_end | 対象メッセージ最新日時 |
| target_source_ids | 対象sourceId |
| message_count | 要約対象メッセージ数 |
| summary | 要約本文 |
| actions_json | 今後の拡張用。TODO抽出など |
| notified_to | 通知先LINE userId |
| raw_row_numbers | 対象RawMessages行番号 |

## Errors

例外や外部APIエラーを保存します。

| 列 | 内容 |
|---|---|
| occurred_at | 発生日時 |
| scope | doPost / runDigest / pushLineMessage など |
| message | エラーメッセージ |
| detail_json | 詳細JSON |
