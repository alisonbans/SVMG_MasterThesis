import os
import subprocess

# Path to Blender executable
BLENDER_EXE = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

def run_in_blender():
    """Launch Blender in background and run blender.py inside it."""
    # Full path to the script we want Blender to run
    script_path = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Blender.py"
    
    cmd = [
        BLENDER_EXE,
        "--background",
        "--python", script_path
    ]
    print(f"Running Blender with: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    try:
        import bpy
        # If bpy is available, we are inside Blender already
        print("Running inside Blender!")
        from blender import main
        main()

    except ModuleNotFoundError:
        # Not inside Blender → launch Blender to run blender.py
        print("Not inside Blender — launching Blender now.")
        run_in_blender()

