import math
import random
import numpy as np
import pandas as pd
from scipy.stats import qmc
from pydacefit.dace import DACE
from pydacefit.regr import regr_constant
from pydacefit.corr import corr_gauss

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

import matplotlib.pyplot as plt

# ============================================================
# Import all that is necessary for simulations
# ============================================================
import subprocess
import shutil
import os
import sys
from pathlib import Path
from FEA.CylExpansion.PostProcFunctions import radial_recoil
from CFD.Blender.BlenderExe import run_in_blender
from CFD.Fluent.FluentExe import main_fluent
from CFD.Workbench.WorkbenchExe import main_wb, move_def_files
from CFD.Workbench.PostProcExe import main_wb_pp
from Design.LHS import lhs
# ============================================================
# Define all files for simulations
# ============================================================
matlab_exe = r"C:\Program Files\MATLAB\R2023b\bin\matlab.exe"
matlab_folder = r"C:/Users/z5713258/SVMG_MasterThesis/Design"
matlab_folder_HS1 = os.path.join(matlab_folder, "HS1")
matlab_folder_HS1_results = os.path.join(matlab_folder_HS1, "HS1_Results")
step_folder = os.path.join(matlab_folder, "HS1_Results")
template_cae = r'C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion\Template.cae'
FreeExp_folder = r"C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion"
working_dir_fea = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA'
fea_sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\job-FEA.sh'
FreeExp_results = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\Results'
fe_pp = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\FreeExpansion\\PostProcFunctions.py'
CylExp_folder = r"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion"
cylexp_functions = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\CylExpFunctions.py'
ce_pp = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\PostProcFunctions.py'
working_dir_ce = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\FEA\\CylExpansion\\INP'
cfd_sh_template = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\\Workbench\\job-cfd.sh'
wb_folder = r'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\Workbench'
wb_results = os.path.join(wb_folder, 'Results')
design_space_csv = r"C:\Users\z5713258\SVMG_MasterThesis\DesignSpaceMOO1.csv"


# ============================================================
# Surrogate problem for pymoo (NSGA-II, vectorized evaluation)
# ============================================================
class SurrogateDTLZ2Problem(Problem):
    def __init__(self, model_f1, model_f2, model_as, xl, xu):
        xl = np.asarray(xl, dtype=float)
        xu = np.asarray(xu, dtype=float)

        super().__init__(
            n_var=xl.size,
            n_obj=2,
            n_constr=1,
            xl=xl,
            xu=xu
        )
        self.model_f1 = model_f1
        self.model_f2 = model_f2
        self.model_as = model_as

    def _evaluate(self, X, out, *args, **kwargs):
        # X : (N, D)
        X = np.atleast_2d(X)

        # pydacefit is already vectorized over X
        f1 = np.asarray(self.model_f1.predict(X)).reshape(-1)
        f2 = np.asarray(self.model_f2.predict(X)).reshape(-1)
        as_val = np.asarray(self.model_as.predict(X)).reshape(-1)

        # Objectives
        F = np.column_stack([f1, f2])

        # Constraint: model_as(x) <= 0
        G = as_val[:, None]

        out["F"] = F
        out["G"] = G


# ============================================================
# Single-objective surrogate problem (f1 or f2) with constraints
# ============================================================
class SurrogateSingleObjectiveProblem(Problem):
    def __init__(self, model_f1, model_f2, model_as, xl, xu,
                 minimize_f="f1", f1_max=None, f2_max=None):
        """
        minimize_f : "f1" or "f2"
        Constraints:
          - model_as(x) <= 0
          - if f2_max is not None: f2(x) <= f2_max
          - if f1_max is not None: f1(x) <= f1_max
        """
        xl = np.asarray(xl, dtype=float)
        xu = np.asarray(xu, dtype=float)

        n_constr = 1   # analysis success: model_as(x) <= 0
        if f1_max is not None:
            n_constr += 1
        if f2_max is not None:
            n_constr += 1

        super().__init__(
            n_var=xl.size,
            n_obj=1,
            n_constr=n_constr,
            xl=xl,
            xu=xu
        )

        self.model_f1 = model_f1
        self.model_f2 = model_f2
        self.model_as = model_as
        self.minimize_f = minimize_f
        self.f1_max = f1_max
        self.f2_max = f2_max

    def _evaluate(self, X, out, *args, **kwargs):
        X = np.atleast_2d(X)

        f1 = np.asarray(self.model_f1.predict(X)).reshape(-1)
        f2 = np.asarray(self.model_f2.predict(X)).reshape(-1)
        as_val = np.asarray(self.model_as.predict(X)).reshape(-1)

        # Select objective
        if self.minimize_f == "f1":
            obj = f1
        else:
            obj = f2

        F = obj[:, None]

        # Constraints
        G_list = [as_val]  # model_as(x) <= 0

        if self.f1_max is not None:
            G_list.append(f1 - self.f1_max)  # f1(x) <= f1_max
        if self.f2_max is not None:
            G_list.append(f2 - self.f2_max)  # f2(x) <= f2_max

        G = np.column_stack(G_list)

        out["F"] = F
        out["G"] = G


