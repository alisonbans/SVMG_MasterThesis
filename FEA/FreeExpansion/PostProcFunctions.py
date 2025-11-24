from abaqus import *
from abaqusConstants import *
import __main__
from abaqus import session
import os
#import stlExport_kernel

def importODB(case_folder,odb_name):
    old_odb = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion\Results\{odb_name}"
    new_job = rf"{case_folder}\{odb_name}"
    cmd = f'abaqus upgrade -job {new_job} -odb "{old_odb}"'
    os.system(cmd)  
    from  abaqus import session
    session.mdbData.summary()
    o1 = session.openOdb(
        name=new_job, 
        readOnly=False)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)

def EnergyRatios(case_folder,odb_name):
    odb_location = rf"{case_folder}\{odb_name}"
    odb = session.odbs[odb_location]
    
    session.XYDataFromHistory(name='ALLIE PI: STENT-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Internal energy: ALLIE PI: STENT-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    session.XYDataFromHistory(name='ALLKE PI: STENT-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Kinetic energy: ALLKE PI: STENT-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    
    xy_ke = session.xyDataObjects[f'ALLKE PI: STENT-1 ELSET SET-ALL-1']
    xy_ie = session.xyDataObjects[f'ALLIE PI: STENT-1 ELSET SET-ALL-1']
    xy_ratio = 100 * xy_ke / xy_ie
    xy_ratio.setValues(sourceDescription=f'100*KE/IE for STENT')
    session.xyDataObjects.changeKey(xy_ratio.name, 'StentEnergyRatio')

    xyp = session.XYPlot(f'StentEnergyRatio')
    chart = xyp.charts[xyp.charts.keys()[0]]
    curve = session.Curve(xyData=session.xyDataObjects['StentEnergyRatio'])
    chart.setValues(curvesToPlot=(curve,))
    
    vp = session.Viewport(name='Viewport-1')
    vp.setValues(displayedObject=xyp)

    # Save plot as PNG
    file_name = os.path.join(case_folder, f"StentEnergyRatio.png")
    vp.viewportAnnotationOptions.setValues(triad=OFF, title=OFF)
    vp.view.setValues(width=3840, height=2160)

    session.printOptions.setValues(vpBackground=OFF)
    session.printToFile(fileName=file_name, format=PNG, canvasObjects=(vp,))


def main(case_folder,odb_name):
    importODB(case_folder,odb_name) 
    EnergyRatios(case_folder, odb_name)

if __name__ == "__main__":
    input = str(sys.argv[-1])
    input = input.split(',')
    case_folder = input[0]
    odb_name = input[1]
    main(case_folder,odb_name)