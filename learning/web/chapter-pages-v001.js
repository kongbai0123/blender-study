

(async () => {
  "use strict";
  const response=await fetch("/engineering-curriculum.json",{cache:"no-store"});
  if(!response.ok)throw new Error("教材讀取失敗");
  const curriculum=await response.json();
  document.getElementById("release-version").textContent="正式教材 · "+curriculum.version;
  if(!curriculum.chapterPages?.sections)throw new Error("此服務仍是舊版，請重新執行 Start-Learning.cmd");
  const O=curriculum.chapterPages.outline;
  window.SECTIONS=curriculum.chapterPages.sections;
  let C=O.chapters.find(c=>c.id===(/^#engineering\/(ch\d{2})/.exec(location.hash)?.[1]||"ch01"))||O.chapters.find(c=>c.id==="ch01");
  let progressLoaded=false,progressBusy=false,doneIds=new Set();
  const stepIds=(chapter)=>chapter.sections.flatMap(s=>{
    const page=window.SECTIONS[s.id];return [page?.prep,...(page?.steps||[])].filter(Boolean).map(c=>c.stepId);
  });
  const mainlineKeys=new Set(curriculum.chapters.flatMap(c=>c.steps.filter(s=>!s.track).map(s=>c.id+":"+s.id)));
  const countDone=(chapter,ids=stepIds(chapter))=>ids.filter(id=>mainlineKeys.has(chapter.id+":"+id)&&doneIds.has(chapter.id+":"+id)).length;
  async function refreshProgress(redraw=true){
    if(progressBusy)return;progressBusy=true;
    try{
      const r=await fetch("/api/bootstrap",{cache:"no-store"});if(!r.ok)throw new Error("共用進度暫時無法讀取");
      const data=await r.json();if(!Array.isArray(data.progress?.events))throw new Error("共用進度格式不完整");
      doneIds=new Set(data.progress.events.filter(e=>e.type==="engineering_step_confirmed"&&e.author==="learner"&&e.curriculumId===curriculum.id).map(e=>e.chapterId+":"+e.stepId));
      progressLoaded=true;document.getElementById("progress-status").textContent="共用進度已讀取";
    }catch(error){progressLoaded=false;document.getElementById("progress-status").textContent=error.message;}
    finally{progressBusy=false;if(redraw)renderNavigation();}
  }
  await refreshProgress(false);
  const EVIDENCE_BASE = "/files/learning/";
  const $ = id => document.getElementById(id);
  const escape = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
  const STORE = "blender-chapter-pages-v001:";
  const read = key => { try { return localStorage.getItem(STORE + key); } catch { return null; } };
  const write = (key, value) => { try { localStorage.setItem(STORE + key, value); } catch {} };
  const narrow = matchMedia("(max-width:1099px)");
  let S, currentId, toastTimer, previousFocus;
  let savedOpen;
  try { savedOpen = JSON.parse(read("expanded-chapters")); } catch {}
  const expanded = new Set(Array.isArray(savedOpen) ? savedOpen.filter(id => O.chapters.some(c => c.id === id)) : [C.id]);
  expanded.add(C.id);
  if (read("nav-hidden") === "1") document.body.classList.add("nav-hidden");
  const shortId = id => id.split("-").map(Number).join(".");
  let first = C.sections[0].id;
  function toast(text) {
    $("toast").textContent = text;
    $("toast").hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { $("toast").hidden = true; }, 2600);
  }
  function syncToggle() {
    const shown = narrow.matches ? document.body.classList.contains("nav-open") : !document.body.classList.contains("nav-hidden");
    $("nav-toggle").textContent = shown ? "« 收合章節" : "☰ 展開章節";
    $("nav-toggle").setAttribute("aria-expanded", String(shown));
  }
  function closeDrawer() { document.body.classList.remove("nav-open"); syncToggle(); }
  $("nav-toggle").onclick = () => {
    if (narrow.matches) document.body.classList.toggle("nav-open");
    else write("nav-hidden", document.body.classList.toggle("nav-hidden") ? "1" : "0");
    syncToggle();
  };
  $("nav-backdrop").onclick = closeDrawer;
  narrow.addEventListener("change", closeDrawer);
  syncToggle();
  function toggleChapter(id) {
    expanded.has(id) ? expanded.delete(id) : expanded.add(id);
    write("expanded-chapters", JSON.stringify([...expanded]));
    renderNavigation();
  }
  function sectionLink(a,chapterId,sectionId){
    a.href=chapterId==="ch00"?"/legacy.html#engineering/ch00/"+sectionId:"#engineering/"+chapterId+"/"+sectionId;
    a.onclick=e=>{
      if(chapterId==="ch00")return;
      closeDrawer();
      if(C.id===chapterId&&currentId===sectionId){e.preventDefault();scrollTo({top:0,behavior:"smooth"});}
    };
  }
  function renderNavigation() {
    $("nav-count").textContent = O.chapters.length + " 章";
    $("nav-total").textContent = (progressLoaded?O.chapters.reduce((n,c)=>n+countDone(c),0):"—") + " / " + O.mainSteps + " 小步已確認";
    $("nav-total").insertAdjacentHTML("beforeend","<small>與聊天共用進度；閱讀本頁不會自動確認</small>");
    $("chapters").replaceChildren();
    const rail = $("rail"); rail.replaceChildren();
    O.chapters.forEach(c => {
      const current = c.id === C.id;
      const open = expanded.has(c.id);
      const wrap = document.createElement("div");
      wrap.className = "ch" + (current ? " current" : "");
      const sub = c.reference ? "速查：不需確認，不計入進度" : (progressLoaded?countDone(c):"—") + " / " + c.steps + " 小步已確認";
      wrap.innerHTML = '<button class="ch-btn" aria-expanded="' + open + '"><span class="ch-num">' + escape(c.number) +
        '</span><span class="ch-name">' + escape(c.title) + '<span class="ch-sub">' + escape(sub) + '</span></span></button><ul class="sec-list"></ul>';
      wrap.querySelector("button").onclick = () => toggleChapter(c.id);
      const list = wrap.querySelector(".sec-list"); list.hidden = !open;
      c.sections.forEach(s => {
        const li = document.createElement("li"), a = document.createElement("a");
        a.innerHTML = '<span class="sid">' + escape(s.id) + '</span><span>' + escape(s.title) +
          '</span><span class="cnt">' + (c.reference?"":s.track?(s.track==="pending"?"實體待執行":"選修"):(progressLoaded?countDone(c,[window.SECTIONS[s.id]?.prep,...(window.SECTIONS[s.id]?.steps||[])].filter(Boolean).map(x=>x.stepId)):"—")+"/"+s.steps) + '</span>';
        if (s.id === currentId) a.setAttribute("aria-current","page");
        sectionLink(a,c.id,s.id); li.append(a); list.append(li);
      });
      $("chapters").append(wrap);
      const head = document.createElement("li"), chapterLink = document.createElement("a");
      chapterLink.className = "r-ch" + (current ? " current" : "");
      chapterLink.href = "#" + c.sections[0].id;
      chapterLink.title = c.number + " " + c.title;
      chapterLink.textContent = Number(c.number);
      chapterLink.setAttribute("aria-expanded",String(open));
      chapterLink.dataset.ch = c.id;
      chapterLink.onclick = e => { e.preventDefault(); toggleChapter(c.id); };
      head.append(chapterLink); rail.append(head);
      if (open) c.sections.forEach(s => {
        const li = document.createElement("li"), a = document.createElement("a");
        a.className = "r-sec"; a.title = s.id + " " + s.title; a.textContent = shortId(s.id);
        if (s.id === currentId) a.setAttribute("aria-current","page");
        sectionLink(a,c.id,s.id); li.append(a); rail.append(li);
      });
    });
  }
  function showGlossary(glossary) {
    $("terms").innerHTML = '<span class="label">名詞</span>';
    $("terms").hidden = !glossary.length;
    $("term-def").hidden = true;
    glossary.forEach(g => {
      const b = document.createElement("button");
      b.className = "term-chip"; b.textContent = g.label; b.setAttribute("aria-expanded","false");
      b.onclick = () => {
        const open = b.getAttribute("aria-expanded") === "true";
        document.querySelectorAll(".term-chip").forEach(x => x.setAttribute("aria-expanded","false"));
        $("term-def").hidden = open;
        if (!open) {
          b.setAttribute("aria-expanded","true");
          $("term-def").textContent = g.label + "：" + g.text;
        }
      };
      $("terms").append(b);
    });
  }
  function linkTerms(root, glossary, seen) {
    const walker = document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{
      acceptNode:n => n.parentElement.closest("kbd,.term,h2,b,summary") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    });
    const nodes=[]; while(walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      // Longest matching term first, then continue in the remaining text.
      const text = node.nodeValue;
      const matches = glossary.filter(g => !seen.has(g.term) && text.includes(g.term))
        .map(g => ({g,at:text.indexOf(g.term)})).sort((a,b)=>a.at-b.at || b.g.term.length-a.g.term.length);
      if (!matches.length) return;
      const fragment = document.createDocumentFragment(); let offset=0;
      matches.forEach(({g,at}) => {
        if (at < offset || seen.has(g.term)) return;
        fragment.append(document.createTextNode(text.slice(offset,at)));
        const span = document.createElement("span"); span.className="term";
        span.title=g.label+"："+g.text; span.textContent=g.term; fragment.append(span);
        offset=at+g.term.length; seen.add(g.term);
      });
      fragment.append(document.createTextNode(text.slice(offset))); node.replaceWith(fragment);
    });
  }
  function shot(fig) {
    const box=document.createElement("div"); box.className="shot";
    const [w,h]=fig.size;
    box.innerHTML='<img src="'+escape(EVIDENCE_BASE+fig.path)+'" alt="'+escape(fig.caption)+'" width="'+w+'" height="'+h+'" loading="eager">';
    for(const m of fig.marks||[]){
      const [x,y,mw,mh]=m.box,mark=document.createElement("div"),badge=document.createElement("span");
      mark.className="mark"+(y<16?" below":"");mark.dataset.n=m.n;
      Object.assign(mark.style,{left:(x/w*100)+"%",top:(y/h*100)+"%",width:(mw/w*100)+"%",height:(mh/h*100)+"%"});
      badge.textContent=m.n;mark.append(badge);box.append(mark);
    }
    box.tabIndex=0; box.setAttribute("role","button"); box.setAttribute("aria-label","放大原圖："+fig.caption); box.title="點一下放大";
    box.onclick=()=>openLightbox(fig,box);
    box.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();openLightbox(fig,box);}};
    // Lay out numbered badges in rendered pixels, keeping them separated at all widths.
    const placeBadges=()=>{
      if(!box.isConnected || !box.clientWidth)return;
      const frame=box.getBoundingClientRect(),used=[];
      box.querySelectorAll(".mark").forEach(mark=>{
        const r=mark.getBoundingClientRect(),span=mark.querySelector("span"),size=22;
        const candidates=[[r.left-11,r.top-11],[r.right-11,r.top-11],[r.left-11,r.bottom-11],[r.right-11,r.bottom-11]];
        // Small adjacent fields can clamp every corner to the same point on mobile.
        // Keep the box fixed; give its numbered badge nearby fallback positions.
        for(const dx of [24,-24,48,-48,72,-72]) candidates.push([r.left-11+dx,r.top-11]);
        const bounded=candidates.map(([x,y])=>[Math.max(frame.left+1,Math.min(x,frame.right-size-1)),Math.max(frame.top+1,Math.min(y,frame.bottom-size-1))]);
        const [x,y]=bounded.find(([x,y])=>used.every(([a,b])=>x+size+2<=a || a+size+2<=x || y+size+2<=b || b+size+2<=y)) || bounded[0];
        span.style.cssText="left:"+(x-r.left-3)+"px;top:"+(y-r.top-3)+"px;right:auto;transform:none";
        used.push([x,y]);
      });
    };
    new ResizeObserver(placeBadges).observe(box);
    return box;
  }
  function legend(fig,host) {
    const ul=document.createElement("ul"); ul.className="legend";
    (fig.marks || []).forEach(m=>{
      const li=document.createElement("li"); li.innerHTML='<span class="n">'+m.n+'</span>'+escape(m.label);
      const mark=()=>host.querySelector('.mark[data-n="'+m.n+'"]');
      li.onmouseenter=()=>mark()?.classList.add("hot");
      li.onmouseleave=()=>mark()?.classList.remove("hot");
      ul.append(li);
    }); return ul;
  }
  function renderFigure(el,figs,k=0,note="本步尚無可用實拍。") {
    el.replaceChildren();
    if (!figs.length) {
      el.innerHTML='<div class="no-figure">'+escape(note)+'</div>';
      return;
    }
    if (figs.length>1) {
      const tabs=document.createElement("div"); tabs.className="fig-tabs"; tabs.setAttribute("role","tablist");
      tabs.setAttribute("aria-label","操作原圖序列");
      figs.forEach((f,j)=>{
        if(j) tabs.insertAdjacentHTML("beforeend",'<span class="arrow" aria-hidden="true">→</span>');
        const b=document.createElement("button"); b.setAttribute("role","tab"); b.setAttribute("aria-selected",String(j===k));
        b.tabIndex=j===k?0:-1; b.textContent=(j+1)+". "+(f.tab || "原圖");
        b.onclick=()=>{renderFigure(el,figs,j);el.querySelectorAll('[role="tab"]')[j].focus({preventScroll:true});};
        b.onkeydown=e=>{
          if(!["ArrowLeft","ArrowRight","Home","End"].includes(e.key)) return;
          e.preventDefault();
          const next=e.key==="Home"?0:e.key==="End"?figs.length-1:(j+(e.key==="ArrowRight"?1:-1)+figs.length)%figs.length;
          renderFigure(el,figs,next);el.querySelectorAll('[role="tab"]')[next].focus({preventScroll:true});
        };
        tabs.append(b);
      }); el.append(tabs);
    }
    const s=shot(figs[k]); el.append(s,legend(figs[k],s));
    const scope=curriculum.chapterPages.evidenceRoles?.[figs[k].evidenceRole];
    if(scope){
      const note=document.createElement("p");note.className="evidence-scope";note.dataset.role=figs[k].evidenceRole;
      const label=document.createElement("b");label.textContent=scope.label;
      note.append(label,document.createTextNode(" · "+scope.description));el.append(note);
    }
    const p=document.createElement("p"); p.className="caption";p.textContent=figs[k].caption+"　點圖可放大";el.append(p);
  }
  function renderCard(p,number,seen) {
    const card=document.createElement("section");card.className="step";card.id=p.kind==="prep"?"step-prep":"step-"+number;
    const badge=p.kind==="prep"?'<span class="dot prep">準備</span>':'<span class="dot">'+number+'</span>';
    const keys=(p.keys || []).map(k=>'<kbd>'+escape(k)+'</kbd>').join("+");
    const figs=[p.figure,...(p.figures || []),p.alternative?.figure].filter(Boolean);
    card.innerHTML='<div class="text"><div class="step-head">'+badge+'<h2>'+escape(p.title)+'</h2></div>' +
      '<p class="lead">'+escape(p.kind==="prep"?p.summary:p.lead)+(keys?'　'+keys:'')+'</p>' +
      '<ol class="actions">'+(p.actions || []).map(a=>'<li>'+a+'</li>').join("")+'</ol>' +
      '<div class="label">做完應該看到</div><ul class="see">'+(p.checks || []).map(c=>'<li>'+c+'</li>').join("")+'</ul>' +
      ((p.pitfalls || []).length?'<div class="label">常見失誤</div>'+p.pitfalls.map(x=>'<div class="pitfall"><b>'+escape(x.title)+'</b>：'+x.text+'</div>').join(""):'')+
      (p.locate?'<details class="more"><summary>找不到位置？</summary>'+escape(p.locate)+'</details>':'')+
      '<details class="more"><summary>'+(p.alternative?'另一種方法、':'')+'示範來源</summary>'+
      (p.alternative?'<div class="alt"><b>'+escape(p.alternative.title)+'</b><br>'+p.alternative.text+'<div class="mini"></div></div>':'')+
      ((p.references || []).length?'<ul class="readbacks">'+p.references.map(r=>'<li><a href="'+escape(EVIDENCE_BASE+r.path)+'" target="_blank" rel="noopener">'+escape(r.label)+'</a></li>').join('')+'</ul>':'')+
      (p.readings?.length?'<div class="readings"><b>程式讀值／觀察來源</b>'+p.readings.map(r=>'<p>'+escape(r.kind||'觀察紀錄')+' · '+escape(r.label||'')+'：'+escape(typeof r.value==='string'?r.value:JSON.stringify(r.value))+'</p>').join('')+'</div>':'')+
      (p.cautions?.length?'<ul class="cautions">'+p.cautions.map(x=>'<li>'+escape(x)+'</li>').join('')+'</ul>':'')+
      '<div class="source">小步代號 <code>'+escape(p.stepId)+'</code><ul>'+figs.map(f=>'<li>'+escape(f.path)+'<br>SHA-256 '+escape(f.sha256)+'</li>').join("")+'</ul></div></details></div><figure class="figure"></figure>';
    $("steps").append(card);
    renderFigure(card.querySelector(".figure"),p.figure?[p.figure]:(p.figures || []),0,p.figureNote);
    if(p.alternative?.figure) renderFigure(card.querySelector(".mini"),[p.alternative.figure]);
    linkTerms(card.querySelector(".text"),S.glossary || [],seen);
    const a=document.createElement("a");a.href="#"+card.id;
    a.innerHTML='<span class="dot'+(p.kind==="prep"?' prep':'')+'">'+(p.kind==="prep"?'準備':number)+'</span>'+escape(p.title);
    a.onclick=e=>{e.preventDefault();card.scrollIntoView({behavior:"smooth",block:"start"});};
    $("toc").append(a);
  }
  function renderPager(section) {
    const i=C.sections.findIndex(s=>s.id===section?.id);
    $("pager").replaceChildren(); if(i<0)return;
    const prev=C.sections[i-1],next=C.sections[i+1];
    if(!prev) $("pager").append(document.createElement("span"));
    [prev,next].forEach((s,j)=>{
      if(!s)return;
      const a=document.createElement("a"); a.className=j?"next":"prev";
      a.innerHTML='<small>'+(j?'下一節 →':'← 上一節')+'</small>'+escape(s.id+" "+s.title);
      sectionLink(a,C.id,s.id);$("pager").append(a);
    });
  }
  function closeLightbox(restore=true) {
    $("lightbox").hidden=true; $("lb-body").replaceChildren();document.body.style.overflow="";
    if(restore && previousFocus?.isConnected) previousFocus.focus({preventScroll:true});
  }
  function openLightbox(fig,opener) {
    previousFocus=opener;$("lb-caption").textContent=fig.caption;$("lb-raw").href=EVIDENCE_BASE+fig.path;
    const s=shot(fig);s.onclick=null;s.onkeydown=null;s.removeAttribute("role");s.removeAttribute("tabindex");s.removeAttribute("aria-label");s.title="";
    $("lb-body").replaceChildren(s);$("lightbox").classList.remove("bare");$("lb-toggle").textContent="隱藏標註";
    $("lightbox").hidden=false;document.body.style.overflow="hidden";$("lb-close").focus({preventScroll:true});
  }
  $("lb-close").onclick=()=>closeLightbox();
  $("lb-toggle").onclick=()=>{
    const bare=$("lightbox").classList.toggle("bare");$("lb-toggle").textContent=bare?"顯示標註":"隱藏標註";
  };
  document.addEventListener("keydown",e=>{
    if(e.key==="Escape") {
      if(!$("lightbox").hidden)closeLightbox();else if(document.body.classList.contains("nav-open")){closeDrawer();$("nav-toggle").focus();}
    }
    if(e.key==="Tab" && !$("lightbox").hidden) {
      const items=[$("lb-toggle"),$("lb-raw"),$("lb-close")],i=items.indexOf(document.activeElement);
      if(e.shiftKey && i<=0){e.preventDefault();items.at(-1).focus();}
      else if(!e.shiftKey && (i<0 || i===items.length-1)){e.preventDefault();items[0].focus();}
    }
  });
  function render() {
    closeLightbox(false);closeDrawer();clearTimeout(toastTimer);$("toast").hidden=true;
    if(/^#(?:journal|versions|lesson)/.test(location.hash)){location.replace("/legacy.html"+location.hash);return;}
    const route=/^#engineering\/(ch\d{2})(?:\/(\d{2}-\d{2}))?$/.exec(location.hash);
    if(route?.[1]==="ch00"){location.replace("/legacy.html"+location.hash);return;}
    const oldChapter=C.id;
    C=O.chapters.find(c=>c.id===(route?.[1]||"ch01"))||O.chapters.find(c=>c.id==="ch01");
    if(C.id!==oldChapter)expanded.add(C.id);
    first=C.sections[0].id;
    currentId=route?.[2] || (location.hash&&!route?"missing-section":first);
    const section=C.sections.find(s=>s.id===currentId);
    S=section && window.SECTIONS?.[currentId];
    $("ch-num").textContent=C.number;$("ch-title").textContent=C.title;
    const title=section?section.id+" "+section.title:"找不到這個小節";
    $("sec-title").textContent=title;$("title").textContent=title;document.title=title+" · Blender 工程學習";document.getElementById("legacy-section").href="/legacy.html#engineering/"+C.id+"/"+currentId;
    $("key").textContent=S?.keyPoint || ""; $("scope").textContent=S?.scope?"ⓘ "+S.scope:"";
    $("scope").hidden=!S?.scope;showGlossary(S?.glossary || []);
    $("toc").replaceChildren();$("steps").replaceChildren();
    const indexSize=(S?.steps.length||0)+(S?.prep?1:0), indexFold=$("toc-fold");
    indexFold.classList.toggle("long",indexSize>8);indexFold.open=indexSize<=8;
    indexFold.querySelector("summary").textContent="本節操作索引（"+indexSize+" 小步）";
    if(S) {
      const seen=new Set();
      if(S.prep)renderCard({kind:"prep",...S.prep},0,seen);
      (S.steps || []).forEach((s,i)=>renderCard({kind:"step",...s},i+1,seen));
      if(S.efficiency){
        const panel=document.createElement("details");panel.className="lesson-method";
        panel.innerHTML='<summary>'+escape(S.efficiency.title)+'</summary><p>'+escape(S.efficiency.workflow)+'</p><p>'+escape(S.efficiency.caution)+'</p><ul>'+S.efficiency.sources.map(u=>'<li><a href="'+escape(u)+'" target="_blank" rel="noopener">官方操作說明</a></li>').join('')+'</ul>';
        $("steps").append(panel);
      }
      if(!S.steps.length&&!S.prep){
        const panel=document.createElement("section");panel.className="empty-state";
        panel.innerHTML="<p>本節完整操作與既有紀錄保留在原版教材。</p><p><a href=\"/legacy.html#engineering/"+C.id+"/"+S.id+"\">開啟本節完整教材 →</a></p>";
        $("steps").append(panel);
      }
    } else {
      const empty=document.createElement("section");empty.className="empty-state";
      empty.innerHTML='<h2>'+(section?'本節尚未製作':'找不到這個小節')+'</h2><p>'+
        (section?'這個小節的資料尚未載入，請返回本章第一節。':'請從左側章節欄選擇本章的小節。')+
        '</p><p><a href="#engineering/'+escape(C.id)+'/'+escape(first)+'">返回本章第一節 →</a></p>';
      $("steps").append(empty);
    }
    renderNavigation();renderPager(section);window.scrollTo({top:0,behavior:"instant"});
  }
  window.addEventListener("hashchange",render);
  document.getElementById("refresh-progress").onclick=()=>refreshProgress();
  window.addEventListener("focus",()=>refreshProgress());
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)void refreshProgress();});
  render();
})().catch(error=>{
  document.getElementById("title").textContent="教材暫時無法開啟";
  document.getElementById("key").textContent=error.message;
  document.getElementById("steps").innerHTML='<a href="/legacy.html">開啟原版教材查閱</a>';
});
