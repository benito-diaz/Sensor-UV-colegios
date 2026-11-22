# Parte 2: techo solar - postes d10 simetricos con insertos, refuerzo izquierdo, tubo de cables del sensor, postes del sensor
O=occs()
tc=O['Techo solar'].component
tB=tc.bRepBodies.item(0)
T=math.radians(20.0); cT=math.cos(T); sT=math.sin(T)
def S(x,s,h): return (x, -24.0+s*cT-h*sT, 104.0+s*sT+h*cT)
def zu(y): return 104.0+(y+24.0)*math.tan(T)

for n in ['Extruir4','Extruir5','Extruir6','Extruir7','Extruir8','Extruir13','Extruir14']:
    delfeat(tc,n)
tB=tc.bRepBodies.item(0)

# drenaje de la capsula (se mantiene, sin el agujero redondo viejo)
cyls(tc,'z',118.0,131.0,[(42.0,25.5)],1.5,CUT,'Drenaje capsula',[tB])

# refuerzo bajo el panel en el lado izquierdo (para que los postes izquierdos calcen igual que los derechos)
hs=tc.sketches.add(tc.xYConstructionPlane); hs.name='Puntos plano refuerzo'
pts=[hs.sketchPoints.add(hs.modelToSketchSpace(P(*[c/10.0 for c in S(x,s,-3.0)]))) for (x,s) in [(0,0),(10,0),(0,10)]]
pi=tc.constructionPlanes.createInput(); pi.setByThreePoints(pts[0],pts[1],pts[2])
pl=tc.constructionPlanes.add(pi); pl.isLightBulbOn=False
s=tc.sketches.add(pl); s.name='Refuerzo postes izquierdos'
a=s.modelToSketchSpace(P(*[c/10.0 for c in S(-55.0,6.7,-3.0)])); b=s.modelToSketchSpace(P(*[c/10.0 for c in S(-39.0,92.0,-3.0)]))
s.sketchCurves.sketchLines.addTwoPointRectangle(a,b)
n=s.xDirection.crossProduct(s.yDirection)
hdir=adsk.core.Vector3D.create(0,-sT,cT)
ei=tc.features.extrudeFeatures.createInput(s.profiles.item(0), JOIN)
dr=adsk.fusion.ExtentDirections.PositiveExtentDirection if n.dotProduct(hdir)>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(0.43)), dr)
ei.participantBodies=[tB]
f=tc.features.extrudeFeatures.add(ei); f.name='Refuerzo postes izquierdos'

# postes d10 simetricos (x +-45, y 18 / 52)
for (x,y,left) in [(-45.0,18.0,True),(45.0,18.0,False),(-45.0,52.0,True),(45.0,52.0,False)]:
    ztop = zu(y-5.0)+0.9 if left else zu(y+5.0)+0.3
    cyls(tc,'z',100.0,ztop,[(x,y)],5.0,JOIN,'Poste techo %s y%d'%('izq' if left else 'der',int(y)),[tB])
inserts(tc,'z',100.0,1,[(-45.0,18.0),(45.0,18.0),(-45.0,52.0),(45.0,52.0)],'Insertos postes techo',[tB],deep=3.0)

# tubo rectangular para los cables del sensor (baja de la capsula y calza sobre el collarin de la caja)
s=sk(tc,'z',101.0,'Tubo cables sensor'); rect(s,'z',101.0,37.5,28.5,46.5,45.5); rect(s,'z',101.0,39.0,30.0,45.0,44.0)
ext(tc,s,ringprofs(s),'z',101.0,zu(45.5)+1.0,JOIN,[tB],'Tubo cables sensor')
s=sk(tc,'z',100.0,'Paso cables sensor'); rect(s,'z',100.0,39.0,30.0,45.0,44.0)
ext(tc,s,allprofs(s),'z',100.0,135.0,CUT,[tB],'Paso cables sensor')

# postes del sensor desde el piso de la capsula, con insertos arriba
for y in (30.0,53.0):
    cyls(tc,'z',zu(y+4.0)+0.5,145.9,[(34.5,y),(49.5,y)],4.0,JOIN,'Postes sensor y%d'%int(y),[tB])
inserts(tc,'z',145.9,-1,[(34.5,30.0),(49.5,30.0),(34.5,53.0),(49.5,53.0)],'Insertos sensor',[tB],deep=3.0)

# ranuras de enganche para la tapa del sensor
s=sk(tc,'y',40.0,'Ranuras enganche tapa sensor'); rect(s,'y',40.0,29.4,147.8,30.0,149.2); rect(s,'y',40.0,54.0,147.8,54.6,149.2)
ext(tc,s,allprofs(s),'y',40.0,50.0,CUT,[tB],'Ranuras enganche tapa sensor')
hidefolders()
print('ok parte2', tc.bRepBodies.count)
