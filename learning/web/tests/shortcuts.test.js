'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');

// Invoke the production guide renderer without polling, network or progress writes.
const appPath = path.resolve(__dirname, '..', 'app.js');
const source = fs.readFileSync(appPath, 'utf8');
const startup = /  void bootstrap\(\{ quiet: true \}\);\r?\n\}\)\(\);\s*$/;
assert.match(source, startup, 'the app startup boundary must be identifiable');
const context = {
  document: { addEventListener() {} },
  window: { addEventListener() {}, setInterval() {} },
};
vm.runInNewContext(source.replace(startup, '  globalThis.renderer = { renderStep, renderShortcut, state };\n})();'), context, { filename: appPath });
const { renderStep, renderShortcut, state } = context.renderer;
const sha256 = 'a'.repeat(64);

function shortcutFor(extra = {}) {
  return {
    keys: 'G → X → 0.5 → Enter',
    effect: '沿 X 軸從目前位置再移動 0.5。',
    requirements: ['滑鼠在 3D Viewport，Cube 已選取。'],
    cautions: ['這是相對位移；欄位輸入是絕對值。', 'Esc 或滑鼠右鍵取消。'],
    evidence: [{ path: 'learning/evidence/01/shortcut-v001/verification.json', sha256, method: 'Blender 5.2.1 獨立操作與讀回', label: '操作驗證' }],
    ...extra,
  };
}

function renderGuide(shortcut) {
  const guide = { where: '3D Viewport 的 Item 側欄', do: '點 Location X 欄位，輸入 0.5 後按 Enter。', see: 'Location X 顯示 0.5。' };
  if (shortcut !== undefined) guide.shortcut = shortcut;
  const step = { id: '01-07', title: '位置', guide: [guide], success: 'Cube 位於 X = 0.5。' };
  const lesson = { id: '01', steps: [step] };
  state.data = { catalog: { lessons: [lesson] }, progress: { activeLesson: '01', lessons: { '01': { completedSteps: [] } } } };
  return { markup: renderStep(lesson, step), step };
}

test('verified shortcuts supplement the original guide and success condition without changing them', () => {
  const shortcut = shortcutFor();
  const before = JSON.stringify(shortcut);
  const { markup, step } = renderGuide(shortcut);
  assert.match(markup, /點 Location X 欄位，輸入 0.5 後按 Enter。/);
  assert.match(markup, /你會看到<\/strong> Location X 顯示 0.5。/);
  assert.match(markup, /成功時應看到<\/strong><p>Cube 位於 X = 0.5。/);
  assert.match(markup, /aria-label="快速方法"><h4>快速方法<\/h4>/);
  assert.match(markup, /<kbd>G → X → 0.5 → Enter<\/kbd>/);
  assert.match(markup, /操作前<\/strong><ul><li>滑鼠在 3D Viewport，Cube 已選取。/);
  assert.match(markup, /注意<\/strong><ul><li>這是相對位移；欄位輸入是絕對值。/);
  assert.ok(markup.indexOf('Location X 顯示 0.5。') < markup.indexOf('<h4>快速方法</h4>'));
  assert.equal(JSON.stringify(step.guide[0].shortcut), before);
});

test('guides without a shortcut keep the standard guide with no empty quick-method block', () => {
  const { markup } = renderGuide();
  assert.match(markup, /點 Location X 欄位，輸入 0.5 後按 Enter。/);
  assert.match(markup, /Location X 顯示 0.5。/);
  assert.doesNotMatch(markup, /guide-shortcut|快速方法|驗證依據/);
});

