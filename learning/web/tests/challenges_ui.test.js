'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class Element {
  constructor(tag='div') { this.tag=tag; this.value=''; this.children=[]; this.listeners={}; this.disabled=false; this.hidden=false; this.textContent=''; this.attrs={}; }
  addEventListener(name, callback) { this.listeners[name]=callback; }
  replaceChildren(...children) { this.children=children; }
  append(...children) { this.children.push(...children); }
  setAttribute(name, value) { this.attrs[name]=value; }
  trigger(name) { this.listeners[name]({preventDefault(){}}); }
}
class Option extends Element { constructor(label,value){super('option');this.textContent=label;this.value=value;} }
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../challenges/challenges-v005.json'),'utf8'));
async function fixture(chapter, mutateManifest = () => {}) {
  const ids=['record-message','loading','challenge','chapter-label','title','goal','deliverable','evidence-status','requirements','checks','limitations','chapter-nav','drawing-status','drawing-view','drawing-link','drawing-image','hints','screenshot-view','screenshot-missing','screenshot','screenshot-link','screenshot-caption','screenshot-hash','extra-demos','source-links','version-block','workspace-hint','confirm-source','version-file','version-submit','confirm-submit','note-submit','record-refresh','record-status','version-list','confirmation-history','note-list','version-form','confirm-form','note-form','confirmation','stuck-note'];
  const elements=Object.fromEntries(ids.map(id=>[id,new Element()]));
  const copy=structuredClone(manifest); mutateManifest(copy);
  let data={progress:{revision:8,events:[],fileVersions:[]},files:[]}, interval, posts=[], response;
  const fetch=async (url,options) => {
    if(url==='/challenges/manifest.json') return {ok:true,json:async()=>copy};
    if(options?.method==='POST'){posts.push({url,body:JSON.parse(options.body)});return response||{ok:true,json:async()=>({})};}
    return {ok:true,json:async()=>structuredClone(data)};
  };
  const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
  const code=fs.readFileSync(path.join(__dirname,'../challenges/app.js'),'utf8');
  vm.runInNewContext(code,{document,Option,fetch,URLSearchParams,location:{search:'?chapter='+chapter,replace(){}},setInterval:fn=>{interval=fn;}});
  await tick(); await tick();
  return {elements, setData:x=>{data=x;}, poll:()=>interval(), posts:()=>posts, conflict:()=>{response={ok:false,status:409,json:async()=>({error:'changed'})};}};
}

