(() => {
  'use strict';
  const escape = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const strings = (value) => Array.isArray(value) ? value.filter((item) => typeof item === 'string' && item.trim()) : [];
  const list = (value, ordered = false) => { const items = strings(value); const tag = ordered ? 'ol' : 'ul'; return items.length ? `<${tag}>${items.map((item) => `<li>${escape(item)}</li>`).join('')}</${tag}>` : ''; };
  const availability = (chapter) => typeof chapter?.availabilityLabel === 'string' && chapter.availabilityLabel.trim() ? chapter.availabilityLabel
    : ({ existing_reference: '有既有教材可參照', new_content_pending: '新內容待製作', mixed: '既有參照＋待補內容' }[chapter?.availability] || '內容狀態待核對');
  // 主線小步計入進度；選修可以確認但不計入、不擋後面章節；待製作可以閱讀但不能確認、不計入；
  // 速查（第 00 章）只供查閱、可留筆記但不能確認；附錄是開發與驗證紀錄，只供查核。
  const stepsOf = (chapter) => Array.isArray(chapter?.steps) ? chapter.steps : [];
  const learnerSteps = (chapter) => stepsOf(chapter).filter((step) => !step?.track);
  const optionalSteps = (chapter) => stepsOf(chapter).filter((step) => step?.track === 'optional');
  const appendixSteps = (chapter) => stepsOf(chapter).filter((step) => step?.track === 'appendix');
  const pendingSteps = (chapter) => stepsOf(chapter).filter((step) => step?.track === 'pending');
  const confirmable = (step) => !['pending', 'reference', 'appendix'].includes(step?.track);
  const TRACK_LABELS = { optional: '選修', pending: '待製作', reference: '速查' };

  function safeFileUrl(path, extensions = ['json', 'md']) {
    if (typeof path !== 'string' || !/^learning\/(evidence|journal)\//.test(path) || /[\\:%?#\x00-\x20]/.test(path)) return null;
    if (path.split('/').some((part) => !part || part.startsWith('.'))) return null;
    const extension = path.split('.').pop().toLowerCase();
    if (!extensions.includes(extension)) return null;
    return '/files/' + path.split('/').map(encodeURIComponent).join('/');
  }

  function sourceUrl(value) {
    if (typeof value !== 'string') return null;
    if (/^https:\/\//.test(value)) return value;
    if (!value.startsWith('/read/learning/journal/')) return null;
    const file = safeFileUrl(value.slice('/read/'.length), ['md']);
    return file ? file.replace('/files/', '/read/') : null;
  }

  function validate(data) {
    if (!data || data.schemaVersion !== 1 || typeof data.title !== 'string' || !Array.isArray(data.chapters) || !data.chapters.length) throw new Error('工程學習路徑資料格式不完整。');
    const ids = new Set();
    for (const chapter of data.chapters) {
      if (!chapter || !/^ch\d{2}$/.test(chapter.id) || ids.has(chapter.id) || typeof chapter.title !== 'string' || typeof chapter.goal !== 'string') throw new Error('工程學習路徑的章節編號或內容不正確。');
      ids.add(chapter.id);
    }
    return data;
  }

  function findReference(bootstrap, lessonId, stepId) {
    const lesson = bootstrap?.catalog?.lessons?.find((item) => item.id === lessonId);
    const step = lesson?.steps?.find((item) => item.id === stepId);
    return step ? { lesson, step } : null;
  }

  // 新版小步是主要進度；原教材只供查閱圖文與示範紀錄。
  function renderProgress(bootstrap, curriculum) {
    const progress = bootstrap?.progress;
    if (!progress) return '<p>共用進度尚未讀取。</p>';
    const chapters = curriculum?.data?.chapters;
    const counts = Array.isArray(chapters) ? chapters.reduce((acc, chapter) => { const c = curriculumCounts(bootstrap, curriculum.data.id, chapter); acc.total += c.total; acc.done += c.done; acc.optional += optionalSteps(chapter).length; acc.pending += pendingSteps(chapter).length; return acc; }, { done: 0, total: 0, optional: 0, pending: 0 }) : null;
    const extra = counts ? [counts.optional ? `選修 ${counts.optional} 步` : '', counts.pending ? `${escape(curriculum?.data?.pendingLabel || '待製作')} ${counts.pending} 步` : ''].filter(Boolean).join('、') : '';
    const line = counts ? `${counts.done} / ${counts.total} 個主線小步已確認${extra ? `（另有${extra}，不計入）` : ''}` : '小步確認數：教材載入後顯示';
    return `<section class="engineering-progress" aria-label="共用進度"><div><strong>學習進度</strong><p>${line} · revision ${escape(progress.revision)}</p><p>確認與筆記都記在各小步；瀏覽章節不會新增完成紀錄。原教材的示範紀錄與排解說明顯示在各小步右欄的分頁。</p></div></section>`;
  }

  function nextStep(bootstrap, curriculum) {
    for (const chapter of curriculum?.data?.chapters || []) {
      const step = learnerSteps(chapter).find((item) => !curriculumEvents(bootstrap, curriculum.data.id, chapter.id, item.id).some((event) => event.type === 'engineering_step_confirmed'));
      if (step) return { chapter, step, section: (chapter.sections || []).find((item) => item.id === step.section) };
    }
    return null;
  }

  function renderReferences(references, bootstrap) {
    const rows = (Array.isArray(references) ? references : []).map((reference) => {
      const found = findReference(bootstrap, reference.lessonId, reference.stepId);
      if (!found) return `<li class="engineering-missing-reference">${escape(reference.label || reference.stepId)}：參照尚不可用</li>`;
      return `<li><button type="button" class="button small" data-reference-lesson="${escape(reference.lessonId)}" data-reference-step="${escape(reference.stepId)}">${escape(reference.label || found.step.title)} <span>${escape(reference.stepId)}</span></button><small>開啟原教材原頁，只供查閱來源。</small></li>`;
    });
    return rows.length ? `<section class="engineering-references"><h4>沿用的教材與實拍</h4><ul>${rows.join('')}</ul></section>` : '<p class="engineering-caption">本章為新內容，實作與實拍將另建版本。</p>';
  }

  function renderFigure(figure) {
    const url = safeFileUrl(figure?.path, ['png', 'jpg', 'jpeg', 'webp']);
    if (!url || !/^[a-f0-9]{64}$/i.test(figure?.sha256 || '')) return '';
    return `<figure class="engineering-figure"><a href="${escape(url)}" target="_blank" rel="noopener"><img src="${escape(url)}" alt="${escape(figure.caption || 'Blender 原始操作截圖')}" loading="lazy"></a><figcaption>${escape(figure.caption)}<a href="${escape(url)}" target="_blank" rel="noopener">開啟完整原圖</a><details><summary>原圖版本與內容指紋</summary><p>${escape(figure.path)}</p><code>SHA-256 ${escape(figure.sha256)}</code></details></figcaption></figure>`;
  }

  // 伺服器依 manage.py 的規則標出記在原教材筆記裡的工程路徑回答；這裡只讀結果，不比對文字。
  function legacyAnswer(bootstrap, activityId) {
    for (const record of Array.isArray(bootstrap?.legacyEngineeringNotes) ? bootstrap.legacyEngineeringNotes : []) {
      if (record?.role !== 'answer' || record.activity !== activityId) continue;
      const note = bootstrap?.progress?.lessons?.[record.lessonId]?.notes?.[record.noteIndex];
      if (note?.author === 'learner' && typeof note.text === 'string') return note.text;
    }
    return null;
  }

  function renderShortcuts(shortcuts) {
    const items = (Array.isArray(shortcuts) ? shortcuts : []).filter((item) => item && typeof item.keys === 'string' && typeof item.effect === 'string');
    if (!items.length) return '<p class="engineering-caption">以具名功能與實際面板為準；尚未核對的快捷鍵不先指定。</p>';
    return `<div class="engineering-shortcuts">${items.map((item) => `<article><kbd>${escape(item.keys)}</kbd><p>${escape(item.effect)}</p>${item.context ? `<small><strong>情境：</strong>${escape(item.context)}</small>` : ''}${item.status ? `<small class="engineering-shortcut-status">${escape(item.status)}</small>` : ''}</article>`).join('')}</div>`;
  }

  function renderBaseline(baseline) {
    if (!baseline) return '';
    const dimensions = (Array.isArray(baseline.dimensions) ? baseline.dimensions : []).map((item) => `<div><dt>${escape(item.label)}</dt><dd>${escape(item.value)}</dd></div>`).join('');
    return `<details class="engineering-baseline"><summary>本路徑共用的小盒基線與試驗條件</summary><p>${escape(baseline.summary)}</p>${dimensions ? `<dl>${dimensions}</dl>` : ''}${list(baseline.limitations)}</details>`;
  }

  function validateCurriculum(data) {
    if (!data || data.schemaVersion !== 1 || !Array.isArray(data.chapters) || !data.chapters.length) throw new Error('分步教材資料格式不完整。');
    const chapters = new Set();
    for (const chapter of data.chapters) {
      if (!chapter || !/^ch\d{2}$/.test(chapter.id) || chapters.has(chapter.id) || typeof chapter.title !== 'string' || !Array.isArray(chapter.steps)) throw new Error('分步教材的章節編號或內容不正確。');
      chapters.add(chapter.id);
      const steps = new Set();
      for (const step of chapter.steps) {
        if (!step || typeof step.id !== 'string' || !step.id || steps.has(step.id) || typeof step.title !== 'string' || !Array.isArray(step.actions)) throw new Error('分步教材的小步資料不正確。');
        steps.add(step.id);
      }
    }
    return data;
  }

  const asStrings = (value) => typeof value === 'string' && value.trim() ? [value] : strings(value);
  const draftKey = (kind, chapterId, stepId) => `engineering:${kind}:${chapterId}:${stepId}`;
  function curriculumEvents(bootstrap, curriculumId, chapterId, stepId) {
    const events = bootstrap?.progress?.events;
    if (!Array.isArray(events)) return [];
    return events.filter((event) => event && event.author === 'learner' && event.curriculumId === curriculumId && event.chapterId === chapterId && event.stepId === stepId && ['engineering_step_confirmed', 'engineering_step_note'].includes(event.type));
  }
  function curriculumCounts(bootstrap, curriculumId, chapter) {
    const steps = learnerSteps(chapter);
    return { total: steps.length, done: steps.reduce((count, step) => count + (curriculumEvents(bootstrap, curriculumId, chapter.id, step.id).some((event) => event.type === 'engineering_step_confirmed') ? 1 : 0), 0) };
  }
  function renderNotices(notices) {
    const items = (Array.isArray(notices) ? notices : []).filter((item) => item && typeof item.label === 'string' && typeof item.text === 'string');
    return items.map((item) => { const url = sourceUrl(item.source); return `<p class="engineering-notice"><strong>${escape(item.label)}：</strong>${escape(item.text)}${url ? `<a href="${escape(url)}" target="_blank" rel="noopener">查看更正依據</a>` : ''}</p>`; }).join('');
  }
  function renderStepShortcuts(shortcuts) {
    const items = Array.isArray(shortcuts) ? shortcuts.filter((item) => item && typeof item.keys === 'string') : [];
    if (!items.length) return '';
    return `<h5>功能、快捷操作與注意事項</h5><div class="engineering-shortcuts">${items.map((item) => {
      const evidence = (Array.isArray(item.evidence) ? item.evidence : []).filter((entry) => entry && typeof entry === 'object').map((entry) => {
        const url = safeFileUrl(entry.path, ['png', 'jpg', 'jpeg', 'webp', 'json', 'md']);
        if (!url || !/^[a-f0-9]{64}$/i.test(entry.sha256 || '')) return '';
        return `<li><a href="${escape(url)}" target="_blank" rel="noopener">${escape(entry.label || entry.path)}</a>${entry.method ? ` · ${escape(entry.method)}` : ''}<details><summary>來源版本與內容指紋</summary><code>SHA-256 ${escape(entry.sha256)}</code></details></li>`;
      }).join('');
      return `<article><kbd>${escape(item.keys)}</kbd>${item.effect ? `<p>${escape(item.effect)}</p>` : ''}${asStrings(item.requirements).length ? `<strong>使用情境</strong>${list(asStrings(item.requirements))}` : ''}${asStrings(item.cautions).length ? `<strong>注意與復原</strong>${list(asStrings(item.cautions))}` : ''}${evidence ? `<strong>來源與證據說明</strong><ul>${evidence}</ul>` : ''}</article>`;
    }).join('')}</div>`;
  }

  function renderArtifacts(artifacts) {
    const localScript = (item) => item?.type === 'python-script' && /^learning\/tutor\/(?:guarded_box_parameters|guarded_manual_box|inspect_stl)_v\d{3}\.py$/.test(item.path || '');
    const items = (Array.isArray(artifacts) ? artifacts : []).filter((item) =>
      item && (safeFileUrl(item.path, ['blend', 'json', 'png', 'stl', 'csv', 'md']) || localScript(item)) && /^[a-f0-9]{64}$/i.test(item.sha256 || ''));
    if (!items.length) return '';
    return `<section class="engineering-references"><h5>檔案版本與驗證</h5><ul>${items.map((item) => `<li>${localScript(item) ? `<strong>${escape(item.label || '本機程式')}</strong><small>專案相對路徑：<code>${escape(item.path)}</code></small>` : `<a href="${escape(safeFileUrl(item.path, ['blend', 'json', 'png', 'stl', 'csv', 'md']))}" target="_blank" rel="noopener">${escape(item.label || item.path)}</a>`}<small>SHA-256 ${escape(item.sha256)}</small></li>`).join('')}</ul></section>`;
  }

  function renderOwnDemonstration(step) {
    const demo = step.demonstration;
    if (!demo || typeof demo !== 'object' || Array.isArray(demo)) return '';
    const figures = (Array.isArray(demo.figures) ? demo.figures : []).filter(item => item?.type === 'screenshot').map(renderFigure).join('');
    const readings = (Array.isArray(demo?.readings) ? demo.readings : []).filter(item => item && item.kind === 'readback' && Object.hasOwn(item, 'value')).map(item => {
      const label = escape(item.label || '程式讀回');
      if (typeof item.value === 'string' || typeof item.value === 'number' || typeof item.value === 'boolean') return `<p><strong>${label}：</strong>${escape(item.value)}</p>`;
      let value;
      try { value = JSON.stringify(item.value, null, 2); } catch { return ''; }
      return typeof value === 'string' ? `<details><summary>${label}（完整原始數值）</summary><pre>${escape(value)}</pre></details>` : '';
    }).join('');
    if (!figures && !readings) return '';
    const source = demo?.source;
    const origin = typeof source?.path === 'string' && /^[a-f0-9]{64}$/i.test(source.sha256 || '')
      ? `<details><summary>本步讀值的來源版本</summary><p>${escape(source.path)}</p><code>SHA-256 ${escape(source.sha256)}</code></details>` : '';
    return `<section class="engineering-own-demonstration"><h5>本小步的助教示範</h5><p>${escape(demo?.scope || '本步附圖是獨立示範參考；可見內容請對照原圖，其他數值須另有讀值來源。')}</p>${readings}${origin}${figures}</section>`;
  }

  const OBSERVED_KINDS = { scripted_description: '文字描述，請對照原圖', mixed: '混合紀錄：文字描述與讀回值', readback: '狀態讀回值' };
  const REVIEW_BLOCKS = ['parameterPlan', 'geometryDraft', 'orientationReview', 'stlReview', 'couponReview', 'threadPlan', 'auditReview'];

  // 小步只拆出操作要點；排解說明與助教示範紀錄直接讀原教材 catalog，不在教材 JSON 複製一份。
  // sourceRecord 由主程式提供，畫出與原教材頁相同的完整紀錄（標示框、參數表、幾何與審查）；沒有時只列操作與原圖。
  function sourceParts(step, bootstrap, sourceRecord = null) {
    const parts = { help: '', record: '', reviews: '' };
    for (const ref of Array.isArray(step.sourceSteps) ? step.sourceSteps : []) {
      const original = findReference(bootstrap, ref?.lessonId, ref?.stepId)?.step;
      if (!original) continue;
      if (typeof original.help === 'string' && original.help.trim()) parts.help += `<section class="engineering-source-help"><h5>原教材 ${escape(original.id)} 的排解說明</h5><p>${escape(original.help)}</p></section>`;
      if (typeof sourceRecord === 'function') {
        const full = sourceRecord(original);
        if (full) parts.record += `<section class="engineering-source-run"><h5>原教材 ${escape(original.id)} 的助教示範紀錄</h5><p>助教在獨立 Blender 的實際操作與當時觀察；不是你的完成紀錄。</p>${full}</section>`;
        continue;
      }
      const events = (Array.isArray(original.operationRun?.events) ? original.operationRun.events : []).filter((event) => event && typeof event.action === 'string');
      const extra = (Array.isArray(original.figures) ? original.figures : []).filter((figure) => figure?.type === 'screenshot');
      const sourceFigure = (figure, caption) => {
        const url = safeFileUrl(figure?.path, ['png', 'jpg', 'jpeg', 'webp']);
        if (!url) return '';
        const fingerprint = /^[a-f0-9]{64}$/i.test(figure.sha256 || '') ? `<details><summary>原圖版本與內容指紋</summary><p>${escape(figure.path)}</p><code>SHA-256 ${escape(figure.sha256)}</code></details>` : '';
        return `<figure class="engineering-figure"><a href="${escape(url)}" target="_blank" rel="noopener"><img src="${escape(url)}" alt="${escape(figure.alt || caption || 'Blender 原始操作截圖')}" loading="lazy"></a><figcaption>${escape(caption || figure.caption || '')}<a href="${escape(url)}" target="_blank" rel="noopener">開啟完整原圖</a>${fingerprint}</figcaption></figure>`;
      };
      const items = events.map((event) => `<li><strong>${escape(event.action)}</strong>${typeof event.observed === 'string' && event.observed ? `<p><small>${escape(OBSERVED_KINDS[event.observedKind] || '觀察紀錄')}</small>${escape(event.observed)}</p>` : ''}${event.figure?.type === 'screenshot' ? sourceFigure(event.figure, event.figure.caption) : ''}</li>`)
        .concat(extra.map((figure) => `<li>${sourceFigure(figure, figure.caption)}</li>`));
      const count = events.filter((event) => event.figure?.type === 'screenshot').length + extra.length;
      if (items.length) parts.record += `<section class="engineering-source-run"><h5>原教材 ${escape(original.id)} 的助教示範紀錄（${count} 張原圖）</h5><p>助教在獨立 Blender 的實際操作與當時觀察；不是你的完成紀錄。</p><ol>${items.join('')}</ol></section>`;
      if (REVIEW_BLOCKS.some((key) => original[key])) parts.reviews += `<p class="engineering-caption">原教材 ${escape(original.id)} 另有參數表、幾何或審查紀錄；用「注意」分頁的原教材按鈕查看完整內容。</p>`;
    }
    return parts;
  }

  // 附錄沿用整段收合的呈現。
  function renderSourceDetail(step, bootstrap) {
    const parts = sourceParts(step, bootstrap);
    return (parts.help ? `<details class="engineering-source-help"><summary>畫面不同，或找不到按鈕？</summary>${parts.help}</details>` : '')
      + (parts.record ? `<details class="engineering-source-run"><summary>原教材示範紀錄</summary>${parts.record}</details>` : '') + parts.reviews;
  }

  const STATUS_LABELS = {
    existing_demo: '本小步附有助教示範原圖或讀值；請核對各圖的範圍',
    source_step_demo: '所屬原教材步驟有助教示範，本小步沒有單獨原圖；請展開下方的原教材示範紀錄核對',
    concept_only: '概念說明；尚無本步實拍',
    documented_lesson: '方法、表格或來源已核對；本步不是實體實驗',
    field_protocol_ready: '現場操作方法與空白紀錄已備妥；實體結果待進行',
    draft_pending_demo: '操作草案；實際示範待製作'
  };

  function renderStep(step, chapterId, curriculum, bootstrap, ui, appendix = false, position = '') {
    const figures = (Array.isArray(step.figures) ? step.figures : []).filter((figure) => figure?.type === 'screenshot').map(renderFigure).join('');
    const answer = step.legacyActivity ? legacyAnswer(bootstrap, step.legacyActivity) : null;
    const recorded = answer ? `<p class="engineering-notice"><strong>你在聊天中的回答已記錄：</strong>「${escape(answer)}」。這一小步還沒確認；確認請用下方表單。</p>` : '';
    const references = (Array.isArray(step.sourceSteps) ? step.sourceSteps : []).filter((ref) => ref && typeof ref.lessonId === 'string' && typeof ref.stepId === 'string').map((ref) => ({ ...ref, label: ref.label || `原教材 ${ref.stepId}` }));
    const status = STATUS_LABELS[step.evidenceStatus] || '證據狀態待核對';
    const events = curriculumEvents(bootstrap, curriculum.data.id, chapterId, step.id);
    const confirmed = events.some((event) => event.type === 'engineering_step_confirmed');
    const confirmation = events.find((event) => event.type === 'engineering_step_confirmed');
    const notes = events.filter((event) => event.type === 'engineering_step_note' && typeof event.text === 'string');
    let recordPanel = '<p class="engineering-caption">附錄紀錄供查核；不需操作，也沒有確認表單。</p>';
    if (!appendix) {
      const confirmKey = draftKey('confirm', chapterId, step.id), noteKey = draftKey('note', chapterId, step.id);
      const confirmDraft = ui?.drafts?.get(confirmKey) || '', noteDraft = ui?.drafts?.get(noteKey) || '';
      const noteList = notes.length ? `<ul class="engineering-record-notes">${notes.map((event) => `<li>${escape(event.text)}</li>`).join('')}</ul>` : '';
      const confirmForm = confirmed ? `<p>已由學員確認這一小步。</p>${typeof confirmation?.evidence === 'string' ? `<p class="engineering-record-text">${escape(confirmation.evidence)}</p>` : ''}` : `<form data-form="engineering-confirm" data-engineering-chapter="${escape(chapterId)}" data-engineering-step="${escape(step.id)}"><label>實際完成情況<textarea data-draft="${escape(confirmKey)}" rows="3" maxlength="10000" placeholder="寫下你實際看到或完成的情況">${escape(confirmDraft)}</textarea></label><button type="submit" class="button small" data-engineering-submit${ui?.busy || !confirmDraft.trim() ? ' disabled' : ''}>確認這一小步</button></form>`;
      recordPanel = `<section class="engineering-record" aria-label="本小步學員紀錄"><h5>本小步學員紀錄</h5><p>只有你送出確認或筆記才會記錄；此紀錄不會確認原教材步驟。</p>${confirmForm}<form data-form="engineering-note" data-engineering-chapter="${escape(chapterId)}" data-engineering-step="${escape(step.id)}"><label>卡關筆記<textarea data-draft="${escape(noteKey)}" rows="3" maxlength="10000" placeholder="寫下你卡住的地方">${escape(noteDraft)}</textarea></label><button type="submit" class="button small" data-engineering-submit${ui?.busy || !noteDraft.trim() ? ' disabled' : ''}>保存卡關筆記</button></form>${noteList}</section>`;
    }
    const label = position ? `<span>${escape(position)}</span>` : `<span>${escape(step.id)}</span>`;
    return `<details class="engineering-curriculum-step${appendix ? ' engineering-appendix-step' : ''}" data-curriculum-step="${escape(step.id)}"><summary>${label} ${escape(step.title)}${confirmed ? ' · 已確認' : ''}</summary><div class="engineering-curriculum-step-body">${recorded}${step.goal ? `<p><strong>小目標：</strong>${escape(step.goal)}</p>` : ''}${step.context ? `<p><strong>操作前核對：</strong>${escape(asStrings(step.context).join('；'))}</p>` : ''}<h5>${appendix ? '當時的操作' : '操作'}</h5>${list(step.actions, true)}${step.success ? `<p><strong>核對結果：</strong>${escape(step.success)}</p>` : ''}<p><strong>證據狀態：</strong>${escape(status)}</p>${renderNotices(step.notices)}${asStrings(step.limitations).length ? `<h5>限制與待核對</h5>${list(asStrings(step.limitations))}` : ''}${renderStepShortcuts(step.shortcuts)}${figures || '<p class="engineering-caption">此小步沒有附單獨的操作原圖；請以文字及下方原教材紀錄為準。</p>'}${renderSourceDetail(step, bootstrap)}${renderArtifacts(step.artifacts)}${references.length ? renderReferences(references, bootstrap) : ''}${recordPanel}<p class="engineering-caption">小步代號 ${escape(step.id)}（在聊天中回報時可以引用）</p></div></details>`;
  }

  const isConfirmed = (bootstrap, curriculum, chapterId, stepId) => curriculumEvents(bootstrap, curriculum.data.id, chapterId, stepId).some((event) => event.type === 'engineering_step_confirmed');
  const sectionsOf = (chapter) => (Array.isArray(chapter?.sections) ? chapter.sections : []).filter((section) => section && typeof section.id === 'string');
  const sectionSteps = (chapter, sectionId) => stepsOf(chapter).filter((step) => step?.track !== 'appendix' && step.section === sectionId);

  // 全課程依序的小節清單，供上一節／下一節使用（跨章）。
  function sectionSequence(curriculum) {
    return (curriculum?.data?.chapters || []).flatMap((chapter) => sectionsOf(chapter).map((section) => ({ chapter, section })));
  }

  function curriculumNotice(curriculum) {
    const message = curriculum?.loading ? '正在讀取分步教材。' : curriculum?.error ? `分步教材暫時無法讀取：${curriculum.error}` : '分步教材尚未讀取。';
    return `<section class="panel engineering-curriculum" role="status"><h3>新版逐步教材</h3><p>${escape(message)}原有路徑與學習進度仍可使用。</p>${curriculum?.error ? '<button type="button" class="button small" data-action="retry-curriculum">重新讀取分步教材</button>' : ''}</section>`;
  }

  // 速查卡的「正式練習」：連到各章實際操作的小步；compact 用在速查表，只顯示節號。
  function renderPractice(step, compact = false) {
    const items = (Array.isArray(step?.practice) ? step.practice : []).filter((item) => item && /^ch\d{2}$/.test(item.chapterId || '') && typeof item.stepId === 'string');
    if (!items.length) return compact ? '—' : '';
    const buttons = items.map((item) => `<button type="button" class="button quiet small" data-goto-chapter="${escape(item.chapterId)}" data-goto-step="${escape(item.stepId)}"${compact ? ` title="${escape(item.label || item.stepId)}"` : ''}>${escape(compact ? item.sectionId || item.stepId : item.label || item.stepId)}</button>`).join('');
    return compact ? `<span class="engineering-practice">${buttons}</span>` : `<div class="engineering-practice"><strong>正式練習：</strong>${buttons}</div>`;
  }

  // 速查章（kind: reference）的章頁以一張表列出全部卡片，取代小節目錄。
  function renderQuickTable(chapter, detail) {
    const keys = (step) => (Array.isArray(step.shortcuts) ? step.shortcuts : []).filter((item) => typeof item?.keys === 'string').map((item) => `<kbd>${escape(item.keys)}</kbd>`).join('') || '—';
    const bodies = sectionsOf(detail).map((section) => `<tbody><tr class="engineering-quick-section"><th colspan="4"><button type="button" class="link-button" data-section-chapter="${escape(chapter.id)}" data-open-section="${escape(section.id)}">${escape(section.id)} ${escape(section.title)}</button></th></tr>${sectionSteps(detail, section.id).map((step) => `<tr><td class="engineering-quick-keys">${keys(step)}</td><td><button type="button" class="link-button" data-goto-chapter="${escape(chapter.id)}" data-goto-step="${escape(step.id)}">${escape(step.title)}</button></td><td>${escape(asStrings(step.context).join('；'))}</td><td>${renderPractice(step, true)}</td></tr>`).join('')}</tbody>`).join('');
    return `<section class="panel engineering-quick"><h4>速查表</h4><p class="engineering-caption">點功能名稱看詳細說明、原圖與注意事項；「正式練習」連到各章實際操作的小步。</p><div class="engineering-quick-scroll"><table><thead><tr><th>按鍵</th><th>功能</th><th>在哪裡按</th><th>正式練習</th></tr></thead>${bodies}</table></div></section>`;
  }

  // 章節頁：精簡總覽與小節目錄；功能、限制、原教材參照與附錄收在「本章補充」。
  function renderChapterPage(data, chapter, curriculum, bootstrap, ui) {
    const detail = curriculum?.data?.chapters?.find((item) => item.id === chapter.id);
    const index = data.chapters.findIndex((item) => item.id === chapter.id);
    const reference = chapter.kind === 'reference';
    // 速查章不是後面章節的先備學習。
    const previous = data.chapters.slice(0, Math.max(index, 0)).reverse().find((item) => item.kind !== 'reference') || null;
    const counts = detail ? curriculumCounts(bootstrap, curriculum.data.id, detail) : null;
    const pending = detail ? learnerSteps(detail).find((step) => !isConfirmed(bootstrap, curriculum, chapter.id, step.id)) : null;
    const resume = pending ? `<button type="button" class="button primary small" data-goto-chapter="${escape(chapter.id)}" data-goto-step="${escape(pending.id)}">接續本章：${escape(pending.section ? pending.section + ' ' : '')}${escape(pending.title)}</button>` : (counts?.total ? '<p>本章主線小步都已確認。</p>' : '');
    const toc = detail && reference ? renderQuickTable(chapter, detail) : detail ? `<section class="panel engineering-toc"><h4>小節目錄</h4><ol>${sectionsOf(detail).map((section) => {
      const own = sectionSteps(detail, section.id).filter(confirmable);
      const done = own.filter((step) => isConfirmed(bootstrap, curriculum, chapter.id, step.id)).length;
      return `<li><button type="button" data-section-chapter="${escape(chapter.id)}" data-open-section="${escape(section.id)}"><span>${escape(section.id)}</span><span>${escape(section.title)}${trackLabel(section) ? ` <em>${escape(trackLabel(section))}</em>` : ''}</span><small>${own.length ? `${done} / ${own.length}` : '—'}</small></button></li>`;
    }).join('')}</ol></section>` : curriculumNotice(curriculum);
    const appendix = detail ? appendixSteps(detail) : [];
    const history = asStrings(detail?.limitationHistory);
    const appendixBlock = appendix.length || history.length ? `<details class="engineering-appendix"><summary>${escape(detail.appendix?.title || '附錄：開發與驗證紀錄')}（${appendix.length} 項，不需操作、不計入進度）</summary>${detail.appendix?.summary ? `<p>${escape(detail.appendix.summary)}</p>` : ''}${appendix.map((step) => renderStep(step, chapter.id, curriculum, bootstrap, ui, true)).join('')}${history.length ? `<h4>本章歷次版本的限制紀錄</h4>${list(history)}` : ''}</details>` : '';
    const extra = `<details class="panel engineering-chapter-extra"><summary>本章補充（實作重點、功能與快捷、限制、原教材參照、備註）</summary><h4>實作內容</h4>${list(chapter.practice, true)}<h4>必要功能與快速操作</h4>${list(chapter.functions)}${renderShortcuts(chapter.shortcuts)}${asStrings(detail?.limitations).length ? `<h4>本章限制</h4>${list(asStrings(detail.limitations))}` : ''}${renderReferences(chapter.references, bootstrap)}${strings(chapter.notes).length ? `<h4>教學安排與待核對條件</h4>${list(chapter.notes)}` : ''}${appendixBlock}</details>`;
    const pilot = reference ? '' : `<section class="panel"><h4>本章練習題</h4><p>查看題目、提示、實際畫面與證據狀態；題目與主線小步分開記錄。</p><a class="button small" href="/challenges/index.html?chapter=${escape(chapter.id)}">開啟本章練習題</a></section>`;
    return `<section class="panel engineering-chapter" aria-labelledby="engineering-chapter-title"><div class="heading-meta"><span class="eyebrow">第 ${escape(chapter.number || chapter.id.slice(2))} 章</span><span class="badge">${escape(availability(chapter))}</span>${counts?.total ? `<span class="badge">${counts.done} / ${counts.total} 小步已確認</span>` : ''}</div><h3 id="engineering-chapter-title" tabindex="-1">${escape(chapter.title)}</h3><dl class="engineering-chapter-summary"><div><dt>學什麼</dt><dd>${escape(chapter.goal)}</dd></div><div><dt>${escape(chapter.deliverableLabel || '做出')}</dt><dd>${escape(chapter.deliverable)}</dd></div>${previous ? `<div><dt>${escape(chapter.prerequisiteLabel || '接續')}</dt><dd>${escape(chapter.prerequisiteSummary || `第 ${previous.number || previous.id.slice(2)} 章 ${previous.title} 的成果`)}</dd></div>` : ''}</dl></section>${pilot}${toc}${extra}`;
  }

  // 速查卡沒有確認表單，只留卡關筆記。
  function renderRecordPanel(step, chapterId, curriculum, bootstrap, ui) {
    const events = curriculumEvents(bootstrap, curriculum.data.id, chapterId, step.id);
    const confirmation = events.find((event) => event.type === 'engineering_step_confirmed');
    const notes = events.filter((event) => event.type === 'engineering_step_note' && typeof event.text === 'string');
    const confirmKey = draftKey('confirm', chapterId, step.id), noteKey = draftKey('note', chapterId, step.id);
    const confirmDraft = ui?.drafts?.get(confirmKey) || '', noteDraft = ui?.drafts?.get(noteKey) || '';
    const confirmForm = step.track === 'reference' ? '' : confirmation ? `<p>已由學員確認這一小步。</p>${typeof confirmation.evidence === 'string' ? `<p class="engineering-record-text">${escape(confirmation.evidence)}</p>` : ''}` : `<form data-form="engineering-confirm" data-engineering-chapter="${escape(chapterId)}" data-engineering-step="${escape(step.id)}"><label>實際完成情況<textarea data-draft="${escape(confirmKey)}" rows="2" maxlength="10000" placeholder="寫下你實際看到或完成的情況">${escape(confirmDraft)}</textarea></label><button type="submit" class="button small" data-engineering-submit${ui?.busy || !confirmDraft.trim() ? ' disabled' : ''}>確認這一小步</button></form>`;
    return `<section class="engineering-record" aria-label="本小步學員紀錄">${confirmForm}<details class="engineering-note-box"${noteDraft.trim() ? ' open' : ''}><summary>卡關筆記${notes.length ? `（${notes.length}）` : ''}</summary><form data-form="engineering-note" data-engineering-chapter="${escape(chapterId)}" data-engineering-step="${escape(step.id)}"><label>卡在哪裡<textarea data-draft="${escape(noteKey)}" rows="2" maxlength="10000" placeholder="寫下你卡住的地方">${escape(noteDraft)}</textarea></label><button type="submit" class="button small" data-engineering-submit${ui?.busy || !noteDraft.trim() ? ' disabled' : ''}>保存卡關筆記</button></form>${notes.length ? `<ul class="engineering-record-notes">${notes.map((event) => `<li>${escape(event.text)}</li>`).join('')}</ul>` : ''}</details></section>`;
  }

  const PENDING_TEXT = '這一步需要的模型或示範還沒完成，現在只能閱讀；不能確認，也不計入主線進度。';
  const REFERENCE_TEXT = '速查卡只供閱讀與查找，不需要確認，也不計入進度；要動手練習，請到各卡「正式練習」列出的小步。';
  const trackLabel = (item) => typeof item?.pendingLabel === 'string' && item.track === 'pending' ? item.pendingLabel : TRACK_LABELS[item?.track];
  const pendingNotice = (item) => `<p class="engineering-notice"><strong>${escape(trackLabel(item) || '待製作')}：</strong>${escape(item.pendingReason || PENDING_TEXT)}</p>`;
  const referenceNotice = () => `<p class="engineering-notice"><strong>速查：</strong>${escape(REFERENCE_TEXT)}</p>`;
  const DETAIL_TABS = [['detail', '詳細步驟'], ['figures', '原圖'], ['shortcuts', '快捷鍵'], ['record', '示範紀錄'], ['notes', '注意'], ['help', '找不到按鈕']];

  // 右欄：目前小步的詳述，用分頁切換。
  function renderDetailPanel(step, chapterId, bootstrap, tab, sourceRecord) {
    const active = DETAIL_TABS.some(([key]) => key === tab) ? tab : 'detail';
    const parts = sourceParts(step, bootstrap, sourceRecord);
    const empty = (text) => `<p class="engineering-caption">${escape(text)}</p>`;
    const references = (Array.isArray(step.sourceSteps) ? step.sourceSteps : []).filter((ref) => ref && typeof ref.lessonId === 'string' && typeof ref.stepId === 'string').map((ref) => ({ ...ref, label: ref.label || `原教材 ${ref.stepId}` }));
    let body;
    if (active === 'detail') {
      const detail = step.detail && Array.isArray(step.detail.steps) ? step.detail : null;
      body = `${step.context ? `<p><strong>操作前：</strong>${escape(asStrings(step.context).join('；'))}</p>` : ''}${detail ? list(detail.steps, true) : `${list(step.actions, true)}<p class="engineering-caption">本章的詳細步驟還沒改寫；先依上面的操作，畫面不同就用卡關筆記回報。</p>`}${step.success ? `<p><strong>看到這樣就對了：</strong>${escape(step.success)}</p>` : ''}${detail?.why ? `<p class="engineering-why"><strong>為什麼：</strong>${escape(detail.why)}</p>` : ''}`;
    } else if (active === 'figures') {
      body = (Array.isArray(step.figures) ? step.figures : []).filter((figure) => figure?.type === 'screenshot').map(renderFigure).join('') || empty('這一步沒有單獨的原圖；可到「示範紀錄」看原教材的操作原圖。');
    } else if (active === 'shortcuts') {
      body = renderStepShortcuts(step.shortcuts) || empty('這一步沒有指定快捷鍵；依詳細步驟的選單操作即可。');
    } else if (active === 'record') {
      body = (renderOwnDemonstration(step) + parts.record + renderArtifacts(step.artifacts)) || empty(step.figures?.length ? '本步參考圖請看「原圖」；圖說說明適用範圍，其他紀錄依「詳細步驟」所列來源查核。' : '本步是文字方法，沒有另附 Blender 操作紀錄；請依「詳細步驟」及「注意」核對適用範圍。');
    } else if (active === 'notes') {
      body = `${step.track === 'pending' ? pendingNotice(step) : step.track === 'reference' ? referenceNotice() : ''}<p><strong>證據狀態：</strong>${escape(STATUS_LABELS[step.evidenceStatus] || '證據狀態待核對')}</p>${renderNotices(step.notices)}${asStrings(step.limitations).length ? `<h5>限制與待核對</h5>${list(asStrings(step.limitations))}` : ''}${parts.reviews}${references.length ? renderReferences(references, bootstrap) : ''}<p class="engineering-caption">小步代號 ${escape(step.id)}（在聊天中回報時可以引用）</p>`;
    } else {
      const own = list(asStrings(step.help));
      body = (own ? `<section class="engineering-source-help"><h5>選單位置與排解</h5>${own}</section>` : '') + parts.help || empty('這一步沒有原教材的排解說明；畫面和描述不同時，用中欄的卡關筆記描述你看到的畫面。');
    }
    return `<aside class="panel engineering-detail" aria-label="小步詳述"><div class="engineering-detail-heading"><span class="eyebrow">詳述</span><strong>${escape(step.title)}</strong></div><div class="engineering-tabs" role="tablist">${DETAIL_TABS.map(([key, label]) => `<button type="button" role="tab" data-detail-tab="${key}" aria-selected="${key === active}">${escape(label)}</button>`).join('')}</div><div class="engineering-tab-body" role="tabpanel">${body}</div></aside>`;
  }

  // 小節頁：中欄是本節小步的簡述與確認，一次只展開一步；右欄是該步的詳述分頁。
  function renderSectionPage(chapter, section, curriculum, bootstrap, ui) {
    const detail = curriculum.data.chapters.find((item) => item.id === chapter.id);
    const steps = sectionSteps(detail, section.id);
    const done = steps.filter((step) => isConfirmed(bootstrap, curriculum, chapter.id, step.id)).length;
    const selected = steps.find((step) => step.id === ui?.step) || steps.find((step) => step.track !== 'pending' && !isConfirmed(bootstrap, curriculum, chapter.id, step.id)) || steps[0];
    const optional = section.track === 'optional';
    const trackBadge = (step) => trackLabel(step) && step.track !== section.track ? ` <em>${escape(trackLabel(step))}</em>` : '';
    const rows = steps.map((step, index) => {
      const confirmed = isConfirmed(bootstrap, curriculum, chapter.id, step.id);
      const mark = confirmed ? '✓' : String(index + 1);
      if (step !== selected) return `<li class="engineering-step-row${confirmed ? ' done' : ''}"><button type="button" data-select-step="${escape(step.id)}"><span class="step-mark">${mark}</span>${escape(step.title)}${trackBadge(step)}</button></li>`;
      const answer = step.legacyActivity ? legacyAnswer(bootstrap, step.legacyActivity) : null;
      return `<li class="engineering-step-row selected${confirmed ? ' done' : ''}" data-curriculum-step="${escape(step.id)}"><div class="engineering-step-current"><h4><span class="step-mark">${mark}</span>${escape(step.title)}${trackBadge(step)}</h4>${answer ? `<p class="engineering-notice"><strong>你在聊天中的回答已記錄：</strong>「${escape(answer)}」。這一小步還沒確認；確認請用下方表單。</p>` : ''}${step.goal ? `<p><strong>小目標：</strong>${escape(step.goal)}</p>` : ''}<h5>操作</h5>${list(step.actions, true)}${step.success ? `<p><strong>成功畫面：</strong>${escape(step.success)}</p>` : ''}${step.track === 'pending' ? pendingNotice(step) : `${step.track === 'reference' ? renderPractice(step) : ''}${renderRecordPanel(step, chapter.id, curriculum, bootstrap, ui)}`}</div></li>`;
    }).join('');
    const sequence = sectionSequence(curriculum);
    const position = sequence.findIndex((item) => item.chapter.id === chapter.id && item.section.id === section.id);
    const link = (item, label) => item ? `<button type="button" class="button quiet small" data-section-chapter="${escape(item.chapter.id)}" data-open-section="${escape(item.section.id)}">${label}</button>` : '<span></span>';
    const pager = `<nav class="engineering-pager" aria-label="小節切換">${link(sequence[position - 1], `← ${escape(sequence[position - 1]?.section.id || '')}`)}<button type="button" class="button quiet small" data-engineering-chapter="${escape(chapter.id)}">回第 ${escape(chapter.number || chapter.id.slice(2))} 章</button>${link(sequence[position + 1], `${escape(sequence[position + 1]?.section.id || '')} →`)}</nav>`;
    const middle = `<section class="panel engineering-section-main"><div class="heading-meta"><span class="eyebrow">第 ${escape(chapter.number || chapter.id.slice(2))} 章 · 小節 ${escape(section.id)}</span>${trackLabel(section) ? `<span class="badge">${escape(trackLabel(section))}</span>` : ''}${steps.some((step) => step.track !== 'reference') ? `<span class="badge">本節 ${done} / ${steps.filter(confirmable).length} 已確認</span>` : ''}</div><h3 id="engineering-section-title" tabindex="-1">${escape(section.id)} ${escape(section.title)}</h3>${optional ? '<p class="engineering-caption">選修：可以照做並確認，但不計入主線進度，也不擋住後面章節。</p>' : ''}${section.track === 'pending' ? pendingNotice(section) : ''}${section.track === 'reference' ? referenceNotice() : ''}${typeof detail.detailNote === 'string' && detail.detailNote.trim() ? `<p class="engineering-caption">${escape(detail.detailNote)}</p>` : ''}<ol class="engineering-step-list">${rows}</ol>${pager}</section>`;
    return `<nav class="engineering-breadcrumb" aria-label="目前位置"><button type="button" class="link-button" data-engineering-chapter="${escape(chapter.id)}">第 ${escape(chapter.number || chapter.id.slice(2))} 章 ${escape(chapter.title)}</button><span>›</span><span>${escape(section.id)} ${escape(section.title)}</span></nav><div class="engineering-section-page">${middle}${selected ? renderDetailPanel(selected, chapter.id, bootstrap, ui?.tab, ui?.sourceRecord) : ''}</div>`;
  }

  function render(data, bootstrap, chapterId = 'ch01', curriculum = null, ui = {}) {
    validate(data);
    const chapter = data.chapters.find((item) => item.id === chapterId);
    const next = nextStep(bootstrap, curriculum);
    const nextButton = next ? `<button type="button" class="button primary engineering-start" data-goto-chapter="${escape(next.chapter.id)}" data-goto-step="${escape(next.step.id)}">前往下一小步：${escape(next.section ? next.section.id + ' ' + next.section.title + ' · ' : '')}${escape(next.step.title)}</button>` : (curriculum?.data ? '<p>主線小步都已確認。</p>' : '');
    const detail = curriculum?.data?.chapters?.find((item) => item.id === chapterId);
    const section = ui?.section && detail ? sectionsOf(detail).find((item) => item.id === ui.section) : null;
    if (chapter && section) return `<div class="engineering-path engineering-path-section">${renderSectionPage(chapter, section, curriculum, bootstrap, ui)}</div>`;
    const environment = data.environment ? `<h4>草圖與參數環境</h4><p>${escape(data.environment.summary)}</p>${safeFileUrl(data.environment.recordPath) ? `<a href="${escape(safeFileUrl(data.environment.recordPath))}" target="_blank" rel="noopener">查看草圖環境驗證紀錄</a>` : ''}` : '';
    const sources = (Array.isArray(data.sources) ? data.sources : []).filter((source) => sourceUrl(source.url)).map((source) => `<li><a href="${escape(sourceUrl(source.url))}" target="_blank" rel="noopener">${escape(source.label || source.url)}</a></li>`).join('');
    const courseLabel = `${data.courseLabel || '工程學習路徑'} · ${curriculum?.data?.version || data.version}`;
    const body = chapter ? renderChapterPage(data, chapter, curriculum, bootstrap, ui) : `<section class="empty-state"><h3>找不到這個路徑章節</h3><p>請從章節清單選擇；原教材進度沒有變動。</p></section>`;
    return `<div class="engineering-path"><header class="page-heading"><div class="eyebrow">${escape(courseLabel)}</div><h2>${escape(data.title)}</h2><p>${escape(data.intro)}</p></header><div class="engineering-content">${body}<details class="panel engineering-policy"><summary>學習與紀錄方式</summary>${list(data.learningPolicy)}${renderBaseline(data.baseline)}${environment}${sources ? `<h4>參考來源</h4><ul>${sources}</ul>` : ''}</details></div></div>`;
  }

  function renderError(message, loading = false) {
    return `<section class="empty-state engineering-error" role="status"><h2>${loading ? '正在讀取工程學習路徑' : '工程學習路徑暫時無法讀取'}</h2><p>${escape(message || (loading ? '正在載入章節安排與既有教材參照。' : '原教材與共用進度仍可使用。'))}</p>${loading ? '' : '<button type="button" class="button" data-action="retry-engineering">重新讀取路徑</button>'}</section>`;
  }

  globalThis.BlenderEngineeringPath = Object.freeze({ validate, validateCurriculum, render, renderError, findReference, curriculumEvents, draftKey, learnerSteps, nextStep, sectionsOf, TRACK_LABELS });
})();
