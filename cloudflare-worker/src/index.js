export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/healthz') {
      return json({ ok: true, service: 'line-sheet-digest-webhook' });
    }

    if (url.pathname !== '/line-webhook') {
      return json({ ok: false, error: 'not_found' }, 404);
    }

    if (request.method !== 'POST') {
      return json({ ok: false, error: 'method_not_allowed' }, 405);
    }

    const body = await request.text();
    const signature = request.headers.get('x-line-signature') || '';

    const isValid = await verifyLineSignature(body, env.LINE_CHANNEL_SECRET, signature);
    if (!isValid) {
      return json({ ok: false, error: 'invalid_line_signature' }, 401);
    }

    let payload;
    try {
      payload = JSON.parse(body);
    } catch (error) {
      return json({ ok: false, error: 'invalid_json', detail: String(error) }, 400);
    }

    const events = Array.isArray(payload.events) ? payload.events : [];
    const filteredEvents = events.filter((event) => isTargetSource(event.source, env.TARGET_SOURCE_IDS));

    if (filteredEvents.length === 0) {
      return json({ ok: true, accepted: 0, skipped: events.length });
    }

    const gasUrl = new URL(requiredEnv(env, 'GAS_WEB_APP_URL'));
    gasUrl.searchParams.set('token', requiredEnv(env, 'FORWARD_SHARED_TOKEN'));

    const forwardedPayload = {
      ...payload,
      events: filteredEvents,
      forwarded_by: 'cloudflare-worker',
      forwarded_at: new Date().toISOString()
    };

    const response = await fetch(gasUrl.toString(), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(forwardedPayload)
    });

    const responseText = await response.text();
    if (!response.ok) {
      return json({
        ok: false,
        error: 'gas_forward_failed',
        gas_status: response.status,
        gas_body: responseText.slice(0, 1000)
      }, 502);
    }

    return json({
      ok: true,
      accepted: filteredEvents.length,
      skipped: events.length - filteredEvents.length,
      gas: safeJson(responseText)
    });
  }
};

export async function verifyLineSignature(body, channelSecret, xLineSignature) {
  if (!body || !channelSecret || !xLineSignature) return false;

  const encoder = new TextEncoder();
  const key = await globalThis.crypto.subtle.importKey(
    'raw',
    encoder.encode(channelSecret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const signature = await globalThis.crypto.subtle.sign('HMAC', key, encoder.encode(body));
  const expected = base64Encode(new Uint8Array(signature));

  return timingSafeEqual(expected, xLineSignature);
}

export function collectSourceIds(source = {}) {
  return [source.userId, source.groupId, source.roomId].filter(Boolean);
}

export function isTargetSource(source = {}, targetSourceIds = '') {
  const targets = String(targetSourceIds || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);

  if (targets.length === 0) return true;

  const targetSet = new Set(targets);
  return collectSourceIds(source).some((id) => targetSet.has(id));
}

export function timingSafeEqual(a, b) {
  const left = String(a || '');
  const right = String(b || '');
  if (left.length !== right.length) return false;

  let diff = 0;
  for (let i = 0; i < left.length; i += 1) {
    diff |= left.charCodeAt(i) ^ right.charCodeAt(i);
  }
  return diff === 0;
}

function base64Encode(bytes) {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

function requiredEnv(env, key) {
  const value = env[key];
  if (!value) throw new Error(`Missing environment variable: ${key}`);
  return value;
}

function safeJson(text) {
  try {
    return JSON.parse(text);
  } catch (_error) {
    return text.slice(0, 1000);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8' }
  });
}
