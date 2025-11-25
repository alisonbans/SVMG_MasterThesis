# Stent Geometry Builders for Independent Ring (IR) and Helical Stent (HS) Designs

## Citing Previous Work

[Kapoor et al.](https://github.com/ankushkapoor2003/stent_geometry_builder) 's work on stent geometry builder has used in order to generate the geometries assessed in this multi-objective optimisation framework. The authour's README file has also been used as a basis for this one to get a thourough set of instructions.

Kapoor, A., Ray, T., Jepson, N. and Beier, S. (2025) ‘A surrogate-assisted multiconcept optimization framework for real-world engineering design’, Journal of Mechanical Design, 147(12), pp. 121701. doi:10.1115/1.4068404.

Kapoor, A., Ray, T., Jepson, N. and Beier, S. (2024) ‘Comprehensive geometric parameterization and computationally efficient 3D shape matching optimization of realistic stents’, Journal of Mechanical Design, pp. 1–24. doi:10.1115/1.4066961.

Kapoor, A., Ray, T., Jepson, N. and Beier, S. (2025) 3D geometry builder for independent ring and helical stent designs. Version 0.0.2. Zenodo. doi:10.5281/zenodo.15117426.

## Overview

This repository contains the geometry builders for HS1 stent design. These tools allow for the automated generation and customization of stent geometries based on specific input parameters.

## Setup Instructions

### Prerequisites

The geometry builder requires the following software to be installed. 

- **MATLAB2023b** 
- **Anaconda**
-  **Solidworks 2024**
- **Abaqus 2025**
- **Blender 4.5**
- **Ansys 2024 R2 - Fluent and Workbench**
- **VSCode** or any other python IDE


The builder is tested only on the software versions listed above.

### Cloning the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/stent-geometry-builder.git
cd stent-geometry-builder
```
### Setting up the solidworks integration Python environment and corresponding modules. 

1. Open the anaconda prompt and navigate to the cloned directory location using cd command
    ```conda
    cd '\\ stent geometry builder location \\'
    ```

2. Create a new conda environent with Python 3.9.18 
    ```conda
    conda create --name Sldwrks_Integration python=3.9.18
    ```

3. Activate the created conda environemnt
    ```conda
    conda activate Sldwrks_Integration
    ```
4. In the anaconda prompt, navigate to the cloned directory location using cd command
    ```conda
    cd '\\ stent geometry builder location \\'
    ```

5. Install the sld_interface package and its dependencies in the Sldwrks_integration environment
    ```conda
    python -m pip install ".\Solidworks_library\sld_interface"
    ```

6. Retrieve the location of the python executable of the conda environement using the following command
    ```conda
    where python
    ```
    The command may show multiple python locations, copy the path within your generated conda environment

7. Open Matlab and change the matlab python environment to the newly generated one by running the following in command window
    ```matlab
    pyenv('Version', '\\ Path to the python executable retrieved from step 5 \\')
    ```

NB: 

Please note that the python library assumes that solidworks is installed in the default location i.e. "C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe". if the solidworks executable is at a different location, change the location in the solidworks library file located at "\stent geometry builder location\Solidworks_Library\sld_interface\sld_interface\sld.py", line 11. 

Similarly, the default solidworks template used for loading new document is assumed at the location "C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\Part.prtdot". Kindly update line 478 in sld.py if the location is different. This template needs to be set up within solidworks as well (Solidworks > Settings > Default Templates).

In Solidworks, go to Settings > Export > STEP and make sure 'Split periodic faces' is not selected.  

## Usage instructions

1. Make sure all file directories are specific to your usage. 

2. Go to main.py, adapt your design intervals, run the file and follow the instructions in the terminal. You will be prompted to ....:   
    a. Create the sets and surfaces for the stent design.   
    b. Launch the free expansion simulations    
    c. Launch the in-artery simulations   
    d. Export the STL file of the final configuration    
    e. Save the definitions files in your workbench environment  
    f. Insert the area of low endothelial shear stress   



