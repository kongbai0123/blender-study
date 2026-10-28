'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const appPath = path.resolve(__dirname, '..', 'app.js');
const modulePath = path.resolve(__dirname, '..', 'engineering-path.js');
const source = fs.readFileSync(appPath, 'utf8');
const startup = /  void bootstrap\(\{ quiet: true \}\);\r?\n\}\)\(\);\s*$/;
assert.match(source, startup);

function lesson(id, stepId) {
  return { id, title: id, goal: '原教材目標', steps: [{ id: stepId, title: stepId, success: '待學員確認', guide: [] }] };
}

function bootstrapData() {
  return {
    projectRoot: 'D:\\example', files: [], journal: [],
    catalog: { lessons: [lesson('01', '01-01'), lesson('05', '05-05')] },
    progress: {
      revision: 6, updatedAt: '2026-10-27T10:00:00+08:00', activeLesson: '01', learner: { interfaceLanguage: 'en' },
      lessons: { '01': { currentStep: '01-01', completedSteps: [], notes: [] }, '05': { currentStep: '05-05', completedSteps: [], notes: [] } },
      events: [], fileVersions: [],
    },
  };
}

function pathData() {
  const chapter = (id) => ({
    id, number: id.slice(2), title: '小盒與量測 ' + id, goal: '辨認名義尺寸與實測值', practice: ['查看既有小盒'], functions: ['尺寸欄位'],
    shortcuts: [{ keys: 'N', effect: '切換側欄', context: '3D Viewport', status: '沿用既有紀錄' }],
    references: [{ lessonId: '05', stepId: '05-05', label: '既有上蓋實拍' }], deliverable: '量測計畫', availability: 'mixed', notes: ['實體結果留空'],
  });
  return {
    schemaVersion: 1, id: 'engineering', title: '工程學習路徑', version: 'v001', intro: '公差與量測前置',
    chapters: [chapter('ch01'), { ...chapter('ch02'), availability: 'new_content_pending' }],
    baseline: { summary: '60 × 40 × 30 mm', dimensions: [{ label: '總間隙', value: '0.4 mm（試驗值）' }], limitations: ['尚未試配'] },
    learningPolicy: ['只有學員回報後才記錄'],
    environment: { summary: '草圖環境待驗證', recordPath: null }, sources: [],
  };
}

function curriculumData() {
  return { schemaVersion: 1, id: 'engineering-curriculum-v002', version: 'v002', description: '逐步', chapters: [{
    id: 'ch01', number: '01', title: '小盒', goal: '理解位置', deliverable: '記錄', limitations: ['實體試配待測'], steps: [{
      id: 'ec01-01', title: '觀察', goal: '定位', context: '3D Viewport / Object Mode', actions: ['查看原圖'], success: '找到盒口', evidenceStatus: 'existing_demo', limitations: ['原圖不能直接量出間隙'],
      shortcuts: [{ keys: 'N', effect: '切換側欄', requirements: ['焦點在 3D Viewport'], cautions: ['核對模式'], evidence: [{ path: 'learning/evidence/05/demo-v001/lid.png', sha256: 'a'.repeat(64), label: '快捷鍵實拍', method: '原生圖' }] }],
      figures: [{ type: 'screenshot', path: 'learning/evidence/05/demo-v001/lid.png', caption: '盒口原圖', sha256: 'a'.repeat(64) }], sourceSteps: [{ lessonId: '05', stepId: '05-05' }], section: '01-01',
    }], sections: [{ id: '01-01', title: '看盒口' }] }, { id: 'ch02', number: '02', title: '間隙', sections: [{ id: '02-01', title: '規劃' }], steps: [{ id: 'ec02-01', title: '試驗規劃', actions: ['觀察'], evidenceStatus: 'draft_pending_demo', figures: [], sourceSteps: [], section: '02-01' }] }] };
}

function harness({ hash = '', fetchImpl, module = true } = {}) {
  const elements = new Map();
  const requests = [];
  const listeners = {};
  const bodyClasses = new Set();
  const getElement = (id) => {
    if (!elements.has(id)) elements.set(id, { innerHTML: '', textContent: '', setAttribute() {}, removeAttribute() {}, focus() {}, replaceChildren() {}, append() {} });
    return elements.get(id);
  };
  const location = { hash, pathname: '/', search: '' };
  const context = {
    document: { body: { classList: { toggle(name, enabled) { if (enabled) bodyClasses.add(name); else bodyClasses.delete(name); } } }, createElement: () => ({ setAttribute() {}, addEventListener() {}, textContent: '' }), getElementById: getElement, querySelectorAll: () => [], querySelector: () => null, addEventListener(name, callback) { listeners[name] = callback; } },
    window: { location, history: { replaceState(_a, _b, value) { location.hash = value.slice(value.indexOf('#')); } }, addEventListener() {}, setInterval() {} },
    async fetch(url, options) { requests.push({ url, method: options.method || 'GET', ...(options.body ? { body: JSON.parse(options.body) } : {}) }); return fetchImpl ? fetchImpl(url, options) : { ok: true, json: async () => url === '/api/bootstrap' ? bootstrapData() : url === '/engineering-curriculum.json' ? curriculumData() : pathData() }; },
  };
  vm.createContext(context);
  if (module) vm.runInContext(fs.readFileSync(modulePath, 'utf8'), context, { filename: modulePath });
  vm.runInContext(source.replace(startup, '  globalThis.app = { state, renderEngineering, loadEngineering, loadCurriculum, saveEngineeringRecord, selectEngineeringChapter, openEngineeringReference, openSection, gotoCurriculumStep, selectCurriculumStep, selectDetailTab, applyViewHash, bootstrap, render };\n})();'), context, { filename: appPath });
  context.app.state.data = bootstrapData();
  context.app.state.lesson = '01';
  context.app.state.browsed.set('01', '01-01');
  return { context, elements, requests, listeners, bodyClasses, app: context.app, renderer: context.BlenderEngineeringPath };
}

