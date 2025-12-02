import os
import subprocess
# Path to Blender executable
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

def run_in_blender(case, blend_path):
    """Launch Blender in background and run BlenderFunctions.py with parameters."""
    script_path = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Blender\BlenderFunctions.py"
    
    # Pass arguments after '--' in key=value format
    cmd = [
        BLENDER_EXE,
        blend_path,
        #"--background",
        "--python", script_path,
        "--",
        f"case={case}"
    ]
    
    print(f"Running Blender with: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    # Example usage
    print('No main for this file')