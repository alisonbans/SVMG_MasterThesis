import os
import subprocess
from PostProcFunctions import RR_Diameter

odb_list = ["alison-dt1e06-MOD-Amp.odb", "alison-dt3e06-MOD-Amp.odb"]
for odb in odb_list:
    odb_, _ = os.path.splitext(odb)
    case_folder = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\BalloonExpansion\Results\{odb_}"
    os.makedirs(case_folder, exist_ok=True)
    command_1 = r'cd C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA'
    proc_1 = subprocess.Popen(command_1, shell=True)
    working_dir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA'
    odb_name = odb
    script_path = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\BalloonExpansion\\PostProcFunctions.py'
    command_2 = f'abaqus cae script="{script_path}" -- "{case_folder},{odb_name}"'
    proc_2 = subprocess.Popen(command_2, shell=True, cwd=working_dir)
    proc_2.wait()
    RR_Diameter(case_folder)
