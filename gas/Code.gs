const SHEET_NAMES = {
  RAW: 'RawMessages',
  DIGESTS: 'Digests',
  ERRORS: 'Errors'
};

const RAW_HEADERS = [
  'received_at',
  'event_timestamp',
  'source_type',
  'source_id',
  'user_id',
  'message_id',
  'message_type',
  'text',
  'raw_json',
  'digest_batch_id'
];

const DIGEST_HEADERS = [
  'digest_id',
  'created_at',
  'period_start',
  'period_end',
  'target_source_ids',
  'message_count',
  'summary',
  'actions_json',
  'notified_to',
  'raw_row_numbers'
];

const ERROR_HEADERS = ['occurred_at', 'scope', 'message', 'detail_json'];

const DEFAULT_SUMMARY_INSTRUCTIONS = `あなたはLINEメッセージの情報整理アシスタントです。
目的は、雑多なLINE会話を読み、あとで行動しやすい形に短く整理することです。

守ること:
- 日本語で出力する。
- メッセージに書かれていない事実を足さない。
- 不明な点は「不明」と書く。
- 個人情報・住所・電話番号・認証情報らしき文字列は必要以上に再掲しない。
- 重要度の高い予定、期限、依頼、決定事項を優先する。
- 雑談は1行程度に圧縮する。

出力形式:
【要約】
- 3〜6項目で全体像

【重要】
- 決定事項、予定、期限、金額、場所など

【TODO】
- 担当者: 内容 / 期限
- 担当者不明: 内容 / 期限不明

【未確認】
- 確認が必要な点

【返信候補】
- 必要なら短い返信文を1〜3個`;

function setupSheets() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  ensureSheet_(spreadsheet, SHEET_NAMES.RAW, RAW_HEADERS);
  ensureSheet_(spreadsheet, SHEET_NAMES.DIGESTS, DIGEST_HEADERS);
  ensureSheet_(spreadsheet, SHEET_NAMES.ERRORS, ERROR_HEADERS);
}

function doPost(e) {
  try {
    assertForwardToken_(e);
    setupSheets();

    const payload = JSON.parse(e.postData.contents || '{}');
    const events = Array.isArray(payload.events) ? payload.events : [];
    const acceptedEvents = events.filter((event) => isTargetSource_(event.source));

    if (acceptedEvents.length > 0) {
      appendRawEvents_(acceptedEvents);
      acceptedEvents.forEach((event) => maybeReplySourceId_(event));
    }

    return jsonOutput_({ ok: true, accepted: acceptedEvents.length, skipped: events.length - acceptedEvents.length });
  } catch (error) {
    logError_('doPost', error, { event: safeEvent_(e) });
    return jsonOutput_({ ok: false, error: String(error) }, 500);
  }
}

function runDigest() {
  const lock = LockService.getScriptLock();
  lock.waitLock(30 * 1000);

  try {
    setupSheets();
    const rawSheet = getSheet_(SHEET_NAMES.RAW);
    const digestSheet = getSheet_(SHEET_NAMES.DIGESTS);
    const rows = readUnsummarizedTextRows_(rawSheet);

    if (rows.length === 0) {
      return { ok: true, message: 'No unsummarized text messages.' };
    }

    const maxInputChars = Number(getOptionalProperty_('MAX_INPUT_CHARS', '12000'));
    const selectedRows = selectRowsWithinLimit_(rows, maxInputChars);
    const digestId = createDigestId_();
    const summary = createSummary_(selectedRows);
    const now = new Date();
    const notifyTo = getRequiredProperty_('NOTIFY_TO_USER_ID');

    const periodStart = new Date(Math.min.apply(null, selectedRows.map((row) => row.eventDate.getTime())));
    const periodEnd = new Date(Math.max.apply(null, selectedRows.map((row) => row.eventDate.getTime())));

    digestSheet.appendRow([
      digestId,
      now,
      periodStart,
      periodEnd,
      getOptionalProperty_('TARGET_SOURCE_IDS', ''),
      selectedRows.length,
      summary,
      JSON.stringify({}),
      notifyTo,
      selectedRows.map((row) => row.rowNumber).join(',')
    ]);

    markRowsSummarized_(rawSheet, selectedRows, digestId);
    pushLineMessage_(notifyTo, formatDigestMessage_(summary, selectedRows, periodStart, periodEnd));

    return { ok: true, digestId, messageCount: selectedRows.length };
  } catch (error) {
    logError_('runDigest', error, {});
    throw error;
  } finally {
    lock.releaseLock();
  }
}

