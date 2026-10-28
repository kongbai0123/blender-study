/* 各章練習題共用進度；畫面刷新不重建使用者文字輸入。 */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const state = {data:null, chapter:null, busy:false};
  const el = (tag, text) => { const node=document.createElement(tag); node.textContent=text; return node; };
  const message = (text) => { $('record-message').textContent=text; $('record-message').hidden=!text; };
  const safeSection = (chapter, section) => /^ch\d{2}$/.test(chapter||'') && /^\d{2}-\d{2}$/.test(section||'') ? `/#engineering/${chapter}/${section}` : null;
  const fileUrl = (path) => /^learning\/evidence\/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp)$/i.test(path||'') && !path.split('/').includes('..') ? '/files/'+path.split('/').map(encodeURIComponent).join('/') : null;
  const summaryUrl = (path) => /^learning\/evidence\/[A-Za-z0-9_./-]+\.json$/i.test(path||'') && !path.split('/').includes('..') ? '/files/'+path.split('/').map(encodeURIComponent).join('/') : null;
  const drawingUrl = (path) => /^\/(?:pilot|challenges)\/[a-z0-9-]+\.svg$/.test(path||'') ? path : null;
  const animationUrl = (path) => /^\/pilot\/[a-z0-9-]+\.gif$/.test(path||'') ? path : null;
  // 第 03 章沿用原試教題的 pilot 事件，既有紀錄不必搬移；其餘各章用 challenge 事件。
  const kind = (item) => item.progressKind==='pilot' ? {confirm:'pilot_confirm',note:'pilot_note',confirmed:'pilot_challenge_confirmed',noted:'pilot_challenge_note'} : {confirm:'challenge_confirm',note:'challenge_note',confirmed:'challenge_confirmed',noted:'challenge_note'};
  const list = (id, values) => $(id).replaceChildren(...(Array.isArray(values)?values:[]).map((value)=>el('li',String(value))));
  function link(text, url) { const a=el('a',text); a.href=url; return a; }
  function staticPage(item, chapters) {
    $('loading').hidden=true; $('challenge').hidden=false;
    $('chapter-label').textContent='第 '+item.chapterId.slice(2)+' 章 · 練習題'; $('title').textContent=item.title; $('goal').textContent=item.goal;
    $('deliverable').textContent=item.deliverable; $('evidence-status').textContent=item.evidenceStatus;
    list('requirements',item.requirements); list('checks',item.checks); list('limitations',item.limitations);
    $('chapter-nav').replaceChildren(...chapters.map((ch)=>{const url='/challenges/index.html?chapter='+encodeURIComponent(ch.chapterId);const a=link(ch.chapterId.slice(2)+'　'+ch.title,url); if(ch.chapterId===item.chapterId)a.setAttribute('aria-current','page');return a;}));
    const drawing=item.drawing && drawingUrl(item.drawing.path);
    $('drawing-status').textContent=drawing?(item.drawingStatus||'名義題圖，非實體或製造合格證據。')+' 請以標註數值為準；窄視窗可在圖內左右捲動，或點圖放大。':'本題尚無經核對的專屬工程圖；請以題目條件及原教材為準，不以其他零件的圖替代。';
    $('drawing-view').hidden=!drawing;
    if(drawing){$('drawing-link').href=drawing;$('drawing-image').src=drawing;$('drawing-image').alt=item.drawing.title||'本題工程圖';}
    $('hints').replaceChildren(...(item.hints||[]).map((hint,index)=>{const detail=document.createElement('details');detail.append(el('summary',hint.title||'提示 '+String(index+1).padStart(2,'0')),el('p',hint.text||''));const url=safeSection(item.chapterId,hint.section);if(url) detail.append(link('查看對應正式小節 →',url));return detail;}));
    const screenshot=item.screenshot && fileUrl(item.screenshot.path);
    $('screenshot-view').hidden=!screenshot; $('screenshot-missing').hidden=!!screenshot;
    if(screenshot){$('screenshot').src=screenshot;$('screenshot-link').href=screenshot;$('screenshot-caption').textContent=item.screenshot.caption||'獨立 Blender 畫面參考，非學員完成證據。';$('screenshot-hash').textContent='SHA-256 '+(item.screenshot.sha256||'未提供');}
    const animation=item.animation&&animationUrl(item.animation.path);
    const animationBlock=[];
    if(animation){const section=document.createElement('section');section.append(el('h3',item.animation.title||'短動畫'),el('p',item.animation.description||''));const a=link('開啟動畫',animation);a.target='_blank';a.rel='noopener';const img=document.createElement('img');img.className='demo';img.src=animation;img.alt=item.animation.title||'獨立 Blender 操作動畫';a.replaceChildren(img);section.append(a,el('p',item.animation.caption||''));for(const record of Array.isArray(item.animation.records)?item.animation.records:[]){const url=fileUrl(record.path);if(url){const r=link((record.label||'原圖')+' →',url);r.target='_blank';r.rel='noopener';section.append(r,el('span',' '));}}animationBlock.push(section);}
    $('extra-demos').replaceChildren(...animationBlock,...(Array.isArray(item.extraDemos)?item.extraDemos:[]).map((demo)=>{const section=document.createElement('section');section.append(el('h3',demo.title||'額外示範'),el('p',demo.description||''));const url=fileUrl(demo.screenshot?.path);if(url){const a=link('開啟 Blender 原圖',url);a.target='_blank';a.rel='noopener';const img=document.createElement('img');img.className='demo';img.src=url;img.alt=demo.screenshot.caption||'獨立 Blender 示範原圖';a.replaceChildren(img);section.append(a,el('p',demo.screenshot.caption||''),el('small','原圖 SHA-256 '+(demo.screenshot.sha256||'未提供')));}const summary=summaryUrl(demo.summaryPath);if(summary){const a=link('查看已去識別的示範摘要 →',summary);a.target='_blank';a.rel='noopener';section.append(el('p',''),a);}return section;}));
    $('source-links').replaceChildren(...(item.sourceSteps||[]).map((step)=>{const url=safeSection(step.chapterId,step.sectionId);return url?link((step.label||step.sectionId)+' →',url):el('span','參照尚待核對');}));
    const workspace=item.workspaceId==='engineering-parametric'?'engineering-parametric':item.workspaceLesson;
    $('version-block').hidden=!workspace;
    $('workspace-hint').textContent=workspace?'先在 Blender 另存至 learning/workspaces/'+workspace+'/，再重新讀取清單；登記不會修改檔案。已登記版本請另存新名稱後再修改。'+(item.workspaceId?'工程工作區如尚未建立，請先依第 07 章指引建立。':''):'';
    $('confirm-source').disabled=!workspace;
  }
  function options(select, entries, blank) {
    const previous=select.value, nodes=[new Option(blank,'')];
    for(const entry of entries) nodes.push(new Option(entry.label,entry.path));
    if(previous&&!entries.some((entry)=>entry.path===previous)){const missing=new Option(previous+'（目前不在清單）',previous);missing.disabled=true;nodes.push(missing);}
    select.replaceChildren(...nodes);select.value=previous||'';
  }
  function renderProgress() {
    if(!state.data||!state.chapter)return;
    const progress=state.data.progress, item=state.chapter, lesson=item.workspaceLesson, workspaceId=item.workspaceId==='engineering-parametric'?item.workspaceId:null;
    const events=(progress.events||[]).filter((event)=>event.challengeId===item.challengeId);
    const types=kind(item);
    const confirmation=events.find((event)=>event.type===types.confirmed&&event.author==='learner');
    const notes=events.filter((event)=>event.type===types.noted);
    const versions=(lesson||workspaceId)?(progress.fileVersions||[]).filter((entry)=>(workspaceId?entry.workspace===workspaceId:entry.lesson===lesson)&&entry.role==='source_scene'):[];
    const workspace=workspaceId||lesson;
    const files=workspace?(state.data.files||[]).filter((entry)=>entry.path.startsWith('learning/workspaces/'+workspace+'/')&&entry.path.toLowerCase().endsWith('.blend')&&!entry.registered):[];
    $('record-status').textContent='revision '+progress.revision+' · '+(confirmation?'本題已由學員確認，正式小步仍分開記錄。':'本題尚未由學員確認。');
    options($('version-file'),files.map((entry)=>({path:entry.path,label:entry.path.split('/').pop()+' · '+entry.bytes+' bytes'})),files.length?'選擇已存檔的 .blend':'目前沒有可登記的 .blend');
    options($('confirm-source'),versions.map((entry)=>({path:entry.path,label:entry.path.split('/').pop()+' · SHA '+String(entry.sha256).slice(0,12)})),'不關聯檔案');
    $('version-file').disabled=state.busy||!files.length;$('version-submit').disabled=state.busy||!files.some((entry)=>entry.path===$('version-file').value);
    $('confirm-source').disabled=state.busy||!!confirmation||!workspace;$('confirm-submit').disabled=state.busy||!!confirmation;
    $('note-submit').disabled=state.busy;$('record-refresh').disabled=state.busy;
    $('version-list').replaceChildren(...(versions.length?versions.map((entry)=>el('li',entry.path+' · SHA-256 '+entry.sha256+' · r'+entry.revision)):[el('li','尚無已登記場景。')]));
    $('confirmation-history').replaceChildren(...(confirmation?[el('p','學員回報：'+confirmation.evidence),...(confirmation.sourcePath?[el('p','關聯版本：'+confirmation.sourcePath+' · SHA-256 '+confirmation.sourceSha256)]:[])]:[]));
    $('note-list').replaceChildren(...(notes.length?notes.map((entry)=>el('li',(entry.at||'')+' · '+({learner:'學員',tutor:'助教'}[entry.author]||'作者未標示')+'：'+entry.text)):[el('li','尚無本題卡關筆記。')]));
  }
  async function json(url,opts){const res=await fetch(url,{cache:'no-store',...opts});let body;try{body=await res.json();}catch{body={};}if(!res.ok){const error=new Error(body.error||'讀取失敗');error.status=res.status;throw error;}return body;}
  async function refresh(quiet=false){try{const data=await json('/api/bootstrap');if(!Number.isInteger(data.progress?.revision))throw Error('進度格式不完整');if(!state.data||data.progress.revision>=state.data.progress.revision){state.data=data;renderProgress();}if(!quiet)message('已重新讀取；未送出的輸入保留。');}catch(error){if(!quiet||!state.data)message('讀取失敗：'+error.message+'；未送出的輸入保留。');}}
  async function submit(url,payload,after){if(state.busy||!state.data)return;state.busy=true;renderProgress();message('正在保存…');try{await json(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...payload,expectedRevision:state.data.progress.revision})});after();await refresh(true);message('已保存至共用進度。');}catch(error){if(error.status===409){await refresh(true);message('其他頁面已更新；內容保留，請核對後自行重送。');}else message('未保存：'+error.message+'；內容保留。');}finally{state.busy=false;renderProgress();}}
  $('record-refresh').addEventListener('click',()=>refresh());$('version-file').addEventListener('change',renderProgress);
  $('version-form').addEventListener('submit',(event)=>{event.preventDefault();const path=$('version-file').value;const workspaceId=state.chapter.workspaceId==='engineering-parametric'?state.chapter.workspaceId:null;const owner=workspaceId?{workspaceId}:{lessonId:state.chapter.workspaceLesson};if(path&&(workspaceId||state.chapter.workspaceLesson))submit('/api/register-file',{...owner,path,role:'source_scene'},()=>{$('version-file').value='';});});
  $('confirm-form').addEventListener('submit',(event)=>{event.preventDefault();const evidence=$('confirmation').value;if(!evidence.trim())return;const sourcePath=$('confirm-source').value;submit('/api/progress',{action:kind(state.chapter).confirm,challengeId:state.chapter.challengeId,evidence,...(sourcePath?{sourcePath}:{})},()=>{$('confirmation').value='';});});
  $('note-form').addEventListener('submit',(event)=>{event.preventDefault();const note=$('stuck-note').value;if(!note.trim())return;submit('/api/progress',{action:kind(state.chapter).note,challengeId:state.chapter.challengeId,note},()=>{$('stuck-note').value='';});});
  (async()=>{try{const manifest=await json('/challenges/manifest.json');if(manifest.schemaVersion!==1||!Array.isArray(manifest.chapters))throw Error('題目資料格式不完整');const chapter=new URLSearchParams(location.search).get('chapter')||'ch01';const item=manifest.chapters.find((entry)=>entry.chapterId===chapter);if(!item)throw Error('找不到此章練習題');state.chapter=item;staticPage(item,manifest.chapters);await refresh(true);setInterval(()=>{if(!state.busy)refresh(true);},5000);}catch(error){$('loading').textContent='練習題無法載入：'+error.message;}})();
})();
