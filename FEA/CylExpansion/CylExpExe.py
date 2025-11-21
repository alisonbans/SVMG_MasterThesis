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
InpDir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\INP'
os.makedirs(InpDir, exist_ok=True)
command_1 = r'cd C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\INP'
proc_1 = subprocess.Popen(command_1, shell=True)

# Set up results directory
stent_inp_dir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\Results'
sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\job-FEA.sh'
i = 1
for filename in os.listdir(stent_inp_dir):
    if filename.startswith("FreeExpFull"):
        #print(filename)
        stent_location = os.path.join(stent_inp_dir, filename)
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')
        print(filename)
        
        
        if len(parts) >= 4:
            nus = parts[1]
            sw_str = parts[2].replace('SW', '')
            st_str = parts[3].replace('ST', '')

            sw_um = int(float(sw_str) * 1000)
            st_um = int(float(st_str) * 1000)
        job_name = f"CylExp_{nus}_SW{sw_um}_ST{st_um}"
        job_name_full = f"CylExpFull_{nus}_SW{sw_um}_ST{st_um}"


        #print(job_name)
        working_dir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\INP'
        script_path = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\CylExpFunctions.py'
        command_2 = f'abaqus cae noGUI="{script_path}" -- "{stent_location},{job_name},{job_name_full}"'

        #command_2 = f'abaqus cae script=FreeExpansion.py -- {stent_location}'
        proc_2 = subprocess.Popen(command_2, shell=True, cwd=working_dir)
        proc_2.wait()

        target_sh = os.path.join(InpDir, f"run_{nus}_SW{sw_um}_ST{st_um}.sh")
        with open(sh_template, 'r') as file:
            content = file.read()
        content = content.replace("POT2", job_name_full)
        with open(target_sh, 'w') as file:
            file.write(content)
            
        i +=1


    #if i % 10 == 0 : print(f"Case {formatted_i} : DONE")
end_time = time.time()
print(f"Time to run : {end_time - start_time}")
