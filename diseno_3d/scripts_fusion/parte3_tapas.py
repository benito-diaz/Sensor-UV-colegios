# Parte 3: tapa del sensor (sin tornillos, a presion con enganches) y tapa frontal (insertos semaforo, frente pegado)
O=occs()
ts=O['Tapa sensor'].component
delfeat(ts,'Extruir5'); delfeat(ts,'Extruir4')
tsB=ts.bRepBodies.item(0)
s=sk(ts,'y',41.0,'Enganches tapa sensor'); rect(s,'y',41.0,29.8,148.0,30.5,149.0); rect(s,'y',41.0,53.5,148.0,54.2,149.0)
ext(ts,s,allprofs(s),'y',41.0,49.0,JOIN,[tsB],'Enganches tapa sensor')

tf=O['Tapa frontal'].component
delfeat(tf,'Extruir12'); delfeat(tf,'Extruir8'); delfeat(tf,'Extruir7')
tapa=[b for b in tf.bRepBodies if b.name=='Tapa'][0]
fre=[b for b in tf.bRepBodies if b.name=='Frente semaforo'][0]
sem=[(-7.75,38.5),(7.75,38.5)]
cyls(tf,'y',-2.5,6.5,sem,4.0,JOIN,'Postes semaforo d8',[tapa])
inserts(tf,'y',6.5,-1,sem,'Insertos semaforo',[tapa],deep=2.0)
pins=[(0.0,54.5),(0.0,93.0)]
cyls(tf,'y',-5.0,-3.5,pins,1.6,CUT,'Alojamiento pasadores frente',[tapa])
cyls(tf,'y',-5.0,-3.6,pins,1.5,JOIN,'Pasadores frente (pegar)',[fre])
hidefolders()
print('ok parte3', [b.name for b in tf.bRepBodies], ts.bRepBodies.count)