test('實際 manifest 的各題提示連結、圖片與來源顯示正確',async()=>{
  for(const chapter of ['ch01','ch05','ch08','ch11']){
    const f=await fixture(chapter), e=f.elements, record=manifest.chapters.find(x=>x.chapterId===chapter);
    assert.equal(e.title.textContent,record.title); assert.equal(e.hints.children.length,3);
    assert.equal(e.hints.children[0].children[2].href,`/#engineering/${chapter}/${record.hints[0].section}`);
    assert.match(e.screenshot.src,/^\/files\/learning\/evidence\//); assert.equal(e['screenshot-view'].hidden,false);
    assert.match(e['screenshot-caption'].textContent,/並非本題完整示範/);
    assert.equal(e['drawing-view'].hidden,!record.drawing);
    if(record.drawing) assert.equal(e['drawing-image'].src,record.drawing.path);
  }
});

test('個人工作區與工程工作區對應檔案及註冊 API',async()=>{
  for(const [chapter,owner,workspace] of [['ch05',{lessonId:'05'},'05'],['ch08',{workspaceId:'engineering-parametric'},'engineering-parametric']]){
    const f=await fixture(chapter),e=f.elements,file=`learning/workspaces/${workspace}/fixture.blend`;
    f.setData({progress:{revision:9,events:[],fileVersions:[]},files:[{path:file,bytes:5,registered:false}]});f.poll();await tick();
    e['version-file'].value=file;e['version-file'].trigger('change');assert.equal(e['version-submit'].disabled,false);
    e['version-form'].trigger('submit');await tick();await tick();
    assert.equal(f.posts()[0].url,'/api/register-file');assert.equal(f.posts()[0].body.path,file);
    for(const [key,value] of Object.entries(owner))assert.equal(f.posts()[0].body[key],value);
    assert.equal(f.posts()[0].body.expectedRevision,9);
  }
  const f=await fixture('ch02'); assert.equal(f.elements['version-block'].hidden,true);assert.equal(f.elements['confirm-source'].disabled,true);
});

test('更新與 revision 衝突保留使用者草稿、不自動重送',async()=>{
  const f=await fixture('ch05'),e=f.elements;e.confirmation.value='未送出的回報';e['stuck-note'].value='未送出的筆記';
  f.setData({progress:{revision:9,events:[],fileVersions:[]},files:[]});f.poll();await tick();
  assert.equal(e.confirmation.value,'未送出的回報');assert.equal(e['stuck-note'].value,'未送出的筆記');
  f.conflict();e['confirm-form'].trigger('submit');await tick();await tick();
  assert.equal(f.posts().length,1);assert.equal(f.posts()[0].body.challengeId,'ch05-fit-coupon-v001');
  assert.equal(e.confirmation.value,'未送出的回報');assert.match(e['record-message'].textContent,/自行重送/);
});

test('不受信任的圖片與小節路徑不會成為連結',async()=>{
  const f=await fixture('ch05',copy=>{let r=copy.chapters.find(x=>x.chapterId==='ch05');r.screenshot.path='learning/evidence/../../private.png';r.drawing.path='//evil.test/payload.svg';r.hints[0].section='../../bad';r.title='<img src=x onerror=alert(1)>';});
  const e=f.elements;assert.equal(e.title.textContent,'<img src=x onerror=alert(1)>');
  assert.equal(e['screenshot-view'].hidden,true);assert.equal(e['drawing-view'].hidden,true);
  assert.equal(e.hints.children[0].children.length,2);
});

test('額外示範只允許本地 evidence 原圖與摘要路徑',async()=>{
  const f=await fixture('ch11',data=>{const item=data.chapters.find(x=>x.chapterId==='ch11');item.extraDemos=[{title:'真實示範',description:'程式建網，GUI 檢查',screenshot:{path:'learning/evidence/08/example.png',sha256:'abc',caption:'原圖'},summaryPath:'learning/evidence/08/summary.json'},{title:'不安全資料',description:'文字',screenshot:{path:'https://example.com/evil.png'},summaryPath:'learning/evidence/../../private.json'}];});
  const [good,bad]=f.elements['extra-demos'].children;
  assert.equal(good.children[2].href,'/files/learning/evidence/08/example.png');
  assert.equal(good.children.at(-1).href,'/files/learning/evidence/08/summary.json');
  assert.equal(bad.children.length,2);
});

test('第 03 章在同一練習題頁：沿用試教題紀錄、顯示動畫並送出 pilot 動作',async()=>{
  const f=await fixture('ch03'), e=f.elements, record=manifest.chapters.find(x=>x.chapterId==='ch03');
  assert.equal(e.title.textContent,record.title);
  assert.ok(e['chapter-nav'].children.every(a=>a.href.startsWith('/challenges/index.html?chapter=')));
  const animation=e['extra-demos'].children[0];
  assert.equal(animation.children[0].textContent,record.animation.title);
  assert.equal(animation.children[2].children[0].src,'/pilot/box-demo.gif');
  assert.equal(animation.children[4].href,'/files/learning/evidence/04/2026-10-28-pilot-box-move-record-v002/pilot-01-before.png');
  f.setData({progress:{revision:9,events:[{type:'pilot_challenge_confirmed',author:'learner',challengeId:'box-opening-v001',evidence:'完成'},{type:'pilot_challenge_note',author:'tutor',challengeId:'box-opening-v001',text:'提示'}],fileVersions:[]},files:[]});
  await f.poll(); await tick();
  assert.match(e['record-status'].textContent,/本題已由學員確認/);
  assert.equal(e['note-list'].children.length,1);
  f.setData({progress:{revision:9,events:[],fileVersions:[]},files:[]});
  const g=await fixture('ch03');
  g.elements['stuck-note'].value='卡住'; g.elements['note-form'].trigger('submit'); await tick(); await tick();
  assert.equal(g.posts()[0].body.action,'pilot_note');
  g.elements.confirmation.value='做好了'; g.elements['confirm-form'].trigger('submit'); await tick(); await tick();
  assert.equal(g.posts()[1].body.action,'pilot_confirm');
  assert.equal(g.posts()[1].body.challengeId,'box-opening-v001');
});

test('動畫只接受 /pilot/ 下的 GIF',async()=>{
  const f=await fixture('ch03',copy=>{copy.chapters.find(x=>x.chapterId==='ch03').animation.path='https://example.com/x.gif';});
  assert.equal(f.elements['extra-demos'].children.length,0);
});
