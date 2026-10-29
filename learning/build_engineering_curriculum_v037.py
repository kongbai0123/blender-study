"""Apply source/browser correspondence corrections, preserving all learner IDs."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT/'learning/web/engineering-curriculum-v036.json'
SOURCE_SHA = 'fceaf4cc951316bfa5e827cd2a4d2bebb713318ecb7f909ad646ba216975db09'
OUTPUT = ROOT/'learning/web/engineering-curriculum-v037.json'
PATCHES = [
    ('learning/patches/2026-10-29-ch01-ch04-corrections-v001.json','6737fbf2946232453ca1ba322ade1d1a73735fad16bc442ebd10052c5a86b0e5'),
    ('learning/patches/2026-10-29-ch05-ch08-corrections-draft-v001.json','b195b6e42df0926d526b3cefe59e0fda68dd2524e55e09284ff07625e9659989'),
    ('learning/patches/2026-10-29-ch09-ch12-keyed-corrections-v001.json','e96eb4df892c88f7d039f065d32b273ec7f1e26ae21a743f28a497d1648b942e'),
    ('learning/patches/2026-10-29-ch11-final-guidance-v001.json','e647a0fb6138d362fb47ff4f6fb00ed26c30580ee3bcf9b7d2842ed8ce2461fa'),
    ('learning/patches/2026-10-29-mount-prefab-and-prereq-v001.json','f6a2129f6b77f2c87493cc5a3ffc16a4767ea06fa92644544db34fab33d056cd'),
]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path, digest):
    if sha(ROOT/path) != digest:
        raise ValueError('source changed: '+path)


def artifact(path, label, kind=None):
    result={'path':path,'sha256':sha(ROOT/path),'label':label}
    if kind: result['type']=kind
    return result


def bind_demonstrations(data):
    """Bind named source fields, never infer observation kind from prose."""
    steps={s['id']:s for c in data['chapters'] for s in c['steps']}
    bound=[]
    for source in data['sourceVersions']:
        if not source['path'].startswith('learning/lesson11_') or 'optional_steps' not in source['path']:
            continue
        verify(source['path'],source['sha256'])
        document=read(ROOT/source['path'])
        for record in document['steps']:
            identifier='ch11-'+record['id'].lower()
            step=steps.get(identifier)
            photo=record.get('screenshot',{})
            if not step or photo.get('sha256') not in {f.get('sha256') for f in step.get('figures',[])}:
                continue
            if identifier in bound: raise ValueError('ambiguous demonstration source')
            raw_path=photo.get('path',photo.get('relativePath'))
            verify(raw_path,photo['sha256'])
            if 'programReadback' in record:
                values=[{'label':'本次示範程式讀回','kind':'readback','value':copy.deepcopy(record['programReadback'])}]
                value=record['programReadback']
                payloads=[value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)]
            else:
                values=[{'label':item['location'],'kind':'readback','value':item['value']} for item in record['readings']]
                payloads=[item['location']+'：'+item['value'] for item in record['readings']]
            step['demonstration']={
                'recordId':record['id'], 'source':copy.deepcopy(source),
                'scope':'本步原圖及讀值屬同一筆獨立示範資料；GUI 與程式準備的範圍依「操作前」和「注意」說明。不是學員結果或實體合格判定。',
                'readings':values,
                'figures':[{'type':'screenshot','path':raw_path,'sha256':photo['sha256'],
                            'caption':'本筆示範的原始 Blender 畫面；數值能否直接看見，依本步成功條件和讀值說明核對。'}],
            }
            # Move only the exact lines produced by the known prior builders;
            # no prose-based guessing or reclassification of observations.
            known={prefix+value for prefix in ('示範讀值：','示範程式讀值：') for value in payloads}
            step['detail']['steps']=[line for line in step['detail']['steps'] if line not in known]
            bound.append(identifier)
    return bound


def main():
    if OUTPUT.exists(): raise FileExistsError('refusing to overwrite '+OUTPUT.name)
    verify(SOURCE.relative_to(ROOT).as_posix(),SOURCE_SHA)
    data=read(SOURCE)
    chapters={c['id']:c for c in data['chapters']}
    steps={s['id']:s for c in data['chapters'] for s in c['steps']}
    updated=[];sources=[]
    for path,digest in PATCHES:
        verify(path,digest);patch=read(ROOT/path)
        sources.append({'path':path,'sha256':digest})
        for identifier,changes in patch['patches'].items():
            if identifier not in steps: raise ValueError('unknown correction '+identifier)
            steps[identifier].update(copy.deepcopy(changes));updated.append(identifier)
        for identifier,changes in patch.get('chapterPatches',{}).items():
            chapters[identifier].update(copy.deepcopy(changes))
    bindings=bind_demonstrations(data)
    numeric_step=steps['ch11-11-cad-thread-07']
    numeric_step['actions']=[text.replace('輸入 約 1.2369316 mm','輸入 1.2369316 mm（此為近似值）') for text in numeric_step['actions']]
    numeric_step['detail']['steps']=[text.replace('輸入 約 1.2369316 mm','輸入 1.2369316 mm（此為近似值）') for text in numeric_step['detail']['steps']]
    summary_path='learning/evidence/parametric/2026-10-29-manual-guard-70x40-reject-v004/safe-summary-v001.json'
    summary=read(ROOT/summary_path);records={r['slug']:r for r in summary['records']}
    step=steps['ch08-manual-guard-y-reject-01']
    step['demonstration']={
        'recordId':'y80-refused','source':{'path':summary_path,'sha256':sha(ROOT/summary_path)},
        'scope':'新場次從70×40未登記副本提出W80；副本、外掛及外部文字由程式準備，Alt+P與尺寸提案／提交為GUI事件。不是學員工作區或實體試配。',
        'readings':[{'label':'提交前（程式讀回）','kind':'readback','value':records['opened']['observed']},
                    {'label':'拒絕後（程式讀回）','kind':'readback','value':records['y80-refused']['observed']}],
        'figures':[{'type':'screenshot',**records[slug]['screenshot'],'caption':records[slug]['action']} for slug in ('y80-proposal','y80-refused')],
    }
    # Each export group has a concrete starting-version link, not an anonymous
    # instruction to open some source. Repaired geometry remains a distinct file.
    stl=read(ROOT/'learning/lesson11_stl_export_optional_steps_v002.json')
    tool='learning/tutor/inspect_stl_v001.py'
    cli_summary='learning/evidence/08/2026-10-29-stl-cli-readback-v001/safe-summary-v002.json'
    if not (ROOT/cli_summary).is_file(): raise ValueError('missing current CLI readback')
    for item in stl['items']:
        start=steps['ch11-11-stl-'+item['id']+'-01']
        verify(item['sourceScene'],item['sourceSha256'])
        start['context'] += ' 本組來源：'+item['sourceScene']+'；SHA-256 '+item['sourceSha256']+'。先保護自己的目前檔案並另存副本。'
        start.setdefault('artifacts',[]).append(artifact(item['sourceScene'],'本組起始場景（請先複製）'))
        parse=steps['ch11-11-stl-'+item['id']+'-04']
        parse.setdefault('artifacts',[]).extend([artifact(tool,'本機唯讀 STL 檢查工具','python-script'),
                                               artifact(cli_summary,'新增 CLI 的六件實檔讀值（非原GUI場次）')])
        parse['limitations'].append('新 CLI 是標準 Python 唯讀方法；原圖片是助教 GUI 匯出當時畫面，並非終端機操作截圖。')
    repaired_note='11-17 的側盒與側帽另經三角化修訂；題目頁原有工程圖對應修訂前網格。局部曲面有改變，不能把舊圖當新版STL完全等同證明。'
    for step in chapters['ch11']['steps']:
        if step.get('section') in ('11-12','11-15','11-17'):
            step.setdefault('limitations',[]).append(repaired_note)
    chapters['ch08']['detailNote']='各節使用的基準副本與不同示範時點已在操作前說明；受控面板9步有對應詳述，超界W80已另從70×40副本重演。範本計算範圍不是製造合格範圍。'
    for step in steps.values():
        if step.get('track')=='appendix': continue
        if step.get('limitations'):
            step['limitations']=list(dict.fromkeys(step['limitations']))
        if not step.get('detail',{}).get('steps') or not step['detail'].get('why'):
            raise ValueError('unfinished detail: '+step['id'])
        if any('本章的詳細步驟還沒改寫' in line for line in step['detail']['steps']):
            raise ValueError('unfinished placeholder: '+step['id'])
        for f in step.get('figures',[])+step.get('artifacts',[])+step.get('demonstration',{}).get('figures',[]):
            if f.get('path') and f.get('sha256'): verify(f['path'],f['sha256'])
    data['version']='v037 · 2026-10-29'
    data['description'] += ' v037 依實頁及證據對照修正操作與基準銜接，補受控面板詳述／70×40超界實拍／STL唯讀CLI，並將本步獨立讀值放回示範紀錄。'
    data['sourceVersions'] += [{'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':SOURCE_SHA}]+sources
    data['contentReview']['reviewV037']={
        'reviewedOn':'2026-10-29','scope':'逐步主操作／詳述的人工內容校對、指定分頁實際瀏覽、447步六分頁的程式渲染與引用驗證，分別記錄；未宣稱所有歷史圖片重新逐張目視。',
        'correctedStepIds':sorted(set(updated)), 'explicitDemonstrationStepIds':bindings+['ch08-manual-guard-y-reject-01'],
        'physicalPrint':None,'physicalMeasurement':None,'physicalInstallation':None,'physicalFit':None,
        'qualifiedClearance':None,'qualifiedStrength':None,'learnerProgressChanged':False,
        'learnerProgressSha256':'b66a08f1e444a47fb6575bbf9a581450bd4a9b1041d33382fbcdd53d7ca25bc1',
    }
    OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(sha(OUTPUT),'corrected',len(set(updated)),'explicit demo sources',len(bindings)+1)


if __name__=='__main__': main()