test('direct engineering URLs select the requested chapter and navigating references never writes progress', async () => {
  const { app, requests, context } = harness({ hash: '#engineering/ch02' });
  const before = JSON.stringify(app.state.data.progress);
  assert.equal(app.state.view, 'engineering');
  assert.equal(app.state.engineering.chapter, 'ch02');
  await app.loadEngineering();
  app.selectEngineeringChapter('ch01');
  assert.equal(context.window.location.hash, '#engineering/ch01');
  assert.equal(app.state.engineering.chapter, 'ch01');
  app.openEngineeringReference('05', '05-05');
  assert.equal(app.state.lesson, '05');
  assert.equal(app.state.browsed.get('05'), '05-05');
  assert.equal(app.state.view, 'lesson');
  assert.equal(context.window.location.hash, '#lesson');
  assert.equal(JSON.stringify(app.state.data.progress), before);
  assert.deepEqual(requests, [{ url: '/engineering-path.json', method: 'GET' }, { url: '/engineering-curriculum.json', method: 'GET' }]);
  app.openEngineeringReference('05', '01-01');
  assert.equal(app.state.browsed.get('05'), '05-05');
});

test('bare entry opens the reordered chapters as the main navigation without modifying legacy progress', async () => {
  const { app, elements, requests } = harness();
  const before = JSON.stringify(app.state.data.progress);
  assert.equal(app.state.view, 'engineering');
  await app.loadEngineering();
  const html = elements.get('engineering-list').innerHTML;
  assert.ok(html.indexOf('data-engineering-chapter="ch01"') < html.indexOf('data-engineering-chapter="ch02"'));
  assert.match(html, /0 \/ 1 小步已確認/);
  assert.equal(elements.get('engineering-sidebar-progress').textContent, '0 / 2 小步已確認');
  assert.equal(elements.has('lesson-list'), false);
  assert.equal(JSON.stringify(app.state.data.progress), before);
  assert.ok(requests.every((item) => item.method === 'GET'));
});

test('bare entry uses shared new-course confirmations to pick the next chapter while explicit legacy links stay legacy', async () => {
  const h = harness();
  h.app.state.data.progress.events.push({ type: 'engineering_step_confirmed', curriculumId: 'engineering-curriculum-v002', chapterId: 'ch01', stepId: 'ec01-01', author: 'learner', evidence: '完成' });
  await h.app.loadEngineering();
  assert.equal(h.app.state.engineering.chapter, 'ch02');
  assert.equal(h.elements.get('engineering-sidebar-progress').textContent, '1 / 2 小步已確認');
  const old = harness({ hash: '#lesson' });
  await old.app.loadEngineering();
  assert.equal(old.app.state.view, 'lesson');
  assert.match(old.elements.get('engineering-list').innerHTML, /data-engineering-chapter="ch01"/);
});

test('entry has only the new chapters in the sidebar and no original-lesson tabs', () => {
  const html = fs.readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8');
  assert.match(html, /<nav id="engineering-list" aria-label="新版工程章節"><\/nav>/);
  assert.match(html, /<nav class="view-tabs" aria-label="學習頁面"><button type="button" data-view="engineering" aria-current="page">新版教學章節<\/button><button type="button" data-view="journal">學習紀錄<\/button><button type="button" data-view="versions">檔案版本<\/button><\/nav>/);
  assert.doesNotMatch(html, /legacy-sidebar|lesson-list|data-view="lesson"|data-view="overview"|completed-count/);
});

test('load failure is visible once, ordinary progress polling does not retry, explicit retry recovers', async () => {
  let failed = true;
  const h = harness({ hash: '#engineering', fetchImpl: async (url) => {
    if (url === '/engineering-path.json' && failed) return { ok: false, status: 404, json: async () => ({ error: '路徑資料尚未提供' }) };
    return { ok: true, json: async () => url === '/api/bootstrap' ? bootstrapData() : pathData() };
  } });
  await h.app.loadEngineering();
  assert.match(h.app.renderEngineering(), /路徑資料尚未提供/);
  await h.app.loadEngineering();
  await h.app.bootstrap({ quiet: true });
  assert.equal(h.requests.filter((item) => item.url === '/engineering-path.json').length, 1);
  failed = false;
  await h.app.loadEngineering({ retry: true });
  assert.match(h.app.renderEngineering(), /小盒與量測 ch01/);
  assert.equal(h.requests.filter((item) => item.url === '/engineering-path.json').length, 2);
  assert.ok(h.requests.every((item) => item.method === 'GET'));
});

test('missing path module leaves the old lessons readable', async () => {
  const { app, elements, requests } = harness({ module: false, hash: '#engineering' });
  await app.loadEngineering();
  assert.match(app.renderEngineering(), /模組尚未載入/);
  app.state.view = 'lesson';
  app.render();
  assert.match(elements.get('view-content').innerHTML, /STEP 01-01/);
  assert.equal(requests.length, 0);
});

test('the header points at the first unconfirmed main step across chapters, skipping optional steps', () => {
  const { renderer } = harness();
  const data = curriculumData(), shared = bootstrapData();
  data.chapters[0].sections = [{ id: '01-01', title: '看盒口' }];
  data.chapters[0].steps[0].section = '01-01';
  data.chapters[0].steps.push({ id: 'ec01-extra', title: '選修練習', actions: ['x'], evidenceStatus: 'draft_pending_demo', track: 'optional', section: '01-01' });
  let html = renderer.render(pathData(), shared, 'ch02', { data });
  assert.match(html, /data-goto-chapter="ch01" data-goto-step="ec01-01">前往下一小步：01-01 看盒口 · 觀察<\/button>/);
  shared.progress.events.push({ type: 'engineering_step_confirmed', curriculumId: data.id, chapterId: 'ch01', stepId: 'ec01-01', author: 'learner' });
  html = renderer.render(pathData(), shared, 'ch01', { data });
  assert.match(html, /data-goto-chapter="ch02" data-goto-step="ec02-01">前往下一小步：02-01 規劃 · 試驗規劃/);
  assert.equal(renderer.nextStep(shared, { data }).step.id, 'ec02-01');
  shared.progress.events.push({ type: 'engineering_step_confirmed', curriculumId: data.id, chapterId: 'ch02', stepId: 'ec02-01', author: 'learner' });
  assert.match(renderer.render(pathData(), shared, 'ch01', { data }), /主線小步都已確認/);
});

