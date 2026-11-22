# Parte 12: traba de la bateria y sus 2 postes con inserto se corren DX mm a la derecha (lejos de los postes de la LiPo Rider)
DX=4.0
O=occs()
def mover(comp, sname):
    s=comp.sketches.itemByName(sname)
    coll=adsk.core.ObjectCollection.create()
    for c in s.sketchCurves: coll.add(c)
    a=s.modelToSketchSpace(P(0,0,0)); b=s.modelToSketchSpace(P(DX/10.0,0,0))
    m=adsk.core.Matrix3D.create(); m.translation=adsk.core.Vector3D.create(b.x-a.x,b.y-a.y,b.z-a.z)
    s.move(coll,m)
cu=O['Cuerpo'].component
for n in ('Postes traba d8','Insertos traba (inserto 5x4)','Insertos traba (paso M3)'): mover(cu,n)
tc=O['Traba bateria'].component
for n in ('Traba bateria','Agujeros traba M3'): mover(tc,n)
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
b=cu.bRepBodies.item(0)
print('poste nuevo (-19,57,45.8):',b.pointContainment(P(-1.9,5.7,4.58)),' viejo (-26.5,58,49.5):',b.pointContainment(P(-2.65,5.8,4.95)))
tb=tc.bRepBodies.item(0); bb=tb.boundingBox
print('traba x %.1f..%.1f'%(bb.minPoint.x*10,bb.maxPoint.x*10))
hidefolders()
