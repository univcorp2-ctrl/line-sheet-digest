import test from 'node:test';
import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { collectSourceIds, isTargetSource, timingSafeEqual, verifyLineSignature } from '../src/index.js';

test('verifyLineSignature accepts a valid LINE signature', async () => {
  const body = JSON.stringify({ events: [{ type: 'message' }] });
  const secret = 'test-channel-secret';
  const signature = createHmac('sha256', secret).update(body).digest('base64');

  assert.equal(await verifyLineSignature(body, secret, signature), true);
});

test('verifyLineSignature rejects an invalid LINE signature', async () => {
  const body = JSON.stringify({ events: [{ type: 'message' }] });
  const secret = 'test-channel-secret';

  assert.equal(await verifyLineSignature(body, secret, 'invalid'), false);
});

test('collectSourceIds collects user, group and room IDs', () => {
  assert.deepEqual(collectSourceIds({ userId: 'U1', groupId: 'G1', roomId: 'R1' }), ['U1', 'G1', 'R1']);
});

test('isTargetSource allows all when no target is configured', () => {
  assert.equal(isTargetSource({ groupId: 'G1' }, ''), true);
});

test('isTargetSource filters by comma separated source IDs', () => {
  assert.equal(isTargetSource({ groupId: 'G1' }, 'G1,U2'), true);
  assert.equal(isTargetSource({ groupId: 'G3' }, 'G1,U2'), false);
});

test('timingSafeEqual compares strings', () => {
  assert.equal(timingSafeEqual('abc', 'abc'), true);
  assert.equal(timingSafeEqual('abc', 'abd'), false);
  assert.equal(timingSafeEqual('abc', 'abcd'), false);
});
