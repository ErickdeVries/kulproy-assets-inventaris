const assert = require('node:assert/strict');
const { test } = require('node:test');
const createConfig = require('../app.config.js');

function resolveConfig(value) {
  const previous = process.env.EXPO_PUBLIC_API_URL;
  if (value === undefined) delete process.env.EXPO_PUBLIC_API_URL;
  else process.env.EXPO_PUBLIC_API_URL = value;
  try {
    return createConfig({ config: { name: 'Asset-Gudang', extra: { retained: true } } });
  } finally {
    if (previous === undefined) delete process.env.EXPO_PUBLIC_API_URL;
    else process.env.EXPO_PUBLIC_API_URL = previous;
  }
}

test('tanpa URL: mode fondasi tanpa koneksi backend', () => {
  assert.equal(resolveConfig(undefined).extra.apiBaseUrl, null);
  assert.equal(resolveConfig('  ').extra.apiBaseUrl, null);
});

test('URL HTTP(S) valid dinormalisasi dan config lain dipertahankan', () => {
  const config = resolveConfig(' https://example.com/api/v1/// ');
  assert.equal(config.extra.apiBaseUrl, 'https://example.com/api/v1');
  assert.equal(config.extra.retained, true);
  assert.equal(config.name, 'Asset-Gudang');
  assert.equal(resolveConfig('http://10.0.2.2:8000/api/v1').extra.apiBaseUrl,
    'http://10.0.2.2:8000/api/v1');
});

test('tolak skema non-HTTP, kredensial, query, fragment, dan URL rusak', () => {
  for (const value of ['not-a-url', 'ftp://example.com', 'https://user:pass@example.com/api',
    'https://example.com/api?token=private', 'https://example.com/api#private']) {
    assert.throws(() => resolveConfig(value), /EXPO_PUBLIC_API_URL/);
  }
});
