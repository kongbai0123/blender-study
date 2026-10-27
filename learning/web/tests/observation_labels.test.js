'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

// Exercise the real renderer without starting polling or issuing progress requests.
const appPath = path.resolve(__dirname, '..', 'app.js');
const source = fs.readFileSync(appPath, 'utf8');
const startup = /  void bootstrap\(\{ quiet: true \}\);\r?\n\}\)\(\);\s*$/;
assert.match(source, startup, 'the app startup boundary must be identifiable');
const context = {
  document: { addEventListener() {} },
  window: { addEventListener() {}, setInterval() {} },
};
vm.runInNewContext(source.replace(startup, '  globalThis.renderer = { renderOperationRun, renderPreviousOperationRuns };\n})();'), context, { filename: appPath });
const { renderOperationRun, renderPreviousOperationRuns } = context.renderer;

function runFor(event = {}, extra = {}) {
  return { performedBy: 'tutor', status: 'completed', events: [{ action: '操作', observed: '選單已展開；長度 10 mm。', ...event }], ...extra };
}

function observationHeading(markup) {
  return markup.match(/class="operation-observed"><strong>([^<]+)<\/strong>/)?.[1];
}

test('explicit classifications have separate labels', () => {
  for (const [observedKind, label] of [
    ['scripted_description', '文字描述，請對照原圖'],
    ['readback', '狀態讀回值'],
    ['mixed', '混合紀錄：文字描述與讀回值'],
  ]) {
    const markup = renderOperationRun(runFor({ observedKind }));
    assert.equal(observationHeading(markup), label);
    assert.doesNotMatch(markup, /<strong>實際結果<\/strong>/);
  }
});

test('missing and unknown classifications remain observations regardless of wording', () => {
  for (const observedKind of [undefined, null, '', 'unknown', 'toString', '__proto__']) {
    for (const observed of ['選單已展開。', 'Dimensions 10 × 10 × 8 mm；Non Manifold 0。']) {
      assert.equal(observationHeading(renderOperationRun(runFor({ observedKind, observed }))), '觀察紀錄');
    }
  }
});

test('classification never changes observed text, screenshots or prior runs', () => {
  const event = {
    observedKind: 'mixed',
    observed: '<Menu> 已展開 & 值 = 2',
    figure: { type: 'screenshot', path: 'learning/evidence/01/original.png', alt: '原圖', caption: '原始截圖' },
  };
  const run = runFor(event, { id: 'historical-run' });
  const before = JSON.stringify(run);
  const markup = renderPreviousOperationRuns([run]);
  assert.equal(JSON.stringify(run), before);
  assert.match(markup, /&lt;Menu&gt; 已展開 &amp; 值 = 2/);
  assert.match(markup, /src="\/files\/learning\/evidence\/01\/original.png"/);
  assert.match(markup, /href="\/files\/learning\/evidence\/01\/original.png"/);
  assert.equal(observationHeading(markup), '混合紀錄：文字描述與讀回值');
});

test('workspace snapshot equality does not assert absence or authorship of writes', () => {
  const markup = renderOperationRun(runFor({}, { workspaceContentsUnchanged: true, learnerWorkspaceWrites: false }));
  assert.match(markup, /前後快照內容一致/);
  assert.match(markup, /不能證明期間未曾寫入，也不能判定寫入者/);
  assert.doesNotMatch(markup, /未寫入學員工作區|學員工作區未寫入|助教未寫入/);
});

test('workspace differences and legacy unknowns remain distinct and escape notes', () => {
  const changed = renderOperationRun(runFor({}, { workspaceContentsUnchanged: false }));
  assert.match(changed, /前後快照內容不同；此比對不能判定寫入者/);
  const legacy = renderOperationRun(runFor({}, {
    workspaceContentsUnchanged: null,
    workspaceEvidenceNote: '舊版執行器只比對第一層檔名，未保存前後雜湊。<script>',
  }));
  assert.match(legacy, /<strong>工作區內容核對<\/strong> 未知。/);
  assert.match(legacy, /舊版執行器只比對第一層檔名，未保存前後雜湊。&lt;script&gt;/);
  assert.doesNotMatch(legacy, /<script>/);
  assert.doesNotMatch(renderOperationRun(runFor()), /<strong>工作區內容核對<\/strong>/);
});

test('an explicit workspace note is rendered once with only a short comparison label', () => {
  const note = '前後快照內容一致；此比對不能證明期間未曾寫入，也不能判定寫入者。';
  for (const [workspaceContentsUnchanged, label] of [[true, '一致'], [false, '不同'], [null, '未知']]) {
    const markup = renderOperationRun(runFor({}, { workspaceContentsUnchanged, workspaceEvidenceNote: note }));
    assert.match(markup, new RegExp(`<strong>工作區內容核對<\\/strong> ${label}。`));
    assert.equal(markup.split(note).length - 1, 1);
  }
  const noNote = renderOperationRun(runFor({}, { workspaceContentsUnchanged: null, workspaceEvidenceNote: '' }));
  assert.match(noNote, /無法由既有證據判定前後內容是否一致/);
});

test('missing observations do not gain readback or qualification claims', () => {
  const markup = renderOperationRun(runFor({ observed: '', observedKind: 'readback' }));
  assert.doesNotMatch(markup, /class="operation-observed"/);
  assert.match(markup, /不能代替學員確認、幾何檢查或實體合格證據/);
  assert.equal(renderOperationRun({ performedBy: 'learner', events: [{ observed: '完成' }] }), '');
});
