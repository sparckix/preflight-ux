import fs from 'node:fs';

const html = fs.readFileSync('web/index.html', 'utf8');
const example = fs.readFileSync('web/example.html', 'utf8');
const css = fs.readFileSync('web/styles.css', 'utf8');

const requiredIds = [
  'how-to', 'briefForm', 'prototypeUrl', 'screenshotInput', 'reviewDepth',
  'synthesisMode', 'importInput', 'validateBrief', 'parseFindings', 'addFinding',
  'downloadRunJson', 'downloadReport', 'findingsList', 'historyList'
];
for (const id of requiredIds) {
  if (!html.includes(`id="${id}"`)) throw new Error(`missing web control #${id}`);
}

for (const cls of ['how-to', 'upload-box', 'quality-controls', 'validation-box', 'findings-box', 'finding-card', 'history-box']) {
  if (!css.includes(`.${cls}`)) throw new Error(`missing CSS class .${cls}`);
}

for (const phrase of ['Review Brief', 'Normalized findings', 'Local history', 'Run panel']) {
  if (!html.includes(phrase)) throw new Error(`missing product text ${phrase}`);
}

if (/preflight packet|panel packet|Run Packet|Generate packet/i.test(html + example)) {
  throw new Error('stale packet terminology found in public HTML');
}

for (const phrase of ['Example workflow', 'Review brief', 'Normalized findings', 'Repo-ready report']) {
  if (!example.includes(phrase)) throw new Error(`example page missing ${phrase}`);
}

if (!css.includes('@media (max-width: 920px)')) throw new Error('missing responsive media query');
if (!css.includes('grid-template-columns: minmax(0, 1.45fr)')) throw new Error('workspace grid contract changed');

console.log('OK: static web UI regression checks passed');
