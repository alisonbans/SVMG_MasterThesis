#!/bin/bash
 
#PBS -l ncpus=48
#PBS -l walltime=24:00:00
#PBS -l mem=190GB
#PBS -l jobfs=300GB
#PBS -l software=abaqus
#PBS -M a.bans@student.unsw.edu.au
#PBS -m abe
 
# Load modules, always specify version number.
module load abaqus/2021
module load intel-mpi/2019.9.304
 
# Must include `#PBS -l storage=scratch/ab12+gdata/yz98` if the job
# needs access to `/scratch/ab12/` and `/g/data/yz98/`. Details on:
# https://opus.nci.org.au/display/Help/PBS+Directives+Explained
 
# Copy input file from submission directory to jobfs.
cp $PBS_O_WORKDIR/POT2.inp $PBS_JOBFS
  
# Change in jobfs directory.
cd $PBS_JOBFS
 
# Construct Abaqus environment file.
cat << EOF > abaqus_v6.env
mp_rsh_command="/opt/pbs/default/bin/pbs_tmrsh -n -l %U %H %C"
mp_mpi_implementation = IMPI
mp_mpirun_path = {IMPI: "$INTEL_MPI_ROOT/intel64/bin/mpiexec.hydra"}
memory = "$(bc<<<"$PBS_VMEM*90/100") b"
cpus = $PBS_NCPUS
EOF
  
# Run Abaqus. change jobname 
/opt/nci/bin/pid-ns-wrapper.x -w -- abaqus analysis job=POT2 input=POT2 scratch=$PBS_JOBFS
 
# Make "results" directory in submission directory.
mkdir -p $PBS_O_WORKDIR/results.$PBS_JOBID
 
# Copy everything back from jobfs to results directory.
cp * $PBS_O_WORKDIR/results.$PBS_JOBID