test('unsafe paths and markup do not become evidence or active content', () => {
  const { renderer } = harness();
  const data = pathData();
  data.chapters[0].title = '<script>bad</script>';
  data.chapters[0].shortcuts[0].keys = '<img src=x onerror=alert(1)>';
  data.sources = [{ label: 'unsafe', url: 'javascript:alert(1)' }];
  const curriculum = curriculumData();
  curriculum.chapters[0].steps[0].figures = ['learning/evidence/../progress.json', 'learning/workspaces/05/lid.png', 'learning/evidence/.private/lid.png', 'https://example.test/lid.png', 'learning/evidence/05/view.svg', 'learning/evidence/05/%2e%2e/lid.png'].map((path) => ({ type: 'screenshot', path, sha256: 'a'.repeat(64), caption: 'unsafe' }));
  const markup = renderer.render(data, bootstrapData(), 'ch01', { data: curriculum });
  assert.match(markup, /&lt;script&gt;bad&lt;\/script&gt;/);
  assert.match(markup, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.doesNotMatch(markup, /<script|<img|javascript:|https:\/\/example.test|\.private/);
});

test('malformed data and unknown chapter addresses fail without changing the shared state', async () => {
  const h = harness({ hash: '#engineering/ch99', fetchImpl: async () => ({ ok: true, json: async () => ({ ...pathData(), chapters: [pathData().chapters[0], pathData().chapters[0]] }) }) });
  const before = JSON.stringify(h.app.state.data.progress);
  await h.app.loadEngineering();
  assert.match(h.app.renderEngineering(), /章節編號或內容不正確/);
  assert.equal(JSON.stringify(h.app.state.data.progress), before);
  assert.match(h.renderer.render(pathData(), bootstrapData(), 'ch99'), /找不到這個路徑章節/);
});

test('source links support local journal reading while rejecting traversal and unrelated local routes', () => {
  const { renderer } = harness();
  const data = pathData();
  data.sources = [
    { label: '本機紀錄', url: '/read/learning/journal/2026-10-27-path-v001.md' },
    { label: '官方資料', url: 'https://docs.blender.org/manual/en/5.2/' },
    { label: '越界', url: '/read/learning/journal/../progress.json' },
    { label: '不可執行', url: '/api/progress' },
  ];
  const markup = renderer.render(data, bootstrapData());
  assert.match(markup, /href="\/read\/learning\/journal\/2026-10-27-path-v001.md"/);
  assert.match(markup, /href="https:\/\/docs.blender.org\/manual\/en\/5.2\/"/);
  assert.doesNotMatch(markup, /越界|不可執行|href="#"/);
});

test('engineering view keeps its mode while original reference links open the original lesson', async () => {
  const { app, bodyClasses } = harness({ hash: '#engineering/ch01' });
  await app.loadEngineering();
  assert.ok(bodyClasses.has('engineering-view'));
  app.openEngineeringReference('05', '05-05');
  assert.equal(bodyClasses.has('engineering-view'), false);
  app.selectEngineeringChapter('ch02');
  assert.ok(bodyClasses.has('engineering-view'));
  app.state.view = 'journal';
  app.render();
  assert.equal(bodyClasses.has('engineering-view'), false);
});

test('chapter labels, notes and shortcut statuses are shown as written in the path data for any curriculum version', () => {
  const { renderer } = harness();
  const path = pathData();
  path.chapters[0].availabilityLabel = '已有新示範＋待補內容';
  path.chapters[0].shortcuts = [{ keys: 'Screw', effect: '修改器', status: '資料中的目前狀態' }];
  path.chapters[0].notes = ['資料中的備註'];
  path.intro = '資料中的導言';
  const data = curriculumData();
  for (const version of ['v002', 'v027', 'v028']) {
    data.version = version;
    const html = renderer.render(path, bootstrapData(), 'ch01', { data });
    assert.match(html, /<span class="badge">已有新示範＋待補內容<\/span>/);
    assert.match(html, /資料中的目前狀態/);
    assert.match(html, /資料中的備註/);
    assert.match(html, /資料中的導言/);
    assert.match(html, new RegExp(`工程學習路徑 · ${version}`));
  }
});

test('revision conflicts refresh without resending and preserve new-path learner drafts', async () => {
  const newer = bootstrapData();
  newer.progress.revision = 7;
  newer.progress.events.push({ type: 'engineering_step_confirmed', author: 'learner', curriculumId: 'engineering-curriculum-v002', chapterId: 'ch01', stepId: 'ec01-01', evidence: '另一視窗已確認' });
  const h = harness({ hash: '#engineering/ch01', fetchImpl: async (url) => {
    if (url === '/api/progress') return { ok: false, status: 409, json: async () => ({ error: 'revision 衝突' }) };
    return { ok: true, json: async () => url === '/api/bootstrap' ? newer : url === '/engineering-curriculum.json' ? curriculumData() : pathData() };
  } });
  await h.app.loadEngineering();
  const key = h.renderer.draftKey('confirm', 'ch01', 'ec01-01');
  h.app.state.drafts.set(key, '保留的草稿');
  await h.app.saveEngineeringRecord('confirm', 'ch01', 'ec01-01', '保留的草稿');
  assert.equal(h.app.state.data.progress.revision, 7);
  assert.equal(h.app.state.drafts.get(key), '保留的草稿');
  assert.equal(h.requests.filter((request) => request.method === 'POST').length, 1);
  await h.app.saveEngineeringRecord('confirm', 'ch01', 'ec01-01', '保留的草稿');
  assert.equal(h.requests.filter((request) => request.method === 'POST').length, 1);
});

test('the original lesson page is read-only and links to the new small steps split from it', () => {
  const h = harness();
  h.app.state.engineering.curriculum.data = curriculumData();
  h.app.state.lesson = '05';
  h.app.state.browsed.set('05', '05-05');
  h.app.state.view = 'lesson';
  h.app.render();
  const html = h.elements.get('view-content').innerHTML;
  assert.match(html, /原教材只供查閱/);
  assert.match(html, /data-goto-chapter="ch01" data-goto-step="ec01-01">第 01 章 01-01 觀察<\/button>/);
  assert.doesNotMatch(html, /data-form="confirm"|data-form="note"|data-confirm-button|確認完成，接下一小步/);
});

test('original lesson notes leave out engineering-path answers while the journal labels them', () => {
  const h = harness();
  const notes = h.app.state.data.progress.lessons['01'].notes;
  notes.push({ author: 'tutor', text: '原教材筆記', at: '2026-10-22T11:10:29+08:00' },
    { author: 'learner', text: '是下方的環形唇邊', at: '2026-10-27T13:06:47+08:00' },
    { author: 'tutor', text: 'engineering:path-01-observe-lip:answered\n學員已辨認唇邊', at: '2026-10-27T13:06:47+08:00' });
  h.app.state.data.legacyEngineeringNotes = [{ lessonId: '01', noteIndex: 1, role: 'answer', activity: 'path-01-observe-lip' },
    { lessonId: '01', noteIndex: 2, role: 'marker', activity: 'path-01-observe-lip' }];
  h.app.state.view = 'lesson';
  h.app.render();
  const lessonHtml = h.elements.get('view-content').innerHTML;
  assert.match(lessonHtml, /已保存 1 則筆記/);
  assert.match(lessonHtml, /原教材筆記/);
  assert.doesNotMatch(lessonHtml, /環形唇邊|engineering:path/);
  h.app.state.view = 'journal';
  h.app.render();
  const journal = h.elements.get('view-content').innerHTML;
  assert.match(journal, /新版工程路徑的回答（不算本單元筆記）/);
  assert.match(journal, /新版工程路徑的助教標記（不算本單元筆記）/);
  assert.match(journal, /學員已辨認唇邊/);
  assert.doesNotMatch(journal, /engineering:path-01-observe-lip/);
});

test('engineering workspace files register with workspaceId instead of a lesson', async () => {
  const current = bootstrapData();
  current.engineeringWorkspaces = { 'engineering-parametric': 'learning/workspaces/engineering-parametric' };
  current.files = [{ path: 'learning/workspaces/engineering-parametric/my_manual_box_v002.blend', bytes: 2048, registered: false }];
  const h = harness({ fetchImpl: async (url, options) => {
    if (url === '/api/register-file') {
      const payload = JSON.parse(options.body);
      current.progress.revision++;
      current.progress.fileVersions.push({ path: payload.path, role: payload.role, workspace: payload.workspaceId, sha256: 'c'.repeat(64), bytes: 2048, registeredAt: '2026-10-27T18:00:00+08:00', revision: current.progress.revision });
      return { ok: true, json: async () => ({ progress: current.progress }) };
    }
    return { ok: true, json: async () => current };
  } });
  h.app.state.data = current;
  h.app.state.view = 'versions';
  h.app.render();
  assert.match(h.elements.get('view-content').innerHTML, /工程參數盒工作區 · 登記檔案/);
  assert.match(h.elements.get('view-content').innerHTML, /my_manual_box_v002\.blend/);
  const selected = { value: 'learning/workspaces/engineering-parametric/my_manual_box_v002.blend', removeAttribute() {} };
  h.context.document.querySelector = (selector) => selector === '#engineering-version-path' ? selected : null;
  await h.listeners.submit({ target: { matches: () => true, dataset: { form: 'engineering-version' } }, preventDefault() {} });
  await new Promise((resolve) => setTimeout(resolve, 0));
  const post = h.requests.find((request) => request.url === '/api/register-file');
  assert.deepEqual(post.body, { workspaceId: 'engineering-parametric', path: selected.value, role: 'source_scene', expectedRevision: 6 });
  assert.match(h.elements.get('view-content').innerHTML, /工程工作區 · 場景 \.blend/);
});


const section = (h, chapter = 'ch01', id = '01-01', extra = {}) => h.renderer.render(pathData(), h.app.state.data, chapter, { data: h.curriculum || curriculumData() }, { section: id, ...extra });

test('chapter page shows a short summary, the section list and a collapsed supplement without forms', () => {
  const { renderer } = harness();
  const data = pathData(), shared = bootstrapData(), curriculum = curriculumData();
  curriculum.chapters[0].sections.push({ id: '01-02', title: '加練', track: 'optional' });
  curriculum.chapters[0].steps.push({ id: 'ec01-opt', title: '選修', actions: ['做'], evidenceStatus: 'draft_pending_demo', section: '01-02', track: 'optional' });
  const before = JSON.stringify([data, shared]);
  const markup = renderer.render(data, shared, 'ch02', { data: curriculum });
  assert.match(markup, /<strong>學習進度<\/strong>/);
  assert.match(markup, /0 \/ 2 個主線小步已確認（另有選修 1 步，不計入） · revision 6/);
  assert.match(markup, /<dt>學什麼<\/dt><dd>辨認名義尺寸與實測值<\/dd>/);
  assert.match(markup, /<dt>接續<\/dt><dd>第 01 章 小盒與量測 ch01 的成果<\/dd>/);
  assert.match(markup, /data-section-chapter="ch02" data-open-section="02-01"><span>02-01<\/span><span>規劃<\/span><small>0 \/ 1<\/small>/);
  assert.match(markup, /<details class="panel engineering-chapter-extra"><summary>本章補充/);
  assert.match(markup, /data-reference-lesson="05" data-reference-step="05-05">既有上蓋實拍 <span>05-05<\/span><\/button><small>開啟原教材原頁，只供查閱來源。<\/small>/);
  assert.doesNotMatch(markup, /<form|data-form=|engineering-step-current|engineering-detail/);
  const first = renderer.render(data, shared, 'ch01', { data: curriculum });
  assert.match(first, /<span>01-02<\/span><span>加練 <em>選修<\/em><\/span>/);
  assert.match(first, /data-goto-chapter="ch01" data-goto-step="ec01-01">接續本章：01-01 觀察/);
  assert.doesNotMatch(first, /<dt>接續<\/dt>/);
  assert.equal(JSON.stringify([data, shared]), before);
});

test('section page lists only its steps, expands one at a time and shows the selected step in the detail tabs', () => {
  const h = harness();
  h.curriculum = curriculumData();
  h.curriculum.chapters[0].steps.push({ id: 'ec01-02', title: '再看一次', actions: ['看'], success: '看到', evidenceStatus: 'draft_pending_demo', section: '01-01',
    detail: { steps: ['滑鼠移到 3D Viewport', '按 <N>'], why: '因為 <側欄>' } });
  let html = section(h);
  assert.match(html, /<nav class="engineering-breadcrumb"[^>]*><button type="button" class="link-button" data-engineering-chapter="ch01">第 01 章 小盒與量測 ch01<\/button><span>›<\/span><span>01-01 看盒口<\/span>/);
  assert.match(html, /<li class="engineering-step-row selected" data-curriculum-step="ec01-01">/);
  assert.match(html, /<button type="button" data-select-step="ec01-02"><span class="step-mark">2<\/span>再看一次<\/button>/);
  assert.equal((html.match(/data-form="engineering-confirm"/g) || []).length, 1);
  assert.match(html, /<aside class="panel engineering-detail"[^>]*>.*<strong>觀察<\/strong>/);
  assert.match(html, /本章的詳細步驟還沒改寫/);
  assert.doesNotMatch(html, /data-curriculum-step="ec02-01"/);
  html = section(h, 'ch01', '01-01', { step: 'ec01-02' });
  assert.match(html, /<li class="engineering-step-row selected" data-curriculum-step="ec01-02">/);
  assert.match(html, /<ol><li>滑鼠移到 3D Viewport<\/li><li>按 &lt;N&gt;<\/li><\/ol>/);
  assert.match(html, /<strong>為什麼：<\/strong>因為 &lt;側欄&gt;/);
  assert.match(html, /data-detail-tab="detail" aria-selected="true">詳細步驟/);
  h.app.state.data.progress.events.push({ type: 'engineering_step_confirmed', curriculumId: 'engineering-curriculum-v002', chapterId: 'ch01', stepId: 'ec01-01', author: 'learner', evidence: '完成' });
  html = section(h);
  assert.match(html, /data-curriculum-step="ec01-02"/);
  assert.match(html, /<li class="engineering-step-row done"><button type="button" data-select-step="ec01-01"><span class="step-mark">✓<\/span>/);
  assert.match(html, /本節 1 \/ 2 已確認/);
});

test('detail tabs show figures, shortcuts, demonstration record, notes and help with safe paths only', () => {
  const h = harness();
  h.curriculum = curriculumData();
  const step = h.curriculum.chapters[0].steps[0];
  step.title = '<img src=x onerror=alert(1)>';
  step.figures.push({ type: 'screenshot', path: 'learning/evidence/../progress.json', sha256: 'a'.repeat(64), caption: '越界' });
  step.shortcuts[0].evidence.push({ path: 'learning/evidence/.private/secret.png', sha256: 'a'.repeat(64), label: '私密' });
  step.notices = [{ label: '尺寸範圍更正', text: 'H−D ≥ B 只是必要條件', source: '/read/learning/journal/2026-10-27-parametric-range-correction-v001.md' }, { label: '<b>不安全</b>', text: 'x', source: 'javascript:alert(1)' }];
  step.artifacts = [{ path: 'learning/evidence/example/model.blend', sha256: 'a'.repeat(64), label: '場景' }, { path: 'learning/evidence/../progress.json', sha256: 'a'.repeat(64), label: '越界版本' }];
  const original = h.app.state.data.catalog.lessons[1].steps[0];
  original.help = '選不到時先核對 <模式>。';
  original.parameterPlan = { rows: [] };
  original.operationRun = { events: [
    { seq: 1, action: '點 File', observed: '選單展開', observedKind: 'readback', figure: { type: 'screenshot', path: 'learning/evidence/05/run/01.png', caption: '原圖一' } },
    { seq: 2, action: '第二步', observed: '圖不應顯示', figure: { type: 'screenshot', path: 'learning/evidence/../progress.png', caption: '越界' } }] };
  const tab = (name) => section(h, 'ch01', '01-01', { tab: name });
  assert.match(tab('figures'), /src="\/files\/learning\/evidence\/05\/demo-v001\/lid.png"/);
  assert.match(tab('figures'), /SHA-256 a{64}/);
  assert.match(tab('shortcuts'), /<kbd>N<\/kbd>.*快捷鍵實拍/);
  assert.match(tab('record'), /原教材 05-05 的助教示範紀錄（2 張原圖）/);
  assert.match(tab('record'), /<strong>點 File<\/strong><p><small>狀態讀回值<\/small>選單展開/);
  assert.match(tab('record'), /\/files\/learning\/evidence\/example\/model\.blend/);
  assert.match(tab('notes'), /<strong>尺寸範圍更正：<\/strong>H−D ≥ B 只是必要條件<a href="\/read\/learning\/journal\/2026-10-27-parametric-range-correction-v001\.md"/);
  assert.match(tab('notes'), /本小步附有助教示範原圖或讀值/);
  assert.match(tab('notes'), /原教材 05-05 另有參數表、幾何或審查紀錄/);
  assert.match(tab('notes'), /小步代號 ec01-01/);
  assert.match(tab('help'), /原教材 05-05 的排解說明<\/h5><p>選不到時先核對 &lt;模式&gt;。<\/p>/);
  for (const name of ['detail', 'figures', 'shortcuts', 'record', 'notes', 'help']) {
    const html = tab(name);
    assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;/);
    assert.doesNotMatch(html, /<img src=x|progress\.(json|png)|\.private|私密|越界|javascript:/, name);
  }
  h.app.state.data.catalog.lessons[1].steps[0] = { id: '05-05', title: '05-05', success: '' };
  assert.match(tab('help'), /這一步沒有原教材的排解說明/);
});

