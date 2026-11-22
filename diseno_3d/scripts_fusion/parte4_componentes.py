# Parte 4 (solo diseno con componentes): bateria contra la pared trasera, cables de bateria y sensor re-ruteados
O=occs()
bo=O['Bateria LiPo 603450 1200mAh (modelado)']
m=adsk.core.Matrix3D.create(); m.translation=adsk.core.Vector3D.create(0.0, 1.09, -0.15)
bo.transform2=m
des.snapshots.add()
cc=O['Cables'].component
def setpts(sname, pts):
    s=cc.sketches.itemByName(sname)
    sp=s.sketchCurves.sketchFittedSplines.item(0)
    assert sp.fitPoints.count==len(pts), (sname, sp.fitPoints.count)
    for i,(x,y,z) in enumerate(pts):
        fp=sp.fitPoints.item(i)
        t=s.modelToSketchSpace(P(x/10,y/10,z/10)); g=fp.geometry
        fp.move(adsk.core.Vector3D.create(t.x-g.x,t.y-g.y,t.z-g.z))
rojo=[(-48.3,60.3,70.5),(-49.3,58.3,69.8),(-49.0,52.0,68.0),(-44.5,42.0,64.5),(-39.0,32.2,61.8),(-35.8,32.2,61.8)]
negro=[(-48.3,58.7,70.5),(-49.3,57.0,68.4),(-49.0,52.0,66.4),(-44.5,42.0,62.9),(-39.0,32.2,60.2),(-35.8,32.2,60.2)]
for n in ('Bateria rojo','Bateria rojo v2'): setpts(n,rojo)
for n in ('Bateria negro','Bateria negro v2'): setpts(n,negro)
starts=[20.2,22.7,25.3]; ends=[39.5,42.0,44.5]
for k,col in enumerate(['rojo','negro','azul']):
    x0=starts[k]; xe=ends[k]; yk=36.8+2.2*k
    pts=[(x0,17.7,34.7),(x0,13.5,36.0),(x0+6.0,11.0,45.0),(42.4+1.6*k,12.0,62.0),(47.0+1.6*k,14.0,80.0),
         (47.5+1.6*k,25.0,90.5),(46.0+1.0*k,yk,95.5),(42.0,yk,99.0),(42.0,yk,133.5),(xe,50.0,139.5),
         (xe,64.0,142.5),(xe,76.6,146.3),(xe,75.6,148.2),(xe,74.0,148.8)]
    for n in ('Dupont sensor %s'%col,'Dupont sensor %s v4'%col): setpts(n,pts)
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
for f in cc.features:
    if isinstance(f, adsk.fusion.PipeFeature) and f.bodies.count:
        L=0
        print(f.name,[b.name for b in f.bodies], f.healthState)
hidefolders()
