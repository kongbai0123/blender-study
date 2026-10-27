"""Small native-event tests of edit selection, Inset, Extrude, Bevel and camera view.

The factory Cube is a disposable shortcut test, not an engineering design.
Python only reads bmesh; no geometry is constructed by a Python operator.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import bmesh
import bpy
from common import Kit, PARK, PROJECT


def build(g):
    k=Kit(g)
    do,key,click,record=k.do,k.key,k.click,k.record
    out=Path(g["OUT"])
    snaps=out/"source-snapshot";snaps.mkdir()
    files=[]
    for rel in ("learning/tutor/run_demo.py","learning/tutor/blender_demo.py",
                "learning/tutor/scenarios/common.py","learning/tutor/scenarios/shortcut_mesh_probe.py"):
        target=snaps/Path(rel).name;target.write_bytes((PROJECT/rel).read_bytes())
        files.append(dict(source=rel,snapshot="source-snapshot/"+target.name,sha256=g["sha256"](str(target))))
    (snaps/"manifest.json").write_text(json.dumps(dict(files=files),indent=2)+"\n","utf-8")
    cases=[]
    memo={}

    def state():
        o=bpy.context.view_layer.objects.active
        value=dict(mode=bpy.context.mode,selectMode=list(bpy.context.scene.tool_settings.mesh_select_mode),
                   active=o.name if o else None,viewPerspective=k.view3d().region_3d.view_perspective)
        if o and o.type=="MESH" and o.mode=="EDIT":
            bm=bmesh.from_edit_mesh(o.data)
            faces=[f for f in bm.faces if f.select]
            value.update(vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),
                selectedVertices=sum(v.select for v in bm.verts),selectedEdges=sum(e.select for e in bm.edges),
                selectedFaces=len(faces),selectedFaceCenters=[list(f.calc_center_median()) for f in faces],
                selectedFaceNormals=[list(f.normal) for f in faces],
                localBounds=[[min(v.co[i] for v in bm.verts),max(v.co[i] for v in bm.verts)] for i in range(3)])
        return value

    def send(kind,**flags):
        do(lambda:key(kind,x=614,y=478,**flags),.4)

    def numeric(text):
        do(lambda:k.type_text(text),.3)
        send("RET")

    def shot(case,action,events,expected,check,step="04-04"):
        def observe():
            s=state();passed=bool(check(s))
            cases.append(dict(case=case,events=events,expected=expected,actual=s,passed=passed))
            if not passed:raise RuntimeError("Mesh shortcut failed: "+json.dumps(cases[-1]))
            return s
        record(step,case,action,observe,park=PARK)

    k.setup()
    send("NUMPAD_0")
    shot("numpad-zero-camera","數字鍵盤 0 切到場景相機視角，沒有移動相機。",["NUMPAD_0"],"CAMERA",
         lambda s:s["viewPerspective"]=="CAMERA",step="03-03")
    send("NUMPAD_1")
    send("TAB")
    send("THREE")
    shot("main-three-face-select","Edit Mode 按主鍵盤上排 3，切到面選取；不是數字鍵盤 3。",["TAB","THREE"],[False,False,True],
         lambda s:s["mode"]=="EDIT_MESH" and s["selectMode"]==[False,False,True])
    send("A",alt=True)
    shot("edit-alt-a-deselect","Edit Mode 按 Alt+A 取消全部元件選取。",["ALT_A"],0,
         lambda s:s["selectedVertices"]==0 and s["selectedEdges"]==0 and s["selectedFaces"]==0)
    do(lambda:click(614,478),.5)
    shot("select-front-face","Front 視圖點 Cube 中央，只選朝 -Y 的正面。",["CLICK",614,478],"one -Y face",
         lambda s:s["selectedFaces"]==1 and s["selectedFaceNormals"][0][1] < -.99)
    send("I")
    numeric("0.2")
    shot("inset-i","選面後按 I → 0.2 → Enter，建立內縮面；本次為出廠單位的測試值。",["I","0.2","RET"],"10 faces and one inset face",
         lambda s:s["faces"]==10 and s["selectedFaces"]==1,step="05-05")
    send("E")
    numeric("0.4")
    shot("extrude-e-normal","按 E → 0.4 → Enter，沿已選面的法向外擠出，不再重按同軸。",["E","0.4","RET"],"14 faces, selected face center Y=-1.4",
         lambda s:s["faces"]==14 and s["selectedFaces"]==1 and abs(s["selectedFaceCenters"][0][1]+1.4)<1e-5,step="05-05")
    send("TWO")
    shot("main-two-edge-select","按主鍵盤上排 2 切到邊選取，剛才面的四條邊保持選取。",["TWO"],"four selected edges",
         lambda s:s["selectMode"]==[False,True,False] and s["selectedEdges"]==4,step="07-02")
    do(lambda:memo.update(beforeBevel=state()),.1)
    send("B",ctrl=True)
    numeric("0.1")
    shot("bevel-ctrl-b","選邊後按 Ctrl+B → 0.1 → Enter，核對原生倒角產生的新面；本次不代表工程圓角半徑。",["CTRL_B","0.1","RET"],"native mesh face count increases",
         lambda s:s["faces"]>memo["beforeBevel"]["faces"] and s["vertices"]>memo["beforeBevel"]["vertices"],step="07-02")

    def finish():
        k.guard()
        images={r["slug"]:dict(path=r["file"],sha256=r["sha256"],width=r["width"],height=r["height"],recordedAt=r["recordedAt"]) for r in g["records"] if "file" in r}
        for c in cases:c["screenshot"]=images[c["case"]]
        value=dict(schemaVersion=1,kind="native_edit_mesh_shortcut_verification",runId=out.name,
            recordedAt=datetime.now(timezone.utc).isoformat(),blender=bpy.app.version_string,buildHash=bpy.app.build_hash.decode(),
            factoryStartup=True,eventSimulate=True,cases=cases,sourceSnapshot="source-snapshot/manifest.json",
            sceneUnitSystem=bpy.context.scene.unit_settings.system,sceneScaleLength=bpy.context.scene.unit_settings.scale_length,
            sceneSaved=False,engineeringDimensionsVerified=False,learnerCompletionAssessed=False,physicalFitAssessed=False,
            workspaceWriteAttribution=None,workspaceContentsComparison="See runner-status; not proof of no intervening writes")
        (out/"mesh-shortcut-verification-v001.json").write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n","utf-8")
    do(finish,.1)
