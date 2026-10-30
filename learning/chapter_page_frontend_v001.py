"""Build the reviewed chapter-page shell for the formal local server."""
import re

def make_page(source):
    text = source.replace('第 01 章小節頁草稿', 'Blender 工程學習')
    text = re.sub(r'<script src="(?:course-outline\.js|sections/[^"]+)"></script>\s*', '', text)
    text = text.replace('(() => {', '(async () => {', 1)
    text = text.replace('  const O = window.OUTLINE;\n  const C = O.chapters.find(c => c.id === "ch01");', '''  const response=await fetch("/engineering-curriculum.json",{cache:"no-store"});
  if(!response.ok)throw new Error("教材讀取失敗");
  const curriculum=await response.json();
  document.getElementById("release-version").textContent="正式教材 · "+curriculum.version;
  if(!curriculum.chapterPages?.sections)throw new Error("此服務仍是舊版，請重新執行 Start-Learning.cmd");
  const O=curriculum.chapterPages.outline;
  window.SECTIONS=curriculum.chapterPages.sections;
  let C=O.chapters.find(c=>c.id===(/^#engineering\\/(ch\\d{2})/.exec(location.hash)?.[1]||"ch01"))||O.chapters.find(c=>c.id==="ch01");
  let progressLoaded=false,progressBusy=false,doneIds=new Set();
  const stepIds=(chapter)=>chapter.sections.flatMap(s=>{
    const page=window.SECTIONS[s.id];return [page?.prep,...(page?.steps||[])].filter(Boolean).map(c=>c.stepId);
  });
  const countDone=(chapter,ids=stepIds(chapter))=>ids.filter(id=>doneIds.has(chapter.id+":"+id)).length;
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
  await refreshProgress(false);''')
    text = text.replace('const EVIDENCE_BASE = "../../";', 'const EVIDENCE_BASE = "/files/learning/";')
    text = text.replace('const STORE = "ux-chapter-01-v001:";', 'const STORE = "blender-chapter-pages-v001:";')
    text = text.replace('  const first = C.sections[0].id;', '  let first = C.sections[0].id;')
    text = text.replace('  if (read("nav-hidden") === "1")', '  expanded.add(C.id);\n  if (read("nav-hidden") === "1")')
    start=text.index('  function sectionLink(')
    end=text.index('  function renderNavigation()', start)
    text=text[:start]+'''  function sectionLink(a,chapterId,sectionId){
    a.href=chapterId==="ch00"?"/legacy.html#engineering/ch00/"+sectionId:"#engineering/"+chapterId+"/"+sectionId;
    a.onclick=e=>{
      if(chapterId==="ch00")return;
      closeDrawer();
      if(C.id===chapterId&&currentId===sectionId){e.preventDefault();scrollTo({top:0,behavior:"smooth"});}
    };
  }
''' + text[end:]
    text=text.replace('$("nav-total").textContent = "0 / " + O.mainSteps + " 小步已確認";', '$("nav-total").textContent = (progressLoaded?O.chapters.reduce((n,c)=>n+countDone(c),0):"—") + " / " + O.mainSteps + " 小步已確認";')
    text=text.replace('草稿顯示值，未連接學習進度', '與聊天共用進度；閱讀本頁不會自動確認')
    text=text.replace('"0 / " + c.steps + " 小步已確認"', '(progressLoaded?countDone(c):"—") + " / " + c.steps + " 小步已確認"')
    text=text.replace('(c.reference ? "" : "0/" + s.steps)', '(c.reference?"":(progressLoaded?countDone(c,[window.SECTIONS[s.id]?.prep,...(window.SECTIONS[s.id]?.steps||[])].filter(Boolean).map(x=>x.stepId)):"—")+"/"+s.steps)')
    text=text.replace('document.title=title+"（小節頁草稿）";', 'document.title=title+" · Blender 工程學習";')
    text=text.replace('    currentId=location.hash.slice(1) || first;', '''    if(/^#(?:journal|versions|lesson)/.test(location.hash)){location.replace("/legacy.html"+location.hash);return;}
    const route=/^#engineering\\/(ch\\d{2})(?:\\/(\\d{2}-\\d{2}))?$/.exec(location.hash);
    if(route?.[1]==="ch00"){location.replace("/legacy.html"+location.hash);return;}
    const oldChapter=C.id;
    C=O.chapters.find(c=>c.id===(route?.[1]||"ch01"))||O.chapters.find(c=>c.id==="ch01");
    if(C.id!==oldChapter)expanded.add(C.id);
    first=C.sections[0].id;
    currentId=route?.[2] || (location.hash&&!route?"missing-section":first);''')
    text=text.replace('      (S.steps || []).forEach((s,i)=>renderCard({kind:"step",...s},i+1,seen));', '''      (S.steps || []).forEach((s,i)=>renderCard({kind:"step",...s},i+1,seen));
      if(!S.steps.length&&!S.prep){
        const panel=document.createElement("section");panel.className="empty-state";
        panel.innerHTML="<p>本節完整操作與既有紀錄保留在原版教材。</p><p><a href=\\"/legacy.html#engineering/"+C.id+"/"+S.id+"\\">開啟本節完整教材 →</a></p>";
        $("steps").append(panel);
      }''')
    text=text.replace('href="#\'+escape(first)+\'"', 'href="#engineering/\'+escape(C.id)+\'/\'+escape(first)+\'"')
    # The source-link target stays per-section; the existing record system retains all note/version forms.
    text=text.replace('版面樣稿：不寫入學習進度', '正式教材')
    text=text.replace('<span class="badge">正式教材</span>', '<span class="badge" id="release-version">正式教材</span><a id="legacy-section" href="/legacy.html">原版操作／確認／筆記 →</a>')
    text=text.replace('document.title=title+" · Blender 工程學習";', 'document.title=title+" · Blender 工程學習";document.getElementById("legacy-section").href="/legacy.html#engineering/"+C.id+"/"+currentId;')

    text=text.replace('<div id="chapters"></div>', '''<div class="portal-tools"><span id="progress-status" role="status">共用進度讀取中…</span><button id="refresh-progress" type="button">重新讀取進度</button><a href="/legacy.html#journal">學習紀錄</a><a href="/legacy.html#versions">檔案版本</a><a href="/legacy.html">原版教材查閱</a></div><div id="chapters"></div>''')
    text=text.replace('</style>', '.portal-tools{display:grid;gap:5px;margin:14px 0;font-size:13px}.portal-tools button{justify-self:start}.record-link{font-size:13px}body.nav-hidden .portal-tools{display:none}\n</style>')
    text=text.replace('  render();\n})();', '''  document.getElementById("refresh-progress").onclick=()=>refreshProgress();
  window.addEventListener("focus",()=>refreshProgress());
  document.addEventListener("visibilitychange",()=>{if(!document.hidden)void refreshProgress();});
  render();
})().catch(error=>{
  document.getElementById("title").textContent="教材暫時無法開啟";
  document.getElementById("key").textContent=error.message;
  document.getElementById("steps").innerHTML='<a href="/legacy.html">開啟原版教材查閱</a>';
});''')
    assert 'src="sections/' not in text and 'src="course-outline' not in text
    assert 'const O = window.OUTLINE' not in text
    return text

