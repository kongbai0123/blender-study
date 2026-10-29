(() => {
  'use strict';
  const state = { data: null, lesson: null, view: 'engineering', browsed: new Map(), drafts: new Map(), busy: false, loading: false, signature: '', notice: null, engineering: { data: null, loading: false, attempted: false, error: '', chapter: 'ch01', section: null, step: null, tab: 'detail', curriculum: { data: null, loading: false, attempted: false, error: '' } } };
  const $ = (id) => document.getElementById(id);
  const e = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const text = (value) => Array.isArray(value) ? value.map(text).join('\n') : value && typeof value === 'object' ? Object.values(value).map(text).join('\n') : String(value ?? '');
  const lessons = () => state.data?.catalog.lessons || [];
  const lessonById = (id) => lessons().find((item) => item.id === id);
  const lp = (id) => state.data?.progress.lessons[id] || { completedSteps: [], notes: [] };
  const completed = (id) => lp(id).completedSteps || [];
  const currentLesson = () => lessonById(state.lesson);
  const selectedStep = (lesson = currentLesson()) => (lesson?.steps || []).find((step) => step.id === state.browsed.get(lesson.id)) || (lesson?.steps || []).find((step) => step.id === lp(lesson.id).currentStep) || lesson?.steps?.[0];
  const fileUrl = (path, read = false) => `${read ? '/read/' : '/files/'}${String(path || '').replace(/\\/g, '/').split('/').filter(Boolean).map(encodeURIComponent).join('/')}`;
  const externalUrl = (value) => /^https:\/\//i.test(String(value || '')) ? e(value) : '#';
  const field = (key, fallback = '') => state.drafts.has(key) ? state.drafts.get(key) : fallback;
  const keyFor = (name, lesson = state.lesson, step = selectedStep()?.id || '') => `${lesson}:${name}${['evidence', 'checked', 'screen'].includes(name) ? ':' + step : ''}`;
  const valueAttr = (key, fallback = '') => e(field(key, fallback));
  const roleName = (role) => ({ source_scene: '場景 .blend', render: '渲染圖', export: '列印／其他輸出' }[role] || role || '檔案');
  // 第 07～08 章的工程工作區不屬於原單元；登記時送 workspaceId，不送 lessonId。
  const ENGINEERING_WORKSPACE = 'engineering-parametric';
  const statusName = (status) => ({ in_progress: '學習中', not_started: '尚未開始', completed: '已完成' }[status] || '尚未開始');
  const badge = (status) => `<span class="badge ${status === 'completed' ? 'done' : status === 'in_progress' ? 'active' : ''}">${e(statusName(status))}</span>`;
  const date = (value) => { if (!value) return '尚未記錄'; const d = new Date(value); return Number.isNaN(d.valueOf()) ? String(value) : new Intl.DateTimeFormat('zh-TW', { timeZone: 'Asia/Taipei', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).format(d); };
  const bytes = (n) => Number(n || 0) < 1024 ? `${Number(n || 0)} B` : Number(n) < 1048576 ? `${(Number(n) / 1024).toFixed(1)} KB` : `${(Number(n) / 1048576).toFixed(1)} MB`;
  const workspaceAbsolute = (lesson = currentLesson()) => `${String(state.data?.projectRoot || '').replace(/[\\/]$/, '')}\\${String(lp(lesson.id).workspace || `learning/workspaces/${lesson.id}`).replace(/\//g, '\\')}`;
  const stepIndex = (lesson, step) => lesson.steps.findIndex((item) => item.id === step?.id);
  const authorName = (author) => ({ learner: '學員', tutor: '助教' }[author] || '未標示作者');
  // 伺服器標出記在原教材筆記裡的工程路徑回答／標記；它們不算該單元的筆記。
  const legacyNotes = (lessonId) => new Map((state.data?.legacyEngineeringNotes || []).filter((item) => item?.lessonId === lessonId)
    .map((item) => [lp(lessonId).notes?.[item.noteIndex], item.role]).filter(([note]) => note && typeof note === 'object'));
  const lessonNotes = (lessonId) => { const legacy = legacyNotes(lessonId); return (lp(lessonId).notes || []).filter((note) => !legacy.has(note)); };
  const interfaceName = (value) => ({ en: 'English', 'zh-Hant': '繁體中文' }[value] || '尚未記錄');
  const stepOrder = (id) => lessons().flatMap((lesson) => lesson.steps.map((item) => item.id)).indexOf(id);
  const languageStep = () => lessons().flatMap((lesson) => lesson.steps).find((item) => item.setsLearner?.interfaceLanguage === 'en');
  // 步驟說明以英文介面名稱撰寫；介面尚未記錄為英文時，切換步驟之後的步驟需提示。
  const needsEnglishHint = (step) => { const target = languageStep(); return Boolean(target) && state.data?.progress.learner?.interfaceLanguage !== 'en' && stepOrder(step?.id) > stepOrder(target.id); };

  function notify(message, type = 'success') {
    const box = $('notice'); box.replaceChildren(); box.className = `notice ${type}`;
    const span = document.createElement('span'); span.textContent = message;
    const close = document.createElement('button'); close.type = 'button'; close.setAttribute('aria-label', '關閉通知'); close.textContent = '×'; close.addEventListener('click', () => { box.hidden = true; });
    box.append(span, close); box.hidden = false;
  }

  async function request(url, options = {}) {
    const response = await fetch(url, { cache: 'no-store', ...options, headers: { 'Content-Type': 'application/json', ...(options.headers || {}) } });
    let data; try { data = await response.json(); } catch { data = {}; }
    if (!response.ok) { const error = new Error(data.error || data.message || `本機服務回應錯誤（${response.status}）。`); error.status = response.status; error.data = data; throw error; }
    return data;
  }

  function preserveDrafts() {
    document.querySelectorAll('[data-draft]').forEach((element) => {
      if (element.type === 'radio') { if (element.checked) state.drafts.set(element.dataset.draft, element.value); }
      else state.drafts.set(element.dataset.draft, element.type === 'checkbox' ? element.checked : element.value);
    });
  }

  function render() {
    if (!state.data) return;
    document.body?.classList.toggle('engineering-view', state.view === 'engineering');
    preserveDrafts();
    const openCurriculumSteps = new Set([...document.querySelectorAll('details.engineering-curriculum-step[open]')].map((element) => element.dataset.curriculumStep));
    const focused = document.activeElement;
    const focusKey = focused?.dataset.draft;
    const selection = focusKey && typeof focused.selectionStart === 'number' ? [focused.selectionStart, focused.selectionEnd] : null;
    renderSidebar();
    document.querySelectorAll('[data-view]').forEach((button) => { if (button.dataset.view === state.view) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current'); });
    $('view-content').innerHTML = state.view === 'engineering' ? renderEngineering() : state.view === 'journal' ? renderJournal() : state.view === 'versions' ? renderVersions() : renderLesson();
    document.querySelectorAll('details.engineering-curriculum-step').forEach((element) => { if (openCurriculumSteps.has(element.dataset.curriculumStep)) element.open = true; });
    placeHighlights();
    $('view-content').setAttribute('aria-busy', 'false');
    $('revision-label').textContent = `revision ${state.data.progress.revision} · ${date(state.data.progress.updatedAt)}`;
    $('connection-status').textContent = '本機共用進度 · 每 5 秒同步';
    updateFormAvailability();
    if (focusKey) {
      const replacement = [...document.querySelectorAll('[data-draft]')].find((element) => element.dataset.draft === focusKey && (element.type !== 'radio' || element.value === focused.value));
      if (replacement) { replacement.focus({ preventScroll: true }); if (selection && replacement.setSelectionRange) replacement.setSelectionRange(...selection); }
    }
  }

  function renderEngineering() {
    const module = globalThis.BlenderEngineeringPath;
    if (!module) return '<section class="empty-state"><h2>工程學習路徑模組尚未載入</h2><p>請重新整理頁面；共用進度沒有變動。</p></section>';
    if (!state.engineering.data) return module.renderError(state.engineering.error, state.engineering.loading || !state.engineering.attempted);
    const route = state.engineering;
    try { return module.render(route.data, state.data, route.chapter, route.curriculum, { drafts: state.drafts, busy: state.busy, section: route.section, step: route.step, tab: route.tab, sourceRecord: renderSourceRecord }); }
    catch (error) { return module.renderError(error.message); }
  }

  async function loadEngineering({ retry = false } = {}) {
    const route = state.engineering;
    if (route.loading || (route.attempted && !retry)) return;
    route.attempted = true; route.loading = true; route.error = '';
    if (state.data && state.view === 'engineering') render();
    try {
      if (!globalThis.BlenderEngineeringPath) throw new Error('工程學習路徑模組尚未載入，請重新整理頁面。');
      const data = await request('/engineering-path.json');
      route.data = globalThis.BlenderEngineeringPath.validate(data);
    } catch (error) { route.error = error.message; route.data = null; }
    finally { route.loading = false; if (state.data) render(); }
    if (route.data) await loadCurriculum();
  }

  async function loadCurriculum({ retry = false } = {}) {
    const curriculum = state.engineering.curriculum;
    if (curriculum.loading || (curriculum.attempted && !retry)) return;
    curriculum.attempted = true; curriculum.loading = true; curriculum.error = '';
    if (state.data && state.view === 'engineering') render();
    try {
      const data = await request('/engineering-curriculum.json');
      curriculum.data = globalThis.BlenderEngineeringPath.validateCurriculum(data);
      // A bare entry URL resumes at the first chapter with an unconfirmed new step.
      // Explicit chapter links and all historical confirmations remain untouched.
      if (state.view === 'engineering' && !window.location?.hash) {
        const events = state.data?.progress?.events || [];
        const done = new Set(events.filter((event) => event?.type === 'engineering_step_confirmed' && event.author === 'learner' && event.curriculumId === data.id).map((event) => `${event.chapterId}:${event.stepId}`));
        const next = data.chapters.find((chapter) => globalThis.BlenderEngineeringPath.learnerSteps(chapter).some((step) => !done.has(`${chapter.id}:${step.id}`)));
        if (next && state.engineering.data?.chapters.some((chapter) => chapter.id === next.id)) state.engineering.chapter = next.id;
      }
    } catch (error) { curriculum.error = error.message; curriculum.data = null; }
    finally { curriculum.loading = false; if (state.data) render(); }
  }

  function setViewHash() {
    if (!window.location || !window.history?.replaceState) return;
    const route = state.engineering;
    const hash = state.view === 'engineering' ? `#engineering/${route.chapter}${route.section ? '/' + route.section : ''}` : `#${state.view}`;
    window.history.replaceState(null, '', window.location.pathname + window.location.search + hash);
  }

  // 網址：#engineering/ch03 是章節頁，#engineering/ch03/03-08 是小節頁。
  function applyViewHash({ initial = false } = {}) {
    const hash = window.location?.hash || '';
    const engineering = /^#engineering(?:\/(ch\d{2})(?:\/(\d{2}-\d{2}))?)?$/.exec(hash);
    const ordinary = /^#(lesson|journal|versions)$/.exec(hash);
    if (!engineering && !ordinary) return;
    if (!initial) preserveDrafts();
    state.view = engineering ? 'engineering' : ordinary[1];
    if (engineering) Object.assign(state.engineering, { chapter: engineering[1] || 'ch01', section: engineering[2] || null, step: null });
    if (!initial && state.data) {
      render();
      if (engineering && !state.engineering.attempted) void loadEngineering();
    }
  }

  // 換頁（章節頁或小節頁）都回到頁首。
  function showEngineeringPage(changes, focusId) {
    preserveDrafts(); Object.assign(state.engineering, changes); state.view = 'engineering'; setViewHash(); render();
    window.scrollTo?.(0, 0);
    $(focusId)?.focus({ preventScroll: true });
  }

  function selectEngineeringChapter(id) {
    if (!state.engineering.data?.chapters.some((chapter) => chapter.id === id)) return;
    showEngineeringPage({ chapter: id, section: null, step: null }, 'engineering-chapter-title');
  }

  function openSection(chapterId, sectionId, stepId = null) {
    if (!state.engineering.data?.chapters.some((chapter) => chapter.id === chapterId)) return;
    showEngineeringPage({ chapter: chapterId, section: sectionId, step: stepId }, 'engineering-section-title');
  }

  // 小步屬於某一節就開那一節並選取它；附錄等沒有節的項目開章節頁。
  function gotoCurriculumStep(chapterId, stepId) {
    const step = state.engineering.curriculum.data?.chapters.find((chapter) => chapter.id === chapterId)?.steps.find((item) => item.id === stepId);
    if (step?.section) openSection(chapterId, step.section, stepId);
    else selectEngineeringChapter(chapterId);
  }

  function selectCurriculumStep(stepId) {
    if (state.view !== 'engineering' || !state.engineering.section) return;
    preserveDrafts(); state.engineering.step = stepId; render();
  }

  function selectDetailTab(tab) {
    preserveDrafts(); state.engineering.tab = tab; render();
  }

  function openEngineeringReference(lessonId, stepId) {
    if (state.busy || !globalThis.BlenderEngineeringPath?.findReference(state.data, lessonId, stepId)) return;
    preserveDrafts(); state.lesson = lessonId; state.browsed.set(lessonId, stepId); state.view = 'lesson'; setViewHash(); render();
    $('step-title')?.focus({ preventScroll: true });
  }

  function renderSidebar() {
    const chapters = state.engineering.data?.chapters || [];
    const curriculum = state.engineering.curriculum.data;
    const events = state.data?.progress?.events || [];
    const confirmedIds = new Set(events.filter((event) => event?.type === 'engineering_step_confirmed' && event.author === 'learner' && event.curriculumId === curriculum?.id).map((event) => `${event.chapterId}:${event.stepId}`));
    let newTotal = 0, newDone = 0;
    $('engineering-chapter-count').textContent = chapters.length || '—';
    $('engineering-list').innerHTML = chapters.length ? chapters.map((chapter) => {
      const teaching = curriculum?.chapters.find((item) => item.id === chapter.id);
      const steps = teaching && globalThis.BlenderEngineeringPath ? globalThis.BlenderEngineeringPath.learnerSteps(teaching) : [];
      const done = steps.filter((step) => confirmedIds.has(`${chapter.id}:${step.id}`)).length;
      newTotal += steps.length; newDone += done;
      const selected = state.view === 'engineering' && chapter.id === state.engineering.chapter;
      // 目前這章展開到「節」：主章節 → 次章節，點節直接捲到該節。
      const sections = selected && Array.isArray(teaching?.sections) ? teaching.sections : [];
      const sectionList = sections.length ? `<div class="section-nav">${sections.map((section) => { const own = (teaching.steps || []).filter((step) => step.section === section.id && !step.track?.match(/^(appendix|pending|reference)$/)); const sectionDone = own.filter((step) => confirmedIds.has(`${chapter.id}:${step.id}`)).length; const current = section.id === state.engineering.section; return `<button type="button" class="${current ? 'current' : ''}" data-section-chapter="${e(chapter.id)}" data-open-section="${e(section.id)}"${current ? ' aria-current="page"' : ''}><span>${e(section.id)}</span><span>${e(section.title)}${globalThis.BlenderEngineeringPath?.TRACK_LABELS?.[section.track] ? `（${e(section.pendingLabel || globalThis.BlenderEngineeringPath.TRACK_LABELS[section.track])}）` : ''}</span><small>${own.length ? `${sectionDone}/${own.length}` : '—'}</small></button>`; }).join('')}</div>` : '';
      return `<button class="primary-chapter-button${selected ? ' selected' : ''}" type="button" data-engineering-chapter="${e(chapter.id)}"${selected ? ' aria-current="page"' : ''}><span class="chapter-number">${e(chapter.number || chapter.id.slice(2))}</span><span><strong>${e(chapter.title)}</strong><small>${teaching ? (steps.length ? `${done} / ${steps.length} 小步已確認` : e(chapter.availabilityLabel || '不計入主線進度')) : '章節內容讀取中'}</small></span></button>${sectionList}`;
    }).join('') : `<p class="sidebar-loading">${state.engineering.error ? '新版章節暫時無法讀取；請在主頁重新讀取。' : '正在載入新版章節…'}</p>`;
    $('engineering-sidebar-progress').textContent = curriculum ? `${newDone} / ${newTotal} 小步已確認` : '新版完成數讀取中…';
  }

  function renderLesson() {
    const lesson = currentLesson(); const step = selectedStep(lesson);
    if (!lesson || !step) return '<section class="empty-state"><h2>找不到課程步驟</h2><button type="button" class="button" data-action="refresh">重新讀取</button></section>';
    return `<nav class="mobile-jump" aria-label="本步快速操作"><button type="button" data-jump="step-title">操作步驟</button><button type="button" data-jump="confirm-panel">新版小步</button><button type="button" data-jump="note-panel">筆記</button></nav><header class="lesson-heading"><div class="heading-meta"><span class="eyebrow">原教材 · 單元 ${e(lesson.id)} / ${lessons().length}</span><span class="badge">只供查閱</span><span class="badge">Blender 介面：${e(interfaceName(state.data.progress.learner?.interfaceLanguage))}</span></div><h2>${e(lesson.title)}</h2><p>${e(lesson.goal)}</p></header><div class="session-banner"><div><strong>原教材只供查閱</strong><p>這裡保留原步驟的圖文與助教示範紀錄；學習進度以新版小步為準。</p></div><button type="button" class="button small" data-view="engineering">回到新版教學</button></div><div class="content-grid"><div class="primary-column">${renderStep(lesson, step)}${renderSource(lesson)}</div><aside class="secondary-column" aria-label="新版小步、筆記與版本"><section class="panel goal-panel"><h3>這一步的內容</h3><p>${e(step.title)}</p><p class="form-hint">每回合只做畫面中的 1–3 個操作。畫面不同時，到新版小步留下卡關筆記。</p></section>${renderNewPathPointer(step)}${renderNote(lesson)}${renderWorkspace(lesson)}${renderVersionPanel(lesson)}<section class="panel resume-panel"><h3>回到聊天接續</h3><p>複製新版下一小步與 revision，貼到這個聊天。助教依專案中的共用進度接續。</p><button type="button" class="button" data-action="copy-resume">複製接續聊天訊息</button></section></aside></div>`;
  }

  // 標示框座標以原圖像素存在 catalog；網頁只疊框與文字，不修改原圖。CSP 不允許 style 屬性，位置在 placeHighlights() 設定。
  function highlightMarks(figure) {
    const width = Number(figure.width); const height = Number(figure.height);
    if (!Array.isArray(figure.highlights) || !(width > 0) || !(height > 0)) return '';
    return figure.highlights.map((mark, i) => {
      const box = ['x', 'y', 'w', 'h'].map((key) => Number(mark?.[key]));
      if (box.some((value) => !Number.isFinite(value))) return '';
      const [left, top, w, h] = [100 * box[0] / width, 100 * box[1] / height, 100 * box[2] / width, 100 * box[3] / height];
      // 靠近上緣時標籤放不下：大框放框內左上角，小框（如選單按鈕）放框下方。
      const place = `${top < 5 ? (h > 8 ? ' inside' : ' below') : ''}${left > 70 ? ' align-right' : ''}`;
      return `<span class="figure-highlight${place}" data-left="${left}" data-top="${top}" data-width="${w}" data-height="${h}"><span class="figure-highlight-label">${e(mark.label || i + 1)}</span></span>`;
    }).join('');
  }

  function placeHighlights() {
    document.querySelectorAll('.figure-highlight').forEach((mark) => {
      for (const side of ['left', 'top', 'width', 'height']) mark.style[side] = `${mark.dataset[side]}%`;
    });
  }

  function observationLabel(kind) {
    switch (kind) {
      case 'scripted_description': return '文字描述，請對照原圖';
      case 'readback': return '狀態讀回值';
      case 'mixed': return '混合紀錄：文字描述與讀回值';
      default: return '觀察紀錄';
    }
  }

  function renderWorkspaceEvidence(run) {
    if (!Object.prototype.hasOwnProperty.call(run, 'workspaceContentsUnchanged') && !run.workspaceEvidenceNote) return '';
    const note = typeof run.workspaceEvidenceNote === 'string' ? run.workspaceEvidenceNote.trim() : '';
    const result = run.workspaceContentsUnchanged === true ? '一致' : run.workspaceContentsUnchanged === false ? '不同' : '未知';
    const comparison = run.workspaceContentsUnchanged === true ? '前後快照內容一致；此比對不能證明期間未曾寫入，也不能判定寫入者。' : run.workspaceContentsUnchanged === false ? '前後快照內容不同；此比對不能判定寫入者。' : '無法由既有證據判定前後內容是否一致。';
    return `<p class="operation-run-context"><strong>工作區內容核對</strong> ${note ? `${e(result)}。${e(note)}` : e(comparison)}</p>`;
  }

  function renderOperationRun(run) {
    if (!run || run.performedBy !== 'tutor' || !Array.isArray(run.events) || !run.events.length) return '';
    const events = run.events.map((event, index) => {
      const figure = event.figure;
      const screenshot = figure?.type === 'screenshot' && String(figure.path || '').startsWith('learning/evidence/') && /\.(png|jpe?g|webp)$/i.test(String(figure.path || ''));
      const alt = figure?.alt || 'Blender 助教操作後的實際截圖';
      const evidence = screenshot ? `<details class="operation-evidence" open><summary>本次操作後的實拍</summary><figure class="figure"><a class="figure-image-link" href="${fileUrl(figure.path)}" target="_blank" rel="noopener" aria-label="${e('查看完整原始截圖：' + alt)}"><img src="${fileUrl(figure.path)}" alt="${e(alt)}" loading="lazy">${highlightMarks(figure)}</a><figcaption><span class="figure-kind">實際截圖</span>${e(figure.caption || '')}<span class="figure-open">點圖查看完整原圖（不含標示框）</span></figcaption></figure></details>` : '';
      return `<li class="operation-event"><div class="operation-event-meta"><span class="operation-sequence">操作 ${e(event.seq || index + 1)}</span>${event.at ? `<time datetime="${e(event.at)}">${e(date(event.at))}</time>` : ''}</div><p class="operation-action">${e(event.action || '')}</p>${event.observed ? `<p class="operation-observed"><strong>${e(observationLabel(event.observedKind))}</strong> ${e(event.observed)}</p>` : ''}${event.note ? `<p class="operation-note">${e(event.note)}</p>` : ''}${evidence}</li>`;
    }).join('');
    const journal = String(run.journal || '').startsWith('learning/journal/') && /\.md$/i.test(String(run.journal || '')) ? `<a href="${fileUrl(run.journal)}" target="_blank" rel="noopener">開啟完整操作紀錄</a>` : '';
    const outputs = (Array.isArray(run.outputFiles) ? run.outputFiles : []).filter((item) => String(item.path || '').startsWith('learning/evidence/') && /\.(stl|blend)$/i.test(String(item.path || '')));
    const outputCaption = outputs.every((item) => /\.stl$/i.test(item.path)) ? '本次助教匯出檔案 · STL 座標按毫米解讀' : '本次助教場景檔案與來源版本';
    const outputTable = outputs.length ? `<div class="version-table-wrap"><table class="version-table"><caption>${e(outputCaption)}</caption><thead><tr><th scope="col">檔案與數位尺寸</th><th scope="col">來源版本與內容指紋</th></tr></thead><tbody>${outputs.map((item) => `<tr><td><a href="${fileUrl(item.path)}" download>${e(item.path.split('/').pop())}</a><small>${e(item.dimensionsLabel || (Array.isArray(item.dimensionsMm) ? item.dimensionsMm.join(' × ') + ' mm' : ''))} · ${e(bytes(item.bytes))}</small><code title="${e(item.sha256)}">${e(String(item.sha256 || '').slice(0,16))}</code></td><td>${e(String(item.sourcePath || '').split('/').pop())}<small>來源 SHA-256</small><code title="${e(item.sourceSha256)}">${e(String(item.sourceSha256 || '').slice(0,16))}</code></td></tr>`).join('')}</tbody></table><p class="caption">這是助教示範輸出；尚未切片、列印或試配，沒有合格間隙判定。</p></div>` : '';
    return `<section class="operation-run" aria-label="助教實際操作紀錄"><div class="operation-run-heading"><h4>助教實際操作紀錄</h4><span class="operation-run-status">${run.status === 'completed' ? '本次操作已執行完成' : '依序執行中'}</span></div><p class="operation-run-context">這裡分別標示助教的文字描述、狀態讀回值或混合紀錄；未分類時只標示觀察紀錄。原始截圖與紀錄供核對，不能代替學員確認、幾何檢查或實體合格證據。</p>${run.summary ? `<p class="operation-run-summary">${e(run.summary)}</p>` : ''}${renderWorkspaceEvidence(run)}${outputTable}<ol class="operation-events">${events}</ol>${journal ? `<p class="operation-run-journal">${journal}</p>` : ''}</section>`;
  }

  function renderPreviousOperationRuns(runs) {
    return (Array.isArray(runs) ? runs : []).filter((run) => run && typeof run.id === 'string' && Array.isArray(run.events)).map((run) => `<details class="operation-history"><summary>先前助教示範（${e(run.events.length)} 筆操作）</summary>${renderOperationRun(run)}</details>`).join('');
  }

  function renderParameterPlan(plan) {
    if (!plan || plan.stage !== 'parameter_planning_only' || !Array.isArray(plan.parameters)) return '';
    const value = (row) => row.value === null || row.value === undefined ? '待定' : `${row.value}${row.unit ? ' ' + row.unit : ''}`;
    const rows = plan.parameters.map((row) => `<tr><th scope="row"><strong>${e(row.symbol)} · ${e(row.label)}</strong><small>${e(row.definition)}</small></th><td>${e(value(row))}</td></tr>`).join('');
    const materials = (Array.isArray(plan.material_parameters) ? plan.material_parameters : []).map((row) => `<li><strong>${e(row.label)}</strong>：${e(value(row))}</li>`).join('');
    const conditions = (Array.isArray(plan.conditions) ? plan.conditions : []).map((item) => `<li>${e(item)}</li>`).join('');
    const sources = (Array.isArray(plan.references) ? plan.references : []).map((item) => `<li><a href="${externalUrl(item.url)}" target="_blank" rel="noopener">${e(item.label)}</a>${item.location ? ` · ${e(item.location)}` : ''}</li>`).join('');
    const record = String(plan.recordPath || '').startsWith('learning/evidence/') && /\.json$/i.test(plan.recordPath) ? `<p class="caption"><a href="${fileUrl(plan.recordPath)}" target="_blank" rel="noopener">開啟參數紀錄 v001（JSON）</a>${plan.recordSha256 ? ` · SHA-256 ${e(String(plan.recordSha256).slice(0,16))}` : ''}</p>` : '';
    return `<section class="parameter-plan" aria-label="懸臂卡扣參數與估算條件"><h4>參數與估算條件 · 規劃版</h4><p>${e(plan.reference_box_summary || '')}</p><div class="parameter-formula"><strong>模型公式，尚未代入</strong><code>${e(plan.formula?.expression || '')}</code><p>${e(plan.formula?.notation_note || '')}</p><strong>允許撓度／裝拆力／強度判定：待定，尚未計算</strong></div><details open><summary>尺寸參數定義（${plan.parameters.length} 項）</summary><table class="parameter-table"><thead><tr><th scope="col">參數與定義</th><th scope="col">目前值</th></tr></thead><tbody>${rows}</tbody></table></details><h4>材料與允許應變</h4><ul>${materials}</ul><details><summary>估算前要核對的條件</summary><ul>${conditions}</ul></details><details><summary>已核對的公式來源</summary><ul>${sources}</ul></details>${record}<p class="caption">尚未建立卡扣；盒體壁厚不直接作為臂厚。列印、試配、強度及配合合格結果均留空。</p></section>`;
  }

  function renderGeometryDraft(plan) {
    if (!plan || plan.stage !== 'experimental_geometry_only' || !Array.isArray(plan.parameters)) return '';
    const rows = plan.parameters.map((row) => `<tr><th scope="row"><strong>${e(row.label)}${row.unit ? `（${e(row.unit)}）` : ''}</strong><small>${e(row.note || '')}</small></th><td>${row.value === null || row.value === undefined ? '待定' : e(row.value)}</td></tr>`).join('');
    const limits = (Array.isArray(plan.limitations) ? plan.limitations : []).map((item) => `<li>${e(item)}</li>`).join('');
    const record = String(plan.recordPath || '').startsWith('learning/evidence/') && /\.json$/i.test(plan.recordPath) ? `<p class="caption"><a href="${fileUrl(plan.recordPath)}" target="_blank" rel="noopener">開啟幾何草案紀錄 v001（JSON）</a>${plan.recordSha256 ? ` · SHA-256 ${e(String(plan.recordSha256).slice(0,16))}` : ''}</p>` : '';
    return `<section class="parameter-plan" aria-label="懸臂卡扣幾何草案"><h4>幾何尺寸草案 · 尚未驗證材料與實體配合</h4><p>尺寸由助教選定，用於這次幾何示範。沿用原盒核心 60 × 40 × 30 mm；新卡扣向前突出，上蓋另做外側蓋裙及凸緣。</p><div class="parameter-formula"><strong>材料／允許應變：待定</strong><p>未計算允許撓度、裝拆力或強度。靜態間距及重疊量只描述目前模型，不能當作彈性裝入或配合合格結果。</p></div><details open><summary>草案參數（${plan.parameters.length} 項）</summary><table class="parameter-table"><thead><tr><th scope="col">幾何參數與定義</th><th scope="col">草案值</th></tr></thead><tbody>${rows}</tbody></table></details><details><summary>本次幾何範圍與未驗證條件</summary><ul>${limits}</ul></details>${record}<p class="caption">根部 Bevel 輸入 offset 與實際網格圓弧讀值分開記錄。實際列印、實測、試配及合格結果留空。</p></section>`;
  }

  function renderOrientationReview(review) {
    if (!review || review.stage !== 'orientation_and_overhang_draft') return '';
    const groups = (Array.isArray(review.comparisons) ? review.comparisons : []).map((part) => `<h4>${e(part.title)}</h4><p>${e(part.description || '')}</p><table class="orientation-table"><thead><tr><th scope="col">統計項目</th><th scope="col">原向</th><th scope="col">候選</th></tr></thead><tbody>${(Array.isArray(part.metrics) ? part.metrics : []).map((row) => `<tr><th scope="row">${e(row.label)}</th><td>${e(row.baseline ?? '待定')}</td><td>${e(row.candidate ?? '待定')}</td></tr>`).join('')}</tbody></table>`).join('');
    const notes = (Array.isArray(review.notes) ? review.notes : []).map((item) => `<li>${e(item)}</li>`).join('');
    const record = String(review.recordPath || '').startsWith('learning/evidence/') && /\.json$/i.test(review.recordPath) ? `<p class="caption"><a href="${fileUrl(review.recordPath)}" target="_blank" rel="noopener">開啟方向與Overhang紀錄 v001（JSON）</a>${review.recordSha256 ? ` · SHA-256 ${e(String(review.recordSha256).slice(0,16))}` : ''}</p>` : '';
    return `<section class="parameter-plan orientation-review" aria-label="列印方向與Overhang候選比較"><h4>列印方向與 Overhang · 候選比較</h4><p>${e(review.settingsSummary || '')}</p><div class="parameter-formula"><strong>材料／允許應變：待定</strong><p>最終方向、支撐及切片設定待核對。顏色與下方面積不代表需要支撐、免支撐或強度合格；床面接觸面也可能顯紅。</p></div><p class="caption">下表由實際 polygon 法線與面積另算；不是原生面板面數或GPU像素讀值。顯示值經四捨五入，完整精度與loop triangle統計見JSON。</p>${groups}<details><summary>方向理由、角度定義與待核對條件</summary><ul>${notes}</ul>${review.sourceUrl ? `<p><a href="${externalUrl(review.sourceUrl)}" target="_blank" rel="noopener">核對此Blender build的原生Overhang定義</a></p>` : ''}</details>${record}<p class="caption">只旋轉／平移既有幾何；未切片、列印、實測或試配。實體及合格結果留空。</p></section>`;
  }

  function renderStlReview(review) {
    if (!review || review.stage !== 'digital_stl_comparison_only') return '';
    const comparisons = (Array.isArray(review.comparisons) ? review.comparisons : []).map((part) => `<h4>${e(part.title)}</h4><table class="parameter-table"><thead><tr><th scope="col">核對項目</th><th scope="col">數位讀值</th></tr></thead><tbody>${(Array.isArray(part.metrics) ? part.metrics : []).map((row) => `<tr><th scope="row">${e(row.label)}</th><td>${e(row.value ?? '待定')}</td></tr>`).join('')}</tbody></table>`).join('');
    const recordLink = (path, label) => String(path || '').startsWith('learning/evidence/') && /\.json$/i.test(path) ? `<a href="${fileUrl(path)}" target="_blank" rel="noopener">${e(label)}</a>` : '';
    const record = recordLink(review.recordPath, '開啟STL版本與來源清單（JSON）');
    const physical = recordLink(review.physicalRecordPath, '開啟尚未填寫的列印／試配結果表（JSON）');
    return `<section class="parameter-plan stl-review" aria-label="STL匯出與數位尺寸核對"><h4>STL 數位核對 · 候選擺向</h4><p>${e(review.summary || '')}</p><div class="parameter-formula"><strong>材料／允許應變：待定</strong><p>列印方向與支撐仍為候選。實際列印、量測與試配結果留空，沒有強度或配合合格判定。</p></div>${comparisons}<p class="caption">STL沒有單位標記，本次座標以毫米解讀。來源世界外框由轉換後頂點取得；來源N面板Dimensions與未套用的物件旋轉分開記錄。完整精度見版本清單。</p>${record ? `<p class="caption">${record}${review.recordSha256 ? ` · SHA-256 ${e(String(review.recordSha256).slice(0,16))}` : ''}</p>` : ''}${physical ? `<p class="caption">${physical}</p>` : ''}<p class="caption">閉合網格與數位尺寸一致只屬檔案核對；未切片、列印或實體試配。</p></section>`;
  }

  function renderCouponReview(review) {
    if (!review || review.stage !== 'parameter_comparison_geometry_draft') return '';
    const variants = (Array.isArray(review.variants) ? review.variants : []);
    const value = (item) => e(item ?? '待定');
    const rows = variants.map((item) => `<tr><th scope="row">${e(item.name)}</th><td>${value(item.geometryLengthMm)}</td><td>${value(item.armHeightMm)}</td><td>${value(item.wholeHeightMm)}</td></tr>`).join('');
    const poses = variants.map((item) => `<tr><th scope="row">${e(item.name)}</th><td>${value(item.worldDimensionsLabel)}</td></tr>`).join('');
    const notes = (Array.isArray(review.notes) ? review.notes : []).map((item) => `<li>${e(item)}</li>`).join('');
    const recordLink = (path, label) => String(path || '').startsWith('learning/evidence/') && /\.json$/i.test(path) ? `<a href="${fileUrl(path)}" target="_blank" rel="noopener">${e(label)}</a>` : '';
    return `<section class="parameter-plan coupon-review" aria-label="卡扣單參數對照試片草案"><h4>臂長對照試片 · 幾何草案</h4><p>${e(review.summary || '')}</p><div class="parameter-formula"><strong>材料／允許應變：待定</strong><p>調整尚未驗證改善。方向與支撐仍為候選；列印、實測與試配結果留空，沒有強度或配合合格判定。</p></div><p>${e(review.heldGeometrySummary || '')}</p><table class="coupon-table"><caption>原建模軸的幾何尺寸（mm）</caption><thead><tr><th scope="col">試片</th><th scope="col">幾何L</th><th scope="col">全臂高</th><th scope="col">整件高</th></tr></thead><tbody>${rows}</tbody></table><p class="caption">幾何L是根平面至承接面；全臂高量到最上端，整件高另包含錨座。三者不同，尚未求力學有效長度。</p><h4>候選擺向的世界外框</h4><table class="parameter-table"><thead><tr><th scope="col">試片</th><th scope="col">世界XYZ（mm）</th></tr></thead><tbody>${poses}</tbody></table><p>${e(review.boundarySummary || '')}</p><details><summary>固定幾何、落床與待定條件</summary><ul>${notes}</ul></details><p class="caption">${recordLink(review.recordPath, '開啟試片幾何與來源紀錄（JSON）')}${review.recordSha256 ? ` · SHA-256 ${e(String(review.recordSha256).slice(0,16))}` : ''}</p><p class="caption">${recordLink(review.physicalRecordPath, '開啟尚未填寫的試片列印／試配表（JSON）')}</p></section>`;
  }

  function renderThreadPlan(plan) {
    if (!plan || plan.stage !== 'specification_planning_only') return '';
    const labels = { specification: '規格與牙型', diameters: '直徑與牙深', helix: '螺距、導程與線數', lengths: '行程、嚙合與端部', clearances: '配合間隙與比較基準', integration: '與小盒整合', hardware: '金屬硬體資料' };
    const parameters = Array.isArray(plan.parameters) ? plan.parameters : [];
    const groups = Object.entries(labels).map(([group, label]) => {
      const rows = parameters.filter((item) => item.group === group).map((item) => `<tr><th scope="row"><strong>${e(item.label)}${item.symbol ? ` ${e(item.symbol)}` : ''}${item.unit ? `（${e(item.unit)}）` : ''}</strong><small>${e(item.definition)}</small></th><td>${item.value === null || item.value === undefined ? '待定<br>草案欄位' : e(item.value)}</td></tr>`).join('');
      return rows ? `<details${['helix', 'clearances'].includes(group) ? ' open' : ''}><summary>${e(label)}</summary><table class="parameter-table"><thead><tr><th scope="col">參數與定義</th><th scope="col">草案</th></tr></thead><tbody>${rows}</tbody></table></details>` : '';
    }).join('');
    const routes = (Array.isArray(plan.routes) ? plan.routes : []).map((route) => `<li><strong>${e(route.label)}</strong>：${e(route.scope)}</li>`).join('');
    const relationships = (Array.isArray(plan.relationships) ? plan.relationships : []).map((line) => `<li>${e(line)}</li>`).join('');
    const conditions = (Array.isArray(plan.conditions) ? plan.conditions : []).map((line) => `<li>${e(line)}</li>`).join('');
    const sources = (Array.isArray(plan.sources) ? plan.sources : []).map((source) => `<li><a href="${externalUrl(source.url)}" target="_blank" rel="noopener">${e(source.title)}</a><small>${e(source.review_scope)}</small></li>`).join('');
    const record = (path, label) => String(path || '').startsWith('learning/evidence/') && /\.json$/i.test(path) ? `<a href="${fileUrl(path)}" target="_blank" rel="noopener">${e(label)}</a>` : '';
    return `<section class="parameter-plan thread-plan" aria-label="螺紋規格與建模參數規劃"><h4>螺紋規格與參數 · 規劃階段</h4><p>${e(plan.referenceBoxSummary)}</p><div class="parameter-formula"><strong>材料：待定 · 尚未建立螺紋</strong><p>尺寸與間隙仍為待補的草案欄位。列印、實測與試配結果留空，沒有強度或配合合格判定。</p></div><h4>路線與硬體規格</h4><p>${e(plan.routeSummary)}</p><ul>${routes}</ul><p class="caption">以下${e(parameters.length)}項是未製作的參數定義，並非Blender已建立螺紋的讀值；原盒實測與操作紀錄另列。</p>${groups}<details open><summary>Blender Screw 的條件與映射</summary><ul>${relationships}</ul><p class="caption">目前沒有Screw修改器；Angle、Screw、Iterations、Steps及Render輸入值均未配置。</p></details><details><summary>列印與試配前待核對的條件</summary><ul>${conditions}</ul></details><details><summary>已核對的官方定義與資料範圍</summary><ul class="thread-sources">${sources}</ul></details><p class="caption">${record(plan.recordPath, '開啟螺紋參數與原盒實測紀錄（JSON）')}${plan.recordSha256 ? ` · SHA-256 ${e(String(plan.recordSha256).slice(0,16))}` : ''}</p><p class="caption">${record(plan.physicalRecordPath, '開啟尚未填寫的列印／試鎖表（JSON）')}</p></section>`;
  }

  function renderAuditReview(review) {
    if (!review || review.status !== 'reviewed_with_limits') return '';
    const findings = (Array.isArray(review.findings) ? review.findings : []).map((item) => `<li><strong>${e(item.title)}</strong><p>${e(item.detail)}</p></li>`).join('');
    const link = (path, label) => typeof path === 'string' && path.startsWith('learning/evidence/audits/') && !path.includes('\\') && path.split('/').every((part) => part && part !== '.' && part !== '..') && /\.json$/i.test(path) ? `<a href="${fileUrl(path)}" target="_blank" rel="noopener">${e(label)}</a>` : '';
    const report = /^\/reports\/[a-z0-9][a-z0-9-]*\.html$/.test(review.reportUrl || '') ? `<a href="${e(review.reportUrl)}" target="_blank" rel="noopener">閱讀完整審查報告</a>` : '';
    return `<section class="parameter-plan audit-review" aria-label="獨立審查補充"><h4>審查補充 · ${e(review.reviewedOn)}</h4><p>${e(review.summary)}</p>${findings ? `<ul>${findings}</ul>` : ''}<p class="caption">${report} · ${link(review.recordPath, '查核範圍與證據（JSON）')}</p></section>`;
  }

  function shortcutEvidencePath(value) {
    if (typeof value !== 'string' || !value.startsWith('learning/evidence/') || /[\\%?#\u0000-\u0020]/.test(value)) return false;
    const parts = value.split('/');
    return parts.every((part) => part && !part.startsWith('.') && /^[A-Za-z0-9_.-]+$/.test(part)) && /\.(png|jpe?g|webp|json)$/i.test(value);
  }

  function renderShortcut(shortcut) {
    if (!shortcut || typeof shortcut !== 'object' || Array.isArray(shortcut) || typeof shortcut.keys !== 'string' || !shortcut.keys.trim() || typeof shortcut.effect !== 'string' || !shortcut.effect.trim()) return '';
    const evidence = (Array.isArray(shortcut.evidence) ? shortcut.evidence : []).filter((item) => item && shortcutEvidencePath(item.path) && /^[a-f0-9]{64}$/i.test(item.sha256 || '') && typeof item.method === 'string' && item.method.trim());
    // 沒有可連回的驗證依據時，不把候選按鍵顯示成已核對的快速方法。
    if (!evidence.length) return '';
    const notes = (values, label) => {
      const items = (Array.isArray(values) ? values : []).filter((value) => typeof value === 'string' && value.trim());
      return items.length ? `<div class="shortcut-notes"><strong>${e(label)}</strong><ul>${items.map((value) => `<li>${e(value)}</li>`).join('')}</ul></div>` : '';
    };
    const references = evidence.map((item) => `<li><a href="${fileUrl(item.path)}" target="_blank" rel="noopener">${e(typeof item.label === 'string' && item.label.trim() ? item.label : item.path.split('/').pop())}</a><span class="shortcut-evidence-method">${e(item.method)}</span><code>SHA-256 ${e(item.sha256)}</code></li>`).join('');
    return `<aside class="guide-shortcut" aria-label="快速方法"><h4>快速方法</h4><p class="shortcut-keys"><kbd>${e(shortcut.keys)}</kbd></p><p class="shortcut-effect">${e(shortcut.effect)}</p>${notes(shortcut.requirements, '操作前')}${notes(shortcut.cautions, '注意')}<details class="shortcut-evidence"><summary>驗證依據</summary><ul>${references}</ul></details></aside>`;
  }

  function renderStep(lesson, step) {
    const index = stepIndex(lesson, step);
    const guide = Array.isArray(step.guide) && step.guide.length ? `<ol class="guide-list">${step.guide.map((item, i) => `<li class="guide-item"><span class="guide-number" aria-hidden="true">${e(item.mark || i + 1)}</span><div class="guide-copy">${item.where ? `<div class="guide-where">${e(item.where)}</div>` : ''}<p class="guide-action">${e(item.do || item.action || '')}</p>${item.see ? `<p class="guide-see"><strong>你會看到</strong> ${e(item.see)}</p>` : ''}${renderShortcut(item.shortcut)}</div></li>`).join('')}</ol>` : `<div class="guide-item"><span class="guide-number" aria-hidden="true">1</span><p class="guide-action">${e(text(step.action))}</p></div>`;
    const review = (step.contentReview?.summary ? `<p class="caption content-review">內容核對：${e(step.contentReview.summary)}</p>` : '') + renderAuditReview(step.auditReview);
    const figures = renderLessonFigures(step);
    const hasPlan = step.parameterPlan || step.geometryDraft || step.orientationReview || step.stlReview || step.couponReview || step.threadPlan;
    return `<article class="panel step-panel"><header class="step-header"><div class="step-kicker"><span class="eyebrow">STEP ${e(step.id)}</span><span>第 ${index + 1} / ${lesson.steps.length} 步</span></div><h3 id="step-title" tabindex="-1">${e(step.title)}</h3></header><div class="step-body"><div class="small-label">現在只做這一小步</div>${needsEnglishHint(step) ? `<p class="language-hint">本步以英文名稱作對照；介面語言還沒核對時，先依實際畫面確認按鈕文字，保留繁中也不照英文名稱猜位置。</p>` : ''}${review}${guide}${hasPlan ? figures : ''}${renderReviewBlocks(step)}${renderOperationRun(step.operationRun)}${renderPreviousOperationRuns(step.previousOperationRuns)}${hasPlan ? '' : figures}<div class="success-box"><strong>成功時應看到</strong><p>${e(text(step.success))}</p></div>${step.help ? `<details><summary>畫面不同，或找不到按鈕？</summary><div class="help-text">${e(text(step.help))}</div></details>` : ''}</div><nav class="step-navigation" aria-label="瀏覽操作步驟"><button type="button" class="button small" data-step="${e(lesson.steps[index - 1]?.id || '')}"${index === 0 ? ' disabled' : ''}>← 上一步</button><button type="button" class="button small" data-step="${e(lesson.steps[index + 1]?.id || '')}"${index === lesson.steps.length - 1 ? ' disabled' : ''}>預覽下一步 →</button></nav></article>`;
  }

  const renderReviewBlocks = (step) => `${renderParameterPlan(step.parameterPlan)}${renderGeometryDraft(step.geometryDraft)}${renderOrientationReview(step.orientationReview)}${renderStlReview(step.stlReview)}${renderCouponReview(step.couponReview)}${renderThreadPlan(step.threadPlan)}`;

  // 新版小步右欄「示範紀錄」：與原教材頁相同的完整紀錄（含標示框、參數表、幾何與審查），不含操作說明與排解。
  function renderSourceRecord(step) {
    return `${renderAuditReview(step.auditReview)}${renderReviewBlocks(step)}${renderOperationRun(step.operationRun)}${renderPreviousOperationRuns(step.previousOperationRuns)}${renderLessonFigures(step)}`;
  }

  // 只顯示專案 evidence 中的實際截圖；不使用示意圖。
  function renderLessonFigures(step) {
    return (step.figures || []).filter((figure) => figure.type === 'screenshot' && String(figure.path || '').startsWith('learning/evidence/') && /\.(png|jpe?g|webp)$/i.test(String(figure.path || ''))).map((figure) => {
      // 局部視圖僅使用核對過的固定白名單；只以 CSS 放大原圖。
      const focus = figure.view === 'outliner-focus'
        ? { className: 'figure-outliner-focus', caption: 'Blender實際畫面局部放大：Camera／Cube／Light' }
        : figure.view === 'edit-menu-focus'
          ? { className: 'figure-edit-menu-focus', caption: 'Blender 實際畫面局部放大：編輯選單' }
          : null;
      const caption = focus ? focus.caption : figure.caption || '';
      const alt = figure.alt || caption || 'Blender 實際截圖';
      return `<figure class="figure"><a class="figure-image-link${focus ? ' ' + focus.className : ''}" href="${fileUrl(figure.path)}" target="_blank" rel="noopener" aria-label="${e('查看完整原始截圖：' + alt)}"><img src="${fileUrl(figure.path)}" alt="${e(alt)}" loading="lazy"></a><figcaption><span class="figure-kind">實際截圖</span>${e(caption)}<span class="figure-open">點圖查看完整原圖</span></figcaption></figure>`;
    }).join('');
  }

  // 原教材只供查閱：確認與筆記改在新版小步記錄，這裡列出由本步拆出的新版小步。
  function renderNewPathPointer(step) {
    const curriculum = state.engineering.curriculum.data;
    const module = globalThis.BlenderEngineeringPath;
    const targets = [];
    for (const chapter of curriculum?.chapters || []) {
      for (const item of chapter.steps || []) {
        if (item.track === 'appendix' || !(item.sourceSteps || []).some((ref) => ref?.stepId === step.id)) continue;
        const done = module?.curriculumEvents(state.data, curriculum.id, chapter.id, item.id).some((event) => event.type === 'engineering_step_confirmed');
        targets.push(`<li><button type="button" class="button small" data-goto-chapter="${e(chapter.id)}" data-goto-step="${e(item.id)}">第 ${e(chapter.number || chapter.id.slice(2))} 章 ${e(item.section ? item.section + ' ' : '')}${e(item.title)}${done ? ' · 已確認' : ''}</button></li>`);
      }
    }
    return `<section class="panel confirm-panel" id="confirm-panel" tabindex="-1"><h3>在新版小步確認</h3><p class="caption">原教材只供查閱圖文與示範紀錄。完成確認與卡關筆記請到新版對應的小步記錄。</p>${targets.length ? `<ul class="new-path-targets">${targets.join('')}</ul>` : `<p class="form-hint">${curriculum ? '這一步沒有對應的新版小步。' : '新版教材讀取中…'}</p>`}</section>`;
  }

  function noteList(notes, max = Infinity, legacy = new Map()) {
    return [...notes].slice(-max).reverse().map((note) => {
      const role = legacy.get(note); const body = typeof note === 'object' ? note.text || note.note || '' : note;
      // 助教標記的第一行是程式用標籤，只顯示後面的說明。
      const shown = role === 'marker' ? String(body).split('\n').slice(1).join('\n') : body;
      const kind = role ? (role === 'answer' ? '新版工程路徑的回答（不算本單元筆記）' : '新版工程路徑的助教標記（不算本單元筆記）') : note.kind === 'stuck' || note.noteKind === 'stuck' ? '卡關筆記' : '一般筆記';
      return `<article class="note-record"><span class="note-author" data-author="${e(note.author || 'unknown')}">${e(authorName(note.author))}</span><time datetime="${e(note.at || '')}">${e(date(note.at))} · ${e(kind)}</time><p>${e(shown)}</p></article>`;
    }).join('');
  }

  function renderNote(lesson) {
    const notes = lessonNotes(lesson.id); const latest = notes[notes.length - 1];
    return `<section class="panel note-panel" id="note-panel" tabindex="-1"><h3>原教材筆記（只供查閱）</h3>${notes.length ? `<details class="notes-preview"><summary>已保存 ${notes.length} 則筆記</summary>${latest ? noteList([latest]) : ''}${notes.length > 1 ? '<button type="button" class="button quiet small" data-view="journal">查看所有紀錄</button>' : ''}</details>` : '<p class="caption">這個單元沒有筆記。</p>'}<p class="form-hint">新的卡關筆記請在新版小步保存。</p></section>`;
  }

  function renderWorkspace(lesson) {
    return `<section class="panel workspace-panel"><h3>我的練習檔案</h3><p class="caption">先在 Blender 另存檔，再登記下方的版本。已登記的檢查點請另存新檔名。</p><div class="button-row"><button type="button" class="button small full" data-action="open-workspace">開啟練習資料夾</button><button type="button" class="button quiet small" data-action="copy-path">複製存檔路徑</button><button type="button" class="button quiet small" data-action="open-blender">開啟 Blender</button></div><code class="workspace-path">${e(workspaceAbsolute(lesson))}</code></section>`;
  }

  function renderVersionForm(lesson) {
    const pathKey = keyFor('file'); const roleKey = keyFor('role'); const sourceKey = keyFor('source');
    const workspace = String(lp(lesson.id).workspace || `learning/workspaces/${lesson.id}`).replace(/\\/g, '/').replace(/\/$/, '') + '/';
    const files = (state.data.files || []).filter((item) => String(item.path).replace(/\\/g, '/').startsWith(workspace));
    const sources = (state.data.progress.fileVersions || []).filter((item) => item.lesson === lesson.id && item.role === 'source_scene');
    const role = field(roleKey, 'source_scene');
    return `<form class="version-form" data-form="version"><p class="caption"><strong>登記已存在的檢查點</strong><br>記錄 SHA-256、大小與來源，方便之後核對。</p>${files.length ? `<div><label class="field-label" for="version-path">此單元的工作區檔案</label><select id="version-path" data-draft="${e(pathKey)}" required><option value="">請選擇已儲存的檔案</option>${files.map((item) => `<option value="${e(item.path)}"${field(pathKey) === item.path ? ' selected' : ''}>${e(item.path.slice(workspace.length))}${item.registered ? '（已登記）' : ''} · ${e(bytes(item.bytes))}</option>`).join('')}</select></div>` : '<p class="form-hint">工作區目前沒有檔案。先到 Blender 使用「Save As／另存新檔」，保存至本單元資料夾，再按「重新讀取」。</p>'}<div><label class="field-label" for="version-role">檔案用途</label><select id="version-role" data-draft="${e(roleKey)}">${['source_scene', 'render', 'export'].map((item) => `<option value="${item}"${role === item ? ' selected' : ''}>${e(roleName(item))}</option>`).join('')}</select></div><div${role === 'source_scene' ? ' hidden' : ''}><label class="field-label" for="version-source">來源場景版本</label><select id="version-source" data-draft="${e(sourceKey)}"${role === 'source_scene' ? ' disabled' : ' required'}><option value="">選擇已登記的 .blend</option>${sources.map((item) => `<option value="${e(item.path)}"${field(sourceKey) === item.path ? ' selected' : ''}>${e(item.path.split('/').pop())} · ${e(String(item.sha256).slice(0, 10))}</option>`).join('')}</select>${!sources.length ? '<p class="form-hint">請先登記同單元的 .blend 場景，才能連結渲染圖或列印輸出。</p>' : ''}</div><button type="submit" class="button small" data-version-button${!files.length ? ' disabled' : ''}>登記這個檔案版本</button></form>`;
  }

  function renderVersionPanel(lesson) {
    const versions = (state.data.progress.fileVersions || []).filter((item) => item.lesson === lesson.id);
    return `<section class="panel version-panel"><div class="version-summary"><h3>檔案版本紀錄</h3><span class="badge">${versions.length} 個</span></div>${versions.length ? `<ul class="compact-versions">${versions.slice(-3).reverse().map((item) => `<li><span class="role-badge">${e(roleName(item.role))}</span><strong>${e(item.path.split('/').pop())}</strong><small>SHA-256 ${e(String(item.sha256 || '').slice(0, 12))} · ${e(bytes(item.bytes))}</small>${item.source ? `<small>來源：${e(item.source.path.split('/').pop())}</small>` : ''}<a href="${fileUrl(item.path)}" download>下載檢查點</a></li>`).join('')}</ul><button type="button" class="button quiet small margin-top" data-view="versions">查看完整版本表</button>` : '<p class="caption">尚無已登記版本。檔案存在與實際學會，會分別記錄。</p>'}${renderVersionForm(lesson)}</section>`;
  }

  function renderEngineeringVersionPanel() {
    const folder = String(state.data.engineeringWorkspaces?.[ENGINEERING_WORKSPACE] || '').replace(/\\/g, '/').replace(/\/$/, '');
    if (!folder) return '';
    const files = (state.data.files || []).filter((item) => String(item.path).replace(/\\/g, '/').startsWith(folder + '/'));
    const sources = (state.data.progress.fileVersions || []).filter((item) => item.workspace === ENGINEERING_WORKSPACE && item.role === 'source_scene');
    const pathKey = `${ENGINEERING_WORKSPACE}:file`, roleKey = `${ENGINEERING_WORKSPACE}:role`, sourceKey = `${ENGINEERING_WORKSPACE}:source`;
    const role = field(roleKey, 'source_scene');
    return `<section class="panel version-panel"><h3>工程參數盒工作區 · 登記檔案</h3><p class="caption">第 07～08 章的個人副本存在 <code>${e(folder)}/</code>。資料夾尚未建立時，先在專案根目錄執行 <code>python learning/manage.py engineering-workspace</code>。已登記的檢查點不能再用受控面板修改，請另存新檔名繼續。</p><form class="version-form" data-form="engineering-version">${files.length ? `<div><label class="field-label" for="engineering-version-path">工程工作區檔案</label><select id="engineering-version-path" data-draft="${e(pathKey)}" required><option value="">請選擇已儲存的檔案</option>${files.map((item) => `<option value="${e(item.path)}"${field(pathKey) === item.path ? ' selected' : ''}>${e(item.path.slice(folder.length + 1))}${item.registered ? '（已登記）' : ''} · ${e(bytes(item.bytes))}</option>`).join('')}</select></div>` : '<p class="form-hint">工程工作區目前沒有檔案（或資料夾尚未建立）。</p>'}<div><label class="field-label" for="engineering-version-role">檔案用途</label><select id="engineering-version-role" data-draft="${e(roleKey)}">${['source_scene', 'render', 'export'].map((item) => `<option value="${item}"${role === item ? ' selected' : ''}>${e(roleName(item))}</option>`).join('')}</select></div><div${role === 'source_scene' ? ' hidden' : ''}><label class="field-label" for="engineering-version-source">來源場景版本</label><select id="engineering-version-source" data-draft="${e(sourceKey)}"${role === 'source_scene' ? ' disabled' : ' required'}><option value="">選擇已登記的 .blend</option>${sources.map((item) => `<option value="${e(item.path)}"${field(sourceKey) === item.path ? ' selected' : ''}>${e(item.path.split('/').pop())} · ${e(String(item.sha256).slice(0, 10))}</option>`).join('')}</select></div><button type="submit" class="button small" data-engineering-version-button${!files.length ? ' disabled' : ''}>登記這個檔案版本</button></form><div class="button-row"><button type="button" class="button quiet small" data-action="open-engineering-workspace">開啟工程工作區</button></div></section>`;
  }

  function renderSource(lesson) {
    const media = state.data.catalog.sourceMedia || {};
    return `<details class="panel source-panel"><summary>教材來源與本單元範圍</summary><p>${e(lesson.sourceRange || '')}</p><p>${e(state.data.catalog.sourceNote || '')}</p><div class="button-row">${media.lessonReadme ? `<a class="button quiet small" href="${externalUrl(media.lessonReadme)}" target="_blank" rel="noopener">SECourses 第一講</a>` : ''}${media.video ? `<a class="button quiet small" href="${externalUrl(media.video)}" target="_blank" rel="noopener">原作者影片</a>` : ''}</div></details>`;
  }

  function renderJournal() {
    const entries = state.data.journal || []; const events = [...(state.data.progress.events || [])].reverse();
    return `<header class="page-heading"><div class="eyebrow">留下過程，才能接著學</div><h2>學習紀錄</h2><p>學員確認、卡關筆記與檔案登記均來自專案內的共用紀錄。</p></header><div class="journal-grid"><div class="journal-list">${lessons().map((lesson) => `<section class="journal-card"><div class="heading-meta"><span class="eyebrow">單元 ${e(lesson.id)}</span>${badge(lp(lesson.id).status)}</div><h3>${e(lesson.title)}</h3>${(lp(lesson.id).notes || []).length ? noteList(lp(lesson.id).notes, Infinity, legacyNotes(lesson.id)) : '<p>尚未新增筆記。</p>'}</section>`).join('')}${entries.length ? `<section class="journal-card"><h3>專案中的完整紀錄</h3>${entries.map((item) => `<p><a href="${fileUrl(item.path, true)}" target="_blank" rel="noopener">${e(item.title || item.path)}</a></p>`).join('')}</section>` : ''}</div><aside class="panel"><h3>共用進度事件</h3><ul class="event-list">${events.slice(0, 50).map((event) => `<li><time datetime="${e(event.at || '')}">${e(date(event.at))}${event.revision ? ` · r${e(event.revision)}` : ''}</time><strong>${e(({ learner_confirmed: '學員確認完成', note_added: '新增筆記', file_registered: '登記檔案', course_started: '開始學習', learner_updated: '更正介面語言' })[event.type] || event.type)}</strong>${event.step ? `<span> · ${e(event.step)}</span>` : ''}${event.type === 'note_added' ? `<span> · ${e(authorName(event.author))}</span>` : ''}<p>${e(event.evidence || event.note || event.path || (event.type === 'note_added' ? '筆記全文顯示於左側所屬單元。' : ''))}</p></li>`).join('')}</ul></aside></div>`;
  }

  function renderVersions() {
    const versions = [...(state.data.progress.fileVersions || [])].reverse(); const lesson = currentLesson();
    return `<header class="page-heading"><div class="eyebrow">資料管理 · 來源與成果連得起來</div><h2>檔案版本紀錄</h2><p>先存檔，再登記。SHA-256 用於核對內容；渲染與列印輸出必須連結同單元的場景版本。</p><a class="button quiet small margin-top" href="/api/export" download>匯出共用進度紀錄</a></header><div class="content-grid"><div class="primary-column"><section class="panel">${versions.length ? `<div class="version-table-wrap"><table class="version-table"><caption class="small-label">全部單元已登記的 ${versions.length} 個檢查點</caption><thead><tr><th scope="col">檔案與用途</th><th scope="col">內容指紋與來源</th><th scope="col">登記</th></tr></thead><tbody>${versions.map((item) => `<tr><td><span class="role-badge">${item.lesson ? `單元 ${e(item.lesson)}` : '工程工作區'} · ${e(roleName(item.role))}</span><br><a href="${fileUrl(item.path)}" download>${e(item.path.split('/').pop())}</a><small>${e(item.path)}</small><small>${e(bytes(item.bytes))}</small></td><td><code title="${e(item.sha256)}">${e(String(item.sha256 || '').slice(0, 16))}</code>${item.source ? `<small>來源：${e(item.source.path)}<br>SHA ${e(String(item.source.sha256 || '').slice(0, 12))}</small>` : '<small>原始場景檢查點</small>'}</td><td>${e(date(item.registeredAt))}<small>r${e(item.revision || '—')}</small></td></tr>`).join('')}</tbody></table></div>` : '<div class="empty-state"><h2>第一個檢查點，從存檔開始</h2><p>目前尚無已登記的檔案。第一單元的「第一次另存檔 v001」會帶你儲存自己的第一個檢查點。</p><button type="button" class="button" data-action="resume">回到新版下一小步</button></div>'}</section></div><aside class="secondary-column"><section class="panel version-panel"><h3>單元 ${e(lesson.id)} · 登記檔案</h3><p class="caption">第 01～06 章的練習檔存在原單元工作區；先選工作區再登記。</p><div class="workspace-picker" role="group" aria-label="選擇單元工作區">${lessons().map((item) => `<button type="button" class="button quiet small${item.id === lesson.id ? ' selected' : ''}" data-version-lesson="${e(item.id)}"${item.id === lesson.id ? ' aria-pressed="true"' : ' aria-pressed="false"'}>${e(item.id)}</button>`).join('')}</div>${renderVersionForm(lesson)}</section>${renderWorkspace(lesson)}${renderEngineeringVersionPanel()}</aside></div>`;
  }

  function updateFormAvailability() {
    const versionButton = document.querySelector('[data-version-button]');
    if (versionButton) {
      const role = field(keyFor('role'), 'source_scene');
      versionButton.disabled = state.busy || !document.querySelector('#version-path')?.value || (role !== 'source_scene' && !document.querySelector('#version-source')?.value);
    }
    const engineeringVersionButton = document.querySelector('[data-engineering-version-button]');
    if (engineeringVersionButton) {
      const role = field(`${ENGINEERING_WORKSPACE}:role`, 'source_scene');
      engineeringVersionButton.disabled = state.busy || !document.querySelector('#engineering-version-path')?.value || (role !== 'source_scene' && !document.querySelector('#engineering-version-source')?.value);
    }
    document.querySelectorAll('[data-action="open-workspace"],[data-action="open-blender"],[data-action="open-engineering-workspace"]').forEach((button) => { button.disabled = state.busy; });
    document.querySelectorAll('[data-engineering-submit]').forEach((button) => {
      const input = button.closest('form')?.querySelector('textarea[data-draft]');
      button.disabled = state.busy || !String(input?.value || '').trim();
      if (input) input.readOnly = state.busy;
    });
  }

  async function bootstrap({ quiet = false, force = false } = {}) {
    if (state.loading || (state.busy && !force)) return;
    state.loading = true;
    try {
      const data = await request('/api/bootstrap');
      if (!data.catalog?.lessons || !data.progress?.lessons) throw new Error('本機服務回傳的課程或進度格式不完整。');
      if (state.data && data.progress.revision < state.data.progress.revision) return;
      const signature = JSON.stringify([data.progress, data.catalog, data.files, data.journal]);
      const changed = state.signature !== signature;
      preserveDrafts(); state.data = data; state.signature = signature;
      if (!state.lesson || !lessonById(state.lesson)) state.lesson = data.progress.activeLesson || data.catalog.lessons[0]?.id;
      if (!state.browsed.has(state.lesson)) state.browsed.set(state.lesson, lp(state.lesson).currentStep || currentLesson()?.steps[0]?.id);
      if (changed || force) render();
      if (!state.engineering.attempted) void loadEngineering();
      $('connection-status').textContent = '本機共用進度 · 每 5 秒同步';
      if (!quiet) notify('已讀取專案中的最新進度。未送出的文字與瀏覽位置已保留。');
    } catch (error) {
      $('connection-status').textContent = '本機服務暫時無法連線';
      if (!state.data) { $('view-content').innerHTML = `<section class="empty-state"><h2>暫時讀不到本機進度</h2><p>${e(error.message)}</p><button type="button" class="button" data-action="refresh">重新讀取</button></section>`; $('view-content').setAttribute('aria-busy', 'false'); }
      if (!quiet || !state.data) notify(error.message, 'error');
    } finally { state.loading = false; }
  }

  async function handleError(error) {
    if (error.status === 409) {
      await bootstrap({ quiet: true, force: true });
      for (const key of state.drafts.keys()) if (key.includes(':checked:')) state.drafts.set(key, false);
      document.querySelectorAll('input[type="checkbox"][data-draft]').forEach((input) => { input.checked = false; state.drafts.set(input.dataset.draft, false); });
      updateFormAvailability();
      notify('共用進度已由聊天或其他視窗更新。已讀取最新 revision；請核對目前步驟與表單後再送出。完成確認需重新勾選，未自動重送。', 'warning');
    } else notify(error.message || '操作尚未完成，請重新檢查後再試。', 'error');
  }

  async function saveEngineeringRecord(kind, chapterId, stepId, content) {
    const module = globalThis.BlenderEngineeringPath;
    const curriculum = state.engineering.curriculum.data;
    if (state.busy || state.view !== 'engineering' || !state.data || !module || !['confirm', 'note'].includes(kind) || curriculum?.id !== 'engineering-curriculum-v002' || chapterId !== state.engineering.chapter || typeof content !== 'string' || !content.trim() || content.length > 10000) return;
    const chapter = curriculum.chapters.find((item) => item.id === chapterId);
    if (!chapter?.steps.some((step) => step.id === stepId)) return;
    if (kind === 'confirm' && module.curriculumEvents(state.data, curriculum.id, chapterId, stepId).some((event) => event.type === 'engineering_step_confirmed')) return;
    preserveDrafts();
    const revision = state.data.progress.revision;
    const key = module.draftKey(kind, chapterId, stepId);
    const payload = { action: kind === 'confirm' ? 'engineering_confirm' : 'engineering_note', chapterId, stepId, expectedRevision: revision, ...(kind === 'confirm' ? { evidence: content } : { note: content, noteKind: 'stuck' }) };
    state.busy = true; updateFormAvailability();
    try {
      const result = await request('/api/progress', { method: 'POST', body: JSON.stringify(payload) });
      if (!result.progress) throw new Error('本機服務尚未回傳保存後的進度，請重新讀取確認。');
      state.data.progress = result.progress;
      document.querySelectorAll('[data-draft]').forEach((input) => { if (input.dataset.draft === key) input.removeAttribute('data-draft'); });
      state.drafts.delete(key); state.signature = ''; render();
      notify(kind === 'confirm' ? '已記錄你對新版小步的實際確認；原教材步驟保持原狀。' : '卡關筆記已保存到新版小步的共用進度。');
    } catch (error) { await handleError(error); }
    finally { state.busy = false; updateFormAvailability(); }
  }

  async function registerFile(engineering = false) {
    if (state.busy) return;
    preserveDrafts(); const lessonId = state.lesson; const prefix = engineering ? '#engineering-version' : '#version';
    const path = document.querySelector(`${prefix}-path`)?.value; const role = engineering ? field(`${ENGINEERING_WORKSPACE}:role`, 'source_scene') : field(keyFor('role'), 'source_scene'); const source = document.querySelector(`${prefix}-source`)?.value;
    if (!path || (role !== 'source_scene' && !source)) return;
    state.busy = true; updateFormAvailability();
    try {
      const owner = engineering ? { workspaceId: ENGINEERING_WORKSPACE } : { lessonId };
      const result = await request('/api/register-file', { method: 'POST', body: JSON.stringify({ ...owner, path, role, ...(role !== 'source_scene' ? { source } : {}), expectedRevision: state.data.progress.revision }) });
      if (!result.progress) throw new Error('本機服務尚未回傳檔案登記結果，請重新讀取確認。');
      state.data.progress = result.progress; state.drafts.set(engineering ? `${ENGINEERING_WORKSPACE}:file` : keyFor('file', lessonId), '');
      document.querySelector(`${prefix}-path`)?.removeAttribute('data-draft'); state.signature = ''; render();
      notify('檔案版本已登記；場景內容與學習完成度分別保存。');
    } catch (error) { await handleError(error); }
    finally { state.busy = false; updateFormAvailability(); }
  }

  async function openTarget(target, owner = { lessonId: state.lesson }) {
    if (state.busy) return;
    state.busy = true; updateFormAvailability();
    try { await request('/api/open', { method: 'POST', body: JSON.stringify({ ...owner, target }) }); notify(target === 'workspace' ? '已送出開啟練習資料夾的要求，請查看檔案總管。' : '已送出開啟 Blender 的要求，請查看 Blender 視窗。'); }
    catch (error) { await handleError(error); }
    finally { state.busy = false; updateFormAvailability(); }
  }

  function resumeMessage() {
    const next = globalThis.BlenderEngineeringPath?.nextStep(state.data, state.engineering.curriculum);
    const where = next ? `新版下一小步：第 ${next.chapter.number || next.chapter.id.slice(2)} 章 ${next.section ? next.section.id + ' ' + next.section.title + ' · ' : ''}${next.step.title}（${next.step.id}）。` : '新版主線小步都已確認，請先回顧成果。';
    return ['請接續 Blender 引導式學習，一次教我一小步。', `專案：${state.data.projectRoot}`, `網頁讀取的共用進度：revision ${state.data.progress.revision}。`, where, '請先讀 AGENTS.md、最新交接 journal 與 learning/progress.json，執行 manage.py status，以專案最新進度為準。', '每回合只有一個小目標、1–3 個具體操作與可見成功條件。依我實際畫面教學；只有我明確回報完成，才更新進度。', '練習檔保留編號版本；場景與渲染／列印輸出需關聯，記錄來源與雜湊。'].join('\n\n');
  }

  async function copy(value, label) {
    try { if (!navigator.clipboard?.writeText) throw new Error('無法存取剪貼簿'); await navigator.clipboard.writeText(value); notify(`${label}已複製。`); }
    catch { $('copy-title').textContent = label; $('copy-text').value = value; $('copy-dialog').showModal(); $('copy-text').focus(); $('copy-text').select(); }
  }

  function selectLesson(id) {
    if (state.busy || !lessonById(id)) return;
    preserveDrafts(); state.lesson = id; if (!state.browsed.has(id)) state.browsed.set(id, lp(id).currentStep || lessonById(id).steps[0]?.id); state.view = state.view === 'versions' ? 'versions' : 'lesson'; setViewHash(); render();
    $('main-content').focus({ preventScroll: true });
  }

  function resume() {
    if (state.busy) return;
    const next = globalThis.BlenderEngineeringPath?.nextStep(state.data, state.engineering.curriculum);
    if (next) gotoCurriculumStep(next.chapter.id, next.step.id);
    else showEngineeringPage({}, 'engineering-chapter-title');
  }

  document.addEventListener('input', (event) => {
    const input = event.target;
    if (!input.matches('[data-draft]')) return;
    if (input.type !== 'radio' || input.checked) state.drafts.set(input.dataset.draft, input.type === 'checkbox' ? input.checked : input.value);
    updateFormAvailability();
  });
  document.addEventListener('change', (event) => {
    const input = event.target;
    if (!input.matches('[data-draft]')) return;
    if (input.type !== 'radio' || input.checked) state.drafts.set(input.dataset.draft, input.type === 'checkbox' ? input.checked : input.value);
    if (input.id === 'version-role' || input.id === 'engineering-version-role') {
      const source = document.querySelector(input.id === 'version-role' ? '#version-source' : '#engineering-version-source');
      if (source) { const needed = input.value !== 'source_scene'; source.closest('div').hidden = !needed; source.disabled = !needed; source.required = needed; }
    }
    updateFormAvailability();
  });
  document.addEventListener('click', (event) => {
    const button = event.target.closest('button'); if (!button || button.disabled) return;
    if (button.dataset.engineeringChapter) { selectEngineeringChapter(button.dataset.engineeringChapter); return; }
    if (button.dataset.referenceLesson) { openEngineeringReference(button.dataset.referenceLesson, button.dataset.referenceStep); return; }
    if (button.dataset.gotoChapter) { gotoCurriculumStep(button.dataset.gotoChapter, button.dataset.gotoStep); return; }
    if (button.dataset.openSection) { openSection(button.dataset.sectionChapter || state.engineering.chapter, button.dataset.openSection); return; }
    if (button.dataset.selectStep) { selectCurriculumStep(button.dataset.selectStep); return; }
    if (button.dataset.detailTab) { selectDetailTab(button.dataset.detailTab); return; }
    if (button.dataset.jump) { const target = document.getElementById(button.dataset.jump); if (target) { target.scrollIntoView({ block: 'start', behavior: 'auto' }); target.focus({ preventScroll: true }); } return; }
    if (button.dataset.versionLesson) { if (!state.busy && lessonById(button.dataset.versionLesson)) { preserveDrafts(); state.lesson = button.dataset.versionLesson; render(); } return; }
    if (button.dataset.lesson) { selectLesson(button.dataset.lesson); return; }
    if (button.dataset.step) { preserveDrafts(); state.browsed.set(state.lesson, button.dataset.step); state.view = 'lesson'; setViewHash(); render(); $('step-title')?.focus({ preventScroll: true }); return; }
    if (button.dataset.view) { preserveDrafts(); state.view = button.dataset.view; setViewHash(); render(); if (state.view === 'engineering' && !state.engineering.attempted) void loadEngineering(); return; }
    switch (button.dataset.action) {
      case 'refresh': void bootstrap({ force: true }); break;
      case 'retry-engineering': void loadEngineering({ retry: true }); break;
      case 'retry-curriculum': void loadCurriculum({ retry: true }); break;
      case 'resume': resume(); break;
      case 'open-workspace': void openTarget('workspace'); break;
      case 'open-blender': void openTarget('blender'); break;
      case 'open-engineering-workspace': void openTarget('workspace', { workspaceId: ENGINEERING_WORKSPACE }); break;
      case 'copy-path': void copy(workspaceAbsolute(), '存檔資料夾路徑'); break;
      case 'copy-resume': preserveDrafts(); void copy(resumeMessage(), '接續聊天訊息'); break;
      default: break;
    }
  });
  document.addEventListener('submit', (event) => {
    const form = event.target; if (!form.matches('[data-form]')) return;
    event.preventDefault(); preserveDrafts();
    if (form.dataset.form === 'engineering-confirm' || form.dataset.form === 'engineering-note') {
      const kind = form.dataset.form === 'engineering-confirm' ? 'confirm' : 'note';
      const chapterId = form.dataset.engineeringChapter, stepId = form.dataset.engineeringStep;
      const key = globalThis.BlenderEngineeringPath?.draftKey(kind, chapterId, stepId);
      if (key) void saveEngineeringRecord(kind, chapterId, stepId, String(field(key)));
    } else if (form.dataset.form === 'version') void registerFile();
    else if (form.dataset.form === 'engineering-version') void registerFile(true);
  });
  window.addEventListener('hashchange', () => { applyViewHash(); });
  applyViewHash({ initial: true });
  window.addEventListener('beforeunload', (event) => { preserveDrafts(); if ([...state.drafts].some(([key, value]) => /:(note|evidence|confirm)(:|$)/.test(key) && String(value).trim())) { event.preventDefault(); event.returnValue = ''; } });
  window.setInterval(() => { if (!document.hidden && !state.busy && !state.loading) void bootstrap({ quiet: true }); }, 5000);
  void bootstrap({ quiet: true });
})();
