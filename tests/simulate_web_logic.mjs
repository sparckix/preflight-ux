import fs from 'node:fs';
import vm from 'node:vm';

const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      id,
      value: '',
      checked: false,
      innerHTML: '',
      textContent: '',
      type: 'text',
      disabled: false,
      classList: { toggle() {} },
      addEventListener() {},
      setAttribute(name, value) { this[name] = value; },
      getAttribute(name) { return this[name]; },
      querySelectorAll() { return []; }
    });
  }
  return elements.get(id);
}

const checkedPersonas = [{ checked: true, value: 'tom-random-visitor' }, { checked: true, value: 'jamie-accessibility' }];
const checkedRisks = [{ checked: true, value: 'empty-state-confusion' }, { checked: false, value: 'loading-abandonment' }];

const context = {
  console,
  Blob: class {},
  URL: { createObjectURL: () => 'blob:mock', revokeObjectURL() {} },
  FileReader: class {
    readAsDataURL(file) {
      this.result = `data:${file.type};base64,aGVsbG8=`;
      if (this.onload) this.onload();
    }
  },
  window: { setTimeout() {} },
  localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
  navigator: { clipboard: { writeText: async () => {} } },
  document: {
    getElementById: element,
    querySelectorAll(selector) {
      if (selector.includes('personaList')) return checkedPersonas;
      if (selector.includes('riskFocus')) return checkedRisks;
      return [];
    },
    createElement: () => ({ click() {} })
  },
  fetch: async () => ({ ok: true, json: async () => ({ markdown: '## Top risks\nMock panel' }) })
};

for (const [id, value] of Object.entries({
  productName: 'Demo Product',
  audience: 'Operators',
  stage: 'prototype',
  surfaceType: 'spec',
  surface: 'A surface description',
  prototypeUrl: 'https://example.com/proto',
  reviewDepth: 'fast',
  synthesisMode: 'prioritized',
  byokProvider: 'anthropic',
  byokModel: 'claude-sonnet-4-6',
  byokKey: ''
})) {
  element(id).value = value;
}
element('byokFields');
element('byokEnabled');
element('byokStatus');
element('packetOutput');
element('panelResult');
element('runPanel');
element('toggleKey');
element('clearKey');
element('selectDefault');
element('loadSample');
element('generatePacket');
element('validateBrief');
element('downloadPacket');
element('downloadResult');
element('downloadReport');
element('downloadRunJson');
element('parseFindings');
element('addFinding');
element('findingsList');
element('copyPacket');
element('importInput');
element('screenshotInput');
element('clearScreenshots');
element('attachmentStatus');
element('screenshotPreview');
element('validationBox');
element('provenanceBox');
element('historyList');
element('clearHistory');
element('output');

vm.createContext(context);
vm.runInContext(fs.readFileSync('web/app.js', 'utf8'), context);
if (!element('packetOutput').textContent.includes('Demo Product')) throw new Error('brief did not render product');
if (!element('packetOutput').textContent.includes('preflight_ux_review_brief')) throw new Error('brief artifact type missing');
if (!element('packetOutput').textContent.includes('web-byok-v0.4')) throw new Error('brief prompt version missing');
if (!element('packetOutput').textContent.includes('https://example.com/proto')) throw new Error('brief did not include prototype URL');
if (!element('packetOutput').textContent.includes('tom-random-visitor')) throw new Error('brief did not include selected persona');
if (!element('packetOutput').textContent.includes('review')) throw new Error('review controls missing from brief');
if (!element('findingsList').innerHTML.includes('No normalized findings')) throw new Error('findings editor did not initialize');
console.log('OK: web logic simulations passed');
