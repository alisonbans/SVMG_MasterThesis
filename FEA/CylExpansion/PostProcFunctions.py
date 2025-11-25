from abaqus import *
from abaqusConstants import *
import __main__
import displayGroupMdbToolset as dgm
import displayGroupOdbToolset as dgo
from abaqus import session
import shutil
import subprocess
import os
#import stlExport_kernel

def importODB(case_folder,odb_name):
    old_odb = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion\Results\{odb_name}"
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
    # Extract XY data for Internal and Kinetic energy
    components = {
        'STENT': ('SET-ALL-1', 'StentEnergyRatio'),
        'ARTERY': ('SET-ALL-1', 'ArteryEnergyRatio')
    }
    session.XYDataFromHistory(name='ALLIE PI: ARTERY-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Internal energy: ALLIE PI: ARTERY-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    session.XYDataFromHistory(name='ALLIE PI: STENT-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Internal energy: ALLIE PI: STENT-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    session.XYDataFromHistory(name='ALLKE PI: ARTERY-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Kinetic energy: ALLKE PI: ARTERY-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    session.XYDataFromHistory(name='ALLKE PI: STENT-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Kinetic energy: ALLKE PI: STENT-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    
    for comp, (elset, ratio_name) in components.items():

        xy_ke = session.xyDataObjects[f'ALLKE PI: {comp}-1 ELSET {elset}']
        xy_ie = session.xyDataObjects[f'ALLIE PI: {comp}-1 ELSET {elset}']
        xy_ratio = 100 * xy_ke / xy_ie
        xy_ratio.setValues(sourceDescription=f'100*KE/IE for {comp}')
        session.xyDataObjects.changeKey(xy_ratio.name, ratio_name)
    
        xyp = session.XYPlot(f'Plot-{ratio_name}')
        chart = xyp.charts[xyp.charts.keys()[0]]
        curve = session.Curve(xyData=session.xyDataObjects[ratio_name])
        chart.setValues(curvesToPlot=(curve,))
        
        vp = session.Viewport(name='Viewport-1')
        vp.setValues(displayedObject=xyp)

        # Save plot as PNG
        file_name = os.path.join(case_folder, f"{ratio_name}.png")
        vp.viewportAnnotationOptions.setValues(triad=OFF, title=OFF)
        vp.view.setValues(width=3840, height=2160)

        session.printOptions.setValues(vpBackground=OFF)
        session.printToFile(fileName=file_name, format=PNG, canvasObjects=(vp,))

        """o7 = session.odbs[odb_location]
        session.viewports['Viewport: 1'].setValues(displayedObject=o7)
        xyp = session.XYPlot(f'Plot-{ratio_name}')
        chartName = xyp.charts.keys()[0]
        chart = xyp.charts[chartName]
        xy1 = session.xyDataObjects[ratio_name]
        c1 = session.Curve(xyData=xy1)
        chart.setValues(curvesToPlot=(c1, ), )
        session.charts[chartName].autoColor(lines=True, symbols=True)
        session.viewports['Viewport: 1'].setValues(displayedObject=xyp)
        session.mdbData.summary()"""
        x0 = session.xyDataObjects[ratio_name]
        session.writeXYReport(fileName= os.path.join(case_folder, f'{ratio_name}.csv'), xyData=(x0, ))
    odb.close()
    #sys.exit(0)
def writeCSV(case_folder, odb_name):
    odb_location = rf"{case_folder}\{odb_name}"
    session.mdbData.summary()
    o7 = session.openOdb(
        odb_location, 
        readOnly=False)
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)
    session.linkedViewportCommands.setValues(_highlightLinkedViewports=True)
    leaf = dgo.LeafFromElementSets(elementSets=("STENT-1.SET-ALL", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    odb = session.odbs[odb_location]
    for step in ['Step-EXP', 'Step-REL2']:
        if step == 'Step-EXP':
            file_name = os.path.join(case_folder,'UExp.csv')
            step_nb = 2
            frame_nb = 20
        elif step == 'Step-REL2':
            file_name = os.path.join(case_folder,'URel.csv')
            step_nb = 3
            frame_nb = 5
        else: print('No step with such name')
        session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
        session.writeFieldReport(fileName=file_name, append=OFF, 
            sortItem='Node Label', odb=odb, step=step_nb, frame=frame_nb, outputPosition=NODAL, 
            variable=(('U', NODAL), ), stepFrame=SPECIFY)
    
    
    odb = session.odbs[odb_location]
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    leaf = dgo.LeafFromElementSets(elementSets=("ARTERY-1.SET-ALL", 
        "STENT-1.SET-ALL", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)

def odb_to_STL(stl_dir):
    odb_location = rf"{case_folder}\{odb_name}"
    session.viewports['Viewport: 1'].animationController.setValues(
        animationType=NONE)
    session.viewports['Viewport: 1'].animationController.setValues(
        animationType=TIME_HISTORY)
    session.viewports['Viewport: 1'].animationController.play(
        duration=UNLIMITED)
    session.viewports['Viewport: 1'].animationController.stop()
    session.viewports['Viewport: 1'].animationController.showLastFrame()
    session.viewports['Viewport: 1'].view.setValues(session.views['Back'])
    session.viewports['Viewport: 1'].view.setValues(nearPlane=47.4824, 
        farPlane=80.365, width=15.4369, height=7.02444, viewOffsetX=0.189971, 
        viewOffsetY=-0.0747198)
    session.linkedViewportCommands.setValues(_highlightLinkedViewports=True)
    session.mdbData.summary()
    odb = session.odbs[odb_location]
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    leaf = dgo.LeafFromElementSets(elementSets=("ARTERY-1.SET-ALL", 
        "STENT-1.SET-ALL", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)

    import stlExport_kernel
    stlExport_kernel.STLExport(moduleName='Visualization', 
        stlFileName=stl_dir, 
        stlFileType='ASCII')
def diameter(step, case_folder):
# --- Load node coordinates ---
    import pandas as pd
    import numpy as np
    if step == 'Step-EXP':
        file_path = os.path.join(case_folder, 'UExp.csv')
    elif step =='Step-REL2':
        file_path = os.path.join(case_folder, 'URel.csv')
    else: print('error')
    
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # remove whitespace in headers

    # Keep numeric coordinates only
    for col in ['X', 'Y', 'Z']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['X','Y','Z'])
    
    # --- Split DataFrame by Step ---
    steps = df['Step'].unique()
    
    # Approximate cylinder axis
    x =(df['X']+ df['U-U1'])
    y= (df['Y']+ df['U-U2'])
    x_center = x.mean()
    y_center =y.mean()
    
    # Compute radial distances
    radii = np.sqrt((x - x_center)**2 + (y - y_center)**2)

    # External diameter
    external_diameter = 2 * radii.max()
    diameter = external_diameter
    #print(f"{step}: Approx. external diameter = {external_diameter:.8f} units")

    return diameter
def RR_Diameter(case_folder):
    d_exp = diameter('Step-EXP', case_folder)
    d_rel = diameter('Step-REL2', case_folder)
    d_shrinkage =d_exp-d_rel
    #print(case_folder)
    #print(f'Diameter Shrinkage = {d_shrinkage}')
    return d_shrinkage

def main(case_folder,odb_name,stl_dir):
    importODB(case_folder,odb_name) 
    EnergyRatios(case_folder, odb_name)
    writeCSV(case_folder, odb_name)
    #odb_to_STL(stl_dir)

if __name__ == "__main__":
    input = str(sys.argv[-1])
    input = input.split(',')
    case_folder = input[0]
    odb_name = input[1]
    stl_dir = input[2]
    main(case_folder,odb_name, stl_dir)