# Parte 14: los 4 agujeros de paso del techo de la caja (pernos que suben al techo solar) pasan de 3,4 a 4,0 mm
O=occs()
cu=O['Cuerpo'].component
s=cu.sketches.itemByName('Pasos M3 techo')
n=0
for c in s.sketchCurves.sketchCircles:
    c.radius=0.2; n+=1
des.computeAll()
tl=des.timeline
print('circulos cambiados',n)
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
b=cu.bRepBodies.item(0)
for (x,y) in [(-45,18),(45,18),(-45,52),(45,52)]:
    print((x,y),'r1.9 hueco:',b.pointContainment(P((x+1.9)/10,y/10,9.875)),' r2.1 solido:',b.pointContainment(P((x+2.1)/10,y/10,9.875)))
hidefolders()