# ============================================================
# Solve surrogate optimization using NSGA-II
# ============================================================
def solve_with_nsga2_surrogates(model_f1, model_f2, model_as, problem,
                                pop_size=100, n_gen=200, seed=1, verbose=False):
    """
    NSGA-II on surrogate models (vectorized evaluation).
    """
    xl = problem["xl"]
    xu = problem["xu"]

    prob_nsga = SurrogateDTLZ2Problem(model_f1, model_f2, model_as, xl, xu)
    algorithm = NSGA2(pop_size=pop_size)
    termination = get_termination("n_gen", n_gen)

    res = minimize(
        prob_nsga,
        algorithm,
        termination,
        seed=seed,
        verbose=verbose
    )

    X_final = res.X        # (N_pop, D)
    F_final = res.F        # (N_pop, 2)

    # Nondominated set of final population
    nds = NonDominatedSorting()
    front = nds.do(F_final, only_non_dominated_front=True)

    return X_final[front], F_final[front]


# ============================================================
# Plots
# ============================================================
def show_plot_nd(F_ND):
    """
    Plot nondominated objective vectors F_ND (N x 2).
    """
    F_ND = np.asarray(F_ND)
    if F_ND.size == 0:
        print("No nondominated points.")
        return

    plt.figure(figsize=(6, 5))
    plt.scatter(F_ND[:, 0], F_ND[:, 1], c='red', s=60)
    plt.xlabel("f1")
    plt.ylabel("f2")
    plt.title("Nondominated Front")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def show_plot(Archive, no_initial_samples):
    """
    Plot all successful evaluations (AS=0):
      - Initial samples nondominated      : green filled
      - Initial samples dominated         : green unfilled
      - Archive nondominated (non-initial): blue filled
      - Archive dominated (non-initial)   : blue unfilled
    """

    F_all = np.vstack(Archive["F"].to_numpy())
    AS_all = Archive["AS"].to_numpy().astype(int)

    mask_success = (AS_all == 0)
    F_success = F_all[mask_success]

    if F_success.size == 0:
        print("Nothing to plot (no AS = 0 rows).")
        return

    # Compute ND on successful points
    nds = NonDominatedSorting()
    nd_success_local = nds.do(F_success, only_non_dominated_front=True)

    # Map ND indices (local within successful array) to global archive indices
    success_indices = np.where(mask_success)[0]
    nd_global_indices = success_indices[nd_success_local]

    # Global mask for ND and dominated (among successful only)
    mask_nd_global = np.zeros(len(Archive), dtype=bool)
    mask_nd_global[nd_global_indices] = True

    mask_dom_global = mask_success & (~mask_nd_global)

    # Identify INITIAL sample region in Archive (in case archive shorter than expected)
    n_initial = min(no_initial_samples, len(Archive))
    initial_indices = np.arange(n_initial)

    mask_initial_global = np.zeros(len(Archive), dtype=bool)
    mask_initial_global[initial_indices] = True

    # Combine boolean masks
    mask_initial_nd = mask_initial_global & mask_nd_global          # green filled
    mask_initial_dom = mask_initial_global & mask_dom_global        # green unfilled

    mask_noninitial_nd = (~mask_initial_global) & mask_nd_global    # blue filled
    mask_noninitial_dom = (~mask_initial_global) & mask_dom_global  # blue unfilled

    # Prepare plotting
    plt.figure(figsize=(6, 5))

    # ---- Plot initial dominated (green unfilled)
    idx = np.where(mask_initial_dom)[0]
    if len(idx) > 0:
        Fp = F_all[idx]
        plt.scatter(Fp[:, 0], Fp[:, 1], facecolors='none', edgecolors='green',
                    s=70, label="Initial Dominated")

    # ---- Plot initial nondominated (green filled)
    idx = np.where(mask_initial_nd)[0]
    if len(idx) > 0:
        Fp = F_all[idx]
        plt.scatter(Fp[:, 0], Fp[:, 1], color='green', s=70,
                    label="Initial Nondominated")

    # ---- Plot non-initial dominated (blue unfilled)
    idx = np.where(mask_noninitial_dom)[0]
    if len(idx) > 0:
        Fp = F_all[idx]
        plt.scatter(Fp[:, 0], Fp[:, 1], facecolors='none', edgecolors='blue',
                    s=70, label="Dominated (Archive)")

    # ---- Plot non-initial nondominated (blue filled)
    idx = np.where(mask_noninitial_nd)[0]
    if len(idx) > 0:
        Fp = F_all[idx]
        plt.scatter(Fp[:, 0], Fp[:, 1], color='blue', s=70,
                    label="Nondominated (Archive)")

    plt.xlabel("f1")
    plt.ylabel("f2")
    plt.title("Archive Solutions (Successful Evaluations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ============================================================
# Build DACE surrogate models (full θ optimization per model)
# ============================================================
def build_dace_models_from_archive(Archive, optimize_theta=True):
    """
    Build DACE models:
      - model_f1 : Kriging surrogate for objective 1
      - model_f2 : Kriging surrogate for objective 2
      - model_as : Kriging surrogate for AS (0/1)

    optimize_theta : bool
        If True, run θ optimization for *each* model independently.
    """
    # Stack data
    X_all = np.vstack(Archive["X"].to_numpy())           # (N, D)
    F_all = np.vstack(Archive["F"].to_numpy())           # (N, 2)
    AS_all = Archive["AS"].to_numpy().astype(float)      # (N,)

    # Valid rows (AS=0) for objectives
    mask_valid = (Archive["AS"].to_numpy() == 1)
    X_valid = X_all[mask_valid]
    F_valid = F_all[mask_valid]

    if X_valid.shape[0] == 0:
        raise RuntimeError("No valid samples (AS=0). Cannot train F models.")

    D = X_all.shape[1]
    theta0 = np.ones(D)

    if optimize_theta:
        thetaL = 1e-5 * np.ones(D)
        thetaU = 1e2 * np.ones(D)
    else:
        thetaL = None
        thetaU = None

    # --- model_f1 ---
    model_f1 = DACE(regr=regr_constant, corr=corr_gauss,
                    theta=theta0, thetaL=thetaL, thetaU=thetaU)
    model_f1.fit(X_valid, F_valid[:, 0])

    # --- model_f2 ---
    model_f2 = DACE(regr=regr_constant, corr=corr_gauss,
                    theta=theta0, thetaL=thetaL, thetaU=thetaU)
    model_f2.fit(X_valid, F_valid[:, 1])

    # --- model_as (uses all points) ---
    model_as = DACE(regr=regr_constant, corr=corr_gauss,
                    theta=theta0, thetaL=thetaL, thetaU=thetaU)
    model_as.fit(X_all, AS_all)

    return model_f1, model_f2, model_as


# ============================================================
# Synthetic DTLZ2-modified test function (fully vectorized)
# ============================================================
"""def evaluate_dtlz2_modified(X):
    
    Vectorized DTLZ2-modified evaluator.
    X : (N, D)
    Returns F : (N, 2), G : dummy (N, 0)
    
    X = np.atleast_2d(X)
    x0 = X[:, 0]
    rest = X[:, 1:]

    # g term: sum over dimensions 1..D-1
    g = np.sum((rest - 0.5) ** 2, axis=1)

    # Objectives
    f1 = (1.0 + g) * np.cos(x0 * np.pi / 2.0)
    f2 = (1.0 + g) * np.sin(x0 * np.pi / 2.0)

    # Failure condition: f1 > 0.6 -> NaN both
    mask_fail = f1 > 0.6
    f1 = f1.astype(float)
    f2 = f2.astype(float)
    f1[mask_fail] = np.nan
    f2[mask_fail] = np.nan

    F = np.column_stack((f1, f2))
    F = np.round(F, 3)
    G = np.zeros((F.shape[0], 0))
    return F, G
    """

problem_dtlz2_modified = {
    "dtlz2": {
        #"eval_func": evaluate_dtlz2_modified,
        "D": 3,
        "xl": np.array([15, 50, 50]),
        "xu": np.array([25, 80, 70]),
    }
}


# ============================================================
# LHS sampling with seed (vectorized)
# ============================================================
"""def qmc_samples_lhs(n_sol, LB, UB, sd=None):
    LB = np.asarray(LB, dtype=float)
    UB = np.asarray(UB, dtype=float)
    D = LB.size

    if sd is None:
        sampler = qmc.LatinHypercube(d=D)
    else:
        sampler = qmc.LatinHypercube(d=D, seed=sd)

    u = sampler.random(n_sol)      # (n_sol, D)
    X = qmc.scale(u, LB, UB)       # scale to [LB, UB]
    return X
"""

# ============================================================
# Conduct simulations for x_chosen and update the Archive
# ============================================================
def evaluate_simulation_update_archive(Archive,x_chosen):
    design_space = pd.read_csv(design_space_csv)
    design_nb = len(design_space)
    # -------------------------------------------------------------------------------------------
    # 1. DEFINE THE DESIGN TO ASSESS ------------------------------------------------
    # -------------------------------------------------------------------------------------------
    design = [19, 0.46, 18, 0.95, 0.1, 1.63339, 0.39003, 0.75959, 0.81258, 1.31384, 0.04872, 0.00164, 0.07540, 0.61571, 4.16285, 1.79921, 0.06, 0.06]
    NUS = x_chosen[0]
    SW = x_chosen[1]
    ST = x_chosen[2]
    case = f'NUS{NUS}_SW{SW}_ST{ST}'
    design[0] = NUS
    design[16] = SW/1000
    design[17] = ST/1000

    # -------------------------------------------------------------------------------------------
    # 2.1 GENERATE THE GEOMETRY -----------------------------------------------------------------
    # -------------------------------------------------------------------------------------------
    design_str = ','.join(map(str, design))
    matlab_cmd = f"cd('{matlab_folder_HS1}'); status = Main([{design_str}]); disp(status);"
    result = subprocess.run(
        [matlab_exe, "-batch", matlab_cmd],
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if line.isdigit():
            status = int(line)
            break
    design_space.loc[design_nb, 'DesignLabel'] = status
    design_space.to_csv(design_space_csv, index=False)
    
    if status ==1: 
        step = f'stent_{case}.STEP'
        print(step)
        step_1 = os.path.join(matlab_folder_HS1_results, step)
        step_2 = os.path.join(step_folder, step)
        shutil.move(step_1, step_2)
        
        # -------------------------------------------------------------------------------------------
        # 2.2 CREATE THE STENT MESH, SETS & SURFACES ------------------------------------------------
        # -------------------------------------------------------------------------------------------
        abaqus_cmd = r"C:\SIMULIA\Commands\abaqus.bat"
        stent_location = step_2
        stent_script = os.path.join(FreeExp_folder,'Stent.py')
        command1 = f'abaqus cae script="{stent_script}" -- "{template_cae},{stent_location}"'
        proc1 = subprocess.Popen(command1, cwd=os.path.join(FreeExp_folder,'INP'), shell=True)
        proc1.wait()
        
        input("Press enter when the mesh is available ...")
        mesh = F'mesh_{case}.inp'
        mesh_path = os.path.join(FreeExp_folder,'INP',mesh)
        while not os.path.exists(mesh_path): 
            print("Mesh file not found.")
            answer = input("Press enter when the mesh is available \nTo force exit this loop type: out ... ")
            if answer.strip().lower() == 'out':
                status = 0
                break
        
        # -------------------------------------------------------------------------------------------
        # 2.3 PREPARE FREE EXPANSION FILES ----------------------------------------------------------
        # -------------------------------------------------------------------------------------------
        job_name = f"FreeExp_{case}"
        base_name = case
        job_name_full = f"FreeExpFull_{case}"
        script_path=os.path.join(FreeExp_folder,'FreeExpFunctions.py')
        command2 = f'abaqus cae noGUI="{script_path}" -- "{mesh_path},{job_name},{job_name_full},{base_name}"'
        proc2 = subprocess.Popen(command2, shell=True, cwd=os.path.join(FreeExp_folder,'INP'))
        proc2.wait()
        target_sh = os.path.join(os.path.join(FreeExp_folder,'INP'), f"run_{case}.sh")
        with open(fea_sh_template, 'r', newline='\n') as file:
            content = file.read()
        content = content.replace("POT2", job_name_full)
        content = content.replace("walltime=24:00:00", "walltime=01:00:00")
        content = content.replace("ncpus=48", "ncpus=48")
        with open(target_sh, 'w', newline='\n') as file:
            file.write(content)

        # ------------------------------------------------------------------------------------------------
        # 3. CYLINDER EXPANSION --------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------
        input("Press enter when free expansion odb files are available ...")

        # --------------------------------------------------------------------------------------------
        # 3.1 POST PROCESSING OF FREE EXPANSION ------------------------------------------------------
        # --------------------------------------------------------------------------------------------
        case_folder = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\FreeExpansion\Results\{case}"
        os.makedirs(case_folder, exist_ok=True)
        odb_name = f'FreeExpFull_{case}.odb'
        while not os.path.exists(os.path.join(FreeExp_results,odb_name)): 
            print(f"Free expansion ODB for {case} cannot be found")
            answer = input("Press enter when it is available \nTo force exit this loop type: out ... ")
            if answer.strip().lower() == 'out':
                break
        command4 = f'abaqus cae script="{fe_pp}" -- "{case_folder},{odb_name}"'
        proc4 = subprocess.Popen(command4, shell=True, cwd=working_dir_fea)
        proc4.wait()

        df_FE = pd.read_csv(os.path.join(case_folder, 'StentEnergyRatio.csv'),sep=r"\s+")
        df_FE['StentEnergyRatio'] = pd.to_numeric(df_FE['StentEnergyRatio'], errors='coerce')
        df_FE['X'] = pd.to_numeric(df_FE['X'], errors='coerce')
        df_exp_FE = df_FE[(df_FE['X'] > 0.15) & (df_FE['X'] < 0.45)]
        max_ratio_FE = df_exp_FE['StentEnergyRatio'].max()
        design_space.loc[design_nb,'EnergyRatioFE'] = max_ratio_FE
        design_space.to_csv(design_space_csv, index=False)
        # --------------------------------------------------------------------------------------------
        # 3.2 PREPARE CYLINDER EXPANSION FILES ------------------------------------------------------
        # --------------------------------------------------------------------------------------------
        job_name = f"CylExp_{case}"
        job_name_full = f"CylExpFull_{case}"
        exp_stent_location = os.path.join(FreeExp_folder,'Results',case, f'FreeExpFull_{str(case)}.odb')
        command3 = f'abaqus cae noGUI="{cylexp_functions}" -- "{exp_stent_location},{job_name},{job_name_full}"'
        proc3 = subprocess.Popen(command3, shell=True, cwd=working_dir_ce)
        proc3.wait()
        target_sh = os.path.join(os.path.join(CylExp_folder,'INP'), f"run_{case}.sh")
        with open(fea_sh_template, 'r', newline='\n') as file:
            content = file.read()
        content = content.replace("POT2", job_name_full)
        content = content.replace("walltime=24:00:00", "walltime=06:00:00")
        content = content.replace("ncpus=48", "ncpus=24")
        with open(target_sh, 'w', newline='\n') as file:
            file.write(content)

        input("Press enter when cylinder expansion odb files are available ...")

        # --------------------------------------------------------------------------------------------
        # 4.1 POST PROCESSING OF CYLINDER EXPANSION --------------------------------------------------
        # --------------------------------------------------------------------------------------------
        case_folder = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion\Results\{case}"
        os.makedirs(case_folder, exist_ok=True)
        odb_name = f'CylExpFull_{case}.odb'
        while not os.path.exists(os.path.join(CylExp_folder, 'Results', odb_name)):
            input(f"CE ODB file for {case} cannot be found ...")
            answer = input("Press enter when it is available \nTo force exit this loop type: out ... ")
            if answer.strip().lower() == 'out':
                break
        stl_file = rf"C:\Users\z5713258\SVMG_MasterThesis\FEA\CylExpansion\Results\{case}\{case}.stl"
        command4 = f'abaqus cae script="{ce_pp}" -- "{case_folder},{odb_name},{stl_file}"'
        proc4 = subprocess.Popen(command4, shell=True, cwd=working_dir_fea)
        proc4.wait()
        while not os.path.exists(stl_file):
            input(f"STL file for {case} cannot be found ...")
            answer = input("Press enter when it is available \nTo force exit this loop type: out ... ")
            if answer.strip().lower() == 'out':
                break
        rr_abs = radial_recoil(case_folder)
        df = pd.read_csv(os.path.join(case_folder, 'StentEnergyRatio.csv'),sep=r"\s+")
        df['StentEnergyRatio'] = pd.to_numeric(df['StentEnergyRatio'], errors='coerce')
        df['X'] = pd.to_numeric(df['X'], errors='coerce')
        df_exp = df[(df['X'] > 0.5) & (df['X'] < 1)]
        max_ratio_exp = df_exp['StentEnergyRatio'].max()
        design_space.loc[design_nb,'EnergyRatioCE'] = round(max_ratio_exp, 2) 
        design_space.loc[design_nb,'RadialRecoil'] = round(rr_abs,3)
        design_space.to_csv(design_space_csv, index=False)

        # --------------------------------------------------------------------------------------------
        # 4.2 RUN BLENDER, FLUENT & WORKBENCH --------------------------------------------------------
        # --------------------------------------------------------------------------------------------
        input("Press enter when blender model has been created ...")
        blend_file = rf'C:/Users/z5713258/SVMG_MasterThesis/CFD/Blender/{case}.blend'
        while not os.path.exists(blend_file):
            input(f"Blender file for {case} cannot be found ...")
            answer = input("Press enter when it is available \nTo force exit this loop type: out ... ")
            if answer.strip().lower() == 'out':
                break
        run_in_blender(case,  blend_file) 
        input("Press enter once the blender part is checked ....")
        main_fluent(case)
        input("Check mesh and press enter when done ...")
        mesh_path = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Fluent/Mesh/{case}.msh"
        wbpj_save_path =  rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}.wbpj"
        main_wb(mesh_path, wbpj_save_path)
        input(f"Press enter when the definition files are ready for {case}...")
        working_dir =  r"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory"
        move_def_files(working_dir, case)
        shutil.copy(cfd_sh_template, os.path.join(r'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\\Workbench\\INP', case))

        old_wbpj = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}.wbpj"
        new_wbpj = rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}_pp.wbpj"
        res = rf'C:\\Users\\z5713258\\SVMG_MasterThesis\\CFD\Workbench\\Results\\{case}\\TRANS2_001.res'
        while not os.path.exists(res):
            input(f"CFD result file for {case} cannot be found ...")
            answer = input("Press enter when it is available \nTo force exit this loop type: out ... ")
            if answer.strip().lower() == 'out':
                break
        main_wb_pp(old_wbpj, new_wbpj, res)
        shutil.move(new_wbpj, rf'C:/Users/z5713258/SVMG_MasterThesis/CFD\Workbench/Results/{case}')
        shutil.move(rf"C:/Users/z5713258/SVMG_MasterThesis/CFD/Workbench/WorkingDirectory/{case}_pp_files", rf'C:/Users/z5713258/SVMG_MasterThesis/CFD\Workbench/Results/{case}')
        
        while True:
            user_input = input(f"Write down the area of low ESS for {case}: ").strip()
            try:
                lowESS = float(user_input)
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value (e.g., 12.5).")

        design_space.loc[design_nb,'lowESSpercentArea'] = lowESS
        a1 = float(input(f"A1 for {case}: ").strip())
        design_space.loc[design_nb,'A1'] = a1
        a2 = float(input(f"A2 for {case}: ").strip())
        design_space.loc[design_nb,'A2'] = a2
        a3 = float(input(f"A3 for {case}: ").strip())
        design_space.loc[design_nb,'A3'] = a3
        a4 = float(input(f"A4 for {case}: ").strip())
        design_space.loc[design_nb,'A4'] = a4
        design_space.loc[design_nb,'WeightedArea'] = 7*a1 + 5*a2 + 3*a3 + a4
        design_space.to_csv(design_space_csv, index=False)

    new_row = pd.DataFrame({
        "X": [x_chosen[0]],   # store as ndarray
        "F": [[rr_abs,lowESS]],
        "AS": [status]
    })

    # Concatenate with existing Archive
    Archive_new = pd.concat([Archive, new_row], ignore_index=True)

    return Archive_new

