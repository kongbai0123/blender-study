"""Make the evidence role visible instead of implying every image proves an action."""
from chapter_page_frontend_v002 import make_assets as previous_assets


def make_assets(source):
    html, css, js = previous_assets(source)
    needle = '    const p=document.createElement("p"); p.className="caption";'
    assert needle in js
    js = js.replace(needle, '''    const scope=curriculum.chapterPages.evidenceRoles?.[figs[k].evidenceRole];
    if(scope){
      const note=document.createElement("p");note.className="evidence-scope";note.dataset.role=figs[k].evidenceRole;
      const label=document.createElement("b");label.textContent=scope.label;
      note.append(label,document.createTextNode(" · "+scope.description));el.append(note);
    }
''' + needle)
    css += '\n.evidence-scope{font-size:13px;line-height:1.6;padding:8px 10px;background:#fff8ee;border-left:3px solid #c45b1b;overflow-wrap:anywhere}.evidence-scope b{font-weight:700}\n'
    return html, css, js
