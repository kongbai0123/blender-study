import bpy,addon_utils,importlib,hashlib,json,os
from pathlib import Path
name='bl_ext.user_default.CAD_Sketcher';addon_utils.enable(name,default_set=True,persistent=True);assert name in bpy.context.preferences.addons
source=Path(os.environ['CAD_TRI_AUDIT_SOURCE']);expect=os.environ['CAD_TRI_AUDIT_SHA'];assert hashlib.sha256(source.read_bytes()).hexdigest()==expect
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();ref=importlib.import_module(name+'.model.sketch_ref');s=ref.get_active_sketch(bpy.context)
assert s is not None and s.solver_state=='OKAY' and s.dof==0
obj=s.target_object;attrs=obj.data.attributes;points=[list(p.vector) for p in attrs['position'].data];fixed=[v.value for v in attrs['fixed'].data];cs=[{'type':c.type,'value':getattr(c,'value',None)} for c in s.constraints.all];dims=sorted(q['value'] for q in cs if q['type']=='DISTANCE');assert sorted(q['type'] for q in cs)==['DISTANCE','DISTANCE','EQUAL','VERTICAL'];assert abs(dims[0]-float(os.environ['CAD_TRI_EXPECT_BASE']))<1e-5
pts=[q for q in points if q[0]>4];bounds=[[min(q[i] for q in pts),max(q[i] for q in pts)] for i in range(2)];assert abs(bounds[0][0]-4.8)<1e-4
report={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'blenderVersion':bpy.app.version_string,'cadSketcherVersion':importlib.import_module(name).get_addon_version(),'solver':s.solver_state,'dof':s.dof,'constraints':cs,'fixedFlags':fixed,'coordinatesXYMm':pts,'boundsXYmm':bounds,'baseDimensionMm':dims[0],'slopeDimensionMm':dims[1],'physicalPrint':None,'physicalMeasurement':None,'physicalFit':None,'limitations':['Sketch is planar XY and fixed point; it is not an XZ Screw output.','No physical fit, print, ISO thread or strength conclusion.']}
out=Path(os.environ['CAD_TRI_AUDIT_OUT']);
with out.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False))
