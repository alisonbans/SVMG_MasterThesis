import os
import subprocess
import re
import shutil
import time
"""
Author:             Alison Bans 
Last update:        November 6th 2025. 
Code description:   
"""
start_time = time.time()
# Set working directory
ResultsMainDir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\INP'
os.makedirs(ResultsMainDir, exist_ok=True)
command_1 = r'cd C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\INP'
proc_1 = subprocess.Popen(command_1, shell=True)

# Set up results directory
stent_step_dir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\HS1_Results'
sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\job-FEA.sh'
i = 1
for filename in os.listdir(stent_step_dir):
    if filename.endswith(".STEP"):
        #print(filename)
        stent_location = os.path.join(stent_step_dir, filename)
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        print(filename)
        
        
        if len(parts) >= 4:
            nus = parts[1]
            sw_str = parts[2].replace('SW', '')
            st_str = parts[3].replace('ST', '')

            sw_um = int(float(sw_str) * 1000)
            st_um = int(float(st_str) * 1000)
        job_name = f"FreeExp_{nus}_SW{sw_um}_ST{st_um}"
        job_name_full = f"FreeExpFull_{nus}_SW{sw_um}_ST{st_um}"


        #print(job_name)
        working_dir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\INP'
        script_path = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpFunctions.py'
        command_2 = f'abaqus cae noGUI="{script_path}" -- "{stent_location},{job_name},{job_name_full}"'

        #command_2 = f'abaqus cae script=FreeExpansion.py -- {stent_location}'
        proc_2 = subprocess.Popen(command_2, shell=True, cwd=working_dir)
        proc_2.wait()

        target_sh = os.path.join(ResultsMainDir, f"run_{nus}_SW{sw_um}_ST{st_um}.sh")
        with open(sh_template, 'r') as file:
            content = file.read()
        content = content.replace("<POT2>", job_name_full)
        with open(target_sh, 'w') as file:
            file.write(content)
            
        i +=1
    #if i == 2:
    #    break 




    # Path to python folder
    # folder_python = os.path.join(config['path'], "CodesPython\\femurfracture\\simulation\\code\\python")
    # os.chdir(folder_python)

    #if i % 10 == 0 : print(f"Case {formatted_i} : DONE")
end_time = time.time()
print(f"Time to run : {end_time - start_time}")