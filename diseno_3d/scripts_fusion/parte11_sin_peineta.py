# Parte 11: se elimina la peineta (pieza y sus 2 postes con insertos)
O=occs()
if 'Peineta dupont' in O: O['Peineta dupont'].deleteMe()
cu=O['Cuerpo'].component
for pre in ('Insertos peineta','Postes peineta'):
    for f in [f for f in cu.features if f.isValid and f.name.startswith(pre)]:
        delfeat(cu,f.name)
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
b=cu.bRepBodies.item(0)
print('poste peineta (39,30,36):', b.pointContainment(P(3.9,3.0,3.6)), ' (-24.5,30,22):', b.pointContainment(P(-2.45,3.0,2.2)))
hidefolders()
print('ok parte11', [o.component.name for o in root.occurrences])