"""def evaluate_update_archive(Archive, x_chosen, prob):
    
    #Evaluate the true problem at x_chosen and append result to Archive.
    
    print(f"Please assess the following design: NUS{x_chosen[0]}_SW{x_chosen[1]}_ST{x_chosen[2]}")
    eval_func = prob["eval_func"]

    # Ensure x_chosen is 2D for eval_func
    x_chosen = np.atleast_2d(x_chosen)

    # Evaluate true problem
    #F_new, G_new = eval_func(x_chosen)     # F_new: (1, 2)
    #F_new = F_new[0]                       # (2,)
    input("Enter")
    # AS = 1 if failure (NaNs), 0 otherwise.
    # Since NaNs are set simultaneously in f1 & f2, checking f1 is enough.
    AS_new = int(np.isnan(F_new[0]))

    # Build a one-row DataFrame to append
    new_row = pd.DataFrame({
        "X": [x_chosen[0]],   # store as ndarray
        "F": [F_new],
        "AS": [AS_new]
    })

    # Concatenate with existing Archive
    Archive_new = pd.concat([Archive, new_row], ignore_index=True)

    return Archive_new"""


# ============================================================
# Distance based subset selection
# ============================================================

def distance_based_subset_selection(Archive, X_ND, F_ND):
    """
    Distance-based selection from surrogate ND set.

    Steps:
    (1) From Archive, take only successful (AS == 0), compute their ND set -> True_ND.
    (2) Compute ideal and nadir from True_ND.
    (3) Combine F_ND and True_ND, compute ND of combined set.
        Elite_NDs = those points from F_ND that are on this combined ND front.
        If none from F_ND, then Elite_NDs = F_ND.
    (4) Scale Elite_NDs and True_ND using ideal/nadir from True_ND.
    (5) For each scaled elite ND, compute distance to nearest scaled True_ND.
        Choose the elite ND with the largest nearest-neighbor distance.
    (6) Return its corresponding x from X_ND (unscaled) and its F.
    """

    # ---------- Extract successful archive solutions ----------
    F_all = np.vstack(Archive["F"].to_numpy())          # (N, 2)
    AS_all = Archive["AS"].to_numpy().astype(int)       # (N,)

    mask_success = (AS_all == 0)
    F_success = F_all[mask_success]

    X_all = np.vstack(Archive["X"].to_numpy())
    X_success = X_all[mask_success]

    if F_success.shape[0] == 0:
        # No successful points in Archive – fall back to random ND point
        idx_rand = np.random.randint(0, X_ND.shape[0])
        return X_ND[idx_rand], F_ND[idx_rand]

    # ---------- True_ND from successful archive solutions ----------
    nds = NonDominatedSorting()
    true_nd_idx = nds.do(F_success, only_non_dominated_front=True)
    True_ND = F_success[true_nd_idx]     # (N_true_nd, 2)

    # Ideal and nadir from True_ND
    ideal = True_ND.min(axis=0)
    nadir = True_ND.max(axis=0)

    # ---------- Combine F_ND and True_ND and find elite ND from F_ND ----------
    F_ND = np.asarray(F_ND)
    X_ND = np.asarray(X_ND)
    n_nd = F_ND.shape[0]

    if n_nd == 0:
        # No ND points from surrogate – fallback: random from successful archive
        idx_rand = np.random.randint(0, X_success.shape[0])
        return X_success[idx_rand], F_success[idx_rand]

    F_combined = np.vstack([F_ND, True_ND])
    combined_nd_idx = nds.do(F_combined, only_non_dominated_front=True)

    # Which of the combined ND are from the F_ND block?
    elite_indices_in_FND = [i for i in combined_nd_idx if i < n_nd]

    if len(elite_indices_in_FND) == 0:
        # If no elite_NDs (no F_ND point on combined ND), take all F_ND
        elite_indices_in_FND = list(range(n_nd))

    elite_indices_in_FND = np.asarray(elite_indices_in_FND, dtype=int)
    elite_NDs = F_ND[elite_indices_in_FND]

    # ---------- Scaling function using ideal/nadir from True_ND ----------
    def scale_with_ideal_nadir(F, ideal, nadir):
        F = np.asarray(F, dtype=float)
        ideal = np.asarray(ideal, dtype=float)
        nadir = np.asarray(nadir, dtype=float)

        denom = nadir - ideal
        scaled = np.zeros_like(F, dtype=float)

        nonzero = denom != 0.0
        scaled[:, nonzero] = (F[:, nonzero] - ideal[nonzero]) / denom[nonzero]
        # where denom == 0, dimension stays at 0
        return scaled

    # Scale True_ND and elite_NDs
    scaled_true_NDs = scale_with_ideal_nadir(True_ND, ideal, nadir)
    scaled_elite_NDs = scale_with_ideal_nadir(elite_NDs, ideal, nadir)

    # ---------- Distance from each elite to its nearest True_ND ----------
    diff = scaled_elite_NDs[:, None, :] - scaled_true_NDs[None, :, :]
    dists = np.linalg.norm(diff, axis=2)               # (n_elite, n_true_nd)
    nearest_dists = dists.min(axis=1)                  # (n_elite,)

    # Elite with **largest** nearest-neighbor distance
    best_elite_local_idx = int(np.argmax(nearest_dists))

    # Map back to original F_ND / X_ND index
    chosen_idx_in_FND = int(elite_indices_in_FND[best_elite_local_idx])

    chosen_x = X_ND[chosen_idx_in_FND]
    chosen_F = F_ND[chosen_idx_in_FND]

    return chosen_x, chosen_F


