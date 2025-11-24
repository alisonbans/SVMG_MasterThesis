import subprocess
import os

FLUENT_EXE = r"C:\Program Files\ANSYS Inc\v242\Fluent\ntbin\win64\fluent.exe"

JN_TEMPLATE = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Fluent\FluentTemplate.jou"
JN_GENERATED = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Fluent\FluentGenerated.jou"

JN2_TEMPLATE = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Fluent\ResizeTemplate.jou"
JN2_GENERATED = r"C:\Users\z5713258\SVMG_MasterThesis\CFD\Fluent\ResizeGenerated.jou"

def generate_journals(case_folder):
    with open(JN_TEMPLATE, "r", encoding="utf-8") as template:
        content = template.read()

    # Replace placeholders
    content = content.replace("{{CASE_FOLDER}}", case_folder)

    with open(JN_GENERATED, "w", encoding="utf-8") as output:
        output.write(content)

    with open(JN2_TEMPLATE, "r", encoding="utf-8") as template:
        content = template.read()

    # Replace placeholders
    content = content.replace("{{CASE_FOLDER}}", case_folder)

    with open(JN2_GENERATED, "w", encoding="utf-8") as output:
        output.write(content)

def run_fluent_meshing():
    """
    Launch Fluent in 3D meshing mode and run a journal file.
    """

    cmd = [
        FLUENT_EXE,
        "3d",            # 3d meshing mode
        "-meshing",
        #"-g",            # batch mode (no GUI splash)
        "-t", "4",       # threads (adjust as needed)
        "-i", JN_GENERATED
    ]

    # Launch Fluent
    subprocess.run(cmd, check=True)

# Example usage

def main_fluent(case_folder):
    generate_journals(case_folder)        # generate the journals first
    run_fluent_meshing()    # run Fluent with the generated journal
    