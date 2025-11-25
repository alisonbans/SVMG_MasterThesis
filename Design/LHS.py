import numpy as np
from scipy.stats import qmc
import matplotlib.pyplot as plt
import pandas as pd
def lhs(N):
    # --------------------- Define design space ---------------------
    NUS_list = np.array([15,16,17,18,19,20,21,22,23,24,25])
    SW_min = 50
    SW_max = 80
    ST_min = 50
    ST_max = 70

    # --------------------- Generate Latin Hypercube Sampling ---------------------
    rng = np.random.default_rng(123)
    lhs = qmc.LatinHypercube(d=3, seed=rng)
    lhs_matrix = lhs.random(N)

    # --------------------- Map lhs values to variables ---------------------
    # x1: assign using sorted lhs first column
    NUS_idx = np.argsort(lhs_matrix[:, 0])
    NUS = NUS_list[NUS_idx % len(NUS_list)]

    # x17: scale second column
    SW = SW_min + lhs_matrix[:, 1] * (SW_max - SW_min)
    SW = np.round(SW, 0)

    # x18: scale third column
    ST = ST_min + lhs_matrix[:, 2] * (ST_max - ST_min)
    ST = np.round(ST, 0)

    # --------------------- Concatenate design space ---------------------
    design_space = np.column_stack((NUS, SW, ST))
    var_names = ['NUS', 'SW', 'ST']

    # --------------- Create CSV file --------------------------
    df = pd.DataFrame(design_space, columns=var_names)
    # Add a 'Label' column filled with NaN
    df['DesignLabel'] = np.nan
    df[['NUS', 'SW', 'ST']] = df[['NUS', 'SW', 'ST']].astype(int)
    # Save to CSV
    csv_path = 'DesignSpace.csv'
    df.to_csv(csv_path, index=False)

    # --------------------- Visualize ---------------------

    fig, axes = plt.subplots(len(var_names), len(var_names), figsize=(8, 8))
    for i in range(len(var_names)):
        for j in range(len(var_names)):
            ax = axes[i, j]
            if i == j:
                ax.hist(design_space[:, i], bins=10, color='lightgray')
            else:
                ax.scatter(design_space[:, j], design_space[:, i], color='blue', s=20)
            if j == 0:
                ax.set_ylabel(var_names[i])
            if i == len(var_names)-1:
                ax.set_xlabel(var_names[j])

    fig.suptitle('Pairwise Scatter Plots of Design Space', fontsize=16)
    plt.tight_layout()
    plt.show()
    plt.close()
