"""Complete section layouts, scoped lesson navigation and traceable readings."""
from chapter_page_frontend_v001 import make_assets as previous_assets


def make_assets(source):
    html, css, js = previous_assets(source)
    needle = '<nav class="toc" id="toc" aria-label="本節小步"></nav>'
    assert needle in html
    html = html.replace(needle, '<details id="toc-fold" open><summary>本節操作索引</summary>' + needle + '</details>')
    js = js.replace('    $("toc").replaceChildren();$("steps").replaceChildren();',
                    '    $("toc").replaceChildren();$("steps").replaceChildren();\n'
                    '    const indexSize=(S?.steps.length||0)+(S?.prep?1:0), indexFold=$("toc-fold");\n'
                    '    indexFold.classList.toggle("long",indexSize>8);indexFold.open=indexSize<=8;\n'
                    '    indexFold.querySelector("summary").textContent="本節操作索引（"+indexSize+" 小步）";')
    js = js.replace(
        'const countDone=(chapter,ids=stepIds(chapter))=>ids.filter(id=>doneIds.has(chapter.id+":"+id)).length;',
        'const mainlineKeys=new Set(curriculum.chapters.flatMap(c=>c.steps.filter(s=>!s.track).map(s=>c.id+":"+s.id)));\n'
        '  const countDone=(chapter,ids=stepIds(chapter))=>ids.filter(id=>mainlineKeys.has(chapter.id+":"+id)&&doneIds.has(chapter.id+":"+id)).length;')
    js = js.replace('(c.reference?"":(progressLoaded?countDone',
                    '(c.reference?"":s.track?(s.track==="pending"?"實體待執行":"選修"):(progressLoaded?countDone')
    needle = '      \'<div class="source">小步代號'
    replacement = '''      (p.readings?.length?'<div class="readings"><b>程式讀值／觀察來源</b>'+p.readings.map(r=>'<p>'+escape(r.kind||'觀察紀錄')+' · '+escape(r.label||'')+'：'+escape(typeof r.value==='string'?r.value:JSON.stringify(r.value))+'</p>').join('')+'</div>':'')+
      (p.cautions?.length?'<ul class="cautions">'+p.cautions.map(x=>'<li>'+escape(x)+'</li>').join('')+'</ul>':'')+
      '<div class="source">小步代號'''
    assert needle in js
    js = js.replace(needle, replacement)
    js = js.replace('      if(!S.steps.length&&!S.prep){', '''      if(S.efficiency){
        const panel=document.createElement("details");panel.className="lesson-method";
        panel.innerHTML='<summary>'+escape(S.efficiency.title)+'</summary><p>'+escape(S.efficiency.workflow)+'</p><p>'+escape(S.efficiency.caution)+'</p><ul>'+S.efficiency.sources.map(u=>'<li><a href="'+escape(u)+'" target="_blank" rel="noopener">官方操作說明</a></li>').join('')+'</ul>';
        $("steps").append(panel);
      }
      if(!S.steps.length&&!S.prep){''')
    css += '\n.lesson-method{padding:16px 22px;background:white;border:1px solid var(--line);border-radius:14px;margin-top:16px}.lesson-method summary{cursor:pointer;font-weight:700}.readings,.cautions{font-size:13px;overflow-wrap:anywhere}.cnt{white-space:normal}#toc-fold:not(.long)>summary{display:none}#toc-fold.long{margin:14px 0}#toc-fold.long>summary{cursor:pointer;padding:10px 14px;border:1px solid var(--line);border-radius:10px;background:white;font-size:14px}\n'
    return html, css, js