function appendRawEvents_(events) {
  const sheet = getSheet_(SHEET_NAMES.RAW);
  const now = new Date();
  const rows = events.map((event) => {
    const source = event.source || {};
    const message = event.message || {};
    return [
      now,
      event.timestamp ? new Date(event.timestamp) : '',
      source.type || '',
      getSourceId_(source),
      source.userId || '',
      message.id || '',
      message.type || event.type || '',
      message.type === 'text' ? message.text || '' : '',
      JSON.stringify(event),
      ''
    ];
  });

  if (rows.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, RAW_HEADERS.length).setValues(rows);
  }
}

function readUnsummarizedTextRows_(sheet) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return [];

  const values = sheet.getRange(2, 1, lastRow - 1, RAW_HEADERS.length).getValues();
  const digestWindowHours = Number(getOptionalProperty_('DIGEST_WINDOW_HOURS', '24'));
  const cutoff = new Date(Date.now() - digestWindowHours * 60 * 60 * 1000);

  return values
    .map((row, index) => ({ row, rowNumber: index + 2 }))
    .filter(({ row }) => {
      const eventDate = row[1] instanceof Date ? row[1] : row[0];
      const text = String(row[7] || '').trim();
      const digestBatchId = String(row[9] || '').trim();
      return text && !digestBatchId && eventDate instanceof Date && eventDate >= cutoff;
    })
    .map(({ row, rowNumber }) => ({
      rowNumber,
      receivedAt: row[0],
      eventDate: row[1] instanceof Date ? row[1] : row[0],
      sourceType: row[2],
      sourceId: row[3],
      userId: row[4],
      text: row[7]
    }));
}

function selectRowsWithinLimit_(rows, maxChars) {
  const selected = [];
  let total = 0;
  for (const row of rows) {
    const line = formatMessageLine_(row);
    if (selected.length > 0 && total + line.length > maxChars) break;
    selected.push(row);
    total += line.length;
  }
  return selected;
}

function createSummary_(rows) {
  const apiKey = getRequiredProperty_('OPENAI_API_KEY');
  const model = getOptionalProperty_('OPENAI_MODEL', 'gpt-4.1-mini');
  const input = rows.map(formatMessageLine_).join('\n');

  const response = UrlFetchApp.fetch('https://api.openai.com/v1/responses', {
    method: 'post',
    muteHttpExceptions: true,
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${apiKey}` },
    payload: JSON.stringify({
      model,
      instructions: getOptionalProperty_('SUMMARY_INSTRUCTIONS', DEFAULT_SUMMARY_INSTRUCTIONS),
      input: `以下はLINEから取得したメッセージです。時系列に整理して要約してください。\n\n${input}`,
      text: { format: { type: 'text' } },
      max_output_tokens: 1200
    })
  });

  const status = response.getResponseCode();
  const body = response.getContentText();
  if (status < 200 || status >= 300) {
    throw new Error(`OpenAI API error: ${status} ${body}`);
  }

  const json = JSON.parse(body);
  return extractOpenAiOutputText_(json);
}

function extractOpenAiOutputText_(response) {
  const chunks = [];
  const output = Array.isArray(response.output) ? response.output : [];
  output.forEach((item) => {
    const content = Array.isArray(item.content) ? item.content : [];
    content.forEach((part) => {
      if (part.type === 'output_text' && part.text) chunks.push(part.text);
    });
  });
  return chunks.join('\n').trim() || JSON.stringify(response).slice(0, 4000);
}

function markRowsSummarized_(sheet, rows, digestId) {
  rows.forEach((row) => {
    sheet.getRange(row.rowNumber, RAW_HEADERS.indexOf('digest_batch_id') + 1).setValue(digestId);
  });
}

function maybeReplySourceId_(event) {
  const message = event.message || {};
  if (event.type !== 'message' || message.type !== 'text') return;

  const text = String(message.text || '').trim().toLowerCase();
  if (!['id', 'sourceid', '登録', 'とうろく'].includes(text)) return;

  const source = event.source || {};
  const replyText = [
    'LINE Sheet Digest ID確認',
    `sourceType: ${source.type || ''}`,
    `userId: ${source.userId || ''}`,
    `groupId: ${source.groupId || ''}`,
    `roomId: ${source.roomId || ''}`,
    '',
    '通知先にする場合はuserIdをNOTIFY_TO_USER_IDへ、取得対象にする場合はsourceIdをTARGET_SOURCE_IDSへ設定してください。'
  ].join('\n');

  if (event.replyToken) replyLineMessage_(event.replyToken, replyText);
}

function replyLineMessage_(replyToken, text) {
  const token = getRequiredProperty_('LINE_CHANNEL_ACCESS_TOKEN');
  const response = UrlFetchApp.fetch('https://api.line.me/v2/bot/message/reply', {
    method: 'post',
    muteHttpExceptions: true,
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${token}` },
    payload: JSON.stringify({
      replyToken,
      messages: [{ type: 'text', text: truncateLineText_(text) }]
    })
  });
  assertLineResponse_(response, 'replyLineMessage');
}

