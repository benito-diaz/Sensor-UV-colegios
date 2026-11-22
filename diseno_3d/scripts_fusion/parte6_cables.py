# Parte 6 (solo con componentes): peineta, panel apoyado en el bolsillo, cables panel/USB/sensor
O=occs()
m=adsk.core.Matrix3D.create(); m.translation=adsk.core.Vector3D.create(0,-0.01,0)
O['Peineta dupont'].transform2=m
po=O['Panel solar 5,5V 170mA 100x80 (modelado)']
t=po.transform2; tr=t.translation
t.translation=adsk.core.Vector3D.create(tr.x, tr.y-0.0078, tr.z-0.0869)
po.transform2=t
des.snapshots.add()
cc=O['Cables'].component
def setpts(sname, pts):
    s=cc.sketches.itemByName(sname)
    sp=s.sketchCurves.sketchFittedSplines.item(0)
    if sp.fitPoints.count==len(pts)+1 and len(pts)==12: pass
    assert sp.fitPoints.count==len(pts), (sname, sp.fitPoints.count, len(pts))
    for i,(x,y,z) in enumerate(pts):
        fp=sp.fitPoints.item(i)
        tt=s.modelToSketchSpace(P(x/10,y/10,z/10)); g=fp.geometry
        fp.move(adsk.core.Vector3D.create(tt.x-g.x,tt.y-g.y,tt.z-g.z))
r13=[(-50.8,71.2,139.6),(-49.6,69.0,133.0),(-44.0,64.5,124.0),(-38.0,57.0,113.0),(-36.8,49.0,106.5),(-38.4,43.0,102.0),(-38.4,43.0,97.0),(-39.0,42.0,94.5),(-40.0,40.5,92.5),(-40.8,38.0,90.5),(-40.2,34.5,89.2),(-38.0,32.4,88.9),(-35.8,32.2,88.9)]
n13=[(-52.6,71.2,139.6),(-51.4,69.0,133.0),(-45.6,64.5,124.0),(-39.6,57.0,113.0),(-38.6,49.0,106.5),(-39.8,41.6,102.0),(-39.8,41.6,97.0),(-40.4,40.6,94.5),(-41.3,39.1,92.4),(-42.2,37.0,90.0),(-41.8,34.0,88.0),(-38.0,32.4,87.2),(-35.8,32.2,87.2)]
setpts('Panel rojo v2',r13); setpts('Panel negro v2',n13)
setpts('Panel rojo',r13[:8]+r13[9:]); setpts('Panel negro',n13[:8]+n13[9:])
setpts('Cable USB alimentacion (USB-A a micro USB)',[(42.0,31.7,80.5),(44.5,33.0,66.0),(46.0,35.5,45.0),(45.3,37.2,33.5),(42.8,37.2,28.5)])
starts=[20.2,22.7,25.3]; ends=[39.5,42.0,44.5]; mids=[40.0,42.0,44.0]
for k,col in enumerate(['rojo','negro','azul']):
    x0=starts[k]; xe=ends[k]; xm=mids[k]; yk=36.8+2.2*k
    pts=[(x0,17.7,34.7),(x0,13.5,36.0),(x0+6.0,11.0,45.0),(42.4+1.6*k,12.0,62.0),(47.0+1.6*k,14.0,80.0),
         (48.5+1.2*k,24.0,94.5),(42.8,yk,95.8),(42.0,yk,100.0),(42.0,yk,133.5),(xm,50.0,139.5),
         (xm,64.0,142.5),(xe,76.6,146.8),(xe,75.6,148.2),(xe,74.0,148.8)]
    for n in ('Dupont sensor %s'%col,'Dupont sensor %s v4'%col): setpts(n,pts)
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
for s in cc.sketches:
    if s.name.endswith('v2') or s.name.endswith('v4') or 'USB' in s.name:
        print(s.name,'largo %.0f mm'%(s.sketchCurves.sketchFittedSplines.item(0).length*10))
hidefolders()
