import handler from '../api/panel.js';

function mockReq(body, method = 'POST') {
  return { method, body };
}

function mockRes() {
  return {
    statusCode: 200,
    headers: {},
    body: null,
    setHeader(key, value) { this.headers[key] = value; },
    status(code) { this.statusCode = code; return this; },
    json(payload) { this.body = payload; return this; }
  };
}

const originalFetch = global.fetch;
const anthropicTestKey = ['sk', 'ant', 'abcdefghijklmnopqrstuvwxyz'].join('-');
const openaiTestKey = ['sk', 'abcdefghijklmnopqrstuvwxyz'].join('-');

global.fetch = async (url, opts) => {
  const target = String(url);
  const body = JSON.parse(opts.body);
  if (target.includes('anthropic.com')) {
    if (!opts.headers['x-api-key'].startsWith('sk-ant-')) throw new Error('missing anthropic key');
    if (!body.system.includes('Preflight UX')) throw new Error('missing system prompt');
    return { ok: true, json: async () => ({ content: [{ type: 'text', text: '## Top risks\nMock anthropic result' }] }) };
  }
  if (target.includes('openai.com')) {
    if (!opts.headers.authorization.startsWith('Bearer sk-')) throw new Error('missing openai key');
    return { ok: true, json: async () => ({ choices: [{ message: { content: '## Top risks\nMock openai result' } }] }) };
  }
  if (target.includes('generativelanguage.googleapis.com')) {
    return { ok: true, json: async () => ({ candidates: [{ content: { parts: [{ text: '## Top risks\nMock google result' }] } }] }) };
  }
  throw new Error(`unexpected fetch ${target}`);
};

const packet = {
  product: { name: 'Sim', audience: 'Builders', stage: 'prototype', surface_type: 'prototype', prototype_url: 'https://example.com/proto', surface: 'A product surface' },
  attachments: { screenshots: [{ name: 'home.png', mime_type: 'image/png', size_bytes: 80, data_url: 'data:image/png;base64,aGVsbG8=' }] },
  panel: { personas: ['tom-random-visitor'], risk_focus: ['empty-state-confusion'] }
};

let res = mockRes();
await handler(mockReq({ byok: null, packet }), res);
if (res.statusCode !== 400 || !String(res.body.error).includes('BYOK')) throw new Error('expected missing BYOK 400');

res = mockRes();
await handler(mockReq({ byok: { provider: 'anthropic', key: 'bad', model: 'claude-sonnet-4-6' }, packet }), res);
if (res.statusCode !== 400 || !String(res.body.error).includes('API key shape')) throw new Error('expected bad key shape');

res = mockRes();
await handler(mockReq({ byok: { provider: 'anthropic', key: anthropicTestKey, model: 'claude-sonnet-4-6' }, packet }), res);
if (res.statusCode !== 200 || !res.body.markdown.includes('Mock anthropic') || res.body.image_count !== 1) throw new Error('anthropic mock failed');

res = mockRes();
await handler(mockReq({ byok: { provider: 'openai', key: openaiTestKey, model: 'gpt-4.1' }, packet }), res);
if (res.statusCode !== 200 || !res.body.markdown.includes('Mock openai')) throw new Error('openai mock failed');

res = mockRes();
await handler(mockReq({ byok: { provider: 'google', key: 'abcdefghijklmnopqrstuvwxyz', model: 'gemini-2.5-flash' }, packet }), res);
if (res.statusCode !== 200 || !res.body.markdown.includes('Mock google')) throw new Error('google mock failed');

global.fetch = originalFetch;
console.log('OK: BYOK API simulations passed');
