# Parte 5 (ambos disenos): collarin del cable del panel a (-39,42) y semaforo con tornillo pasante + tuerca
O=occs()
cu=O['Cuerpo'].component
for sn in ('Collarin cable panel','Paso cable panel'):
    s=cu.sketches.itemByName(sn)
    for c in s.sketchCurves.sketchCircles:
        g=c.centerSketchPoint.geometry
        t=s.modelToSketchSpace(P(-3.9,4.2,s.sketchToModelSpace(g).z))
        c.centerSketchPoint.move(adsk.core.Vector3D.create(t.x-g.x,t.y-g.y,0))
tf=O['Tapa frontal'].component
for f in list(tf.features):
    if f.isValid and (f.name.startswith('Insertos semaforo') ):
        delfeat(tf,f.name)
for f in list(tf.features):
    if f.isValid and f.name.startswith('Postes semaforo d8'):
        delfeat(tf,f.name)
tapa=[b for b in tf.bRepBodies if b.name=='Tapa'][0]
av=tf.features.itemByName('Extruir6')
tap=0.0
try: tap=av.extentOne and av.taperAngleOne.value
except: tap=0.0
print('taper avellanado tapa', tap)
sem=[(-7.75,38.5),(7.75,38.5)]
cyls(tf,'y',-2.5,6.5,sem,3.0,JOIN,'Postes semaforo d6',[tapa])
cyls(tf,'y',-6.0,7.0,sem,1.7,CUT,'Pasantes M3 semaforo',[tapa])
s=sk(tf,'y',-5.0,'Avellanado semaforo')
for (x,z) in sem: circ(s,'y',-5.0,x,z,3.2)
n=s.xDirection.crossProduct(s.yDirection)
coll=adsk.core.ObjectCollection.create()
for p in allprofs(s): coll.add(p)
ei=tf.features.extrudeFeatures.createInput(coll, CUT)
dr=adsk.fusion.ExtentDirections.PositiveExtentDirection if n.y>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(0.15)), dr, adsk.core.ValueInput.createByReal(tap))
ei.participantBodies=[tapa]
f=tf.features.extrudeFeatures.add(ei); f.name='Avellanado semaforo'
hidefolders()
print('ok parte5')