# ============================================================
# Function to compute the statistics
# ============================================================
def compute_statistics(Archive, no_initial_samples):
    """
    Compute statistics:
      (a) Number of Initial Samples
      (b) Number of solutions which resulted in Analysis Failure in the Initial Samples
      (c) Number of Nondominated solutions in the Initial Samples
      (d) Number of solutions which resulted in Analysis Failure in the Archive
      (e) Number of Nondominated solutions in the Archive
      (f) Number of Initial Samples that are member of the final ND front based on Archive
    """

    nds = NonDominatedSorting()

    # Convert to arrays
    F_all = np.vstack(Archive["F"].to_numpy())          # (N, n_obj)
    AS_all = Archive["AS"].to_numpy().astype(int)       # (N,)

    n_archive = len(Archive)

    # (a) Effective number of initial samples in Archive
    n_initial = min(no_initial_samples, n_archive)

    # indices for initial sample region
    init_idx = np.arange(n_initial)

    # (b) Failures in Initial Samples (AS == 1)
    AS_init = AS_all[init_idx]
    n_fail_initial = int(np.sum(AS_init == 1))

    # (c) Nondominated solutions in Initial Samples (among successful initial samples)
    mask_init_success = (AS_init == 0)
    if np.any(mask_init_success):
        F_init_success = F_all[init_idx][mask_init_success]
        nd_init_idx = nds.do(F_init_success, only_non_dominated_front=True)
        n_nd_initial = len(nd_init_idx)
    else:
        n_nd_initial = 0

    # (d) Failures in Archive (AS == 1 over all rows)
    n_fail_archive = int(np.sum(AS_all == 1))

    # (e) Nondominated solutions in Archive (among successful points)
    mask_success_all = (AS_all == 0)
    if np.any(mask_success_all):
        F_success_all = F_all[mask_success_all]
        nd_archive_idx_in_success = nds.do(F_success_all, only_non_dominated_front=True)
        n_nd_archive = len(nd_archive_idx_in_success)

        # Map ND (among successful) back to Archive row indices
        success_indices = np.where(mask_success_all)[0]          # indices in Archive
        nd_archive_indices = success_indices[nd_archive_idx_in_success]
    else:
        n_nd_archive = 0
        nd_archive_indices = np.array([], dtype=int)

    # (f) Number of Initial Samples that are members of the final ND front
    n_initial_in_final_nd = int(np.sum(nd_archive_indices < n_initial))

    stats = {
        "n_initial": n_initial,
        "n_fail_initial": n_fail_initial,
        "n_nd_initial": n_nd_initial,
        "n_fail_archive": n_fail_archive,
        "n_nd_archive": n_nd_archive,
        "n_initial_in_final_nd": n_initial_in_final_nd
    }

    return stats


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    sd = 42
    random.seed(sd)
    np.random.seed(sd)

    # User inputs
    no_initial_solutions = 180
    max_solutions_evaluated = 250   # total desired Archive size

    # User-defined scaling parameter for eps
    eps_factor = 0.05

    # --------------------------------------------------------
    # Generate initial data
    # --------------------------------------------------------
    prob = problem_dtlz2_modified["dtlz2"]
    LB, UB = prob["xl"], prob["xu"]
    #eval_func = prob["eval_func"]
    #X = qmc_samples_lhs(no_initial_solutions, LB, UB, sd=sd)
    #F, G = eval_func(X)
    design_space = r"C:\Users\z5713258\SVMG_MasterThesis\DesignSpace.csv"
    df = pd.read_csv(design_space)
    X_list = df[["NUS", "SW", "ST"]].to_numpy().tolist()
    F_list = df[["RadialRecoil", "lowESSpercentArea"]].to_numpy().tolist()

    Archive = pd.DataFrame({"X": X_list, "F": F_list, "AS": df[["DesignLabel"]].to_numpy})

    # If initial designs already exceed max_solutions_evaluated, truncate
    if len(Archive) > max_solutions_evaluated:
        Archive = Archive.iloc[:max_solutions_evaluated].copy()

    # --------------------------------------------------------
    # Adaptive loop: add points until Archive reaches target size
    # --------------------------------------------------------
    while len(Archive) < max_solutions_evaluated:

        print(f"|Archive Size| = {len(Archive)}")

        # 1) Train surrogates (θ optimized independently for each model)
        model_f1, model_f2, model_as = build_dace_models_from_archive(
            Archive,
            optimize_theta=True
        )

        # 2) Solve surrogate problem with NSGA-II (bi-objective)
        X_ND, F_ND = solve_with_nsga2_surrogates(
            model_f1,
            model_f2,
            model_as,
            prob,
            pop_size=100,
            n_gen=100,
            seed=sd,
            verbose=False
        )

        # ------------------------------------------------------------------
        # 2b) Find extremal ND solutions A (left) and B (right) and
        #     run two additional single-objective optimizations
        #     (a) minimize f1, s.t. AS & f2 <= f2(A) + eps_f2
        #     (b) minimize f2, s.t. AS & f1 <= f1(B) + eps_f1
        #     Add these solutions to the candidate set if feasible.
        # ------------------------------------------------------------------
        if F_ND.shape[0] >= 2:
            # A: extreme in f1 (smallest f1)
            idx_A = np.argmin(F_ND[:, 0])
            # B: extreme in f2 (smallest f2)
            idx_B = np.argmin(F_ND[:, 1])

            f1_A, f2_A = F_ND[idx_A]
            f1_B, f2_B = F_ND[idx_B]

            # eps_f1 = eps_factor * (f1_B - f1_A)
            # eps_f2 = eps_factor * (f2_A - f2_B)
            eps_f1 = eps_factor * (f1_B - f1_A)
            eps_f2 = eps_factor * (f2_A - f2_B)

            # Proceed only if eps are positive (typical monotone front case)
            if eps_f1 > 0.0 and eps_f2 > 0.0:
                f2_max_for_f1 = f2_A + eps_f2
                f1_max_for_f2 = f1_B + eps_f1

                # Common GA + termination for the two SO runs
                so_algorithm_f1 = GA(pop_size=100)
                so_algorithm_f2 = GA(pop_size=100)
                so_termination = get_termination("n_gen", 100)

                # ---- (a) minimize f1, s.t. AS and f2 <= f2(A)+eps_f2 ----
                prob_f1 = SurrogateSingleObjectiveProblem(
                    model_f1=model_f1,
                    model_f2=model_f2,
                    model_as=model_as,
                    xl=LB,
                    xu=UB,
                    minimize_f="f1",
                    f1_max=None,
                    f2_max=f2_max_for_f1
                )

                res_f1 = minimize(
                    prob_f1,
                    so_algorithm_f1,
                    so_termination,
                    seed=sd,
                    verbose=False
                )

                x_star_f1 = np.atleast_1d(res_f1.X)

                # Evaluate both objectives and AS with surrogates for bookkeeping
                f1_star_f1 = np.asarray(model_f1.predict(x_star_f1.reshape(1, -1))).reshape(-1)[0]
                f2_star_f1 = np.asarray(model_f2.predict(x_star_f1.reshape(1, -1))).reshape(-1)[0]
                as_star_f1 = np.asarray(model_as.predict(x_star_f1.reshape(1, -1))).reshape(-1)[0]

                # Add only if (predicted) constraints satisfied
                if (as_star_f1 <= 0.0) and (f2_star_f1 <= f2_max_for_f1 + 1e-8):
                    X_ND = np.vstack([X_ND, x_star_f1])
                    F_ND = np.vstack([F_ND, [f1_star_f1, f2_star_f1]])

                # ---- (b) minimize f2, s.t. AS and f1 <= f1(B)+eps_f1 ----
                prob_f2 = SurrogateSingleObjectiveProblem(
                    model_f1=model_f1,
                    model_f2=model_f2,
                    model_as=model_as,
                    xl=LB,
                    xu=UB,
                    minimize_f="f2",
                    f1_max=f1_max_for_f2,
                    f2_max=None
                )

                res_f2 = minimize(
                    prob_f2,
                    so_algorithm_f2,
                    so_termination,
                    seed=sd + 1,
                    verbose=False
                )

                x_star_f2 = np.atleast_1d(res_f2.X)

                f1_star_f2 = np.asarray(model_f1.predict(x_star_f2.reshape(1, -1))).reshape(-1)[0]
                f2_star_f2 = np.asarray(model_f2.predict(x_star_f2.reshape(1, -1))).reshape(-1)[0]
                as_star_f2 = np.asarray(model_as.predict(x_star_f2.reshape(1, -1))).reshape(-1)[0]

                if (as_star_f2 <= 0.0) and (f1_star_f2 <= f1_max_for_f2 + 1e-8):
                    X_ND = np.vstack([X_ND, x_star_f2])
                    F_ND = np.vstack([F_ND, [f1_star_f2, f2_star_f2]])

        # ------------------------------------------------------------------
        # 3) Select one candidate from the (possibly augmented) candidate set
        # ------------------------------------------------------------------
        x_chosen, F_chosen = distance_based_subset_selection(Archive, X_ND, F_ND)
        

        # 4) Evaluate and update Archive with the true model
        Archive = evaluate_update_archive(Archive, x_chosen, prob)

    # --------------------------------------------------------
    # After loop: final plots / ND set from Archive
    # --------------------------------------------------------
    print(f"\nFinished: |Archive| = {len(Archive)}")

    # Compute statistics
    stats = compute_statistics(Archive, no_initial_solutions)

    print("\n=== Statistics ===")
    print(f"(a) Number of Initial Samples:                                  {stats['n_initial']}")
    print(f"(b) Number of Analysis Failures in Initial Samples:             {stats['n_fail_initial']}")
    print(f"(c) Number of Nondominated solutions in Initial Samples:        {stats['n_nd_initial']}")
    print(f"(d) Number of Analysis Failures in Archive:                     {stats['n_fail_archive']}")
    print(f"(e) Number of Nondominated solutions in Archive:                {stats['n_nd_archive']}")
    print(f"(f) Initial Samples in final ND front based on Archive:         {stats['n_initial_in_final_nd']}")

    # Final plot of all successful evaluations in Archive
    show_plot(Archive, no_initial_solutions)

    # Final ND plot from Archive
    F_all = np.vstack(Archive["F"].to_numpy())
    mask_valid = (Archive["AS"].to_numpy() == 0)
    F_valid = F_all[mask_valid]

    if F_valid.size > 0:
        nds = NonDominatedSorting()
        nd_idx = nds.do(F_valid, only_non_dominated_front=True)
        F_ND_final = F_valid[nd_idx]
        show_plot_nd(F_ND_final)
