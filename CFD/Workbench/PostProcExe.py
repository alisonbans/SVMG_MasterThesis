import subprocess
import os

# --- PATHS ---
RUNWB2 = r"C:\Program Files\ANSYS Inc\v242\Framework\bin\Win64\RunWB2.exe"
WBJN_TEMPLATE = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\PostProcTemplate.wbjn"
WBJN_GENERATED = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\PostProcGenerated.wbjn"
RES = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\Results\TRANS2_001.res"
OLD_WBPJ = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\Example11Nov_3.wbpj"
NEW_WBPJ = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench\Example11Nov_3_PostProc.wbpj"

def generate_journal(old_wbpj, new_wbpj, res):
    with open(WBJN_TEMPLATE, "r", encoding="utf-8") as template:
        content = template.read()

    # Replace placeholders
    content = content.replace("{{OLD_WBPJ}}", old_wbpj)
    content = content.replace("{{NEW_WBPJ}}", new_wbpj)
    content = content.replace("{{RES_PATH}}", res)

    with open(WBJN_GENERATED, "w", encoding="utf-8") as output:
        output.write(content)

def run_postproc():
    cmd = [RUNWB2, "-R", WBJN_GENERATED]
    print("Running Workbench journal...")
    print(" ".join(cmd))

    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    generate_journal(OLD_WBPJ, NEW_WBPJ, RES)
    run_postproc()
    #move_def_files(def_path_steady, def_path_trans1, def_path_trans2)



