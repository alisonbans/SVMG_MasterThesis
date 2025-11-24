import subprocess
import os 
import shutil

# === CONFIGURABLE INPUTS ===
WB_EXE = r"C:\Program Files\ANSYS Inc\v242\Framework\bin\Win64\RunWB2.exe"
WBJN_TEMPLATE = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\WorkbenchTemplate.wbjn"
WBJN_GENERATED = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\WorkbenchGenerated.wbjn"

def generate_journal(mesh,save_path):
    with open(WBJN_TEMPLATE, "r", encoding="utf-8") as template:
        content = template.read()

    # Replace placeholders
    content = content.replace("{{MESH_PATH}}", mesh)
    content = content.replace("{{WBPJ_FILE_PATH}}", save_path)

    with open(WBJN_GENERATED, "w", encoding="utf-8") as output:
        output.write(content)

def run_workbench():
    cmd = f'"{WB_EXE}" -R "{WBJN_GENERATED}"'
    subprocess.run(cmd, shell=True, check=True, cwd = r'C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\WorkingDirectory')

def main_wb(mesh_path, wbpj_save_path):
    generate_journal(mesh_path, wbpj_save_path)
    run_workbench()

def move_def_files(working_dir, case):

    # Destination folder
    def_path_final = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/INP/{case}"
    os.makedirs(def_path_final, exist_ok=True)

    # Move files
    shutil.move(os.path.join(working_dir, f"{case}_files", "dp0","CFX", "CFX","STEADY.def"), os.path.join(def_path_final, "STEADY.def"))
    shutil.move(os.path.join(working_dir, f"{case}_files", "dp0","CFX-1","CFX", "TRANS1.def"),os.path.join(def_path_final, "TRANS1.def"))
    shutil.move(os.path.join(working_dir, f"{case}_files", "dp0","CFX-2","CFX", "TRANS2.def"), os.path.join(def_path_final, "TRANS2.def"))
