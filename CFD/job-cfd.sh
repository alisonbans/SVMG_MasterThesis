#!/bin/bash
 
#PBS -q normal
#PBS -l ncpus=48
#PBS -l walltime=10:00:00
#PBS -l mem=190GB
#PBS -l jobfs=300GB
#PBS -l software=unsw_ansys
#PBS -l wd
#PBS -M a.colombo@unsw.edu.au
#PBS -m abe
 
# Load modules, always specify version number.
module load ansys/2024r1
module load ansys_licence/unsw
 
# Must include `#PBS -l storage=scratch/ab12+gdata/yz98` if the job
# needs access to `/scratch/ab12/` and `/g/data/yz98/`. Details on:
# https://opus.nci.org.au/display/Help/PBS+Directives+Explained
 
export CFX5_OPENMPI_DIR=$OPENMPI_ROOT
cfx5solve -batch -def "b100dd-steady.def" -part $PBS_NCPUS -start-method Gadi_openmpi
cfx5solve -batch -continue-from-file "b100dd-steady_001.res" -def "b100dd-trans1.def" -part $PBS_NCPUS -start-method Gadi_openmpi
cfx5solve -batch -continue-from-file "b100dd-trans1_001.res" -def "b100dd-trans2.def" -part $PBS_NCPUS -start-method Gadi_openmpi