test('a recorded chat answer appears on its step only when the server marks a learner note', () => {
  const h = harness();
  h.curriculum = curriculumData();
  h.curriculum.chapters[0].steps[0].legacyActivity = 'path-01-observe-lip';
  const notes = h.app.state.data.progress.lessons['01'].notes;
  notes.push({ author: 'learner', text: '是下方的<b>環形唇邊</b>' }, { author: 'tutor', text: 'engineering:path-01-observe-lip:answered\n說明' });
  assert.doesNotMatch(section(h), /聊天中的回答已記錄/);
  h.app.state.data.legacyEngineeringNotes = [{ lessonId: '01', noteIndex: 1, activity: 'path-01-observe-lip', role: 'answer' }, { lessonId: '01', noteIndex: 0, activity: 'path-99', role: 'answer' }];
  assert.doesNotMatch(section(h), /聊天中的回答已記錄/);
  h.app.state.data.legacyEngineeringNotes.push({ lessonId: '01', noteIndex: 0, activity: 'path-01-observe-lip', role: 'answer' });
  assert.match(section(h), /你在聊天中的回答已記錄：<\/strong>「是下方的&lt;b&gt;環形唇邊&lt;\/b&gt;」。這一小步還沒確認/);
});

test('optional sections accept confirmation but never count, and the header next step skips them', () => {
  const h = harness();
  h.curriculum = curriculumData();
  h.curriculum.chapters[0].sections.push({ id: '01-02', title: '加練', track: 'optional' });
  h.curriculum.chapters[0].steps.push({ id: 'ec01-opt', title: '選修練習', actions: ['做'], evidenceStatus: 'draft_pending_demo', section: '01-02', track: 'optional' });
  const html = section(h, 'ch01', '01-02');
  assert.match(html, /<span class="badge">選修<\/span>/);
  assert.match(html, /選修：可以照做並確認，但不計入主線進度/);
  assert.match(html, /data-engineering-step="ec01-opt"/);
  const shared = h.app.state.data;
  shared.progress.events.push({ type: 'engineering_step_confirmed', curriculumId: 'engineering-curriculum-v002', chapterId: 'ch01', stepId: 'ec01-01', author: 'learner' });
  const page = h.renderer.render(pathData(), shared, 'ch01', { data: h.curriculum });
  assert.match(page, /data-goto-chapter="ch02" data-goto-step="ec02-01">前往下一小步：02-01 規劃 · 試驗規劃/);
  assert.equal(h.renderer.nextStep(shared, { data: h.curriculum }).step.id, 'ec02-01');
  shared.progress.events.push({ type: 'engineering_step_confirmed', curriculumId: 'engineering-curriculum-v002', chapterId: 'ch02', stepId: 'ec02-01', author: 'learner' });
  assert.match(h.renderer.render(pathData(), shared, 'ch01', { data: h.curriculum }), /主線小步都已確認/);
});

