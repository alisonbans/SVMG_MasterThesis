import subprocess
import os
import shutil

# === CONFIGURABLE INPUTS ===
WB_EXE = r"C:\Program Files\ANSYS Inc\v242\Framework\bin\Win64\RunWB2.exe"
WBJN_TEMPLATE = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\WorkbenchTemplate.wbjn"
WBJN_GENERATED = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\WorkbenchGenerated.wbjn"

# === DYNAMIC PARAMETERS ===
mesh_path = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/CFD_STL_input/EXAMPLE2.msh"
def_path_steady = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/WorkbenchFiles/Example11Nov_3_files/dp0/CFX/CFX/STEADY.def"
def_path_trans1 = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/WorkbenchFiles/Example11Nov_3_files/dp0/CFX-1/CFX/TRANS1.def"
def_path_trans2 = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/WorkbenchFiles/Example11Nov_3_files/dp0/CFX-2/CFX/TRANS2.def"
wbpj_save_path = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/WorkbenchFiles/Example11Nov_3.wbpj"
def_path_steady = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/Example11Nov_3_files/dp0/CFX/CFX/STEADY.def"
def_path_trans1 = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/Example11Nov_3_files/dp0/CFX-1/CFX/TRANS1.def"
def_path_trans2 = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/Example11Nov_3_files/dp0/CFX-2/CFX/TRANS2.def"
wbpj_save_path = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/Example11Nov_3.wbpj"

def_path_final = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/INP/NUS19_SW60_ST60"


def generate_journal(mesh, def1, def2, def3, save_path):
    with open(WBJN_TEMPLATE, "r", encoding="utf-8") as template:
        content = template.read()

    # Replace placeholders
    content = content.replace("{{MESH_PATH}}", mesh)
    content = content.replace("{{DEF_PATH_STEADY}}", def1)
    content = content.replace("{{DEF_PATH_TRANS1}}", def2)
    content = content.replace("{{DEF_PATH_TRANS2}}", def3)
    content = content.replace("{{WBPJ_FILE_PATH}}", save_path)

    with open(WBJN_GENERATED, "w", encoding="utf-8") as output:
        output.write(content)

def run_workbench():
    cmd = f'"{WB_EXE}" -B -R "{WBJN_GENERATED}"'
    print("Launching:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def move_def_files(def_path_steady, def_path_trans1, def_path_trans2):

    # Destination folder
    def_path_final = r"C:/Users/z5713258/SVMG_MasterThesis/CFD/INP/NUS19_SW60_ST60"
    os.makedirs(def_path_final, exist_ok=True)

    # Move files
    shutil.move(def_path_steady, os.path.join(def_path_final, "STEADY.def"))
    shutil.move(def_path_trans1, os.path.join(def_path_final, "TRANS1.def"))
    shutil.move(def_path_trans2, os.path.join(def_path_final, "TRANS2.def"))

if __name__ == "__main__":
    generate_journal(mesh_path, def_path_steady, def_path_trans1, def_path_trans2, wbpj_save_path)
    #run_workbench()
    #move_def_files(def_path_steady, def_path_trans1, def_path_trans2)




