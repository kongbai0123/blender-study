"""Clarify the distinction between the historical detached boss and the new joined draft."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'learning/web/challenges/challenges-v003.json'
OUTPUT=ROOT/'learning/web/challenges/challenges-v004.json'
EXPECTED='c9020835ea7a8af411c8fafe48096a0b2b1bf7fa4d8c4bfe862a312de6b0825a'

def build():
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED: raise ValueError('v003 source changed')
    data=copy.deepcopy(json.loads(raw))
    item=next(x for x in data['chapters'] if x['chapterId']=='ch11')
    old='Screw 開放曲面不等於可列印封閉螺紋；盲孔柱是未接盒體草案。'
    if item['limitations'][0]!=old: raise ValueError('expected historical text differs')
    item['limitations'][0]='Screw 開放曲面不等於可列印封閉螺紋；原盲孔柱示範與後續盒體接合草案為不同版本，兩者均未完成五金或實體驗證。'
    data['version']='v004'
    data['previousVersion']={'path':'learning/web/challenges/challenges-v003.json','sha256':EXPECTED}
    return data

def main():
    if OUTPUT.exists(): raise FileExistsError('refusing to overwrite '+OUTPUT.name)
    OUTPUT.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(hashlib.sha256(OUTPUT.read_bytes()).hexdigest())

if __name__=='__main__': main()