test('new progress counts only unique learner confirmations of the current curriculum', () => {
  const { renderer } = harness();
  const data = curriculumData(), shared = bootstrapData();
  const event = { type: 'engineering_step_confirmed', author: 'learner', curriculumId: data.id, chapterId: 'ch01', stepId: 'ec01-01', evidence: '完成' };
  shared.progress.events.push(event, { ...event }, { ...event, author: 'tutor', chapterId: 'ch02', stepId: 'ec02-01' }, { ...event, curriculumId: 'old', chapterId: 'ch02', stepId: 'ec02-01' }, { ...event, stepId: 'wrong' }, { ...event, type: 'engineering_step_note', chapterId: 'ch02', stepId: 'ec02-01' });
  shared.progress.lessons['05'].completedSteps.push('05-05');
  const html = renderer.render(pathData(), shared, 'ch01', { data });
  assert.match(html, /1 \/ 2 個主線小步已確認 · revision 6/);
  assert.match(html, /<span class="badge">1 \/ 1 小步已確認<\/span>/);
  assert.match(html, /本章主線小步都已確認/);
});

test('section pagers move across chapters and the breadcrumb returns to the chapter page', () => {
  const h = harness();
  h.curriculum = curriculumData();
  const first = section(h, 'ch01', '01-01');
  assert.match(first, /data-section-chapter="ch02" data-open-section="02-01">02-01 →<\/button>/);
  assert.match(first, /data-engineering-chapter="ch01">回第 01 章<\/button>/);
  const last = section(h, 'ch02', '02-01');
  assert.match(last, /data-section-chapter="ch01" data-open-section="01-01">← 01-01<\/button>/);
  assert.match(h.renderer.render(pathData(), h.app.state.data, 'ch01', { data: h.curriculum }, { section: '09-99' }), /小節目錄/);
});

