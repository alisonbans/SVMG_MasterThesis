from abaqus import *
from abaqusConstants import *
import __main__
import displayGroupMdbToolset as dgm
import mesh
from abaqus import session

# Balloon and Cylinder ------------------------------------------------------------
def cylinder_exp(model):
    # Geometry
    s = mdb.models[model].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(13.75, -1.25))
    s.ObliqueDimension(vertex1=v[0], vertex2=v[1], textPoint=(-2.43898773193359, 
        -23.2342948913574), value=0.3)
    p = mdb.models[model].Part(name='CYL-EXP', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model].parts['CYL-EXP']
    p.BaseShellExtrude(sketch=s, depth=22.0)
    s.unsetPrimaryObject()
    p = mdb.models[model].parts['CYL-EXP']
    del mdb.models[model].sketches['__profile__']
    #Mesh
    p = mdb.models[model].parts['CYL-EXP']
    p.seedPart(size=0.05, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()
    # Sets and Surfaces
    p = mdb.models[model].parts['CYL-EXP']
    n = p.nodes
    nodes = n.getSequenceFromMask(mask=('[#ffffffff:528 #3fff ]', ), )
    p.Set(nodes=nodes, name='SET-NODE')
    e = p.elements
    elements = e.getSequenceFromMask(mask=('[#ffffffff:527 #ff ]', ), )
    p.Set(elements=elements, name='SET-ELE')
    s = p.elements
    side1Elements = s.getSequenceFromMask(mask=('[#ffffffff:527 #ff ]', ), )
    p.Surface(side1Elements=side1Elements, name='SURF-OUT')
    # Selection Assignment
    mdb.models[model].SurfaceSection(name='Section-CYL-EXP', useDensity=ON, 
        density=1.0)
    region = p.sets['SET-ELE']
    p.SectionAssignment(region=region, sectionName='Section-CYL-EXP', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
def cylinder_cri(model, name='CYL-CRI'):
    # Geometry
    s = mdb.models[model].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(13.75, -1.25))
    s.ObliqueDimension(vertex1=v[0], vertex2=v[1], textPoint=(-2.43898773193359, 
        -23.2342948913574), value=1.7)
    p = mdb.models[model].Part(name=name, dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models[model].parts[name]
    p.BaseShellExtrude(sketch=s, depth=22.0)
    s.unsetPrimaryObject()
    p = mdb.models[model].parts[name]
    del mdb.models[model].sketches['__profile__']
    #Mesh
    p = mdb.models[model].parts[name]
    p.seedPart(size=0.05, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()
    # Sets and Surfaces
    p = mdb.models[model].parts[name]
    n = p.nodes
    nodes = n.getSequenceFromMask(mask=('[#ffffffff:3451 #ff ]', ), )
    p.Set(nodes=nodes, name='SET-NODE')
    e = p.elements
    elements = e.getSequenceFromMask(mask=('[#ffffffff:3443 #1fff ]', ), )
    p.Set(elements=elements, name='SET-ELE')
    s = p.elements
    side2Elements = s.getSequenceFromMask(mask=('[#ffffffff:3443 #1fff ]', ), )
    p.Surface(side2Elements=side2Elements, name='SURF-IN')
    # Selection Assignment
    name_surf_selection = 'Selection-'+name
    mdb.models[model].SurfaceSection(name=name_surf_selection, useDensity=ON, 
        density=1.0)
    region = p.sets['SET-ELE']
    p.SectionAssignment(region=region, sectionName=name_surf_selection, offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)

# Stent ---------------------------------------------------------------------------
def MatCoCr(model): 
    mdb.models[model].Material(name='CoCr')
    mdb.models[model].materials['CoCr'].Damping(alpha=50.0)
    mdb.models[model].materials['CoCr'].Density(table=((8e-09, ), ))
    mdb.models[model].materials['CoCr'].Elastic(table=((233000.0, 0.35), ))
    mdb.models[model].materials['CoCr'].Plastic(scaleStress=None, table=((
        414.0, 0.0), (933.0, 0.425), (933.0, 1)))
    mdb.models[model].materials['CoCr'].Damping(alpha=70.0)
    mdb.models[model].HomogeneousSolidSection(name='Section-CoCr', 
        material='CoCr', thickness=None)
def expanded_stent(model, stent_location):
    session.openOdb(stent_location)
    odb = session.odbs[stent_location]
    p = mdb.models[model].PartFromOdb(name='STENT', instance='STENT-1', 
        odb=odb, shape=DEFORMED, step=1, frame=5)
    p = mdb.models[model].parts['STENT']
    odb.close()
    mdb.models[model].parts['STENT'].deleteSets(setNames=('_SURF-ALL_S1', 
        '_SURF-ALL_S1_1', '_SURF-ALL_S2', '_SURF-ALL_S2_1', '_SURF-ALL_S3', 
        '_SURF-ALL_S3_1', '_SURF-ALL_S4', '_SURF-ALL_S4_1', '_SURF-ALL_S5', 
        '_SURF-ALL_S5_1', '_SURF-ALL_S6', '_SURF-ALL_S6_1', '_SURF-OUT_S1','_SURF-IN_S2',))
    region = p.sets['SET-ALL']
    p.SectionAssignment(region=region, sectionName='Section-CoCr', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)

# Artery --------------------------------------------------------------------------
def artery(model):
    # Make the main artery tube
    s = mdb.models[model].ConstrainedSketch(name='__profile__', sheetSize=20.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, 1.5))
    s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, 2.4))
    p = mdb.models[model].Part(name='ARTERY', dimensionality=THREE_D,type=DEFORMABLE_BODY)
    p = mdb.models[model].parts['ARTERY']
    p.BaseSolidExtrude(sketch=s, depth=30.0)
    s.unsetPrimaryObject()
    del mdb.models[model].sketches['__profile__']  
    f, e, d1 = p.faces, p.edges, p.datums
    # Divide it in a three layered artery
    t = p.MakeSketchTransform(sketchPlane=f[2], sketchUpEdge=e[2],sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 20.0))
    s1 = mdb.models[model].ConstrainedSketch(name='__profile__', sheetSize=42.21, gridSpacing=1.05, transform=t)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
    s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, 1.74))
    s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, 2.06))
    pickedFaces = f.getSequenceFromMask(mask=('[#4 ]', ), )
    e1, d2 = p.edges, p.datums
    p.PartitionFaceBySketch(sketchUpEdge=e1[2], faces=pickedFaces, sketch=s1)
    s1.unsetPrimaryObject()
    del mdb.models[model].sketches['__profile__']
    f1, e, d1 = p.faces, p.edges, p.datums
    t = p.MakeSketchTransform(sketchPlane=f1[5], sketchUpEdge=e[5],sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
    s = mdb.models[model].ConstrainedSketch(name='__profile__', sheetSize=42.21, gridSpacing=1.05, transform=t)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
    s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, -1.74))
    s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(0.0, -2.06))
    f = p.faces
    pickedFaces = f.getSequenceFromMask(mask=('[#20 ]', ), )
    e1, d2 = p.edges, p.datums
    p.PartitionFaceBySketch(sketchUpEdge=e1[5], faces=pickedFaces, sketch=s)
    s.unsetPrimaryObject()
    del mdb.models[model].sketches['__profile__']
    c = p.cells
    pickedCells = c.getSequenceFromMask(mask=('[#1 ]', ), )
    v1, e, d1 = p.vertices, p.edges, p.datums
    p.PartitionCellByPlaneThreePoints(point1=v1[7], point2=v1[2], point3=v1[5], cells=pickedCells)
    # Seed the edges 
    e = p.edges
    pickedEdges = e.getSequenceFromMask(mask=('[#77dd ]', ), )
    p.seedEdgeByNumber(edges=pickedEdges, number=3, constraint=FINER)
    pickedEdges = e.getSequenceFromMask(mask=('[#ffff0000 ]', ), )
    p.seedEdgeByNumber(edges=pickedEdges, number=94, constraint=FINER)
    pickedEdges = e.getSequenceFromMask(mask=('[#e15a0000 ]', ), )
    pickedEdges = e.getSequenceFromMask(mask=('[#8822 ]', ), )
    p.seedEdgeByNumber(edges=pickedEdges, number=375, constraint=FINER)
    p.generateMesh()
    # Sets and Surfaces
    p = mdb.models[model].parts['ARTERY']
    f = p.elements
    face2Elements = f.getSequenceFromMask(mask=(
        '[#ffffffff:1101 #3ffff #0:8812 #fffffffc #ffffffff:1100 #fffff ]', ), 
        )
    p.Surface(face2Elements=face2Elements, name='SURF-IN')
    face1Elements = f.getSequenceFromMask(mask=(
        '[#0:8812 #ffff0000 #ffffffff:1101 #3 #0:8811 #fffc0000 #ffffffff:1101', 
        ' #f ]', ), )
    p.Surface(face1Elements=face1Elements, name='SURF-OUT')
    face1Elements = f.getSequenceFromMask(mask=(
        '[#0:8812 #ffff0000 #ffffffff:1101 #3 #0:8811 #fffc0000 #ffffffff:1101',
        ' #f ]', ), )
    face2Elements = f.getSequenceFromMask(mask=(
        '[#ffffffff:1101 #3ffff #0:8812 #fffffffc #ffffffff:1100 #fffff ]', ),
        )
    p.Surface(face1Elements=face1Elements, face2Elements=face2Elements,
        name='SURF-ALL')
    n = p.nodes
    nodes = n.getSequenceFromMask(mask=(
        '[#ffff #0:11 #ffffffc0 #ffffffff:2 #7 #0:10 #fe000000',
        ' #ffffffff:2 #3fffff #0:11 #fffff000 #ffffffff:2 #1ff #0:10',
        ' #80000000 #ffffffff:38 #ffff #0:2173 #fffff000 #ffffffff:34 #ff',
        ' #0:2360 #fffffff0 #ffffffff:34 ]', ), )    
    p.Set(nodes=nodes, name='SET-NODE')
    e = p.elements
    elements = e.getSequenceFromMask(mask=(
        '[#ffffffff:9937 #ffff #0:1054 #ffffffc0 #ffffffff:46 #3 #0:1053', 
        ' #ff000000 #ffffffff:46 #fffff #0:1054 #fffffc00 #ffffffff:34 #fffc7fff', 
        ' #ffffffff:11 #3f #0:1053 #80000000 #ffffffff:35 #1 #ffffff00', 
        ' #ffffffff:9 #ffffff #0:1055 #ffe00000 #ffffffff:33 #7ffff #0', 
        ' #c0000000 #ffffffff:9 #3ff #0:1056 #fffff800 #ffffffff:32 #1f', 
        ' #0:2 #fff80000 #ffffffff:7 #fffffff #0:1058 #ffffffff:31 #7fffff', 
        ' #0:4 #fffff000 #ffffffff:6 #3fff #0:1058 #fe000000 #ffffffff:30', 
        ' #1ff #0:5 #fffffff0 #ffffffff:5 #0:1060 #fffe0000 #ffffffff:17', 
        ' #f ]', ), )
    p.Set(elements=elements, name='SET-HALF')
    elements = e.getSequenceFromMask(mask=('[#ffffffff:19828 #f ]', ), )
    p.Set(elements=elements, name='SET-ALL')
    elements = e.getSequenceFromMask(mask=(
        '[#ffffffff:3304 #3fffff #0:6609 #fffffffc #ffffffff:3303 #ffffff ]', 
        ), )
    p.Set(elements=elements, name='SET-INTIMA')
    set1 = mdb.models[model].parts['ARTERY'].sets['SET-INTIMA']
    leaf = dgm.LeafFromSets(sets=(set1, ))
    elements = e.getSequenceFromMask(mask=(
        '[#0:3304 #ffc00000 #ffffffff:3304 #fff #0:6608 #ff000000 #ffffffff:3304', 
        ' #3fff ]', ), )
    p.Set(elements=elements, name='SET-MEDIA')
    set1 = mdb.models[model].parts['ARTERY'].sets['SET-MEDIA']
    leaf = dgm.LeafFromSets(sets=(set1, ))
    elements = e.getSequenceFromMask(mask=(
        '[#0:6609 #fffff000 #ffffffff:3304 #3 #0:6608 #ffffc000 #ffffffff:3304', 
        ' #f ]', ), )
    p.Set(elements=elements, name='SET-ADVENTITIA') 
    # Section Assignment 
    mdb.models[model].HomogeneousSolidSection(name='Section-ADVENTITIA', 
        material='Adventitia', thickness=None)
    region = p.sets['SET-ADVENTITIA']
    p.SectionAssignment(region=region, sectionName='Section-ADVENTITIA', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    mdb.models[model].HomogeneousSolidSection(name='Section-MEDIA', 
        material='Media', thickness=None)
    region = p.sets['SET-MEDIA']
    p.SectionAssignment(region=region, sectionName='Section-MEDIA', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    mdb.models[model].HomogeneousSolidSection(name='Section-INTIMA', 
        material='Intima', thickness=None)
    region = p.sets['SET-INTIMA']
    p.SectionAssignment(region=region, sectionName='Section-INTIMA', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
def ArteryMaterial(model):
    # Intima
    mdb.models[model].Material(name='Intima')
    mdb.models[model].materials['Intima'].Density(table=((1.12e-09, ), ))
    mdb.models[model].materials['Intima'].Hyperelastic(
        materialType=ISOTROPIC, testData=OFF, type=REDUCED_POLYNOMIAL, n=6, 
        volumetricResponse=VOLUMETRIC_DATA, table=((0.00679, 0.54, -1.11, 10.65, -7.27, 1.63, 0.0, 
        0.0, 0.0, 0.0, 0.0, 0.0), ))
    mdb.models[model].materials['Intima'].Damping(alpha=2000.0)
    # Media
    mdb.models[model].Material(name='Media')
    mdb.models[model].materials['Media'].Density(table=((1.12e-09, ), ))
    mdb.models[model].materials['Media'].Hyperelastic(
        materialType=ISOTROPIC, testData=OFF, type=REDUCED_POLYNOMIAL, n=6, 
        volumetricResponse=VOLUMETRIC_DATA, table=((0.00652, 0.0489, 0.00926, 
        0.76, -0.43, 0.0869, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), ))
    mdb.models[model].materials['Media'].Damping(alpha=2000.0)
    # Adventitia
    mdb.models[model].Material(name='Adventitia')
    mdb.models[model].materials['Adventitia'].Density(table=((1.12e-09, 
        ), ))
    mdb.models[model].materials['Adventitia'].Hyperelastic(
        materialType=ISOTROPIC, testData=OFF, type=REDUCED_POLYNOMIAL, n=6, 
        volumetricResponse=VOLUMETRIC_DATA, table=((0.00827, 0.012, 0.52, 
        -5.63, 21.44, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), ))
    mdb.models[model].materials['Adventitia'].Damping(alpha=2000.0)

# Model -----------------------------------------------------------------------
def assembly_cylexp(model):
    a = mdb.models[model].rootAssembly
    p = mdb.models[model].parts['ARTERY']
    a.Instance(name='ARTERY-1', part=p, dependent=ON)
    p = mdb.models[model].parts['CYL-CRI']
    a.Instance(name='CYL-CRI-1', part=p, dependent=ON)
    p = mdb.models[model].parts['CYL-EXP']
    a.Instance(name='CYL-EXP-1', part=p, dependent=ON)
    p = mdb.models[model].parts['STENT']
    a.Instance(name='STENT-1', part=p, dependent=ON)
    a.translate(instanceList=('ARTERY-1', ), vector=(0.0, 0.0, -4.0))   
def cyl_exp_addons(model, deltaT = 2e-06):

    cyl_cri = mdb.models[model].parts['CYL-CRI']
    cyl_cri.DatumCsysByThreePoints(name='Dat-CYL', coordSysType=CYLINDRICAL, origin=(0.0, 
        0.0, 0.0), line1=(1.0, 0.0, 0.0), line2=(0.0, 1.0, 0.0))
    # Define mesh element types 
    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=EXPLICIT, 
        kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT)
    p = mdb.models[model].parts['ARTERY']
    z1 = p.elements
    elems1 = z1[0:634500]
    pickedRegions =(elems1, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
    elemType1 = mesh.ElemType(elemCode=SFM3D4R, elemLibrary=EXPLICIT)
    p = mdb.models[model].parts['CYL-CRI']
    z1 = p.elements
    elems1 = z1[0:110189]
    pickedRegions =(elems1, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
    p = mdb.models[model].parts['STENT']
    elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=EXPLICIT, 
        kinematicSplit=AVERAGE_STRAIN, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT, distortionControl=DEFAULT)
    z1 = p.elements
    elems1 = z1[0:140991]
    pickedRegions =(elems1, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
    p = mdb.models[model].parts['CYL-EXP']
    elemType1 = mesh.ElemType(elemCode=SFM3D4R, elemLibrary=EXPLICIT)
    z1 = p.elements
    elems1 = z1[0:16872]
    pickedRegions =(elems1, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
    a = mdb.models[model].rootAssembly
    a.regenerate()
    # Create the steps 
    mdb.models[model].ExplicitDynamicsStep(name='Step-CRI', 
        previous='Initial', timePeriod=0.45, massScaling=((SEMI_AUTOMATIC, 
        MODEL, THROUGHOUT_STEP, 0.0, deltaT, BELOW_MIN, 1, 0, 0.0, 0.0, 0, 
        None), ), improvedDtMethod=ON)
    mdb.models[model].ExplicitDynamicsStep(name='Step-REL1', 
        previous='Step-CRI', timePeriod=0.05, improvedDtMethod=ON)
    mdb.models[model].ExplicitDynamicsStep(name='Step-EXP', 
        previous='Step-REL1', timePeriod=0.45, improvedDtMethod=ON)
    mdb.models[model].ExplicitDynamicsStep(name='Step-REL2', previous='Step-EXP', 
        timePeriod=0.05, improvedDtMethod=ON)
    # Define field and history outputs
    mdb.models[model].FieldOutputRequest(name='F-Output-1', 
        createStepName='Step-CRI', variables=('RF', 'U', 'V','LE', 'PE', 'PEEQ', 'S','CFORCE', 'CSTRESS'))
    mdb.models[model].fieldOutputRequests['F-Output-1'].setValuesInStep(
        stepName='Step-REL1', numIntervals=5)
    mdb.models[model].fieldOutputRequests['F-Output-1'].setValuesInStep(
        stepName='Step-EXP', numIntervals=20)
    mdb.models[model].fieldOutputRequests['F-Output-1'].setValuesInStep(
        stepName='Step-REL2', numIntervals=5)
    mdb.models[model].HistoryOutputRequest(name='H-Output-1', 
        createStepName='Step-CRI', variables=('ALLIE', 'ALLKE'))
    regionDef=mdb.models[model].rootAssembly.allInstances['STENT-1'].sets['SET-ALL']
    mdb.models[model].historyOutputRequests['H-Output-1'].setValues(variables=(
        'ALLIE', 'ALLKE'), region=regionDef, sectionPoints=DEFAULT, 
        rebar=EXCLUDE)
    mdb.models[model].HistoryOutputRequest(name='H-Output-2', 
        createStepName='Step-CRI', variables=('ALLIE', 'ALLKE'))
    regionDef=mdb.models[model].rootAssembly.allInstances['ARTERY-1'].sets['SET-ALL']
    mdb.models[model].historyOutputRequests['H-Output-2'].setValues(variables=(
        'ALLIE', 'ALLKE'), region=regionDef, sectionPoints=DEFAULT, 
        rebar=EXCLUDE)
    # Create interaction properties 
    mdb.models[model].ContactProperty('CYL-STENT')
    mdb.models[model].interactionProperties['CYL-STENT'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, 
        table=((0.0, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models[model].interactionProperties['CYL-STENT'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)
    mdb.models[model].ContactProperty('STENT-ARTERY')
    mdb.models[model].interactionProperties['STENT-ARTERY'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF,
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0,
        table=((0.2, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION,
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models[model].interactionProperties['STENT-ARTERY'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON,
        constraintEnforcementMethod=DEFAULT)
    # Create the interaction
    mdb.models[model].ContactExp(name='STENT_ARTERY_CYL', 
        createStepName='Initial')
    cri_in=mdb.models[model].rootAssembly.instances['CYL-CRI-1'].surfaces['SURF-IN']
    stent_out=mdb.models[model].rootAssembly.instances['STENT-1'].surfaces['SURF-OUT']
    stent_all=mdb.models[model].rootAssembly.instances['STENT-1'].surfaces['SURF-ALL']
    stent_in=mdb.models[model].rootAssembly.instances['STENT-1'].surfaces['SURF-IN']
    exp_out=mdb.models[model].rootAssembly.instances['CYL-EXP-1'].surfaces['SURF-OUT']
    artery_in =mdb.models[model].rootAssembly.instances['ARTERY-1'].surfaces['SURF-IN']
    mdb.models[model].interactions['STENT_ARTERY_CYL'].includedPairs.setValuesInStep(
        stepName='Initial', useAllstar=OFF, addPairs=((cri_in, stent_out), (stent_all, stent_all)))
    mdb.models[model].interactions['STENT_ARTERY_CYL'].contactPropertyAssignments.appendInStep(
        stepName='Initial', assignments=((GLOBAL, SELF, 'STENT-ARTERY'), (cri_in, 
        stent_out, 'CYL-STENT'),(exp_out, 
        stent_in, 'CYL-STENT')))
    mdb.models[model].interactions['STENT_ARTERY_CYL'].includedPairs.setValuesInStep(
        stepName='Step-REL1', removePairs=((cri_in, stent_out), ))
    mdb.models[model].interactions['STENT_ARTERY_CYL'].includedPairs.setValuesInStep(
        stepName='Step-EXP', addPairs=((stent_all, artery_in), (exp_out, stent_in), ))
    mdb.models[model].interactions['STENT_ARTERY_CYL'].includedPairs.setValuesInStep(
        stepName='Step-REL2', removePairs=((exp_out, stent_in), ))
    # Add amplitudes 
    a = mdb.models[model].rootAssembly
    mdb.models[model].SmoothStepAmplitude(name='AMP-CRI', timeSpan=TOTAL, 
        data=((0.0, 0.0), (0.4, 1.0), (0.45, 1.0), (0.5, 1.0), (1, 1.0)))
    mdb.models[model].SmoothStepAmplitude(name='AMP-EXP', timeSpan=TOTAL, 
        data=((0.5, 0.0), (0.9, 1.0), (0.95, 1.0), (1.0, 1.0)))    
    # Create loads and boundary conditions 
    a = mdb.models[model].rootAssembly
    region = a.instances['ARTERY-1'].surfaces['SURF-ALL']
    mdb.models[model].Pressure(name='ARTERY-VISC', createStepName='Step-CRI',
        region=region, distributionType=VISCOUS, field='', magnitude=1e-05,
        amplitude=UNSET)
    region = a.instances['STENT-1'].surfaces['SURF-ALL']
    mdb.models[model].Pressure(name='STENT-VISC', createStepName='Step-CRI', 
        region=region, distributionType=VISCOUS, field='', magnitude=0.0006, 
        amplitude=UNSET)
    region = a.instances['CYL-EXP-1'].sets['SET-NODE']
    datum = mdb.models[model].rootAssembly.instances['CYL-CRI-1'].datums[6]
    mdb.models[model].DisplacementBC(name='CYL-EXP', createStepName='Step-EXP', 
        region=region, u1=1.35, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, 
        ur3=UNSET, amplitude='AMP-EXP', fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=datum)
    region = a.instances['CYL-CRI-1'].sets['SET-NODE']
    mdb.models[model].DisplacementBC(name='CYL-CRI', 
        createStepName='Step-CRI', region=region, u1=-1.24, u2=UNSET, u3=UNSET, 
        ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude='AMP-CRI', 
        distributionType=UNIFORM, fieldName='', localCsys=datum)
    region = a.instances['ARTERY-1'].sets['SET-NODE']
    mdb.models[model].EncastreBC(name='ARTERY-ENCASTRE', createStepName='Initial',
        region=region, localCsys=None)

# Main ---------------------------------------------------------------------------
def CylinderExpansion(stent_location, job_name, job_name_full):
    model = 'CYLINDER-STENT-ARTERY'
    mdb.models.changeKey(fromName = 'Model-1', toName=model)
    MatCoCr(model)
    cylinder_exp(model)
    expanded_stent(model, stent_location)
    ArteryMaterial(model)
    artery(model)
    cylinder_cri(model)
    assembly_cylexp(model)
    mdb.Job(name=job_name, model=model, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    mdb.jobs[job_name].writeInput(consistencyChecking=OFF)
    mdb.close()
    mdb.ModelFromInputFile(name=job_name, inputFileName=os.path.join(os.getcwd(), f"{job_name}.inp"))
    del mdb.models['Model-1']
    cyl_exp_addons(job_name)
    mdb.Job(name=job_name_full, model=job_name, description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    mdb.jobs[job_name_full].writeInput(consistencyChecking=OFF)


if __name__ == "__main__":
    input = str(sys.argv[-1])
    input = input.split(',')
    stent_location = input[0]
    job_name = input[1]
    job_name_full = input[2]
    CylinderExpansion(stent_location, job_name, job_name_full)