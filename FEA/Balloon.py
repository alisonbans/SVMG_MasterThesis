from abaqus import *
from abaqusConstants import *
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
import math
def Balloon(E = 850):
    density = 1e-09
    poisson = 0.45
    viscous_const = float(0.01 * density * math.sqrt(E*(1-poisson)/density/(1+poisson)/(1-2*poisson)))
    atm_pressure = [5, 10, 12, 15, 20, 25]
    mpa_pressure = [float(p * 0.101325) for p in atm_pressure]
    #Import balloon
    mdb.models['Model-1'].PartFromInputFile(
        inputFileName='D:/Alison/b3x18_mesh.inp')
    p = mdb.models['Model-1'].parts['PART-1']
    mdb.models['Model-1'].parts.changeKey(fromName='PART-1', toName='BALLOON')
    # Sets and Surfaces
    p = mdb.models['Model-1'].parts['BALLOON']
    e = p.elements
    elements = e.getSequenceFromMask(mask=('[#ffffffff:262 #ffff ]', ), )
    p.Set(elements=elements, name='Set-ELE')
    elements = e.getSequenceFromMask(mask=('[#0:131 #ffffff00 #ffffffff:3 ]', ), )
    p.Set(elements=elements, name='Set-EXT1')
    e = p.elements
    elements = e.getSequenceFromMask(mask=('[#0:95 #fff00000 #ffffffff:3 #fff ]', 
        ), )
    p.Set(elements=elements, name='Set-EXT2')   
    s = p.elements
    side2Elements = s.getSequenceFromMask(mask=('[#ffffffff:262 #ffff ]', ), )
    p.Surface(side2Elements=side2Elements, name='Surf-IN')
    side1Elements = s.getSequenceFromMask(mask=('[#ffffffff:262 #ffff ]', ), )
    p.Surface(side1Elements=side1Elements, name='Surf-OUT') 
    side12Elements = s.getSequenceFromMask(mask=('[#ffffffff:262 #ffff ]', ), )
    p.Surface(side12Elements=side12Elements, name='Surf-ALL') 
    #Create and assign material 
    mdb.models['Model-1'].Material(name='BALLOON')
    mdb.models['Model-1'].materials['BALLOON'].Density(table=((density, ), ))
    mdb.models['Model-1'].materials['BALLOON'].Elastic(table=((E, poisson), ))
    mdb.models['Model-1'].MembraneSection(name='Section-BALLOON', 
        material='BALLOON', thicknessType=UNIFORM, thickness=0.03, 
        thicknessField='', poissonDefinition=DEFAULT)
    region = p.sets['Set-ELE']
    p.SectionAssignment(region=region, sectionName='Section-BALLOON', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    # Assign mesh element type
    elemType1 = mesh.ElemType(elemCode=M3D4R, elemLibrary=EXPLICIT, 
        secondOrderAccuracy=OFF, hourglassControl=DEFAULT)
    z1 = p.elements
    elems1 = z1[0:8400]
    pickedRegions =(elems1, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
    # Create the assembly
    a = mdb.models['Model-1'].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    a.Instance(name='BALLOON-1', part=p, dependent=ON)
    a  = mdb.models['Model-1'].rootAssembly
    a.LinearInstancePattern(instanceList=('BALLOON-1', ), direction1=(1.0, 0.0, 
        0.0), direction2=(0.0, 1.0, 0.0), number1=6, number2=1, spacing1=6.0, 
        spacing2=1.0074)
    # Reference points 
    n11 = a.instances['BALLOON-1'].nodes
    a.ReferencePoint(point=n11[3269])    
    n21 = a.instances['BALLOON-1'].nodes
    a.ReferencePoint(point=n21[4415])
    mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-2', 
        toName='RP-EXT1')
    mdb.models['Model-1'].rootAssembly.features.changeKey(fromName='RP-1', 
        toName='RP-EXT2')
    n11 = a.instances['BALLOON-1-lin-2-1'].nodes
    a.ReferencePoint(point=n11[4303])
    n21 = a.instances['BALLOON-1-lin-3-1'].nodes
    a.ReferencePoint(point=n21[4303])
    n11 = a.instances['BALLOON-1-lin-4-1'].nodes
    a.ReferencePoint(point=n11[4303])
    n21 = a.instances['BALLOON-1-lin-5-1'].nodes
    a.ReferencePoint(point=n21[4303])
    n11 = a.instances['BALLOON-1-lin-6-1'].nodes
    a.ReferencePoint(point=n11[4303])
    n21 = a.instances['BALLOON-1-lin-2-1'].nodes
    a.ReferencePoint(point=n21[3254])
    n11 = a.instances['BALLOON-1-lin-3-1'].nodes
    a.ReferencePoint(point=n11[3254])
    n21 = a.instances['BALLOON-1-lin-4-1'].nodes
    a.ReferencePoint(point=n21[3254])
    n11 = a.instances['BALLOON-1-lin-5-1'].nodes
    a.ReferencePoint(point=n11[3254])
    n21 = a.instances['BALLOON-1-lin-6-1'].nodes
    a.ReferencePoint(point=n21[3254])
    # Rigid body
    region2=a.instances['BALLOON-1'].sets['Set-EXT1']
    r1 = a.referencePoints
    refPoints1=(r1[15], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='RB_EXT1', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1'].sets['Set-EXT2']
    r1 = a.referencePoints
    refPoints1=(r1[14], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='RB_EXT2', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-2-1'].sets['Set-EXT1']
    r1 = a.referencePoints
    refPoints1=(r1[16], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-3', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-2-1'].sets['Set-EXT2']
    r1 = a.referencePoints
    refPoints1=(r1[21], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-4', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-3-1'].sets['Set-EXT1']
    r1 = a.referencePoints
    refPoints1=(r1[17], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-5', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-3-1'].sets['Set-EXT2']
    r1 = a.referencePoints
    refPoints1=(r1[22], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-6', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-4-1'].sets['Set-EXT1']
    r1 = a.referencePoints
    refPoints1=(r1[18], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-7', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-4-1'].sets['Set-EXT2']
    r1 = a.referencePoints
    refPoints1=(r1[23], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-8', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-5-1'].sets['Set-EXT1']
    r1 = a.referencePoints
    refPoints1=(r1[19], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-9', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-5-1'].sets['Set-EXT2']
    r1 = a.referencePoints
    refPoints1=(r1[24], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-10', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-6-1'].sets['Set-EXT1']
    r1 = a.referencePoints
    refPoints1=(r1[20], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-11', refPointRegion=region1, 
        bodyRegion=region2)
    region2=a.instances['BALLOON-1-lin-6-1'].sets['Set-EXT2']
    r1 = a.referencePoints
    refPoints1=(r1[25], )
    region1=regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-1'].RigidBody(name='Constraint-12', refPointRegion=region1, 
        bodyRegion=region2)
    # Create amplitude 
    mdb.models['Model-1'].SmoothStepAmplitude(name='AMP-EXP', timeSpan=TOTAL, data=((
        0.0, 0.0), (0.4, 1.0)))
    # Create steps 
    mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-EXP', previous='Initial', 
        timePeriod=0.4, massScaling=((SEMI_AUTOMATIC, MODEL, THROUGHOUT_STEP, 
        0.0, 1e-06, BELOW_MIN, 1, 0, 0.0, 0.0, 0, None), ), 
        improvedDtMethod=ON)
    # Create loads and boundary conditions
    region = a.instances['BALLOON-1'].surfaces['Surf-ALL']
    mdb.models['Model-1'].Pressure(name='ViscousPressure', 
        createStepName='Step-EXP', region=region, distributionType=VISCOUS, 
        field='', magnitude=viscous_const, amplitude='AMP-EXP')
    region = a.instances['BALLOON-1'].surfaces['Surf-IN']
    mdb.models['Model-1'].Pressure(name='ExpPressure', createStepName='Step-EXP', 
        region=region, distributionType=UNIFORM, field='', magnitude=mpa_pressure[0], 
        amplitude='AMP-EXP')
    r1 = a.referencePoints
    refPoints1=(r1[14], r1[15], r1[16], r1[17], r1[18], r1[19], r1[20], r1[21], 
        r1[22], r1[23], r1[24], r1[25], )
    region = a.Set(referencePoints=refPoints1, name='Set-4')
    mdb.models['Model-1'].EncastreBC(name='Encaster', createStepName='Initial', 
        region=region, localCsys=None)
    # Copy the expansion pressure load
    mdb.models['Model-1'].loads.changeKey(fromName='ExpPressure', 
        toName='ExpPressure1')
    mdb.models['Model-1'].Load(name='ExpPressure2', 
        objectToCopy=mdb.models['Model-1'].loads['ExpPressure1'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ExpPressure3', 
        objectToCopy=mdb.models['Model-1'].loads['ExpPressure2'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ExpPressure4', 
        objectToCopy=mdb.models['Model-1'].loads['ExpPressure2'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ExpPressure5', 
        objectToCopy=mdb.models['Model-1'].loads['ExpPressure3'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ExpPressure6', 
        objectToCopy=mdb.models['Model-1'].loads['ExpPressure2'], 
        toStepName='Step-EXP')
    region = a.instances['BALLOON-1-lin-2-1'].surfaces['Surf-IN']
    mdb.models['Model-1'].loads['ExpPressure2'].setValues(region=region, magnitude = mpa_pressure[1])
    region = a.instances['BALLOON-1-lin-3-1'].surfaces['Surf-IN']
    mdb.models['Model-1'].loads['ExpPressure3'].setValues(region=region, magnitude = mpa_pressure[2])
    region = a.instances['BALLOON-1-lin-4-1'].surfaces['Surf-IN']
    mdb.models['Model-1'].loads['ExpPressure4'].setValues(region=region, magnitude = mpa_pressure[3])
    region = a.instances['BALLOON-1-lin-5-1'].surfaces['Surf-IN']
    mdb.models['Model-1'].loads['ExpPressure5'].setValues(region=region, magnitude = mpa_pressure[4])
    region = a.instances['BALLOON-1-lin-6-1'].surfaces['Surf-IN']
    mdb.models['Model-1'].loads['ExpPressure6'].setValues(region=region, magnitude = mpa_pressure[5])
    # Copy the viscous pressures
    mdb.models['Model-1'].Load(name='ViscousPressure2', 
        objectToCopy=mdb.models['Model-1'].loads['ViscousPressure'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ViscousPressure3', 
        objectToCopy=mdb.models['Model-1'].loads['ViscousPressure2'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ViscousPressure4', 
        objectToCopy=mdb.models['Model-1'].loads['ViscousPressure3'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ViscousPressure5', 
        objectToCopy=mdb.models['Model-1'].loads['ViscousPressure4'], 
        toStepName='Step-EXP')
    mdb.models['Model-1'].Load(name='ViscousPressure6', 
        objectToCopy=mdb.models['Model-1'].loads['ViscousPressure5'], 
        toStepName='Step-EXP')
    region = a.instances['BALLOON-1-lin-2-1'].surfaces['Surf-ALL']
    mdb.models['Model-1'].loads['ViscousPressure2'].setValues(region=region)
    region = a.instances['BALLOON-1-lin-3-1'].surfaces['Surf-ALL']
    mdb.models['Model-1'].loads['ViscousPressure3'].setValues(region=region)
    region = a.instances['BALLOON-1-lin-4-1'].surfaces['Surf-ALL']
    mdb.models['Model-1'].loads['ViscousPressure4'].setValues(region=region)
    region = a.instances['BALLOON-1-lin-5-1'].surfaces['Surf-ALL']
    mdb.models['Model-1'].loads['ViscousPressure5'].setValues(region=region)
    region = a.instances['BALLOON-1-lin-6-1'].surfaces['Surf-ALL']
    mdb.models['Model-1'].loads['ViscousPressure6'].setValues(region=region)
    # Field and History outputs 
    mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
        'ALLIE', 'ALLKE'))
    mdb.models['Model-1'].fieldOutputRequests['F-Output-1'].setValues(variables=(
        'CSTRESS', 'LE', 'PE', 'PEEQ', 'RF', 'S', 'U', 'V', 'CFORCE'))


def Balloon6():

    
    

    
    