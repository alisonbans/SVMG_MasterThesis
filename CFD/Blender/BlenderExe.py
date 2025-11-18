import os
import subprocess
# Path to Blender executable
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

def run_in_blender1():

    """Launch Blender in background and run blender.py inside it."""

    # Full path to the script we want Blender to run
    script_path = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\BlenderFunctions.py"
    
    cmd = [
        BLENDER_EXE,
        "--background",
        "--python", script_path
    ]
    print(f"Running Blender with: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

#if __name__ == "__main__":
#    run_in_blender()

import subprocess

#BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"

def run_in_blender(case, stl_path):
    """Launch Blender in background and run BlenderFunctions.py with parameters."""
    script_path = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Blender\BlenderFunctions.py"
    
    # Pass arguments after '--' in key=value format
    cmd = [
        BLENDER_EXE,
        "--background",
        "--python", script_path,
        "--",
        f"case={case}",
        f"stl={stl_path}"
    ]
    
    print(f"Running Blender with: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    # Example usage
    run_in_blender("Case001", r"C:\Users\z5713258\AbaqusWD\MOD\alison-dt1e06-MOD-Amp-2.stl")