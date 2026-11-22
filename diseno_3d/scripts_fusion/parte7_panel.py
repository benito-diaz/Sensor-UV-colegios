# Parte 7: panel solar deslizante. Rieles laterales unidos al techo, entrada por el extremo alto,
# cierre en cola de milano que entra de lado (sin tornillos) con un retén a presión.
O=occs()
tc=O['Techo solar'].component
tB=tc.bRepBodies.item(0)
T=math.radians(20.0); cT=math.cos(T); sT=math.sin(T)
def S(x,s,h): return P(x/10.0, (-24.0+s*cT-h*sT)/10.0, (104.0+s*sT+h*cT)/10.0)
SDIR=adsk.core.Vector3D.create(0,cT,sT); HDIR=adsk.core.Vector3D.create(0,-sT,cT)
def plane3(comp, a, b, c, name):
    hs=comp.sketches.add(comp.xYConstructionPlane); hs.name='Puntos '+name; hs.isVisible=False
    pts=[hs.sketchPoints.add(hs.modelToSketchSpace(p)) for p in (a,b,c)]
    pi=comp.constructionPlanes.createInput(); pi.setByThreePoints(pts[0],pts[1],pts[2])
    pl=comp.constructionPlanes.add(pi); pl.isLightBulbOn=False
    s=comp.sketches.add(pl); s.name=name; return s
def planeH(comp,h,name): return plane3(comp,S(0,0,h),S(10,0,h),S(0,10,h),name)
def planeSs(comp,s0,name): return plane3(comp,S(0,s0,0),S(10,s0,0),S(0,s0,10),name)
def polyP(s,pts):
    q=[s.modelToSketchSpace(p) for p in pts]; L=s.sketchCurves.sketchLines; lines=[]
    for i in range(len(q)):
        a=lines[-1].endSketchPoint if lines else q[0]
        b=lines[0].startSketchPoint if i==len(q)-1 else q[i+1]
        lines.append(L.addByTwoPoints(a,b))
def extD(comp,s,profs,dirv,dist,op,bodies,name):
    n=s.xDirection.crossProduct(s.yDirection)
    coll=adsk.core.ObjectCollection.create()
    for p in profs: coll.add(p)
    ei=comp.features.extrudeFeatures.createInput(coll,op)
    dr=adsk.fusion.ExtentDirections.PositiveExtentDirection if n.dotProduct(dirv)*dist>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(abs(dist)/10.0)),dr)
    if bodies: ei.participantBodies=bodies
    f=comp.features.extrudeFeatures.add(ei); f.name=name; return f
def rectH(comp,h0,h1,x0,x1,s0,s1,op,name):
    s=planeH(comp,h0,name)
    polyP(s,[S(x0,s0,h0),S(x1,s0,h0),S(x1,s1,h0),S(x0,s1,h0)])
    return extD(comp,s,allprofs(s),HDIR,h1-h0,op,[tc.bRepBodies.item(0)],name)

# 1. quitar las pestanas traseras (las delanteras quedan como tope)
rectH(tc,3.95,6.0,-41.0,11.0,103.0,108.0,CUT,'Quitar pestanas traseras')
# 2. entrada del panel por el extremo alto (incluye la pared izquierda para que pase el cierre)
rectH(tc,1.4,4.3,-58.0,25.6,105.0,114.0,CUT,'Entrada panel')
# 3. refuerzo bajo el extremo alto para alojar la cola de milano
rectH(tc,-3.0,0.1,-57.5,26.0,104.0,113.0,JOIN,'Refuerzo cierre panel')
# 4. rieles laterales unidos al techo (labio 1 mm sobre el panel, 0,35 mm de holgura)
s=planeSs(tc,2.75,'Riel panel izquierdo')
polyP(s,[S(-57.5,2.75,4.0),S(-55.0,2.75,4.0),S(-55.0,2.75,4.2),S(-54.0,2.75,4.2),S(-54.0,2.75,5.4),S(-57.5,2.75,5.4)])
extD(tc,s,allprofs(s),SDIR,105.0-2.75,JOIN,[tc.bRepBodies.item(0)],'Riel panel izquierdo')
s=planeSs(tc,2.75,'Riel panel derecho')
polyP(s,[S(28.0,2.75,4.0),S(25.6,2.75,4.0),S(25.6,2.75,4.2),S(24.6,2.75,4.2),S(24.6,2.75,5.4),S(28.0,2.75,5.4)])
extD(tc,s,allprofs(s),SDIR,113.0-2.75,JOIN,[tc.bRepBodies.item(0)],'Riel panel derecho')
# 5. ranura en cola de milano atravesada (abierta a la izquierda, cerrada en x 24)
s=sk(tc,'x',24.0,'Ranura cola milano cierre')
polyP(s,[S(24.0,106.5,1.5),S(24.0,111.5,1.5),S(24.0,112.5,-1.6),S(24.0,105.5,-1.6)])
ext(tc,s,allprofs(s),'x',24.0,-59.0,CUT,[tc.bRepBodies.item(0)],'Ranura cola milano cierre')
# 6. la pasada del cable del panel se alarga hasta el borde para que el cable avance con el panel
rectH(tc,-3.5,1.5,-55.0,-48.2,95.0,114.0,CUT,'Pasada cable panel alargada')
# 7. hoyito del reten en el fondo de la ranura
rectH(tc,-2.2,-1.6,17.5,21.5,107.5,110.5,CUT,'Hoyo reten cierre')

# 8. pieza de cierre (nueva)
oc=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); cc=oc.component; cc.name='Cierre panel'
s=sk(cc,'x',23.5,'Perfil cierre')
polyP(s,[S(23.5,105.25,3.7),S(23.5,112.0,3.7),S(23.5,112.0,1.5),S(23.5,111.3,1.5),S(23.5,112.3,-1.4),S(23.5,105.7,-1.4),S(23.5,106.7,1.5),S(23.5,105.25,1.5)])
ext(cc,s,allprofs(s),'x',23.5,-60.5,NEWB,None,'Cierre panel')
cb=cc.bRepBodies.item(0); cb.name='Cierre panel'; cb.appearance=tc.bRepBodies.item(0).appearance
s=planeH(cc,-1.4,'Reten cierre')
polyP(s,[S(18.0,108.0,-1.4),S(21.0,108.0,-1.4),S(21.0,110.0,-1.4),S(18.0,110.0,-1.4)])
extD(cc,s,allprofs(s),HDIR,-0.4,JOIN,[cb],'Reten cierre')
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
hidefolders()
print('ok parte7', tc.bRepBodies.count, cc.bRepBodies.count)
