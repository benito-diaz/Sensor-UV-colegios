# Parte 10: ESP32 y semaforo con insertos M2.5 (medida tipica: exterior 3,5 mm x 4 mm de largo; CONFIRMAR con los insertos reales)
D25=3.5   # diametro del agujero para el inserto M2.5
P25=5.0   # profundidad (inserto 4 mm + 1 mm)
O=occs()
def delprefix(comp,pre):
    for f in [f for f in comp.features if f.isValid and f.name.startswith(pre)]: delfeat(comp,f.name)
cu=O['Cuerpo'].component
delprefix(cu,'Ranuras tuerca M2.5 ESP32'); delprefix(cu,'Pasos M2.5 ESP32')
s=cu.sketches.itemByName('Postes ESP32 d9')
for c in s.sketchCurves.sketchCircles: c.radius=0.35
s.name='Postes ESP32 d7'
for f in cu.features:
    if f.name.startswith('Postes ESP32 d9'): f.name='Postes ESP32 d7'
esp=[(-18.0,10.5),(33.0,10.5),(-18.0,33.5),(33.0,33.5)]
cuB=cu.bRepBodies.item(0)
cyls(cu,'y',35.9,35.9+P25,esp,D25/2,CUT,'Insertos ESP32 M2.5',[cuB])
cyls(cu,'y',35.9+P25,35.9+P25+4.0,esp,1.35,CUT,'Insertos ESP32 (paso M2.5)',[cu.bRepBodies.item(0)])
tf=O['Tapa frontal'].component
delprefix(tf,'Pasantes M3 semaforo'); delprefix(tf,'Avellanado semaforo')
tapa=[b for b in tf.bRepBodies if b.name=='Tapa'][0]
sem=[(-7.75,38.5),(7.75,38.5)]
cyls(tf,'y',6.5,6.5-P25,sem,D25/2,CUT,'Insertos semaforo M2.5',[tapa])
tapa=[b for b in tf.bRepBodies if b.name=='Tapa'][0]
cyls(tf,'y',6.5-P25,-0.5,sem,1.35,CUT,'Insertos semaforo (paso M2.5)',[tapa])
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
hidefolders()
print('ok parte10')
