"""
LHS

for i in N/2:
    run_matlab()
    if label ==0:
        break
    while mesh does not exist:
        print("Create the mesh for stent ...")
        input("Press Enter to continue")

    run_FreeExp
"""

import subprocess
import numpy as np
import random
import shutil
import os
random.seed(42)
matlab_exe = r"C:\Program Files\MATLAB\R2023b\bin\matlab.exe"
matlab_folder = r"C:/Users/z5713258/SVMG_MasterThesis/Design"
matlab_folder_HS1 = os.path.join(matlab_folder, "HS1")
matlab_folder_HS1_results = os.path.join(matlab_folder_HS1, "HS1_Results")
step_folder = os.path.join(matlab_folder, "HS1_Results")
FreeExp_folder = r"C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion"
fea_sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\job-FEA.sh'

design = [19, 0.46, 18, 0.95, 0.1, 1.63339, 0.39003, 0.75959, 0.81258, 1.31384, 0.04872, 0.00164, 0.07540, 0.61571, 4.16285, 1.79921, 0.06, 0.06]
#NUS_list = 
#SW_min =
#SW_max =
#ST_min = 
#STmax = 
#LHS
for i in range(1,2):
    # 1. Create the design ------------------------------------------------------------------------------------------
    #design[0] =
    #design[16] =
    #design[17] =
    """design_str = ','.join(map(str, design))
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
    #add status to csv
    if status == 0:
        continue
    #correct this
    step = 'stent_NUS19_SW0.0600_ST0.0600.STEP'
    step_1 = os.path.join(matlab_folder_HS1_results, step)
    step_2 = os.path.join(step_folder, step)
    shutil.move(step_1, step_2)
"""
    # 2. Make the stent mesh ---------------------------------------------------------------------------------------------------------
    input("Press enter when the mesh is available ...")
    mesh = 'mesh_NUS19_SW60_ST60.inp'
    mesh_path = os.path.join(FreeExp_folder,'INP',mesh)
    while not os.path.exists(mesh_path): 
        print("Mesh file not found.")
        answer = input("Press enter when the mesh is available \nTo force exit this loop type: out ... ")
        if answer.strip().lower() == 'out':
            break
    
    # 3. Prepare and run the free expansion --------------------------------------------------------------------------------------------
    #job_name = f"FreeExp_{nus}_SW{sw_um}_ST{st_um}"
    job_name = "FreeExp_NUS19_SW60_ST60"
    job_name_full = "FreeExpFull_NUS19_SW60_ST60"
    base_name = "NUS19_SW60_ST60"
    #job_name_full = f"FreeExpFull_{nus}_SW{sw_um}_ST{st_um}"
    script_path=os.path.join(FreeExp_folder,'FreeExpFunctions.py')
    command_2 = f'abaqus cae noGUI="{script_path}" -- "{mesh_path},{job_name},{job_name_full},{base_name}"'
    proc_2 = subprocess.Popen(command_2, shell=True, cwd=os.path.join(FreeExp_folder,'INP'))
    proc_2.wait()
    #target_sh = os.path.join(os.path.join(FreeExp_folder,'INP'), f"run_{nus}_SW{sw_um}_ST{st_um}.sh")
    target_sh = os.path.join(os.path.join(FreeExp_folder,'INP'), "run_NUS19_SW60_ST60.sh")    
    with open(fea_sh_template, 'r') as file:
        content = file.read()
    content = content.replace("POT2", job_name_full)
    with open(target_sh, 'w') as file:
        file.write(content)

    #input("Press enter to continue when simulation is launched on Gadi ...")

#for i in range(1,2):
    # free exp post processing 
    # 
    # 
        