test('routes, step selection and tabs keep state in the app without writing progress', async () => {
  const h = harness({ hash: '#engineering/ch01/01-01' });
  assert.equal(h.app.state.engineering.section, '01-01');
  await h.app.loadEngineering();
  const before = JSON.stringify(h.app.state.data.progress);
  assert.match(h.app.renderEngineering(), /engineering-section-page/);
  h.listeners.click({ target: { closest: () => ({ disabled: false, dataset: { detailTab: 'notes' } }) } });
  assert.equal(h.app.state.engineering.tab, 'notes');
  assert.match(h.app.renderEngineering(), /data-detail-tab="notes" aria-selected="true"/);
  h.listeners.click({ target: { closest: () => ({ disabled: false, dataset: { gotoChapter: 'ch02', gotoStep: 'ec02-01' } }) } });
  assert.deepEqual([h.app.state.engineering.chapter, h.app.state.engineering.section, h.app.state.engineering.step], ['ch02', '02-01', 'ec02-01']);
  assert.equal(h.context.window.location.hash, '#engineering/ch02/02-01');
  h.listeners.click({ target: { closest: () => ({ disabled: false, dataset: { selectStep: 'ec02-01' } }) } });
  assert.equal(h.app.state.engineering.step, 'ec02-01');
  h.listeners.click({ target: { closest: () => ({ disabled: false, dataset: { sectionChapter: 'ch01', openSection: '01-01' } }) } });
  assert.deepEqual([h.app.state.engineering.chapter, h.app.state.engineering.section, h.app.state.engineering.step], ['ch01', '01-01', null]);
  h.app.selectEngineeringChapter('ch02');
  assert.equal(h.app.state.engineering.section, null);
  assert.equal(h.context.window.location.hash, '#engineering/ch02');
  assert.match(h.app.renderEngineering(), /小節目錄/);
  assert.equal(JSON.stringify(h.app.state.data.progress), before);
  assert.ok(h.requests.every((request) => request.method === 'GET'));
});

