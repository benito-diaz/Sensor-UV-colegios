# Parte 8: panel solo deslizante (sin cierre), tope delantero continuo simple, peineta M3, frente sin pasadores, postes LiPo unidos al techo
O=occs()
tc=O['Techo solar'].component
T=math.radians(20.0); cT=math.cos(T); sT=math.sin(T)
def S(x,s,h): return P(x/10.0, (-24.0+s*cT-h*sT)/10.0, (104.0+s*sT+h*cT)/10.0)
HDIR=adsk.core.Vector3D.create(0,-sT,cT)
def byprefix(comp,pre):
    return [f for f in comp.features if f.isValid and f.name.startswith(pre)]
def delprefix(comp,pre):
    for f in byprefix(comp,pre): delfeat(comp,f.name)
def plane3(comp, a, b, c, name):
    hs=comp.sketches.add(comp.xYConstructionPlane); hs.name='Puntos '+name; hs.isVisible=False
    pts=[hs.sketchPoints.add(hs.modelToSketchSpace(p)) for p in (a,b,c)]
    pi=comp.constructionPlanes.createInput(); pi.setByThreePoints(pts[0],pts[1],pts[2])
    pl=comp.constructionPlanes.add(pi); pl.isLightBulbOn=False
    s=comp.sketches.add(pl); s.name=name; return s
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

# 1. sacar el cierre en cola de milano y todo lo suyo
if 'Cierre panel' in O: O['Cierre panel'].deleteMe()
for pre in ('Hoyo reten cierre','Ranura cola milano cierre','Refuerzo cierre panel'): delprefix(tc,pre)
# 2. la entrada ya no abre la pared izquierda; el riel izquierdo llega hasta el borde
s=tc.sketches.itemByName('Entrada panel')
for p in s.sketchPoints:
    m=s.sketchToModelSpace(p.geometry)
    if abs(m.x*10+58.0)<0.01:
        t=s.modelToSketchSpace(P(-5.5,m.y,m.z)); g=p.geometry
        p.move(adsk.core.Vector3D.create(t.x-g.x,t.y-g.y,t.z-g.z))
fr=byprefix(tc,'Riel panel izquierdo')[0]
fr.extentOne.distance.expression='-( 110.25 mm )'
# 3. tope delantero: un labio continuo igual a los rieles (reemplaza las 2 pestanas)
tB=tc.bRepBodies.item(0)
s=plane3(tc,S(0,0,3.95),S(10,0,3.95),S(0,10,3.95),'Quitar pestanas delanteras')
polyP(s,[S(-41,2.75,3.95),S(11,2.75,3.95),S(11,7.0,3.95),S(-41,7.0,3.95)])
extD(tc,s,allprofs(s),HDIR,2.05,CUT,[tB],'Quitar pestanas delanteras')
s=sk(tc,'x',-57.5,'Tope delantero panel')
polyP(s,[S(-57.5,2.75,4.0),S(-57.5,4.7,4.0),S(-57.5,4.7,4.2),S(-57.5,5.7,4.2),S(-57.5,5.7,5.4),S(-57.5,2.75,5.4)])
ext(tc,s,allprofs(s),'x',-57.5,28.0,JOIN,[tc.bRepBodies.item(0)],'Tope delantero panel')
# 4. peineta: agujeros para M3 (d3.4) en (-24.5,22) y (39,36), se rellena el ovalado y el d2.7
pc=O['Peineta dupont'].component; pb=pc.bRepBodies.item(0)
cyls(pc,'y',15.9,17.9,[(-24.0,22.0),(-24.5,22.0),(39.0,36.0)],2.0,JOIN,'Relleno agujeros viejos',[pb])
cyls(pc,'y',15.5,18.3,[(-24.5,22.0),(39.0,36.0)],1.7,CUT,'Agujeros peineta M3',[pc.bRepBodies.item(0)])
# 5. frente negro sin pasadores (se centra con los LED y se pega)
tf=O['Tapa frontal'].component
delprefix(tf,'Pasadores frente'); delprefix(tf,'Alojamiento pasadores frente')
# 6. postes superiores de la LiPo Rider unidos al techo de la caja (sin rendija de 0,2 mm)
cu=O['Cuerpo'].component
s=sk(cu,'z',96.0,'Union postes LiPo al techo')
for x in (-31.0,32.0): rect(s,'z',96.0,x-2.9,36.9,x+2.9,62.5)
ext(cu,s,allprofs(s),'z',96.0,97.6,JOIN,[cu.bRepBodies.item(0)],'Union postes LiPo al techo')
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
hidefolders()
print('ok parte8')
