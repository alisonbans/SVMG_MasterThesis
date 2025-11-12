import os
import subprocess

PlotDir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\Results\\NUS19_SW60_ST60'
os.makedirs(PlotDir, exist_ok=True)
print(1)
command_1 = r'cd C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA'
proc_1 = subprocess.Popen(command_1, shell=True)
print(2)
working_dir = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA'
odb_location=r'C:\\Users\\z5713258\\AbaqusWD\\MOD\\BalloonArteryCriExp3Nov7e06.odb'
script_path = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\PostProcFunctions.py'
command_2 = f'abaqus cae script="{script_path}" -- "{odb_location},{PlotDir}"'
proc_2 = subprocess.Popen(command_2, shell=True, cwd=working_dir)
proc_2.wait()