test('missing curriculum keeps the chapter page usable and supports explicit retry', async () => {
  let missing = true;
  const h = harness({ hash: '#engineering', fetchImpl: async (url) => {
    if (url === '/engineering-curriculum.json' && missing) return { ok: false, status: 404, json: async () => ({ error: '分步教材尚未提供' }) };
    return { ok: true, json: async () => url === '/api/bootstrap' ? bootstrapData() : url === '/engineering-curriculum.json' ? curriculumData() : pathData() };
  } });
  await h.app.loadEngineering();
  assert.match(h.app.renderEngineering(), /小盒與量測 ch01/);
  assert.match(h.app.renderEngineering(), /分步教材尚未提供/);
  assert.match(h.app.renderEngineering(), /data-action="retry-curriculum"/);
  await h.app.loadCurriculum();
  assert.equal(h.requests.filter((item) => item.url === '/engineering-curriculum.json').length, 1);
  missing = false;
  await h.app.loadCurriculum({ retry: true });
  assert.match(h.app.renderEngineering(), /data-open-section="01-01"/);
  assert.equal(h.requests.filter((item) => item.url === '/engineering-curriculum.json').length, 2);
});

test('curriculum rejects duplicate chapter IDs', () => {
  const { renderer } = harness();
  const data = curriculumData();
  assert.throws(() => renderer.validateCurriculum({ ...data, chapters: [data.chapters[0], data.chapters[0]] }), /章節編號/);
});

test('appendix entries stay on the chapter page supplement without forms and never count', () => {
  const { renderer } = harness();
  const data = curriculumData();
  data.chapters[0].steps.push({ id: 'ch01-trial-log', title: '假專案測試', actions: ['對照原圖'], evidenceStatus: 'existing_demo', figures: [], track: 'appendix' });
  data.chapters[0].appendix = { title: '附錄：測試紀錄', summary: '不需操作' };
  data.chapters[0].limitationHistory = ['v020 當時的限制'];
  const html = renderer.render(pathData(), bootstrapData(), 'ch01', { data });
  assert.match(html, /<details class="engineering-appendix"><summary>附錄：測試紀錄（1 項，不需操作、不計入進度）<\/summary>/);
  assert.match(html, /v020 當時的限制/);
  assert.doesNotMatch(html.slice(html.indexOf('engineering-appendix"')), /<form/);
  assert.match(html, /<span class="badge">0 \/ 1 小步已確認<\/span>/);
  assert.equal(renderer.learnerSteps(data.chapters[0]).map((step) => step.id).join(), 'ec01-01');
});

test('confirmation and stuck notes on the section page are explicit learner actions with their own IDs', async () => {
  const current = bootstrapData();
  const h = harness({ hash: '#engineering/ch01/01-01', fetchImpl: async (url, options) => {
    if (url === '/api/progress') {
      const payload = JSON.parse(options.body);
      assert.equal(payload.expectedRevision, current.progress.revision);
      current.progress.revision++;
      current.progress.events.push({ type: payload.action === 'engineering_confirm' ? 'engineering_step_confirmed' : 'engineering_step_note', curriculumId: 'engineering-curriculum-v002', author: 'learner', chapterId: payload.chapterId, stepId: payload.stepId,
        ...(payload.action === 'engineering_confirm' ? { evidence: payload.evidence } : { text: payload.note, noteKind: payload.noteKind }) });
      return { ok: true, json: async () => ({ progress: current.progress }) };
    }
    return { ok: true, json: async () => url === '/api/bootstrap' ? current : url === '/engineering-curriculum.json' ? curriculumData() : pathData() };
  } });
  h.app.state.data = current;
  await h.app.loadEngineering();
  await h.app.saveEngineeringRecord('confirm', 'ch01', 'wrong-id', '已完成');
  await h.app.saveEngineeringRecord('confirm', 'ch02', 'ec02-01', '已完成');
  await h.app.saveEngineeringRecord('confirm', 'ch01', 'ec01-01', '  ');
  await h.app.saveEngineeringRecord('confirm', 'ch01', 'ec01-01', '看到唇邊');
  await h.app.saveEngineeringRecord('confirm', 'ch01', 'ec01-01', '看到唇邊');
  await h.app.saveEngineeringRecord('note', 'ch01', 'ec01-01', '  卡住 <script>\n下一行  ');
  const posts = h.requests.filter((request) => request.method === 'POST');
  assert.equal(posts.length, 2);
  assert.deepEqual(posts[0].body, { action: 'engineering_confirm', chapterId: 'ch01', stepId: 'ec01-01', expectedRevision: 6, evidence: '看到唇邊' });
  assert.deepEqual(posts[1].body, { action: 'engineering_note', chapterId: 'ch01', stepId: 'ec01-01', expectedRevision: 7, note: '  卡住 <script>\n下一行  ', noteKind: 'stuck' });
  assert.deepEqual(current.progress.lessons['01'].completedSteps, []);
  h.app.state.engineering.step = 'ec01-01';
  const html = h.app.renderEngineering();
  assert.match(html, /已由學員確認這一小步/);
  assert.match(html, /卡關筆記（1）/);
  assert.match(html, /卡住 &lt;script&gt;/);
  assert.doesNotMatch(html, /卡住 <script>/);
});

