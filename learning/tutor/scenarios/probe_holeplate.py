"""獨立探測 Boolean 修改器的真實介面；不匯入教材。"""
import bpy
from common import Kit, PARK


def build(g):
    k=Kit(g)
    k.setup()
    k.add_mesh(80)
    k.click_outliner("Cube")
    k.do(lambda:k.click(1245,503),0.5)
    k.do(lambda:k.key("F3",x=700,y=600),0.5)
    k.do(lambda:k.type_text("Add Boolean Modifier"),0.7)
    k.record("05-03","search","搜尋 Add Boolean Modifier",lambda:k.selection())
    k.do(lambda:k.key("RET"),1.0)
    k.record("05-03","modifier","讀取 Boolean 修改器與物件欄位",lambda:str([(m.name,m.type) for m in bpy.data.objects['Cube'].modifiers]),park=PARK)
