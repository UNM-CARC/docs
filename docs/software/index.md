# QuickByte Tutorials

Short, practical CARC guides for software, programming environments, and research workflows.

## Programming environments

* [Conda and Anaconda: introduction](conda-intro.md) - What conda is, how environments work, and how to use Anaconda/Miniconda on CARC systems.
* [Managing conda environments](conda-environments.md) - Create, activate, export, and remove conda environments on CARC clusters.
* [Conda channels and pip](conda-channels-pip.md) - Use conda channels (conda-forge, bioconda) and mix pip installs safely inside environments.
* [Conda environments in JupyterHub](conda-jupyterhub.md) - Make your conda environments available as kernels in CARC JupyterHub.
* [Julia in JupyterHub](julia-jupyterhub.md) - Register a Julia kernel and use Julia notebooks in CARC JupyterHub.
* [MPI parallelization from JupyterHub](jupyterhub-mpi.md) - Run MPI-parallel Python (mpi4py/ipyparallel) from CARC JupyterHub sessions.
* [R on CARC systems](r-usage.md) - Load R, run scripts in batch jobs, and use R interactively on CARC clusters.
* [Getting R software](getting-r.md) - Available R versions and how to load them with environment modules.
* [Installing R packages](r-packages.md) - Install R packages into your user library on CARC systems.
* [Parallel R with the future package](parallel-r-future.md) - Parallelize R code across cores and nodes using the future framework.
* [Gurobi optimizer with R](gurobi-r.md) - Use the Gurobi optimization solver from R on CARC clusters.
* [Haskell at CARC](haskell.md) - Install GHC with ghcup and build a Stack project on CARC clusters.
* [Installing Perl libraries](perl-libraries.md) - Install Perl modules into your own home directory with cpan.

## Mathematical and numerical computing

* [Running MATLAB jobs](matlab-jobs.md) - Run MATLAB non-interactively in Slurm batch jobs on CARC clusters.
* [Parallel MATLAB: profile setup and batch submission](parallel-matlab.md) - Configure a cluster profile and submit parallel MATLAB jobs.
* [MATLAB Parallel Server](matlab-parallel-server.md) - Use MATLAB Parallel Server to scale parpool jobs across multiple nodes.
* [MATLAB on GPUs](matlab-gpu.md) - Accelerate MATLAB computations with GPUs on CARC clusters.
* [MATLAB deep learning](matlab-deep-learning.md) - Train deep learning models in MATLAB using CARC GPU nodes.
* [Mathematica on Easley](mathematica.md) - Run Mathematica and WolframScript on Easley with interactive, serial, multicore, multinode, GPU, and license-server examples.

## AI and machine learning

* [Installing deep learning packages](deep-learning-packages.md) - Install GPU-enabled deep learning frameworks (PyTorch, TensorFlow) into conda environments.
* [PyTorch on CARC GPUs](pytorch.md) - Install and run GPU-enabled PyTorch on CARC clusters.
* [PyTorch image classifier walkthrough](pytorch-classifier.md) - End-to-end example: train an image classifier with PyTorch on a CARC GPU node.
* [TensorFlow on CARC GPUs](tensorflow.md) - Install and run GPU-enabled TensorFlow on CARC clusters.
* [Multi-GPU TensorFlow](tensorflow-multi-gpu.md) - Distribute TensorFlow training across multiple GPUs on a CARC node.
* [AlphaFold](alphafold.md) - Run AlphaFold protein structure prediction on CARC systems.

## Data, visualization, and parallel computing

* [Parallel Python with Dask and scikit-learn](dask-scikit-learn.md) - Scale scikit-learn workloads across cluster nodes from JupyterHub using Dask.
* [Apache Spark](spark.md) - Launch Apache Spark clusters inside Slurm allocations for large-scale data analysis.
* [ParaView remote visualization](paraview.md) - Run the ParaView server on CARC compute nodes and connect from your desktop client.
* [CUDA-aware MPI](cuda-aware-mpi.md) - Pass GPU device pointers directly to MPI calls with the CUDA-aware OpenMPI/UCX stack, and fix the mixed-environment segfault.

## Bioinformatics

* [Variant calling with GATK](../tutorials/gatk.md) - A genomics variant-calling workflow using GATK best practices on CARC systems.
* [Metabarcoding analysis](../tutorials/metabarcoding.md) - Process environmental DNA metabarcoding data on CARC clusters.
* [RAD-seq analysis with Stacks](../tutorials/stacks.md) - Analyze restriction-site associated DNA sequencing (RAD-seq) data with Stacks.
* [Genome assembly evaluation with QUAST and BUSCO](../tutorials/genome-evaluation.md) - Evaluate genome assembly quality and completeness with QUAST and BUSCO.
* [Coalescent simulation with msprime](../tutorials/msprime.md) - Simulate genealogical histories and genome sequences with msprime.
* [Demographic inference with PSMC](../tutorials/psmc.md) - Infer population size history from diploid genomes using PSMC.
* [Bayesian phylogenetics with BEAST](../tutorials/beast.md) - Run BEAST Bayesian evolutionary analyses on CARC clusters.

## Domain science

* [VASP materials simulation](../tutorials/vasp.md) - Set up and run VASP density-functional-theory calculations on CARC clusters.
* [ORCA quantum chemistry](../tutorials/orca.md) - Run ORCA quantum chemistry calculations in parallel on CARC clusters.
* [SimCov epidemiological simulation](../tutorials/simcov.md) - Run the SimCov agent-based model of SARS-CoV-2 infection dynamics in lung tissue.
* [Parallel CASA for radio astronomy](../tutorials/mpi-casa.md) - Run mpiCASA for parallel radio astronomy imaging on CARC clusters.

## Containers

* [Singularity / Apptainer containers](singularity.md) - Build, pull, and run software containers on CARC clusters.