test('pending steps are readable in their section but cannot be confirmed, never count and are skipped by next step', () => {
  const h = harness();
  h.curriculum = curriculumData();
  const chapter = h.curriculum.chapters[0];
  chapter.detailNote = '本章詳細步驟尚未逐步重新實拍。';
  chapter.sections.push({ id: '01-02', title: '螺紋', track: 'pending' });
  chapter.steps.unshift({ id: 'ec01-pend', title: '還不能做', actions: ['等待示範'], evidenceStatus: 'draft_pending_demo', section: '01-01', track: 'pending' });
  chapter.steps.push({ id: 'ec01-pend2', title: '試鎖', actions: ['旋入'], evidenceStatus: 'draft_pending_demo', section: '01-02', track: 'pending' });
  let html = section(h);
  assert.match(html, /<li class="engineering-step-row selected" data-curriculum-step="ec01-01">/);
  assert.match(html, /data-select-step="ec01-pend"><span class="step-mark">1<\/span>還不能做 <em>待製作<\/em><\/button>/);
  assert.match(html, /本節 0 \/ 1 已確認/);
  assert.match(html, /<p class="engineering-caption">本章詳細步驟尚未逐步重新實拍。<\/p>/);
  html = section(h, 'ch01', '01-01', { step: 'ec01-pend', tab: 'notes' });
  assert.match(html, /<strong>待製作：<\/strong>這一步需要的模型或示範還沒完成/);
  assert.doesNotMatch(html.slice(html.indexOf('engineering-step-current'), html.indexOf('engineering-detail')), /<form/);
  html = section(h, 'ch01', '01-02');
  assert.match(html, /<span class="badge">待製作<\/span><span class="badge">本節 0 \/ 0 已確認<\/span>/);
  assert.doesNotMatch(html, /<em>待製作<\/em>|data-form=/);
  const page = h.renderer.render(pathData(), h.app.state.data, 'ch01', { data: h.curriculum });
  assert.match(page, /0 \/ 2 個主線小步已確認（另有待製作 2 步，不計入）/);
  assert.match(page, /<span>01-02<\/span><span>螺紋 <em>待製作<\/em><\/span><small>—<\/small>/);
  assert.equal(h.renderer.nextStep(h.app.state.data, { data: h.curriculum }).step.id, 'ec01-01');
});

test('demonstration record tab uses the full original record from the app, including highlight boxes and review tables', async () => {
  const h = harness({ hash: '#engineering/ch01/01-01' });
  const original = h.app.state.data.catalog.lessons[1].steps[0];
  original.parameterPlan = { stage: 'parameter_planning_only', parameters: [{ symbol: 'C', label: '總間隙', definition: '蓋與盒之間', value: null }] };
  original.operationRun = { performedBy: 'tutor', status: 'completed', events: [{ seq: 1, action: '點 File', observed: '選單展開', observedKind: 'readback',
    figure: { type: 'screenshot', path: 'learning/evidence/05/run/01.png', caption: '原圖一', width: 100, height: 50, highlights: [{ x: 10, y: 5, w: 20, h: 10, label: 'File' }] } }] };
  await h.app.loadEngineering();
  h.app.state.engineering.tab = 'record';
  const html = h.app.renderEngineering();
  assert.match(html, /原教材 05-05 的助教示範紀錄<\/h5>/);
  assert.match(html, /C · 總間隙<\/strong><small>蓋與盒之間<\/small><\/th><td>待定<\/td>/);
  assert.match(html, /<span class="figure-highlight" data-left="10" data-top="10" data-width="20" data-height="20"><span class="figure-highlight-label">File<\/span><\/span>/);
  assert.match(html, /狀態讀回值<\/strong> 選單展開/);
  h.app.state.engineering.tab = 'notes';
  assert.doesNotMatch(h.app.renderEngineering(), /另有參數表、幾何或審查紀錄/);
});

test('resume and the versions page work without the original-lesson sidebar', async () => {
  const h = harness({ hash: '#versions' });
  await h.app.loadEngineering();
  h.app.render();
  let html = h.elements.get('view-content').innerHTML;
  assert.match(html, /data-version-lesson="01" aria-pressed="true">01<\/button><button type="button" class="button quiet small" data-version-lesson="05" aria-pressed="false">05<\/button>/);
  h.listeners.click({ target: { closest: () => ({ disabled: false, dataset: { versionLesson: '05' } }) } });
  assert.equal(h.app.state.lesson, '05');
  assert.equal(h.app.state.view, 'versions');
  assert.match(h.elements.get('view-content').innerHTML, /<h3>單元 05 · 登記檔案<\/h3>/);
  h.listeners.click({ target: { closest: () => ({ disabled: false, dataset: { action: 'resume' } }) } });
  assert.deepEqual([h.app.state.view, h.app.state.engineering.chapter, h.app.state.engineering.section, h.app.state.engineering.step], ['engineering', 'ch01', '01-01', 'ec01-01']);
  assert.ok(h.requests.every((request) => request.method === 'GET'));
});

test('every chapter page links to the shared challenge page, chapter 03 included', () => {
  const { renderer } = harness();
  const data = pathData();
  data.chapters.push({ ...data.chapters[0], id: 'ch03', number: '03' });
  const html = renderer.render(data, bootstrapData(), 'ch03', { data: curriculumData() });
  assert.match(html, /href="\/challenges\/index.html\?chapter=ch03"/);
  assert.doesNotMatch(html, /pilot\/box-lesson|data-action="resume"|查閱原教材/);
});
