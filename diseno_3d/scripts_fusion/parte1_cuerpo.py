# Parte 1: chasis integrado al Cuerpo, insertos de la tapa, persianas, techo de la caja
O=occs()
cu=O['Cuerpo'].component
cuB=cu.bRepBodies.item(0)

# --- 1. Rescatar peineta y traba del chasis como piezas sueltas, borrar chasis ---
if 'Chasis' in O:
    ch=O['Chasis']
    pe_b=[b for b in ch.component.bRepBodies if b.name=='Peineta dupont'][0]
    tr_b=[b for b in ch.component.bRepBodies if b.name=='Traba bateria'][0]
    ap_pe=pe_b.appearance; ap_tr=tr_b.appearance
    oPe=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); oPe.component.name='Peineta dupont'
    oTr=root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); oTr.component.name='Traba bateria'
    # peineta: copia de la geometria v3 + agujero izquierdo corrido a x -24.5
    pc=oPe.component
    bf=pc.features.baseFeatures.add(); bf.startEdit()
    nb=pc.bRepBodies.add(adsk.fusion.TemporaryBRepManager.get().copy(pe_b), bf)
    bf.finishEdit()
    pb=pc.bRepBodies.item(0); pb.name='Peineta dupont'; pb.appearance=ap_pe
    cyls(pc,'y',15.0,19.0,[(-24.5,22.0)],1.7,CUT,'Agujero peineta izq (x -24.5)',[pb])
    ch.deleteMe()
    # traba nueva (fleje delante de la bateria)
    tc=oTr.component
    s=sk(tc,'y',54.0,'Traba bateria'); rect(s,'y',54.0,-26.5,45.5,-19.5,96.5)
    f=ext(tc,s,allprofs(s),'y',54.0,56.0,NEWB,None,'Traba bateria')
    tb=tc.bRepBodies.item(0); tb.name='Traba bateria'; tb.appearance=ap_tr
    cyls(tc,'y',53.0,57.0,[(-23.0,49.5),(-23.0,92.5)],1.7,CUT,'Agujeros traba M3',[tb])

# --- 2. Borrar rieles, torretas de piso, persianas viejas, pasos de techo viejos ---
for n in ['Extruir5','Extruir6','Extruir7','Extruir8','Extruir9','Extruir14','Extruir15','Extruir4']:
    delfeat(cu,n)
cuB=cu.bRepBodies.item(0)

# --- 3. Torretas de la tapa: d8 -> d9, insertos 5x4 ---
cyls(cu,'y',0.0,12.0,[(-48.8,12.0),(-48.8,88.0),(48.8,12.0),(48.8,88.0)],4.5,JOIN,'Torretas tapa d9',[cuB])
inserts(cu,'y',0.0,1,[(-48.8,12.0),(-48.8,88.0),(48.8,12.0),(48.8,88.0)],'Insertos tapa',[cuB],deep=4.0)

# --- 4. Persianas: canal a 45 grados + aleta 1,5 mm ---
As=[22.0,29.0,36.0,64.0,71.0,78.0]
s=sk(cu,'y',6.0,'Aletas persiana 45')
for A in As:
    for g in (1,-1):
        poly(s,'y',6.0,[(g*54.5,A-2.0),(g*60.0,A-7.5),(g*60.0,A-6.0),(g*54.5,A-0.5)])
ext(cu,s,allprofs(s),'y',6.0,36.0,JOIN,[cuB],'Aletas persiana 45')
s=sk(cu,'y',6.0,'Canales persiana 45')
for A in As:
    for g in (1,-1):
        poly(s,'y',6.0,[(g*51.5,A+1.0),(g*56.5,A-4.0),(g*56.5,A-8.0),(g*51.5,A-3.0)])
ext(cu,s,allprofs(s),'y',6.0,36.0,CUT,[cuB],'Canales persiana 45')

# --- 5. Techo de la caja: pasos de tornillo del techo, collarin panel, collarin rectangular sensor ---
cyls(cu,'z',96.0,101.0,[(-45.0,18.0),(45.0,18.0),(-45.0,52.0),(45.0,52.0)],1.7,CUT,'Pasos M3 techo',[cuB])
s=sk(cu,'z',100.0,'Collarin cable panel'); circ(s,'z',100.0,-30.0,57.0,6.0); circ(s,'z',100.0,-30.0,57.0,3.5)
ext(cu,s,ringprofs(s),'z',100.0,104.0,JOIN,[cuB],'Collarin cable panel')
cyls(cu,'z',96.0,105.0,[(-30.0,57.0)],3.5,CUT,'Paso cable panel',[cuB])
s=sk(cu,'z',100.0,'Collarin cables sensor'); rect(s,'z',100.0,39.3,30.3,44.7,43.7); rect(s,'z',100.0,40.5,31.5,43.5,42.5)
ext(cu,s,ringprofs(s),'z',100.0,103.0,JOIN,[cuB],'Collarin cables sensor')
s=sk(cu,'z',96.0,'Paso cables sensor'); rect(s,'z',96.0,40.5,31.5,43.5,42.5)
ext(cu,s,allprofs(s),'z',96.0,104.0,CUT,[cuB],'Paso cables sensor')

# --- 6. Chasis integrado a la pared trasera ---
Y0=63.0
lipo=[(-31.0,48.7),(32.0,48.7),(-31.0,93.3),(32.0,93.3)]
esp=[(-18.0,10.5),(33.0,10.5),(-18.0,33.5),(33.0,33.5)]
pein=[(-24.5,22.0),(39.0,36.0)]
trab=[(-23.0,49.5),(-23.0,92.5)]
cyls(cu,'y',Y0,36.9,lipo,4.0,JOIN,'Postes LiPo Rider d8',[cuB])
cyls(cu,'y',Y0,35.9,esp,4.5,JOIN,'Postes ESP32 d9',[cuB])
cyls(cu,'y',Y0,17.8,pein,4.0,JOIN,'Postes peineta d8',[cuB])
cyls(cu,'y',Y0,56.0,trab,4.0,JOIN,'Postes traba d8',[cuB])
s=sk(cu,'y',Y0,'Bolsillo bateria'); rect(s,'y',Y0,-50.0,51.5,4.0,90.5); rect(s,'y',Y0,-48.5,53.0,2.5,89.0)
ext(cu,s,ringprofs(s),'y',Y0,56.0,JOIN,[cuB],'Bolsillo bateria')
s=sk(cu,'y',55.0,'Paso cable bateria'); rect(s,'y',55.0,-50.5,62.0,-48.0,72.0)
ext(cu,s,allprofs(s),'y',55.0,62.4,CUT,[cuB],'Paso cable bateria')
inserts(cu,'y',36.9,1,lipo,'Insertos LiPo Rider',[cuB],deep=3.0)
inserts(cu,'y',17.8,1,pein,'Insertos peineta',[cuB],deep=3.0)
inserts(cu,'y',56.0,1,trab,'Insertos traba',[cuB],deep=3.0)
cyls(cu,'y',35.9,47.0,esp,1.4,CUT,'Pasos M2.5 ESP32',[cuB])
s=sk(cu,'y',38.4,'Ranuras tuerca M2.5 ESP32')
for (x,z) in esp: rect(s,'y',38.4,x-2.65,z-3.0,x+2.65,z+5.0)
ext(cu,s,allprofs(s),'y',38.4,40.8,CUT,[cuB],'Ranuras tuerca M2.5 ESP32')
hidefolders()
print('ok parte1', cu.bRepBodies.count, [f.name for f in cu.features][-6:])
