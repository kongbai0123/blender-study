"""Programmatically prepare 4 cylinders, 8 ribs, and cutter tools.

This is not a GUI construction tutorial. Geometry follows the parent-approved
draft; `probe_four_insert_bosses_v001.py` independently tested the same layout.
"""
import bpy
CENTRES=[(x,y) for x in (-21,21) for y in (-11,11)]
def group(name,objs):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:obj.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();objs[0].name=name
    return objs[0]
def cylinders(name,r,zmin,zmax):
    objs=[]
    for x,y in CENTRES:
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=zmax-zmin,location=(x,y,(zmin+zmax)/2))
        objs.append(bpy.context.object)
    return group(name,objs)
def ribs(name,axis):
    objs=[]
    for x,y in CENTRES:
        if axis=='X':loc=((1 if x>0 else -1)*25.75,y,-1.75);dims=(5.5,2,23.5)
        else:loc=(x,(1 if y>0 else -1)*15.75,-1.75);dims=(2,5.5,23.5)
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);objs.append(o)
    return group(name,objs)
def prepare():
    tools=[cylinders('zz_Boss_Pillars',4,-13.5,15),ribs('zz_Boss_Ribs_X','X'),ribs('zz_Boss_Ribs_Y','Y'),
           cylinders('zz_Boss_Pilot_Tools',2,6,15.5),cylinders('zz_Boss_Lid_Tools',1.7,10.5,17.5)]
    for t in tools:t.hide_set(True)
    bpy.data.objects['Body'].hide_set(False);bpy.data.objects['Lid'].hide_set(True)
    bpy.ops.object.select_all(action='DESELECT');body=bpy.data.objects['Body'];body.select_set(True);bpy.context.view_layer.objects.active=body
    bpy.context.view_layer.update()
    return tools