def make_assets(source):
    """Keep the formal server's script-src/style-src 'self' policy intact."""
    text=make_page(source)
    css=re.search(r'<style>([\s\S]*?)</style>',text).group(1)
    script=re.search(r'<script>([\s\S]*?)</script>',text).group(1)
    start=script.index('    box.innerHTML=')
    end=script.index('    box.tabIndex=',start)
    script=script[:start]+'''    box.innerHTML='<img src="'+escape(EVIDENCE_BASE+fig.path)+'" alt="'+escape(fig.caption)+'" width="'+w+'" height="'+h+'" loading="eager">';
    for(const m of fig.marks||[]){
      const [x,y,mw,mh]=m.box,mark=document.createElement("div"),badge=document.createElement("span");
      mark.className="mark"+(y<16?" below":"");mark.dataset.n=m.n;
      Object.assign(mark.style,{left:(x/w*100)+"%",top:(y/h*100)+"%",width:(mw/w*100)+"%",height:(mh/h*100)+"%"});
      badge.textContent=m.n;mark.append(badge);box.append(mark);
    }
''' + script[end:]
    script=script.replace(' style="margin:0"','')
    css+='\n.figure{margin:0}\n'
    text=re.sub(r'<style>[\s\S]*?</style>','<link rel="stylesheet" href="/chapter-pages-v001.css">',text,count=1)
    text=re.sub(r'<script>[\s\S]*?</script>','<script src="/chapter-pages-v001.js" defer></script>',text,count=1)
    return text,css,script
