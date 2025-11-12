from abaqus import *
from abaqusConstants import *
import __main__
import displayGroupMdbToolset as dgm
import displayGroupOdbToolset as dgo
from abaqus import session
import shutil
import subprocess

#import pandas as pd
def importODB(odb_location='C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb'):
    #from abaqus import session
    #session.mdbData.summary()
    #o1 = session.openOdb(
    #    name='C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb', 
    #    readOnly=False)
    #session.viewports['Viewport: 1'].setValues(displayedObject=o1)
    #from  abaqus import session
    #session.upgradeOdb(
    #    "C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06-old.odb", 
    #    "C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb", )
    from  abaqus import session
    session.mdbData.summary()
    o1 = session.openOdb(
        name='C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb', 
        readOnly=False)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1)
def EnergyRatios(odb_location='C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb',
                 output_path='C:/Users/z5713258/SVMG_MasterThesis/FEA/Results/NUS19_SW60_ST60'):
    odb = session.odbs[odb_location]
    # Extract XY data for Internal and Kinetic energy
    components = {
        'STENT': ('SET-ALL-1', 'StentEnergyRatio'),
        'BALLOON': ('SET-ELE-1', 'BalloonEnergyRatio'),
        'ARTERY': ('SET-ALL-1', 'ArteryEnergyRatio')
    }
    session.XYDataFromHistory(name='ALLIE PI: ARTERY-1 ELSET SET-ALL-1', odb=odb, 
        outputVariableName='Internal energy: ALLIE PI: ARTERY-1 in ELSET SET-ALL', 
        steps=('Step-CRI', 'Step-REL1', 'Step-EXP', 'Step-REL2', ), 
        __linkedVpName__='Viewport: 1')
    session.XYDataFromHistory(name='ALLIE PI: BALLOON-1 ELSET SET-ELE-1', odb=odb, 
        outputVariableName='Internal energy: ALLIE PI: BALLOON-1 in ELSET SET-ELE', 
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
    session.XYDataFromHistory(name='ALLKE PI: BALLOON-1 ELSET SET-ELE-1', odb=odb, 
        outputVariableName='Kinetic energy: ALLKE PI: BALLOON-1 in ELSET SET-ELE', 
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
        file_name = os.path.join(output_path, f"{ratio_name}.png")
        vp.viewportAnnotationOptions.setValues(triad=OFF, title=OFF)
        vp.view.setValues(width=1920, height=1080)  # set the viewport size

        session.printOptions.setValues(vpBackground=OFF)
        session.printToFile(fileName=file_name, format=PNG, canvasObjects=(vp,))

        print(f"Saved plot: {file_name}")
    odb.close()
    print(f"Energy ratio plots saved in: {output_path}")
def writeCSV(step,odb_location='C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb',output_path='C:/Users/z5713258/SVMG_MasterThesis/FEA/Results/NUS19_SW60_ST60'):
    session.mdbData.summary()
    o7 = session.openOdb(
        odb_location, 
        readOnly=False)
    session.viewports['Viewport: 1'].setValues(displayedObject=o7)
    session.linkedViewportCommands.setValues(_highlightLinkedViewports=True)
    leaf = dgo.LeafFromElementSets(elementSets=("STENT-1.SET-ALL", ))
    session.viewports['Viewport: 1'].odbDisplay.displayGroup.replace(leaf=leaf)
    odb = session.odbs[odb_location]
    if step == 'Step-EXP':
        file_name = os.path.join(output_path,'UExp.csv')
        step_nb = 2
        frame_nb = 20
    elif step == 'Step-REL2':
        file_name = os.path.join(output_path,'URel.csv')
        step_nb = 3
        frame_nb = 5
    else: print('No step with such name')
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    session.writeFieldReport(fileName=file_name, append=OFF, 
        sortItem='Node Label', odb=odb, step=step_nb, frame=frame_nb, outputPosition=NODAL, 
        variable=(('U', NODAL), ), stepFrame=SPECIFY)
def diameter(step, case_folder='C:/Users/z5713258/SVMG_MasterThesis/FEA/Results/NUS19_SW60_ST60' ):
# --- Load node coordinates ---
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
    print(f"{step}: Approx. external diameter = {external_diameter:.8f} units")

    return diameter
def RR_Diameter():
    d_exp = diameter('Step-EXP')
    d_rel = diameter('Step-REL2')
    d_shrinkage =d_exp-d_rel
    print(f'Diameter Shrinkage = {d_shrinkage}')

def main(odb_location,output_path):
    importODB(odb_location) 
    EnergyRatios(odb_location, output_path)
    writeCSV('Step-EXP')
    writeCSV('Step-REL2')
    #RR_Diameter()

if __name__ == "__main__":
    input = str(sys.argv[-1])
    input = input.split(',')
    if len(input) !=2:
        raise ValueError("Make sure your input variable contains stent location only.")
    odb_location = input[0]
    output_dir = input[1]
    EnergyRatios(odb_location,output_dir)