test('all shortcut text, reference labels and method text are escaped', () => {
  const markup = renderShortcut(shortcutFor({
    keys: '<img src=x onerror=alert(1)>',
    effect: '<script>effect</script> & "absolute"',
    requirements: ['<input autofocus>'],
    cautions: ['<iframe>'],
    evidence: [{ path: 'learning/evidence/01/original.png', sha256, method: '<svg onload=alert(1)>', label: '<b>原圖</b>' }],
  }));
  assert.match(markup, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.match(markup, /&lt;script&gt;effect&lt;\/script&gt; &amp; &quot;absolute&quot;/);
  assert.match(markup, /&lt;input autofocus&gt;/);
  assert.match(markup, /&lt;iframe&gt;/);
  assert.match(markup, /&lt;svg onload=alert\(1\)&gt;/);
  assert.match(markup, /&lt;b&gt;原圖&lt;\/b&gt;/);
  assert.doesNotMatch(markup, /<img|<script|<input|<iframe|<svg|<b>/);
});

test('evidence links are limited to raw images or JSON inside learning evidence', () => {
  for (const filename of ['screen.png', 'screen.JPG', 'screen.jpeg', 'screen.webp', 'verification.json']) {
    const evidencePath = `learning/evidence/01/demo-v001/${filename}`;
    const markup = renderShortcut(shortcutFor({ evidence: [{ path: evidencePath, sha256, method: '核對' }] }));
    assert.ok(markup.includes(`href="/files/${evidencePath}"`));
    assert.match(markup, /target="_blank" rel="noopener"/);
    assert.ok(markup.includes(`SHA-256 ${sha256}`));
  }
  for (const evidencePath of [
    'https://example.com/screen.png', 'javascript:alert(1)', '/learning/evidence/screen.png',
    'learning/workspaces/01/screen.png', 'learning/evidence/../progress.json',
    'learning/evidence/01/../../progress.json', 'learning/evidence/01/./screen.png',
    'learning/evidence//screen.png', 'learning/evidence/.private/screen.png',
    'learning/evidence/01/%2e%2e/progress.json', 'learning/evidence/01\\screen.png',
    'learning/evidence/01/screen.png?x=1', 'learning/evidence/01/screen.png#x',
    'learning/evidence/01/screen.svg', 'learning/evidence/01/screen.html', 'learning/evidence/01/test.js',
    'learning/evidence/01/screen\n.png',
  ]) {
    assert.equal(renderShortcut(shortcutFor({ evidence: [{ path: evidencePath, sha256, method: '核對' }] })), '', evidencePath);
  }
});

test('unverified or malformed shortcut data does not become a quick method', () => {
  for (const shortcut of [undefined, null, '', 'G X 0.5', ['G'], 1, true, {},
    shortcutFor({ keys: '' }), shortcutFor({ keys: ['G', 'X'] }),
    shortcutFor({ effect: null }), shortcutFor({ evidence: [] }),
    shortcutFor({ evidence: undefined }), shortcutFor({ evidence: [{ path: 'learning/evidence/test.json', sha256: 'abc', method: '核對' }] }),
    shortcutFor({ evidence: [{ path: 'learning/evidence/test.json', sha256, method: '' }] }),
  ]) {
    assert.equal(renderShortcut(shortcut), '');
  }
});

test('unknown properties do not infer a shortcut or change its effect', () => {
  const markup = renderShortcut(shortcutFor({
    unsupported: '<script>unknown</script>',
    requirements: 'Do not infer this string as an array.',
    cautions: [null, {}, '<b>listed caution</b>'],
  }));
  assert.match(markup, /沿 X 軸從目前位置再移動 0.5。/);
  assert.doesNotMatch(markup, /unknown|Do not infer this string|操作前|\[object Object\]/);
  assert.match(markup, /&lt;b&gt;listed caution&lt;\/b&gt;/);
  assert.doesNotMatch(renderGuide({ key: 'G', effect: 'Unsupported old shape' }).markup, /guide-shortcut/);
});

test('mixed valid and invalid evidence renders only the valid references', () => {
  const markup = renderShortcut(shortcutFor({ evidence: [
    { path: 'learning/evidence/01/verified.png', sha256, method: '選單快捷鍵標示', label: '原始截圖' },
    { path: 'learning/workspaces/private.json', sha256, method: 'not evidence', label: 'private' },
    { path: 'learning/evidence/01/missing.json', sha256: 'bad', method: 'missing hash' },
  ] }));
  assert.match(markup, /原始截圖/);
  assert.doesNotMatch(markup, /private|missing\.json|not evidence|missing hash/);
});
