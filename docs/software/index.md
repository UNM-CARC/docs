# Software

Language environments, machine learning frameworks, containers, and applications on CARC systems.

## Python & Jupyter

* [Conda and Anaconda: introduction](conda-intro.md) - What conda is, how environments work, and how to use Anaconda/Miniconda on CARC systems.
* [Managing conda environments](conda-environments.md) - Create, activate, export, and remove conda environments on CARC clusters.
* [Conda channels and pip](conda-channels-pip.md) - Use conda channels (conda-forge, bioconda) and mix pip installs safely inside environments.
* [Conda environments in JupyterHub](conda-jupyterhub.md) - Make your conda environments available as kernels in CARC JupyterHub.
* [Installing deep learning packages](deep-learning-packages.md) - Install GPU-enabled deep learning frameworks (PyTorch, TensorFlow) into conda environments.
* [Parallel Python with Dask and scikit-learn](dask-scikit-learn.md) - Scale scikit-learn workloads across cluster nodes from JupyterHub using Dask.
* [MPI parallelization from JupyterHub](jupyterhub-mpi.md) - Run MPI-parallel Python (mpi4py/ipyparallel) from CARC JupyterHub sessions.
* [Julia in JupyterHub](julia-jupyterhub.md) - Register a Julia kernel and use Julia notebooks in CARC JupyterHub.

## R

* [R on CARC systems](r-usage.md) - Load R, run scripts in batch jobs, and use R interactively on CARC clusters.
* [Getting R software](getting-r.md) - Available R versions and how to load them with environment modules.
* [Installing R packages](r-packages.md) - Install R packages into your user library on CARC systems.
* [Parallel R with the future package](parallel-r-future.md) - Parallelize R code across cores and nodes using the future framework.
* [Gurobi optimizer with R](gurobi-r.md) - Use the Gurobi optimization solver from R on CARC clusters.
* [R batch jobs with PBS (retired)](r-pbs-jobs.md) - Historical instructions for submitting R jobs with PBS/Torque, which CARC has replaced with Slurm. *(legacy)*

## MATLAB

* [Running MATLAB jobs](matlab-jobs.md) - Run MATLAB non-interactively in Slurm batch jobs on CARC clusters.
* [Parallel MATLAB: profile setup and batch submission](parallel-matlab.md) - Configure a cluster profile and submit parallel MATLAB jobs.
* [MATLAB Parallel Server](matlab-parallel-server.md) - Use MATLAB Parallel Server to scale parpool jobs across multiple nodes.
* [MATLAB on GPUs](matlab-gpu.md) - Accelerate MATLAB computations with GPUs on CARC clusters.
* [MATLAB deep learning](matlab-deep-learning.md) - Train deep learning models in MATLAB using CARC GPU nodes.

## AI & machine learning

* [PyTorch on CARC GPUs](pytorch.md) - Install and run GPU-enabled PyTorch on CARC clusters.
* [PyTorch image classifier walkthrough](pytorch-classifier.md) - End-to-end example: train an image classifier with PyTorch on a CARC GPU node.
* [TensorFlow on CARC GPUs](tensorflow.md) - Install and run GPU-enabled TensorFlow on CARC clusters.
* [Multi-GPU TensorFlow](tensorflow-multi-gpu.md) - Distribute TensorFlow training across multiple GPUs on a CARC node.
* [AlphaFold](alphafold.md) - Run AlphaFold protein structure prediction on CARC systems.

## Containers & tools

* [Singularity / Apptainer containers](singularity.md) - Build, pull, and run software containers on CARC clusters.
* [Apache Spark](spark.md) - Launch Apache Spark clusters inside Slurm allocations for large-scale data analysis.
* [ParaView remote visualization](paraview.md) - Run the ParaView server on CARC compute nodes and connect from your desktop client.
* [CUDA-aware MPI](cuda-aware-mpi.md) - Pass GPU device pointers directly to MPI calls with the CUDA-aware OpenMPI/UCX stack, and fix the mixed-environment segfault.
* [Installing Perl libraries](perl-libraries.md) - Install Perl modules into your own home directory with cpan.
* [Haskell at CARC](haskell.md) - Install GHC with ghcup and build a Stack project on CARC clusters.
