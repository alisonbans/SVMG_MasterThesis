from abaqus import *
from abaqusConstants import *
import regionToolset
import step
import __main__
def template(template,stent_location):
    openMdb(
        pathName=template)
    step = mdb.openStep(
        stent_location, 
        scaleFromFile=OFF)
    mdb.models['Model-1'].PartFromGeometryFile(name='STENT', geometryFile=step, 
        combine=False, dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['STENT']
    s = p.faces
    side1Faces = s.getSequenceFromMask(mask=('[#100 ]', ), )
    p.Surface(side1Faces=side1Faces, name='SURF-OUT')
    side1Faces = s.getSequenceFromMask(mask=('[#800 ]', ), )
    p.Surface(side1Faces=side1Faces, name='SURF-IN')
    e = p.edges
    pickedEdges = e.getSequenceFromMask(mask=('[#88888888 #ffffffff:35 #ff ]', ), )
    p.seedEdgeBySize(edges=pickedEdges, size=0.02, deviationFactor=0.1, 
        constraint=FINER)
    c = p.cells
    pickedRegions = c.getSequenceFromMask(mask=('[#1 ]', ), )
    p.setMeshControls(regions=pickedRegions, technique=BOTTOM_UP)
    mdb.meshEditOptions.setValues(enableUndo=True, maxUndoCacheElements=0.5)
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#100 ]', ), )
    pickedGeomSourceSide=regionToolset.Region(faces=faces)
    c = p.cells
    f = p.faces
    p.generateBottomUpSweptMesh(cell=c[0], targetSide=f[11], 
        geometrySourceSide=pickedGeomSourceSide, numberOfLayers=3)
    a = mdb.models['Model-1'].rootAssembly
    a.Instance(name='STENT-1', part=p, dependent=ON)
    a = mdb.models['Model-1'].rootAssembly
    f11 = a.instances['STENT-1'].faces
    f12 = a.instances['CYL-EXP-1'].faces
    a.Coaxial(movableAxis=f11[8], fixedAxis=f12[0], flip=OFF)

if __name__ == "__main__":
    input = str(sys.argv[-1])
    input = input.split(',')
    template_location = input[0]
    stent_location = input[1]
    template(template_location,stent_location)