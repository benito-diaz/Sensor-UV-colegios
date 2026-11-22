# Parte 13: se elimina el tubo rectangular que tapaba el cable del sensor UV (bajo la capsula)
O=occs()
tc=O['Techo solar'].component
for f in [f for f in tc.features if f.isValid and f.name.startswith('Tubo cables sensor')]:
    delfeat(tc,f.name)
des.computeAll()
tl=des.timeline
print('unhealthy',[(tl.item(i).name,tl.item(i).errorOrWarningMessage) for i in range(tl.count) if tl.item(i).healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
b=tc.bRepBodies.item(0)
print('tubo (38.2,37,115):', b.pointContainment(P(3.82,3.7,11.5)), ' paso piso (42,37,130):', b.pointContainment(P(4.2,3.7,13.0)))
hidefolders()
