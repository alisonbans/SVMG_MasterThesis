import subprocess
import numpy as np
import random
import shutil
import os
import sys
import pandas as pd
from pathlib import Path
from FEA.CylExpansion.PostProcFunctions import RR_Diameter
from CFD.Blender.BlenderExe import run_in_blender
from CFD.Fluent.FluentExe import main_fluent
from CFD.Workbench.WorkbenchExe import main_wb, move_def_files
from CFD.Workbench.PostProcExe import main_wb_pp
from Design.LHS import lhs
"""
Author:             Alison Bans 
Last update:        24 November 2025
Code description:   This code is the entire loop allowing for optimisation 
"""
# ------------------------------------------------------------------------------------------------
# 0. DEFINITIONS ---------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

random.seed(42)
matlab_exe = r"C:\Program Files\MATLAB\R2023b\bin\matlab.exe"
matlab_folder = r"C:/Users/z5713258/SVMG_MasterThesis/Design"
matlab_folder_HS1 = os.path.join(matlab_folder, "HS1")
matlab_folder_HS1_results = os.path.join(matlab_folder_HS1, "HS1_Results")
step_folder = os.path.join(matlab_folder, "HS1_Results")
template_cae = r'C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion\Template.cae'
FreeExp_folder = r"C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion"
working_dir_fea = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA'
fea_sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\job-FEA.sh'
FreeExp_results = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\Results'
fe_pp = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\PostProcFunctions.py'
CylExp_folder = r"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion"
cylexp_functions = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\CylExpFunctions.py'
ce_pp = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\PostProcFunctions.py'
working_dir_ce = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\INP'
cfd_sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\\Workbench\\job-cfd.sh'
wb_folder = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\Workbench'
wb_results = os.path.join(wb_folder, 'Results')
design_space_csv = r"C:\Users\z5713258\SVMG_MasterThesis\DesignSpace.csv"
design = [19, 0.46, 18, 0.95, 0.1, 1.63339, 0.39003, 0.75959, 0.81258, 1.31384, 0.04872, 0.00164, 0.07540, 0.61571, 4.16285, 1.79921, 0.06, 0.06]
N = 1

# ------------------------------------------------------------------------------------------------
# 1. LATIN HYPERCUBE SAMPLING --------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
if not os.path.isfile(design_space_csv):
    lhs(N)

