# WorkbenchExe.py
import subprocess

# Paths
WB_EXE = r"C:\Program Files\ANSYS Inc\v242\Framework\bin\Win64\RunWB2.exe"
WB_SCRIPT = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Workbench.wbjn"

def run_workbench():
    # Properly quote both executable and script
    cmd = f'"{WB_EXE}" -B -R "{WB_SCRIPT}"'
    print("Launching:", cmd)
    subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    run_workbench()