function pushLineMessage_(to, text) {
  const token = getRequiredProperty_('LINE_CHANNEL_ACCESS_TOKEN');
  const response = UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method: 'post',
    muteHttpExceptions: true,
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${token}` },
    payload: JSON.stringify({
      to,
      messages: [{ type: 'text', text: truncateLineText_(text) }]
    })
  });
  assertLineResponse_(response, 'pushLineMessage');
}

function assertLineResponse_(response, scope) {
  const status = response.getResponseCode();
  if (status < 200 || status >= 300) {
    throw new Error(`${scope} failed: ${status} ${response.getContentText()}`);
  }
}

function formatDigestMessage_(summary, rows, periodStart, periodEnd) {
  const timezone = getOptionalProperty_('TIMEZONE', 'Asia/Tokyo');
  const start = Utilities.formatDate(periodStart, timezone, 'yyyy-MM-dd HH:mm');
  const end = Utilities.formatDate(periodEnd, timezone, 'yyyy-MM-dd HH:mm');
  return [`LINE Digest`, `${start} - ${end}`, `${rows.length}件`, '', summary].join('\n');
}

function formatMessageLine_(row) {
  const timezone = getOptionalProperty_('TIMEZONE', 'Asia/Tokyo');
  const timestamp = Utilities.formatDate(row.eventDate, timezone, 'yyyy-MM-dd HH:mm:ss');
  return `[${timestamp}] source=${row.sourceId} user=${row.userId}: ${row.text}`;
}

function assertForwardToken_(e) {
  const expected = getRequiredProperty_('FORWARD_SHARED_TOKEN');
  const actual = e && e.parameter ? e.parameter.token : '';
  if (!actual || actual !== expected) throw new Error('Invalid forward token');
}

function isTargetSource_(source) {
  const targets = getOptionalProperty_('TARGET_SOURCE_IDS', '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
  if (targets.length === 0) return true;
  const ids = [source && source.userId, source && source.groupId, source && source.roomId].filter(Boolean);
  return ids.some((id) => targets.indexOf(id) >= 0);
}

function getSourceId_(source) {
  if (!source) return '';
  return source.groupId || source.roomId || source.userId || '';
}

function ensureSheet_(spreadsheet, name, headers) {
  let sheet = spreadsheet.getSheetByName(name);
  if (!sheet) sheet = spreadsheet.insertSheet(name);
  const firstRow = sheet.getRange(1, 1, 1, headers.length).getValues()[0];
  const hasHeaders = firstRow.some((value) => String(value || '').trim());
  if (!hasHeaders) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getSheet_(name) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(name);
  if (!sheet) throw new Error(`Sheet not found: ${name}. Run setupSheets first.`);
  return sheet;
}

function getRequiredProperty_(key) {
  const value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) throw new Error(`Missing script property: ${key}`);
  return value;
}

function getOptionalProperty_(key, defaultValue) {
  const value = PropertiesService.getScriptProperties().getProperty(key);
  return value === null || value === undefined || value === '' ? defaultValue : value;
}

function createDigestId_() {
  return `digest_${Utilities.formatDate(new Date(), 'UTC', 'yyyyMMdd_HHmmss')}_${Utilities.getUuid().slice(0, 8)}`;
}

function truncateLineText_(text) {
  const value = String(text || '');
  return value.length > 4900 ? `${value.slice(0, 4900)}\n...` : value;
}

function logError_(scope, error, detail) {
  try {
    setupSheets();
    getSheet_(SHEET_NAMES.ERRORS).appendRow([
      new Date(),
      scope,
      error && error.stack ? error.stack : String(error),
      JSON.stringify(detail || {})
    ]);
  } catch (loggingError) {
    console.error(loggingError);
  }
}

function safeEvent_(e) {
  if (!e) return {};
  return {
    parameter: e.parameter || {},
    postDataLength: e.postData && e.postData.contents ? e.postData.contents.length : 0
  };
}

function jsonOutput_(data, statusCode) {
  const output = ContentService.createTextOutput(JSON.stringify(data));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