# ------------------------------------------------------------------------------------------------
# 2. FREE EXPANSION ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
r"""design_space = pd.read_csv(design_space_csv)
for design_nb in range(0,N):
    # -------------------------------------------------------------------------------------------
    # 2.1 GENERATE THE COMPUTER AIDED DESIGN ----------------------------------------------------
    # -------------------------------------------------------------------------------------------
    NUS = design_space['NUS'].iloc[design_nb]
    SW = design_space['SW'].iloc[design_nb]
    ST = design_space['ST'].iloc[design_nb]
    case = f'NUS{NUS}_SW{SW}_ST{ST}'
    design[0] = NUS
    design[16] = SW/1000
    design[17] = ST/1000
    design_str = ','.join(map(str, design))
    matlab_cmd = f"cd('{matlab_folder_HS1}'); status = Main([{design_str}]); disp(status);"
    result = subprocess.run(
        [matlab_exe, "-batch", matlab_cmd],
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if line.isdigit():
            status = int(line)
            break
    design_space.loc[design_nb, 'DesignLabel'] = status
    if status == 0:
        continue
    step = f'stent_{case}.STEP'
    step_1 = os.path.join(matlab_folder_HS1_results, step)
    step_2 = os.path.join(step_folder, step)
    shutil.move(step_1, step_2)

    # -------------------------------------------------------------------------------------------
    # 2.2 CREATE THE STENT MESH, SETS & SURFACES ------------------------------------------------
    # -------------------------------------------------------------------------------------------
    abaqus_cmd = r"C:\SIMULIA\Commands\abaqus.bat"
    stent_location = step_2
    stent_script = os.path.join(FreeExp_folder,'Stent.py')
    command1 = f'abaqus cae script="{stent_script}" -- "{template_cae},{stent_location}"'
    proc1 = subprocess.Popen(command1, cwd=os.path.join(FreeExp_folder,'INP'), shell=True)
    proc1.wait()
    
    input("Press enter when the mesh is available ...")
    mesh = F'mesh_{case}.inp'
    mesh_path = os.path.join(FreeExp_folder,'INP',mesh)
    while not os.path.exists(mesh_path): 
        print("Mesh file not found.")
        answer = input("Press enter when the mesh is available \nTo force exit this loop type: out ... ")
        if answer.strip().lower() == 'out':
            break
    
    # -------------------------------------------------------------------------------------------
    # 2.3 PREPARE FREE EXPANSION FILES ----------------------------------------------------------
    # -------------------------------------------------------------------------------------------
    job_name = f"FreeExp_{case}"
    base_name = case
    job_name_full = f"FreeExpFull_{case}"
    script_path=os.path.join(FreeExp_folder,'FreeExpFunctions.py')
    command2 = f'abaqus cae noGUI="{script_path}" -- "{mesh_path},{job_name},{job_name_full},{base_name}"'
    proc2 = subprocess.Popen(command2, shell=True, cwd=os.path.join(FreeExp_folder,'INP'))
    proc2.wait()
    target_sh = os.path.join(os.path.join(FreeExp_folder,'INP'), f"run_{case}.sh")
    with open(fea_sh_template, 'r', newline='\n') as file:
        content = file.read()
    content = content.replace("POT2", job_name_full)
    content = content.replace("walltime=24:00:00", "walltime=01:00:00")
    content = content.replace("ncpus=48", "ncpus=48")
    with open(target_sh, 'w', newline='\n') as file:
        file.write(content)

design_space.to_csv(design_space_csv, index=False)
design_space = pd.read_csv(design_space_csv)
design_space['EnergyRatioFE'] = np.nan
input("Press enter when free expansion odb files are available ...")
design_space = pd.read_csv(design_space_csv)
# ------------------------------------------------------------------------------------------------
# 3. CYLINDER EXPANSION --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
for design_nb in range(0,N):
    if design_space['DesignLabel'].iloc[design_nb] ==0:
        continue
    NUS = design_space['NUS'].iloc[design_nb]
    SW = design_space['SW'].iloc[design_nb]
    ST = design_space['ST'].iloc[design_nb]
    case = f'NUS{NUS}_SW{SW}_ST{ST}'
    
    # --------------------------------------------------------------------------------------------
    # 3.1 POST PROCESSING OF FREE EXPANSION ------------------------------------------------------
    # --------------------------------------------------------------------------------------------
    case_folder = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion\Results\{case}"
    os.makedirs(case_folder, exist_ok=True)
    odb_name = f'FreeExpFull_{case}.odb'
    command4 = f'abaqus cae script="{fe_pp}" -- "{case_folder},{odb_name}"'
    proc4 = subprocess.Popen(command4, shell=True, cwd=working_dir_fea)
    proc4.wait()

    df = pd.read_csv(os.path.join(case_folder, 'StentEnergyRatio.csv'),sep=r"\s+")
    df['StentEnergyRatio'] = pd.to_numeric(df['StentEnergyRatio'], errors='coerce')
    df['X'] = pd.to_numeric(df['X'], errors='coerce')
    df_exp = df[(df['X'] > 0.15) & (df['X'] < 0.45)]
    max_ratio = df_exp['StentEnergyRatio'].max()
    design_space.loc[design_nb,'EnergyRatioFE'] = max_ratio
    # --------------------------------------------------------------------------------------------
    # 3.2 PREPARE CYLINDER EXPANSION FILES ------------------------------------------------------
    # --------------------------------------------------------------------------------------------
    job_name = f"CylExp_{case}"
    job_name_full = f"CylExpFull_{case}"
    exp_stent_location = os.path.join(FreeExp_folder,'Results',case, f'FreeExpFull_{str(case)}.odb')
    command3 = f'abaqus cae noGUI="{cylexp_functions}" -- "{exp_stent_location},{job_name},{job_name_full}"'
    proc3 = subprocess.Popen(command3, shell=True, cwd=working_dir_ce)
    proc3.wait()
    target_sh = os.path.join(os.path.join(FreeExp_folder,'INP'), f"run_{case}.sh")
    with open(fea_sh_template, 'r', newline='\n') as file:
        content = file.read()
    content = content.replace("POT2", job_name_full)
    content = content.replace("walltime=24:00:00", "walltime=06:00:00")
    content = content.replace("ncpus=48", "ncpus=24")
    with open(target_sh, 'w', newline='\n') as file:
        file.write(content)
"""
#design_space.to_csv(design_space_csv, index=False)
design_space = pd.read_csv(design_space_csv)
r"""design_space['EnergyRatioCE'] = np.nan
design_space['RRabs'] = np.nan
input("Press enter when cylinder expansion odb files are available ...")"""
# ------------------------------------------------------------------------------------------------
# 4. CARRY OUT POST-PROCESSING OF THE FEA AND PREPARE CFD FILES ----------------------------------
# ------------------------------------------------------------------------------------------------
for design_nb in range(0,N):
    if design_space['DesignLabel'].iloc[design_nb] ==0:
        continue
    NUS = design_space['NUS'].iloc[design_nb]
    SW = design_space['SW'].iloc[design_nb]
    ST = design_space['ST'].iloc[design_nb]
    case = f'NUS{NUS}_SW{SW}_ST{ST}'

    # --------------------------------------------------------------------------------------------
    # 4.1 POST PROCESSING OF CYLINDER EXPANSION --------------------------------------------------
    # --------------------------------------------------------------------------------------------
    case_folder = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion\Results\{case}"
    os.makedirs(case_folder, exist_ok=True)
    odb_name = f'CylExpFull_{case}.odb'
    r"""
    stl_file = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion\Results\{case}\{case}.stl"
    command4 = f'abaqus cae script="{ce_pp}" -- "{case_folder},{odb_name},{stl_file}"'
    proc4 = subprocess.Popen(command4, shell=True, cwd=working_dir_fea)
    proc4.wait()
    input("Press enter when the stl is available ...")
    rr_abs = RR_Diameter(case_folder)
    df = pd.read_csv(os.path.join(case_folder, 'StentEnergyRatio.csv'),sep=r"\s+")
    df['StentEnergyRatio'] = pd.to_numeric(df['StentEnergyRatio'], errors='coerce')
    df['X'] = pd.to_numeric(df['X'], errors='coerce')
    df_exp = df[(df['X'] > 0.45) & (df['X'] < 0.9)]
    max_ratio_exp = df_exp['StentEnergyRatio'].max()
    design_space.loc[design_nb,'EnergyRatioCE'] = round(max_ratio_exp, 2) 
    design_space.loc[design_nb,'RRabs'] = round(rr_abs,4)
    design_space.to_csv(design_space_csv, index=False)
    # --------------------------------------------------------------------------------------------
    # 4.2 RUN BLENDER, FLUENT & WORKBENCH --------------------------------------------------------
    # --------------------------------------------------------------------------------------------
    run_in_blender(case, stl_file) 
    input("Press enter once the blender part is checked ....")
    main_fluent(case)
    input("Check mesh and press enter when done ...")
    mesh_path = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Fluent/Mesh/{case}.msh"
    wbpj_save_path =  rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}.wbpj"
    main_wb(mesh_path, wbpj_save_path)
    input(f"Press enter when the definition files are ready for {case}...")
    working_dir =  r"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory"
    move_def_files(working_dir, case)
    shutil.copy(cfd_sh_template, os.path.join(r'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\\Workbench\\INP', case))"""

