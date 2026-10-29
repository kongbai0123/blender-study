/* Render all current steps/tabs without writing learner state or operating a browser.
 * Browser visits and visual review are separate evidence, never inferred here.
 */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const [curriculumFile, pathFile, outputFile] = process.argv.slice(2);
if (!curriculumFile || !pathFile || !outputFile) throw Error('arguments: curriculum.json path.json NEW-output.json');
if (fs.existsSync(outputFile)) throw Error('refusing to overwrite report');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const data = read(curriculumFile), route = read(pathFile), catalog = read(path.join(__dirname, 'catalog.json'));
const progressFile = path.join(__dirname, 'progress.json'), before = sha(progressFile);
const sandbox = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname, 'web/engineering-path.js'), 'utf8'), sandbox);
const renderer = sandbox.BlenderEngineeringPath;
const bootstrap = {catalog, progress:{revision:8,events:[],lessons:{}}};
const tabs = ['detail','figures','shortcuts','record','notes','help'];
const sources = new Map(catalog.lessons.flatMap(l => l.steps.map(s => [`${l.id}:${s.id}`, s])));
const items = [], assets = new Map();
for (const chapter of data.chapters) {
  for (const step of chapter.steps.filter(s => s.track !== 'appendix')) {
    const findings = [];
    for (const key of ['title','goal','context','success']) if (!step[key]) findings.push('missing '+key);
    if (!Array.isArray(step.actions) || !step.actions.length) findings.push('missing actions');
    if (!Array.isArray(step.detail?.steps) || !step.detail.steps.length || !step.detail.why) findings.push('missing instructional detail or rationale');
    for (const source of step.sourceSteps || []) if (!sources.has(`${source.lessonId}:${source.stepId}`)) findings.push('missing original source');
    const rendered = {};
    for (const tab of tabs) {
      const html = renderer.render(route,bootstrap,chapter.id,{data},{section:step.section,step:step.id,tab});
      if (!html.includes(`data-curriculum-step="${escape(step.id)}"`)) findings.push('step not rendered: '+tab);
      if (tab === 'detail' && html.includes('本章的詳細步驟還沒改寫')) findings.push('visible unfinished-detail fallback');
      if (tab === 'record' && step.evidenceStatus === 'existing_demo' && !step.figures?.some(image => image.type === 'screenshot') && !/<img\b|<a\b[^>]*href="\/files\//.test(html)) findings.push('demo is claimed but neither a reference image nor a record/download is available');
      for (const match of html.matchAll(/(?:href|src)="(\/files\/[^"#]+)"/g)) {
        const rel = decodeURIComponent(match[1].slice('/files/'.length));
        const absolute = path.resolve(root, rel);
        const inside = !path.relative(root, absolute).startsWith('..') && !path.isAbsolute(path.relative(root, absolute));
        if (!inside || !fs.existsSync(absolute)) findings.push('broken rendered evidence URL: '+match[1]);
        else assets.set(match[1], {path:rel,sha256:sha(absolute)});
      }
      rendered[tab] = {htmlBytes:Buffer.byteLength(html),instructionalFallback:html.includes('本章的詳細步驟還沒改寫')};
    }
    for (const artifact of [...(step.figures||[]),...(step.artifacts||[])]) {
      if (artifact.path && artifact.sha256) {
        const file=path.resolve(root,artifact.path);
        if (!fs.existsSync(file) || sha(file)!==artifact.sha256) findings.push('evidence hash mismatch: '+artifact.path);
      }
    }
    items.push({chapter:chapter.id,section:step.section,step:step.id,track:step.track||'main',tabs:rendered,findings});
  }
}
if (sha(progressFile)!==before) throw Error('learner progress changed');
const output={schemaVersion:1,scope:'Standalone real renderer for every non-appendix step and six tabs; not browser navigation, full original-catalog app callback, screenshot visual review, Blender re-execution or physical testing.',
  sources:[curriculumFile,pathFile,path.join(__dirname,'web/engineering-path.js')].map(p=>({path:path.relative(root,p).replaceAll('\\','/'),sha256:sha(p)})),
  counts:{chapters:data.chapters.length,sections:data.chapters.reduce((sum,c)=>sum+c.sections.length,0),steps:items.length,tabRenders:items.length*tabs.length,uniqueRenderedFileUrls:assets.size,stepsWithFindings:items.filter(s=>s.findings.length).length},
  learnerProgressBeforeSha256:before,learnerProgressAfterSha256:sha(progressFile),assets:[...assets.values()],items};
fs.mkdirSync(path.dirname(outputFile),{recursive:true});fs.writeFileSync(outputFile,JSON.stringify(output,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(output.counts));
for (const item of items.filter(s=>s.findings.length)) console.log(item.step+': '+item.findings.join('; '));
