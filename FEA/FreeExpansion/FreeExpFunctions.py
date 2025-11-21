import sys
import os 
from abaqus import *
from abaqusConstants import *
import __main__
import displayGroupMdbToolset as dgm
import mesh
def CylExp(model):
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

def Assembly(model):
    # Add cylindrical datum to cyl-exp
    cyl_exp = mdb.models[model].parts['CYL-EXP']
    cyl_exp.DatumCsysByThreePoints(name='Dat-CYL', coordSysType=CYLINDRICAL, origin=(0.0, 
        0.0, 0.0), line1=(1.0, 0.0, 0.0), line2=(0.0, 1.0, 0.0))
    #create the assembly
    a = mdb.models[model].rootAssembly  
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name='CYL-EXP-1', part=cyl_exp, dependent=ON)
    stent = mdb.models[model].parts['STENT']
    a.Instance(name='STENT-1', part=stent, dependent=ON)
    f1 = a.instances['STENT-1'].faces
    f2 = a.instances['CYL-EXP-1'].faces
    a.Coaxial(movableAxis=f1[8], fixedAxis=f2[0], flip=OFF)
    a.translate(instanceList=('STENT-1', ), vector=(0.0, 0.0, 26.0))
def MatCoCr(model): 
    mdb.models[model].Material(name='CoCr')
    mdb.models[model].materials['CoCr'].Density(table=((8e-09, ), ))
    mdb.models[model].materials['CoCr'].Elastic(table=((233000.0, 0.35), ))
    mdb.models[model].materials['CoCr'].Plastic(scaleStress=None, table=((
        414.0, 0.0), (933.0, 0.425), (933.0, 1)))
    mdb.models[model].materials['CoCr'].Damping(alpha=70.0)
    mdb.models[model].HomogeneousSolidSection(name='Section-CoCr', 
        material='CoCr', thickness=None)
    #Section Assignment 
    p = mdb.models[model].parts['STENT']
    region = p.sets['SET-ALL']
    p.SectionAssignment(region=region, sectionName='Section-CoCr', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)   
def FreeExp_AddOns(model):
    # Define the expansion and release steps 
    mdb.models[model].ExplicitDynamicsStep(name='Step-EXP', previous='Initial', 
        timePeriod=0.3, improvedDtMethod=ON)
    mdb.models[model].steps['Step-EXP'].setValues(timePeriod=0.3, massScaling=(
        (SEMI_AUTOMATIC, MODEL, THROUGHOUT_STEP, 0.0, 1e-05, BELOW_MIN, 1, 0, 
        0.0, 0.0, 0, None), ), improvedDtMethod=ON)
    mdb.models[model].ExplicitDynamicsStep(name='Step-REL', previous='Step-EXP', 
        timePeriod=0.05, improvedDtMethod=ON)
    # Define the contact between cylinder and stent
    mdb.models[model].ContactProperty('CYL-STENT')
    mdb.models[model].interactionProperties['CYL-STENT'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, 
        table=((0.0, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models[model].interactionProperties['CYL-STENT'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)
    mdb.models[model].ContactExp(name='CYL-STENT', createStepName='Initial')
    r11=mdb.models[model].rootAssembly.instances['CYL-EXP-1'].surfaces['SURF-OUT']
    r12=mdb.models[model].rootAssembly.instances['STENT-1'].surfaces['SURF-IN']
    r21=mdb.models[model].rootAssembly.instances['STENT-1'].surfaces['SURF-ALL']
    mdb.models[model].interactions['CYL-STENT'].includedPairs.setValuesInStep(
        stepName='Initial', useAllstar=OFF, addPairs=((r11, r12), (r21, SELF)))
    mdb.models[model].interactions['CYL-STENT'].contactPropertyAssignments.appendInStep(
        stepName='Initial', assignments=((GLOBAL, SELF, 'CYL-STENT'), ))
    r11=mdb.models[model].rootAssembly.instances['CYL-EXP-1'].surfaces['SURF-OUT']
    r12=mdb.models[model].rootAssembly.instances['STENT-1'].surfaces['SURF-IN']
    mdb.models[model].interactions['CYL-STENT'].includedPairs.setValuesInStep(
        stepName='Step-REL', removePairs=((r11, r12), ))
    mdb.models[model].SmoothStepAmplitude(name='AMP-FREE-EXP', timeSpan=TOTAL, 
        data=((0.0, 0.0), (0.3, 1.0), (0.35, 1.0)))
    # Define element type 
    p = mdb.models[model].parts['CYL-EXP']
    elemType1 = mesh.ElemType(elemCode=SFM3D4R, elemLibrary=EXPLICIT)
    z1 = p.elements
    elems1 = z1[0:16872]
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
    a = mdb.models[model].rootAssembly
    a.regenerate()
    # Create viscous load and displacement
    a = mdb.models[model].rootAssembly
    region = a.instances['STENT-1'].surfaces['SURF-ALL']
    mdb.models[model].Pressure(name='StentSurfViscous', createStepName='Step-EXP', # check the step of creation
        region=region, distributionType=VISCOUS, field='', magnitude=0.0006, 
        amplitude=UNSET)
    cyl_exp = mdb.models[model].parts['CYL-EXP']
    cyl_exp.DatumCsysByThreePoints(name='Dat-CYL', coordSysType=CYLINDRICAL, origin=(0.0, 
        0.0, 0.0), line1=(1.0, 0.0, 0.0), line2=(0.0, 1.0, 0.0))
    a = mdb.models[model].rootAssembly
    a.regenerate()
    region = a.instances['CYL-EXP-1'].sets['SET-NODE']
    datum = mdb.models[model].rootAssembly.instances['CYL-EXP-1'].datums[6]
    mdb.models[model].DisplacementBC(name='CYL-EXP', createStepName='Step-EXP', 
        region=region, u1=1.2, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, 
        ur3=UNSET, amplitude='AMP-FREE-EXP', fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=datum)
    mdb.models[model].FieldOutputRequest(name='F-Output-1', 
        createStepName='Step-EXP', variables=('RF', 'U', 'V','LE', 'PE', 'PEEQ', 'S','CFORCE', 'CSTRESS'))
    mdb.models[model].fieldOutputRequests['F-Output-1'].setValuesInStep(
        stepName='Step-REL', numIntervals=5)
    mdb.models[model].HistoryOutputRequest(name='H-Output-1', 
        createStepName='Step-EXP', variables=('ALLIE', 'ALLKE'))
    regionDef=mdb.models[model].rootAssembly.allInstances['STENT-1'].sets['SET-ALL']
    mdb.models[model].historyOutputRequests['H-Output-1'].setValues(variables=(
        'ALLIE', 'ALLKE'), region=regionDef, sectionPoints=DEFAULT, 
        rebar=EXCLUDE)
def FreeExpansion(stent_location, job_name, job_name_full,base_name):
    mdb.ModelFromInputFile(name=base_name, inputFileName=stent_location)
    del mdb.models['Model-1']
    model = 'CYL-STENT'
    mdb.models.changeKey(fromName = base_name, toName=model)
    MatCoCr(model)
    CylExp(model)
    Assembly(model)
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
    FreeExp_AddOns(job_name)
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
    base_name = input[3]
    FreeExpansion(stent_location, job_name, job_name_full, base_name)