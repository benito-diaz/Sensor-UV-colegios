# Parte 9: esquina trasera izquierda del panel simplificada: sin canal al borde, sin pared de 0,2 mm, un solo agujero para el cable
O=occs()
tc=O['Techo solar'].component
T=math.radians(20.0); cT=math.cos(T); sT=math.sin(T)
def S(x,s,h): return P(x/10.0, (-24.0+s*cT-h*sT)/10.0, (104.0+s*sT+h*cT)/10.0)
HDIR=adsk.core.Vector3D.create(0,-sT,cT)
for f in [f for f in tc.features if f.isValid and f.name.startswith('Pasada cable panel alargada')]:
    delfeat(tc,f.name)
def plane3(comp, a, b, c, name):
    hs=comp.sketches.add(comp.xYConstructionPlane); hs.name='Puntos '+name; hs.isVisible=False
    pts=[hs.sketchPoints.add(hs.modelToSketchSpace(p)) for p in (a,b,c)]
    pi=comp.constructionPlanes.createInput(); pi.setByThreePoints(pts[0],pts[1],pts[2])
    pl=comp.constructionPlanes.add(pi); pl.isLightBulbOn=False
    s=comp.sketches.add(pl); s.name=name; return s
def boxH(h0,h1,x0,x1,s0,s1,op,name):
    s=plane3(tc,S(0,0,h0),S(10,0,h0),S(0,10,h0),name)
    q=[s.modelToSketchSpace(S(x0,s0,h0)),s.modelToSketchSpace(S(x1,s1,h0))]
    s.sketchCurves.sketchLines.addTwoPointRectangle(q[0],q[1])
    n=s.xDirection.crossProduct(s.yDirection)
    ei=tc.features.extrudeFeatures.createInput(s.profiles.item(0),op)
    d=h1-h0
    dr=adsk.fusion.ExtentDirections.PositiveExtentDirection if n.dotProduct(HDIR)*d>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(abs(d)/10.0)),dr)
    ei.participantBodies=[tc.bRepBodies.item(0)]
    f=tc.features.extrudeFeatures.add(ei); f.name=name; return f
# piso parejo en toda la franja izquierda bajo el panel (rellena la pared de 0,2 mm, la muesca vieja y el escalon de 0,1 mm)
boxH(0.0,1.4,-55.0,-39.0,6.7,103.3,JOIN,'Piso franja izquierda panel')
# un solo agujero rectangular para el cable del panel
boxH(-3.5,1.6,-55.0,-47.0,97.0,103.3,CUT,'Agujero cable panel')
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
hidefolders()
print('ok parte9')
