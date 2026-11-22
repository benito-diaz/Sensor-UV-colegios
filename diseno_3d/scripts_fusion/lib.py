import adsk.core, adsk.fusion, math
app=adsk.core.Application.get()
des=adsk.fusion.Design.cast(app.activeProduct)
root=des.rootComponent
V=adsk.core.ValueInput.createByReal
P=adsk.core.Point3D.create
JOIN=adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT=adsk.fusion.FeatureOperations.CutFeatureOperation
NEWB=adsk.fusion.FeatureOperations.NewBodyFeatureOperation
def occs(): return {o.component.name:o for o in root.occurrences}
def plane(comp, axis, val):
    base={'x':comp.yZConstructionPlane,'y':comp.xZConstructionPlane,'z':comp.xYConstructionPlane}[axis]
    for sgn in (1,-1):
        pi=comp.constructionPlanes.createInput(); pi.setByOffset(base, V(sgn*val/10.0))
        pl=comp.constructionPlanes.add(pi)
        o=pl.geometry.origin; c={'x':o.x,'y':o.y,'z':o.z}[axis]
        if abs(c*10-val)<1e-4 or abs(val)<1e-9:
            pl.isLightBulbOn=False; return pl
        pl.deleteMe()
    raise Exception('plane fail')
def sk(comp, axis, val, name):
    s=comp.sketches.add(plane(comp,axis,val)); s.name=name; return s
def mp(axis,val,u,v):
    # u,v are the two other coords in order (x,y,z minus axis)
    if axis=='x': return P(val/10,u/10,v/10)
    if axis=='y': return P(u/10,val/10,v/10)
    return P(u/10,v/10,val/10)
def circ(s,axis,val,u,v,r):
    return s.sketchCurves.sketchCircles.addByCenterRadius(s.modelToSketchSpace(mp(axis,val,u,v)), r/10.0)
def rect(s,axis,val,u0,v0,u1,v1):
    return s.sketchCurves.sketchLines.addTwoPointRectangle(s.modelToSketchSpace(mp(axis,val,u0,v0)), s.modelToSketchSpace(mp(axis,val,u1,v1)))
def poly(s,axis,val,pts):
    L=s.sketchCurves.sketchLines; q=[s.modelToSketchSpace(mp(axis,val,u,v)) for (u,v) in pts]
    lines=[]
    for i in range(len(q)):
        a=lines[-1].endSketchPoint if lines else q[0]
        b=lines[0].startSketchPoint if i==len(q)-1 else q[i+1]
        lines.append(L.addByTwoPoints(a,b))
def ext(comp, s, profs, axis, a0, a1, op, bodies=None, name=None):
    n=s.xDirection.crossProduct(s.yDirection)
    cn={'x':n.x,'y':n.y,'z':n.z}[axis]
    d=a1-a0
    coll=adsk.core.ObjectCollection.create()
    for p in profs: coll.add(p)
    ei=comp.features.extrudeFeatures.createInput(coll, op)
    dr=adsk.fusion.ExtentDirections.PositiveExtentDirection if d*cn>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
    ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(abs(d)/10.0)), dr)
    if bodies: ei.participantBodies=bodies
    f=comp.features.extrudeFeatures.add(ei)
    if name: f.name=name
    return f
def allprofs(s): return [s.profiles.item(i) for i in range(s.profiles.count)]
def ringprofs(s): return [p for p in allprofs(s) if p.profileLoops.count==2]
def cyls(comp, axis, a0, a1, centers, r, op, name, bodies=None):
    s=sk(comp,axis,a0,name)
    for (u,v) in centers: circ(s,axis,a0,u,v,r)
    return ext(comp,s,allprofs(s),axis,a0,a1,op,bodies,name)
def inserts(comp, axis, face, sgn, centers, name, bodies=None, deep=3.0):
    # inserto 5 x 4 mm: agujero d5 prof 5 + paso d3.2 'deep' mas
    cyls(comp,axis,face,face+sgn*5.0,centers,2.5,CUT,name+' (inserto 5x4)',bodies)
    cyls(comp,axis,face+sgn*5.0,face+sgn*(5.0+deep),centers,1.6,CUT,name+' (paso M3)',bodies)
def sketchOf(f):
    p=f.profile
    if isinstance(p, adsk.core.ObjectCollection) or hasattr(p,'count'): p=p.item(0)
    return adsk.fusion.Profile.cast(p).parentSketch
def delfeat(comp, fname):
    f=comp.features.itemByName(fname)
    s=None
    try: s=sketchOf(f)
    except: pass
    f.deleteMe()
    if s and s.isValid:
        try: s.deleteMe()
        except: pass
def hidefolders():
    for c in des.allComponents:
        for a in ('isConstructionFolderLightBulbOn','isOriginFolderLightBulbOn','isSketchFolderLightBulbOn','isJointsFolderLightBulbOn'):
            try: setattr(c,a,False)
            except: pass
