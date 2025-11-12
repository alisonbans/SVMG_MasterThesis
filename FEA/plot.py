import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # registers the 3D projection
import numpy as np
from abaqus import session
import displayGroupOdbToolset as dgo
from abaqus import *
from abaqusConstants import *
def plot_deformed():
    file_path = r"C:\Users\z5713258\SVMG_MasterThesis\FEA\UExp.csv"

    # --- Read CSV ---
    df = pd.read_csv(file_path, header=0, low_memory=False)
    df.columns = df.columns.str.strip()  # remove spaces from headers

    # --- Clean numeric columns ---
    for col in ['X', 'Y', 'Z']:
        # Remove leading/trailing spaces and convert to float
        df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')

    # Drop rows where any coordinate is NaN (non-numeric)
    df = df.dropna(subset=['X', 'Y', 'Z'])

    # Extract coordinates
    x = df['X'].values + df['U-U1'].values
    y = df['Y'].values + df['U-U2'].values
    z = df['Z'].values + df['U-U3'].values

    # --- Create 3D plot ---
    fig = plt.figure(figsize=(4, 16))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='b', marker='o', s=10)

    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_zlabel('Z coordinate')
    ax.set_title('3D Coordinate Plot')

    ax.set_box_aspect([1, 1, 4])
    plt.tight_layout()
    plt.show()
    
#plot_deformed()

def diameter(step, case_folder=r"C:\Users\z5713258\SVMG_MasterThesis\FEA" ):
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
RR_Diameter()

def RR_Disp_Mag( case_folder=r"C:\Users\z5713258\SVMG_MasterThesis\FEA"):
    Exp_file_path = os.path.join(case_folder, 'UExp.csv')
    df_exp = pd.read_csv(Exp_file_path)
    df_exp.columns = df_exp.columns.str.strip()  
    df_exp['U-Magnitude'] = pd.to_numeric(df_exp['U-Magnitude'], errors='coerce')
    Rel_file_path = os.path.join(case_folder, 'URel.csv')
    df_rel = pd.read_csv(Rel_file_path)
    df_rel.columns = df_rel.columns.str.strip()  
    df_rel['U-Magnitude'] = pd.to_numeric(df_rel['U-Magnitude'], errors='coerce')

    mean_disp_diff = (df_rel['U-Magnitude']-df_exp['U-Magnitude']).mean()
    print(f'Mean difference in displacement magnitude = {mean_disp_diff}')

RR_Disp_Mag()

def RR_Disp_Mag( case_folder=r"C:\Users\z5713258\SVMG_MasterThesis\FEA"):
    Exp_file_path = os.path.join(case_folder, 'UExp.csv')
    df_exp = pd.read_csv(Exp_file_path)
    df_exp.columns = df_exp.columns.str.strip()  
    df_exp['U-U1'] = pd.to_numeric(df_exp['U-U1'], errors='coerce')
    df_exp['U-U2'] = pd.to_numeric(df_exp['U-U2'], errors='coerce')
    Rel_file_path = os.path.join(case_folder, 'URel.csv')
    df_rel = pd.read_csv(Rel_file_path)
    df_rel.columns = df_rel.columns.str.strip()  
    df_rel['U-U1'] = pd.to_numeric(df_rel['U-U1'], errors='coerce')
    df_rel['U-U2'] = pd.to_numeric(df_rel['U-U2'], errors='coerce')

    #mean_disp_diff = (df_rel['U-U1']-df_exp['U-U1']).mean()
    #print(f'Mean difference in displacement using U1 and U2 = {mean_disp_diff}')

def writeCSV(step,odb_location='C:/Users/z5713258/AbaqusWD/MOD/BalloonArteryCriExp3Nov7e06.odb'):
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
        file_name = 'UExp.csv'
        step_nb = 2
        frame_nb = 20
    elif step == 'Step-REL2':
        file_name = 'URel.csv'
        step_nb = 3
        frame_nb = 5
    else: print('No step with such name')
    session.fieldReportOptions.setValues(reportFormat=COMMA_SEPARATED_VALUES)
    session.writeFieldReport(fileName=file_name, append=OFF, 
        sortItem='Node Label', odb=odb, step=step_nb, frame=frame_nb, outputPosition=NODAL, 
        variable=(('U', NODAL), ), stepFrame=SPECIFY)