design_space.to_csv(design_space_csv, index=False)
design_space = pd.read_csv(design_space_csv)
design_space['lowESSpercentArea'] = np.nan
input("Press enter when the cfd result files are available ...")
# ------------------------------------------------------------------------------------------------
# 5. CARRY OUT POST-PROCESSING OF THE CFD --------------------------------------------------------
# ------------------------------------------------------------------------------------------------
for design_nb in range(0,N):
    if design_space['DesignLabel'].iloc[design_nb] ==0:
        continue
    NUS = design_space['NUS'].iloc[design_nb]
    SW = design_space['SW'].iloc[design_nb]
    ST = design_space['ST'].iloc[design_nb]
    case = f'NUS{NUS}_SW{SW}_ST{ST}'
    old_wbpj = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}_e6.wbpj"
    new_wbpj = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}_e6_pp.wbpj"
    res = rf'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\Workbench\\Results\\{case}_e6\\TRANS2_001.res'
    main_wb_pp(old_wbpj, new_wbpj, res)
    shutil.move(new_wbpj, rf'C:/Users/z5713258/SVMG_MasterThesis/CFD\Workbench/Results/{case}_e6')
    shutil.move(rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}_e6_pp_files", rf'C:/Users/z5713258/SVMG_MasterThesis/CFD\Workbench/Results/{case}_e6')
    lowESS = float(input(f"Write down the area of low ESS for {case}: "))
    design_space.loc[design_nb,'lowESSpercentArea'] = lowESS

design_space.to_csv(design_space_csv, index=False)
