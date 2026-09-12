#!/usr/bin/env python3
"""Migrate UNM-CARC QuickBytes + webinfo content into the OKF/Zensical docs tree.

Reproducible pipeline:
  1. Clones (or reuses) the source repos.
  2. For every mapped file: normalizes the title, prepends OKF v0.2 frontmatter
     (type, description, tags, generated, sources w/ git last_modified, status),
     rewrites image/asset/inter-doc links, injects legacy-cluster warnings, and
     appends a human-readable provenance line.
  3. Converts Jupyter notebooks to Markdown (requires nbconvert).
  4. Copies images and downloadable assets into docs/assets/.
  5. Generates OKF §8 section index.md directory listings.

Usage:
  QB_DIR=/tmp/QuickBytes WEBINFO_DIR=/tmp/webinfo python3 scripts/migrate_quickbytes.py

Idempotent: re-running overwrites previously migrated files.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMG_DIR = DOCS / "assets" / "images" / "quickbytes"
FILES_DIR = DOCS / "assets" / "files"

QB_DIR = Path(os.environ.get("QB_DIR", ROOT / ".cache" / "QuickBytes"))
WEBINFO_DIR = Path(os.environ.get("WEBINFO_DIR", ROOT / ".cache" / "webinfo"))

QB_URL = "https://github.com/UNM-CARC/QuickBytes"
WEBINFO_URL = "https://github.com/UNM-CARC/webinfo"

GENERATED_AT = "2026-08-29T00:00:00Z"
GENERATED_BY = "claude/fable-5"
HW_STALE = "2027-08-31T00:00:00Z"  # staleness horizon for hardware-specific pages


@dataclass
class Page:
    src: str                      # path relative to source repo ("" => hand-written)
    dest: str                     # path relative to docs/
    title: str
    description: str
    type: str = "Guide"           # OKF concept type
    tags: list = field(default_factory=list)
    status: str = ""              # "", "draft", "deprecated"
    stale_after: str = ""
    repo: str = "quickbytes"      # quickbytes | webinfo | hand
    notebook: bool = False
    note: str = ""                # extra admonition inserted after the H1
    frozen: bool = False          # migrated once, now curated in-repo: never overwrite
    code_lang: str = "bash"       # default language for fenced tab-indented code
    videos: list = field(default_factory=list)  # [(youtube_id, title), ...] appended as embeds


# --------------------------------------------------------------------------
# Content mapping
# --------------------------------------------------------------------------

PAGES: list[Page] = [
    # ---- Getting started (hand-written pages declared for index generation)
    Page("", "getting-started/overview.md", "Getting started at CARC",
         "Create a CARC account, join a project in ColdFront, and find support.",
         "Guide", ["Accounts", "New users"], repo="hand"),
    Page("", "getting-started/good-neighbor-policy.md", "Good Neighbor Use Policy",
         "Acceptable-use rules that all CARC users agree to: account sharing, data restrictions, job monitoring, and security.",
         "Policy", ["Policy", "New users"], repo="hand"),
    Page("logging_in.md", "getting-started/logging-in.md", "Logging in to CARC systems",
         "Connect to CARC clusters with SSH from Linux, macOS, or Windows.",
         "Guide", ["SSH", "New users"], videos=[("Puhaf6tCNO0", "Logging into CARC Systems")]),
    Page("password_reset.md", "getting-started/password-reset.md", "Password reset and one-time passwords",
         "Reset your CARC password and manage one-time-password (OTP) settings.",
         "Guide", ["Accounts", "Security"]),
    Page("ssh_keygen_config.md", "getting-started/ssh-keys.md", "SSH keys and client configuration",
         "Generate SSH key pairs and configure your SSH client for convenient, secure logins.",
         "Guide", ["SSH", "Security"]),
    Page("X11_forwarding.md", "getting-started/x11-forwarding.md", "X11 forwarding",
         "Display graphical applications from CARC machines on your local screen with X11 forwarding.",
         "Guide", ["SSH", "Visualization"], videos=[("-5ic9JWHuqI", "X11 Forwarding")]),
    Page("transfer_data.md", "getting-started/transferring-data.md", "Transferring data",
         "Move data to and from CARC systems with scp, rsync, sftp, and Globus.",
         "Guide", ["Data", "Storage"], videos=[("2UphEzHOHGM", "Transferring data")]),
    Page("linux_intro.md", "getting-started/linux-intro.md", "Introduction to Linux",
         "A first tour of the Linux command line for new HPC users.",
         "Tutorial", ["Linux", "New users"]),
    Page("learning_linux.md", "getting-started/learning-linux.md", "Learning Linux resources",
         "Curated external resources for learning the Linux command line.",
         "Reference", ["Linux", "New users"]),

    # ---- Systems & storage
    Page("", "systems/overview.md", "Systems overview",
         "Current CARC clusters (Easley and Hopper), storage tiers, and web portals such as JupyterHub, Open OnDemand, and XDMoD.",
         "Reference", ["Systems", "Hardware"], stale_after=HW_STALE, repo="hand"),
    Page("resource_limits.md", "systems/resource-limits.md", "Storage and compute usage policies",
         "Storage quotas, per-cluster partition and walltime limits, Slurm fairshare policy, and the job time-limit extension policy.",
         "Policy", ["Policy", "Storage", "Slurm"], stale_after=HW_STALE, repo="webinfo",
         frozen=True),  # 2026-09-01: curated against CARC-knowledge-store observed facts
    Page("storage_and_backup.md", "systems/storage.md", "Storage and backups",
         "CARC storage spaces (home, project, scratch), the real filesystem paths, retention windows, and what is backed up.",
         "Guide", ["Storage", "Data"], videos=[("WwsbLyl7d1A", "Storage Systems")],
         frozen=True),  # 2026-09-01: curated against CARC-knowledge-store observed facts
    Page("storage_permissions_BeeGFS.md", "systems/storage-permissions.md", "Storage permissions on BeeGFS",
         "Manage file and directory permissions, including ACLs, on CARC BeeGFS scratch storage.",
         "Guide", ["Storage", "Security"]),
    Page("systems_information.md", "systems/cluster-specifications.md", "Cluster specifications (legacy reference)",
         "Historical hardware tables for CARC clusters, including retired systems such as Wheeler, Taos, Gibbs, and Xena.",
         "Reference", ["Systems", "Hardware", "Legacy"], status="deprecated", repo="webinfo",
         note="This page is kept for history and links. Wheeler, Taos, Gibbs, and Xena have been retired — see the [Systems overview](overview.md) for current clusters."),

    # ---- Running jobs
    Page("Intro_to_slurm.md", "running-jobs/slurm-intro.md", "Introduction to Slurm",
         "Slurm basics on CARC clusters: partitions, interactive jobs, and your first batch script.",
         "Guide", ["Slurm", "Jobs", "New users"], videos=[("cIRyG8C3CVk", "Slurm Job Scheduler")]),
    Page("submitting_jobs.md", "running-jobs/submitting-jobs.md", "Submitting jobs",
         "Submit, monitor, and cancel batch and interactive jobs with Slurm.",
         "Guide", ["Slurm", "Jobs"]),
    Page("slurm-sbatch.md", "running-jobs/slurm-reference.md", "Slurm command reference",
         "Common Slurm commands and sbatch directives with examples.",
         "Reference", ["Slurm", "Jobs"]),
    Page("submitting_sbatch_jobs.md", "running-jobs/example-slurm-scripts.md", "Example Slurm scripts",
         "Ready-to-adapt sbatch scripts for serial, parallel, and GPU jobs.",
         "Reference", ["Slurm", "Jobs", "Examples"]),
    Page("slurm_accounting.md", "running-jobs/slurm-accounting.md", "Slurm accounting and fairshare",
         "How Slurm accounts, job accounting, and the fairshare system work at CARC.",
         "Guide", ["Slurm", "Allocations"]),
    Page("pbs2slurm.md", "running-jobs/pbs-to-slurm.md", "PBS to Slurm migration",
         "Translate PBS/Torque commands and scripts to their Slurm equivalents.",
         "Reference", ["Slurm", "PBS", "Legacy"]),
    Page("module_management.md", "running-jobs/modules.md", "Environment modules",
         "Find, load, and manage software with environment modules on CARC clusters.",
         "Guide", ["Modules", "Software"], videos=[("tz-w3vc7cGQ", "Environment Modules")]),
    Page("GNU Parallel.md", "running-jobs/gnu-parallel.md", "GNU Parallel",
         "Run many small tasks efficiently inside a single Slurm job with GNU Parallel.",
         "Guide", ["Slurm", "Parallel"], videos=[("Rl06WD60afA", "Parallelization 3: GNU Parallel")]),

    # ---- Interactive computing (hand-written)
    Page("", "interactive/open-ondemand.md", "Open OnDemand",
         "Use CARC clusters from your browser: files, shells, job management, and interactive apps.",
         "Guide", ["Interactive", "Open OnDemand", "New users"], repo="hand"),
    Page("", "interactive/jupyterhub.md", "JupyterHub",
         "Run Jupyter notebooks on Hopper and Easley compute nodes through CARC JupyterHub.",
         "Guide", ["Interactive", "Jupyter", "New users"], repo="hand"),

    # ---- Software: Python & Jupyter
    Page("anaconda_general_intro.md", "software/conda-intro.md", "Conda and Anaconda: introduction",
         "What conda is, how environments work, and how to use Anaconda/Miniconda on CARC systems.",
         "Guide", ["Python", "Conda"]),
    Page("anaconda_intro.md", "software/conda-environments.md", "Managing conda environments",
         "Create, activate, export, and remove conda environments on CARC clusters.",
         "Guide", ["Python", "Conda"], videos=[("gMJzDSeGk50", "Conda environments")]),
    Page("anaconda_pip_channels.md", "software/conda-channels-pip.md", "Conda channels and pip",
         "Use conda channels (conda-forge, bioconda) and mix pip installs safely inside environments.",
         "Guide", ["Python", "Conda"]),
    Page("Conda_JupyterHub.md", "software/conda-jupyterhub.md", "Conda environments in JupyterHub",
         "Make your conda environments available as kernels in CARC JupyterHub.",
         "Guide", ["Python", "Conda", "Jupyter"]),
    Page("julia_with_jupyterhub.md", "software/julia-jupyterhub.md", "Julia in JupyterHub",
         "Register a Julia kernel and use Julia notebooks in CARC JupyterHub.",
         "Guide", ["Julia", "Jupyter"]),
    Page("Install deep learning packages.md", "software/deep-learning-packages.md", "Installing deep learning packages",
         "Install GPU-enabled deep learning frameworks (PyTorch, TensorFlow) into conda environments.",
         "Guide", ["Python", "GPU", "Machine learning"], frozen=True),
    Page("parallel_jupyterhub_with_dask_and_scikit-learn.md", "software/dask-scikit-learn.md", "Parallel Python with Dask and scikit-learn",
         "Scale scikit-learn workloads across cluster nodes from JupyterHub using Dask.",
         "Tutorial", ["Python", "Jupyter", "Parallel", "Dask"]),
    Page("", "software/cuda-aware-mpi.md", "CUDA-aware MPI",
         "Pass GPU device pointers directly to MPI calls with the CUDA-aware OpenMPI/UCX stack, and fix the mixed-environment segfault.",
         "Guide", ["MPI", "GPU", "CUDA"], repo="hand"),
    Page("parallelization_with Jupyterhub_using_mpi.md", "software/jupyterhub-mpi.md", "MPI parallelization from JupyterHub",
         "Run MPI-parallel Python (mpi4py/ipyparallel) from CARC JupyterHub sessions.",
         "Tutorial", ["Python", "Jupyter", "MPI", "Parallel"]),

    # ---- Software: R
    Page("R_usage.md", "software/r-usage.md", "R on CARC systems",
         "Load R, run scripts in batch jobs, and use R interactively on CARC clusters.",
         "Guide", ["R"]),
    Page("R_at_CARC/getting_R_software.md", "software/getting-r.md", "Getting R software",
         "Available R versions and how to load them with environment modules.",
         "Guide", ["R", "Modules"]),
    Page("R_at_CARC/installing_packages.md", "software/r-packages.md", "Installing R packages",
         "Install R packages into your user library on CARC systems.",
         "Guide", ["R"]),
    Page("Parallel_R_with_Future.ipynb", "software/parallel-r-future.md", "Parallel R with the future package",
         "Parallelize R code across cores and nodes using the future framework.",
         "Tutorial", ["R", "Parallel"], notebook=True,
         videos=[("G5xGfF151Co", "Parallel R with Future")]),
    Page("Gurobi optimizer with R.md", "software/gurobi-r.md", "Gurobi optimizer with R",
         "Use the Gurobi optimization solver from R on CARC clusters.",
         "Guide", ["R", "Optimization"]),
    Page("R_at_CARC/PBS_job_submission.md", "software/r-pbs-jobs.md", "R batch jobs with PBS (retired)",
         "Historical instructions for submitting R jobs with PBS/Torque, which CARC has replaced with Slurm.",
         "Guide", ["R", "PBS", "Legacy"], status="deprecated",
         note="CARC schedulers now run Slurm. See [R on CARC systems](r-usage.md) and [Example Slurm scripts](../running-jobs/example-slurm-scripts.md) instead."),

    # ---- Software: MATLAB
    Page("running_matlab_jobs.md", "software/matlab-jobs.md", "Running MATLAB jobs",
         "Run MATLAB non-interactively in Slurm batch jobs on CARC clusters.",
         "Guide", ["MATLAB", "Jobs"]),
    Page("Parallel MATLAB profile setup and batch submission.md", "software/parallel-matlab.md", "Parallel MATLAB: profile setup and batch submission",
         "Configure a cluster profile and submit parallel MATLAB jobs.",
         "Guide", ["MATLAB", "Parallel"]),
    Page("ParallelMatlabServer.md", "software/matlab-parallel-server.md", "MATLAB Parallel Server",
         "Use MATLAB Parallel Server to scale parpool jobs across multiple nodes.",
         "Guide", ["MATLAB", "Parallel"]),
    Page("Using GPUs on Xena with MATLAB.md", "software/matlab-gpu.md", "MATLAB on GPUs",
         "Accelerate MATLAB computations with GPUs on CARC clusters.",
         "Guide", ["MATLAB", "GPU"], status="draft"),
    Page("MATLAB Deep Learning on Xena.md", "software/matlab-deep-learning.md", "MATLAB deep learning",
         "Train deep learning models in MATLAB using CARC GPU nodes.",
         "Tutorial", ["MATLAB", "GPU", "Machine learning"], status="draft"),

    # ---- Software: AI & ML
    Page("PyTorch_1.9_Xena.md", "software/pytorch.md", "PyTorch on CARC GPUs",
         "Install and run GPU-enabled PyTorch on CARC clusters.",
         "Guide", ["Python", "GPU", "Machine learning", "PyTorch"], status="draft"),
    Page("PyTorch_Classifier_Xena .ipynb", "software/pytorch-classifier.md", "PyTorch image classifier walkthrough",
         "End-to-end example: train an image classifier with PyTorch on a CARC GPU node.",
         "Tutorial", ["Python", "GPU", "Machine learning", "PyTorch"], notebook=True, status="draft"),
    Page("Tensorflow_documentation.md", "software/tensorflow.md", "TensorFlow on CARC GPUs",
         "Install and run GPU-enabled TensorFlow on CARC clusters.",
         "Guide", ["Python", "GPU", "Machine learning", "TensorFlow"], code_lang="python"),
    Page("multiGPU_tensorflow_tutorial.md", "software/tensorflow-multi-gpu.md", "Multi-GPU TensorFlow",
         "Distribute TensorFlow training across multiple GPUs on a CARC node.",
         "Tutorial", ["Python", "GPU", "Machine learning", "TensorFlow"]),
    Page("alphafold.md", "software/alphafold.md", "AlphaFold",
         "Run AlphaFold protein structure prediction on CARC systems.",
         "Guide", ["Bioinformatics", "GPU", "Machine learning"]),

    # ---- Software: containers & tools
    Page("singularity-markdown-version.md", "software/singularity.md", "Singularity / Apptainer containers",
         "Build, pull, and run software containers on CARC clusters.",
         "Guide", ["Containers", "Singularity"]),
    Page("spark_tutorial.md", "software/spark.md", "Apache Spark",
         "Launch Apache Spark clusters inside Slurm allocations for large-scale data analysis.",
         "Tutorial", ["Spark", "Big data", "Parallel"]),
    Page("paraview.md", "software/paraview.md", "ParaView remote visualization",
         "Run the ParaView server on CARC compute nodes and connect from your desktop client.",
         "Guide", ["Visualization", "ParaView"]),
    Page("install_perl_libraries.md", "software/perl-libraries.md", "Installing Perl libraries",
         "Install Perl modules into your own home directory with cpan.",
         "Guide", ["Perl"]),
    Page("haskell.md", "software/haskell.md", "Haskell at CARC",
         "Install GHC with ghcup and build a Stack project on CARC clusters.",
         "Guide", ["Haskell"]),

    # ---- Tutorials (domain applications)
    Page("GATK_QuickByte.md", "tutorials/gatk.md", "Variant calling with GATK",
         "A genomics variant-calling workflow using GATK best practices on CARC systems.",
         "Tutorial", ["Bioinformatics", "Genomics"]),
    Page("Metabarcoding.md", "tutorials/metabarcoding.md", "Metabarcoding analysis",
         "Process environmental DNA metabarcoding data on CARC clusters.",
         "Tutorial", ["Bioinformatics", "Ecology"]),
    Page("Stacks_quickbyte.md", "tutorials/stacks.md", "RAD-seq analysis with Stacks",
         "Analyze restriction-site associated DNA sequencing (RAD-seq) data with Stacks.",
         "Tutorial", ["Bioinformatics", "Genomics"]),
    Page("genome_evaluation.md", "tutorials/genome-evaluation.md", "Genome assembly evaluation with QUAST and BUSCO",
         "Evaluate genome assembly quality and completeness with QUAST and BUSCO.",
         "Tutorial", ["Bioinformatics", "Genomics"]),
    Page("msprime_quickbyte.md", "tutorials/msprime.md", "Coalescent simulation with msprime",
         "Simulate genealogical histories and genome sequences with msprime.",
         "Tutorial", ["Bioinformatics", "Population genetics"]),
    Page("psmc_quickbyte.md", "tutorials/psmc.md", "Demographic inference with PSMC",
         "Infer population size history from diploid genomes using PSMC.",
         "Tutorial", ["Bioinformatics", "Population genetics"]),
    Page("Beast_at_CARC.md", "tutorials/beast.md", "Bayesian phylogenetics with BEAST",
         "Run BEAST Bayesian evolutionary analyses on CARC clusters.",
         "Tutorial", ["Bioinformatics", "Phylogenetics"]),
    Page("SimCov.md", "tutorials/simcov.md", "SimCov epidemiological simulation",
         "Run the SimCov agent-based model of SARS-CoV-2 infection dynamics in lung tissue.",
         "Tutorial", ["Simulation", "Epidemiology"], videos=[("7x3voqNX0QY", "CS491/591: Computational Immunology — SimCov Compilation and Submission")]),
    Page("test_vasp_quickbyte.md", "tutorials/vasp.md", "VASP materials simulation",
         "Set up and run VASP density-functional-theory calculations on CARC clusters.",
         "Tutorial", ["Materials science", "Chemistry"]),
    Page("orca_easley_hopper.md", "tutorials/orca.md", "ORCA quantum chemistry",
         "Run ORCA quantum chemistry calculations in parallel on CARC clusters.",
         "Tutorial", ["Chemistry"]),
    Page("mpiCASA.md", "tutorials/mpi-casa.md", "Parallel CASA for radio astronomy",
         "Run mpiCASA for parallel radio astronomy imaging on CARC clusters.",
         "Tutorial", ["Astronomy", "MPI"]),

    # ---- FAQ (hand-written)
    Page("", "faq/general.md", "General FAQ",
         "Quick answers about accounts, projects, cost, storage, software, and GPUs at CARC.",
         "Reference", ["FAQ", "New users"], repo="hand"),
    Page("", "faq/troubleshooting.md", "Troubleshooting",
         "Diagnose the most common problems: login failures, quota errors, pending or failing jobs, and module conflicts.",
         "Guide", ["FAQ", "Support"], repo="hand"),

    # ---- Training
    Page("", "training/videos.md", "Video tutorials",
         "Embedded CARC recordings: the QuickBytes tutorial series, CARC Annual Meeting talks, and research presentations from the UNMCARC YouTube channel.",
         "Reference", ["Training", "Videos"], repo="hand"),
    Page("workshop_slides.md", "training/workshops.md", "Workshops and slides",
         "Slide decks from CARC workshops and university courses, organized by series, plus how to hear about upcoming sessions.",
         "Reference", ["Training", "Workshops"], frozen=True),

    # ---- Support
    Page("", "support/help.md", "Getting help",
         "Open a help ticket, email CARC support, or drop into office and consultation hours.",
         "Guide", ["Support"], repo="hand"),
    Page("", "support/acknowledging-carc.md", "Acknowledging CARC",
         "The acknowledgement statement to include in publications that used CARC resources.",
         "Policy", ["Support", "Publications"], repo="hand"),

    # ---- About
    Page("", "about/mission.md", "Mission and vision",
         "CARC's vision and mission: leading and growing the computational research community at UNM.",
         "Reference", ["About"], repo="hand"),
    Page("", "about/facilities.md", "Facilities description",
         "Boilerplate facilities description for grant proposals: clusters, storage, networking, and the data center.",
         "Reference", ["About", "Grants"], stale_after=HW_STALE, repo="hand"),
    Page("", "about/partners.md", "Partner cyberinfrastructure",
         "National and regional platforms CARC users can reach: ACCESS-CI, Jetstream2, CyVerse, and MESA.",
         "Reference", ["About", "Partners"], repo="hand"),
    Page("", "about/contributing.md", "Contributing to these docs",
         "How to edit pages, the OKF frontmatter contract, verifying migrated content, and building the site locally.",
         "Guide", ["About", "Contributing"], repo="hand"),
    Page("", "about/ai-agents.md", "For AI agents",
         "How agents and harnesses should consume this documentation: llms.txt, per-page Markdown with OKF frontmatter, and trust signals.",
         "Reference", ["About", "AI agents", "OKF"], repo="hand"),
]

SECTIONS = {
    "getting-started": ("Getting started",
        "New to CARC? Start here: accounts, policies, logging in, and moving data."),
    "systems": ("Systems & storage",
        "CARC clusters, storage spaces, quotas, and usage policies."),
    "running-jobs": ("Running jobs",
        "Schedule and manage work on CARC clusters with Slurm."),
    "interactive": ("Interactive computing",
        "Point-and-click access to CARC clusters: Open OnDemand and JupyterHub."),
    "software": ("Software",
        "Language environments, machine learning frameworks, containers, and applications on CARC systems."),
    "tutorials": ("Tutorials",
        "Domain-science QuickBytes: complete worked examples from genomics to materials science."),
    "faq": ("FAQ & troubleshooting",
        "Quick answers to common questions and fixes for the problems users hit most."),
    "training": ("Training",
        "Workshops, courses, and video tutorials from the CARC team."),
    "support": ("Support",
        "Help tickets, office hours, and acknowledging CARC in your publications."),
    "about": ("About CARC",
        "Mission, facilities, partner cyberinfrastructure, and this documentation project."),
}

# Software section subgroups for the index page (mirrors zensical.toml nav)
SOFTWARE_GROUPS = [
    ("Python & Jupyter", ["conda-intro.md", "conda-environments.md", "conda-channels-pip.md",
                          "conda-jupyterhub.md", "deep-learning-packages.md", "dask-scikit-learn.md",
                          "jupyterhub-mpi.md", "julia-jupyterhub.md"]),
    ("R", ["r-usage.md", "getting-r.md", "r-packages.md", "parallel-r-future.md", "gurobi-r.md",
           "r-pbs-jobs.md"]),
    ("MATLAB", ["matlab-jobs.md", "parallel-matlab.md", "matlab-parallel-server.md", "matlab-gpu.md",
                "matlab-deep-learning.md"]),
    ("AI & machine learning", ["pytorch.md", "pytorch-classifier.md", "tensorflow.md",
                               "tensorflow-multi-gpu.md", "alphafold.md"]),
    ("Containers & tools", ["singularity.md", "spark.md", "paraview.md", "cuda-aware-mpi.md",
                            "perl-libraries.md", "haskell.md"]),
]

# Extra downloadable assets: (repo-relative source, docs/assets/files-relative dest)
FILE_ASSETS = [
    ("spark/slurm-spark-submit", "spark/slurm-spark-submit"),
    ("vasp_assets/INCAR", "vasp/INCAR"),
    ("vasp_assets/KPOINTS", "vasp/KPOINTS"),
    ("vasp_assets/POSCAR", "vasp/POSCAR"),
    ("vasp_assets/README_POTCAR.md", "vasp/README_POTCAR.txt"),
    ("R_at_CARC/parallel.r", "r/parallel.r"),
    ("R_at_CARC/parallel_r.pbs", "r/parallel_r.pbs"),
    ("R_at_CARC/sequential.R", "r/sequential.R"),
    ("R_at_CARC/sequential_r.pbs", "r/sequential_r.pbs"),
    ("matlabImportWheelerProfile.pbs", "matlab/matlabImportWheelerProfile.pbs"),
    ("beginner_intro_slides_2022.pdf", "workshops/beginner_intro_slides_2022.pdf"),
]

# Surgical, reproducible content fixes applied to migrated pages
# (dest path -> list of literal (old, new) replacements).
PATCHES = {
    "software/parallel-r-future.md": [
        ("seet the", "see the"),
        ("the plan() object", "the `plan()` object"),
        ("the future({}) object", "the `future({})` object"),
        ("the value() object", "the `value()` object"),
        ("The value() object", "The `value()` object"),
        ("the future() object", "the `future()` object"),
        ("with the unlist object", "with the `unlist` object"),
        ("https://wheeler.alliance.unm.edu:8000/",
         "the CARC JupyterHub on [Hopper](https://hopper.alliance.unm.edu){target=_blank} "
         "or [Easley](https://easley.alliance.unm.edu/jupyter){target=_blank}."),
    ],
    "software/matlab-parallel-server.md": [
        ("\n\nparallel.cluster.generic.runProfileWizard()\n\n",
         "\n\n```matlab\nparallel.cluster.generic.runProfileWizard()\n```\n\n"),
    ],
    # Blockquotes -> admonitions so errors/warnings carry proper symbols.
    "systems/storage-permissions.md": [
        ("The key point is:\n\n"
         "> **Location does not determine quota usage. Group ownership does.**",
         "The key point is:\n\n"
         "!!! warning \"Key point\"\n\n"
         "    **Location does not determine quota usage. Group ownership does.**"),
        ("That can cause confusing quota errors such as:\n\n"
         "> \"I copied the data to the project directory, so why am I out of personal quota?\"\n\n"
         "The answer is usually:\n\n"
         "> The files are in the right place, but they are owned by the wrong group.",
         "That can cause confusing quota errors:\n\n"
         "!!! danger \"Why am I out of personal quota?\"\n\n"
         "    *\"I copied the data to the project directory, so why am I out of\n"
         "    personal quota?\"*\n\n"
         "    The answer is usually that the files are in the right place, but they\n"
         "    are owned by the wrong group."),
        ("This usually tells Linux:\n\n"
         "> New files and directories created here should inherit the group ownership of the parent directory.\n\n"
         "That helps project directories behave as shared spaces.\n\n"
         "However, this is not foolproof.\n\n"
         "Some copy tools, synchronization programs, editors, and applications may:\n\n"
         "- preserve the source group\n"
         "- explicitly set their own group\n"
         "- create temporary files elsewhere and then move them into place\n"
         "- use transfer behavior that bypasses the expected destination ownership\n\n"
         "Because of this, users should always verify group ownership after large transfers.",
         "This usually tells Linux:\n\n"
         "!!! note \"What setgid means\"\n\n"
         "    New files and directories created here should inherit the group\n"
         "    ownership of the parent directory.\n\n"
         "That helps project directories behave as shared spaces.\n\n"
         "!!! warning \"setgid is not foolproof\"\n\n"
         "    Some copy tools, synchronization programs, editors, and applications\n"
         "    may:\n\n"
         "    - preserve the source group\n"
         "    - explicitly set their own group\n"
         "    - create temporary files elsewhere and then move them into place\n"
         "    - use transfer behavior that bypasses the expected destination ownership\n\n"
         "    Because of this, always verify group ownership after large transfers."),
    ],
    # 2026-09-01 knowledge-store reconciliation: partition list corrected against
    # observed cluster state (CARC-knowledge-store facts/raw/easley/2026-07-25 —
    # debug is 1 hour, Easley has no "condo" partition) and the ticket-derived
    # GPU-partition access path documented.
    "running-jobs/slurm-intro.md": [
        ("Key partitions you may have access to:\n\n"
         "- **general** — The default community partition. Maximum wall time of 2 days. Use this if you are not a member of a specific condo group.\n"
         "- **debug** — Short jobs only (4-hour limit). Useful for testing scripts before submitting long runs.\n"
         "- **condo** — Purchased nodes available to specific research groups. If you are a member of a condo group, you likely already know your partition name. Check with your PI if you are unsure.\n"
         "- **scavenger** - Whenever a purchased/reserved node is not in use, this partition grabs them and allows them to be used by the public, but be warned you will be kicked off if the owner begins a job on it.",
         "Key partitions on Easley (limits as observed 2026-07-25 — `sinfo` or\n"
         "`scontrol show partition <name>` always shows the current values):\n\n"
         "- **general** — The default community partition. Maximum wall time of 2 days.\n"
         "- **bigmem** — Two large-memory nodes (about 2 TB of RAM each) for jobs that need far more memory than a general node provides. Maximum wall time of 2 days.\n"
         "- **h100** — GPU nodes with 2× NVIDIA H100 per node. Maximum wall time of 2 days.\n"
         "- **l40s** — GPU nodes with 4× NVIDIA L40S per node. Maximum wall time of 2 days.\n"
         "- **interactive** — Interactive sessions of up to 4 hours, scheduled at elevated priority.\n"
         "- **debug** — Short test jobs only (1-hour limit — note the `1:00:00` in the `sinfo` output above). Useful for checking scripts before submitting long runs.\n"
         "- **scavenger** — Runs on reserved nodes whenever they sit idle. Open to everyone, but preemptible: your job is killed if the owner submits work.\n"
         "- **liulab** — A lab-restricted partition (7-day limit) belonging to a specific research group.\n\n"
         "!!! warning \"GPU partitions are group-gated\"\n\n"
         "    The `h100` and `l40s` partitions are restricted by group membership.\n"
         "    Access is provisioned through a ColdFront allocation for the specific\n"
         "    partition, requested by your project's PI — support cannot simply add\n"
         "    you to the group on request. If a submission is rejected with\n"
         "    `uid not in group permitted to use this partition`, see the\n"
         "    [troubleshooting FAQ](../faq/troubleshooting.md#my-job-wont-start)."),
        ("- Time limits use the format `D-HH:MM:SS` (e.g., `1-12:00:00` for 1 day and 12 hours) or `MM:SS` / `HH:MM:SS` for shorter jobs.",
         "- Time limits use the format `D-HH:MM:SS` (e.g., `1-12:00:00` for 1 day and 12 hours) or `MM:SS` / `HH:MM:SS` for shorter jobs.\n"
         "- If you omit `--time`, you do **not** get the partition maximum: `general` applies a default of 8 hours (`DefaultTime=08:00:00`). Check `scontrol show partition <name>` for the partition you use.\n"
         "- If you omit `--mem`/`--mem-per-cpu`, memory defaults to an amount proportional to the CPUs you request (`DefMemPerCPU` — observed ≈3.7 GB per CPU on Easley's `general` partition, ≈2.9 GB on Hopper's). A small `--cpus-per-task` therefore caps your memory well below what the node physically has — the usual cause of jobs killed `OUT_OF_MEMORY` on nodes with plenty of free RAM. See [troubleshooting](../faq/troubleshooting.md#my-job-failed-or-was-killed)."),
    ],
    # 2026-09-01: plain intel/18–20 modules do exist on Easley
    # (observed in module avail under /opt/local/modules).
    "running-jobs/modules.md": [
        ("Note that there's no plain `intel` module on Easley — `module load intel` fails with \"The following module(s) are unknown.\" Easley's Intel software all lives under the `intel-oneapi-*` family instead (`intel-oneapi-compilers`, `intel-oneapi-mkl`, `intel-oneapi-mpi`, etc.).",
         "The current Intel toolchain on Easley lives under the `intel-oneapi-*` family (`intel-oneapi-compilers`, `intel-oneapi-mkl`, `intel-oneapi-mpi`, etc.). Older `intel/18.x`–`intel/20.x` compiler modules also remain available for rebuilding legacy software — `module avail intel` shows both families."),
    ],
    # 2026-09-01: ticket-derived login-failure guidance (knowledge store,
    # fix-login-failure-password-reset).
    "getting-started/password-reset.md": [
        ("You can also log in with the above link to find other information about your CARC account",
         "!!! tip \"If the reset doesn't seem to take\"\n\n"
         "    - \"Forgot password\" needs your **exact CARC username** — confirm it first,\n"
         "      and [open a ticket](../support/help.md) if you are unsure of your login name.\n"
         "    - A freshly reset password can fail on the first attempt: Easley and Hopper\n"
         "      share one authentication backend and the new password can take a little\n"
         "      while to propagate. Try again shortly — and if needed, simply run the\n"
         "      reset a second time.\n"
         "    - If you can log into one cluster but not the other after a reset, SSH to\n"
         "      the affected cluster *from* the working cluster's login node (e.g.\n"
         "      `ssh easley` from a Hopper session) as a workaround, and\n"
         "      [open a ticket](../support/help.md) if direct login keeps failing.\n\n"
         "You can also log in with the above link to find other information about your CARC account"),
    ],
    # 2026-09-01: ticket-derived transfer-hang guidance (knowledge store,
    # fix-large-rsync-transfer-hangs).
    "getting-started/transferring-data.md": [
        ("The `-vhatP` flags instruct rsync to print the progress of the transfer verbosely and in a human-readable format.",
         "The `-vhatP` flags instruct rsync to print the progress of the transfer verbosely and in a human-readable format.\n\n"
         "!!! tip \"Large transfer keeps hanging or timing out?\"\n\n"
         "    A single huge `rsync` that repeatedly stalls usually points to network\n"
         "    stability on the client side (wireless, VPN, off-campus path) rather than\n"
         "    a problem at CARC:\n\n"
         "    - **Chunk the transfer** — loop over subdirectories with separate `rsync`\n"
         "      calls instead of one massive invocation. Since `rsync` skips files that\n"
         "      have already arrived, re-running after a failure resumes where it left off.\n"
         "    - Note whether it dies at the same file each run or at random, your client\n"
         "      OS, wired vs. wireless, and on- vs. off-campus. Those details make a\n"
         "      [support ticket](../support/help.md) much faster to resolve — support can\n"
         "      also try reproducing the transfer to rule out a CARC-side issue.\n"
         "    - Increase verbosity (`-v`/`-vv`) only on a **small subset** of the data\n"
         "      while diagnosing, not on the full transfer."),
    ],
}

# --- 2026-08-30 legacy purge -------------------------------------------------
# Retired systems (Wheeler, Taos, Gibbs, Xena) and PBS/Torque-as-current
# references are scrubbed from active pages. Anything historically valuable
# lives on the legacy reference page (systems/cluster-specifications.md).
# Literal fixes (applied with str.replace, so they hit every occurrence):

LEGACY_FIXES = {
    "systems/storage.md": [
        ("subdirectories of /users. User project directories are subdirectories "
         "of /project. Scratch directories are subdirectories of the directory /scratch.",
         "subdirectories of `/users`. User project directories are subdirectories "
         "of `/project`. Scratch directories are subdirectories of `/scratch`."),
        ("how to write a PBS script that first moves data",
         "how to write a Slurm batch script that first moves data"),
        ("For storage limits [see the resource policy page]"
         "(https://github.com/UNM-CARC/QuickBytes/blob/master/Resource_usage.md){target=_blank}.",
         "For storage limits see the [resource limits page](resource-limits.md)."),
        ("- /users/username - Upon", "- `/users/username` - Upon"),
        ("in /user/username, replacing", "in `/users/username`, replacing"),
        ("goes by “~” and “$HOME”", "goes by `~` and `$HOME`"),
        ("* Machine-wide scratch disk  - ~/machine-scratch -> /machine/scratch/username - The",
         "* Machine-wide scratch disk - `~/machine-scratch` → `/machine/scratch/username` - The"),
        ("- /tmp - [On the machines that support these]"
         "(https://carc.unm.edu/systems/Systems1.html){target=_blank}, compute nodes",
         "- `/tmp` - On the machines that support these, compute nodes"),
        ("(see sample PBS script below)", "(see the sample script below)"),
        ("creating a directory in /tmp and then placing",
         "creating a directory in `/tmp` and then placing"),
        ("- /dev/shm - This is actually direct access",
         "- `/dev/shm` - This is actually direct access"),
        ("The directory at /dev/shm appears", "The directory at `/dev/shm` appears"),
        ("just like /tmp,", "just like `/tmp`,"),
        ("Like /tmp, /dev/shm is also cleared at the end of a PBS job",
         "Like `/tmp`, `/dev/shm` is also cleared at the end of a job"),
    ],
    "systems/resource-limits.md": [
        ("Scratch storage is limited to 1 TB (2 TB on Xena).",
         "Scratch storage is limited to 1 TB."),
        ("limited to 100G (/carc/scratch).", "limited to 100G (`/carc/scratch`)."),
        ("The 'quotas' command shows", "The `quotas` command shows"),
        ("# Compute Usage Policy", "## Compute usage policy"),
        ("For more on slurm accounts see this quickbyte: "
         "[https://github.com/UNM-CARC/QuickBytes/blob/master/slurm_accounting.md]"
         "(../running-jobs/slurm-accounting.md)",
         "For more on Slurm accounts see "
         "[Slurm accounting](../running-jobs/slurm-accounting.md)."),
    ],
    "systems/cluster-specifications.md": [
        ("| **GPU** | N/A | N/A | 2 x Nvidia Tesla<br>K40M per node | 1 x Nvidia Tesla<br>K40M per node |",
         "| **GPU** | N/A | N/A | 2 x Nvidia Tesla<br>K40M per node | 1 x Nvidia Tesla<br>K40M per node |\n"
         "\n"
         "### Historical queue limits\n"
         "\n"
         "Queue limits in force when these systems were retired:\n"
         "\n"
         "#### Xena\n"
         "\n"
         "| Queue                | GPU                             | Bigmem                                | Debug    |\n"
         "|---:                  |:---:                            |:---:                                  |:---:     |\n"
         "| Number of Processors | 192                             | 128                                   | 8        |\n"
         "| Number of Nodes      | 12 (singleGPU) <br> 4 (dualGPU) | 1                                     | 2        |\n"
         "| Processors per Node  | 16                              | 32                                    | 4        |\n"
         "| Walltime(H:M:S)      | 48:00:00                        | 48:00:00                              | 04:00:00 |\n"
         "| Memory Limit         | 60 Gb (singleGPU and dualGPU)   | 1 Tb (bigmem-1TB)<br>3 Tb (bigmem-3TB)| 60 Gb    |\n"
         "\n"
         "#### Wheeler\n"
         "\n"
         "|                Queue: |   Default  |    Debug   |\n"
         "|----------------------:|:----------:|:----------:|\n"
         "| Number of Processors  |     400    |     32     |\n"
         "|      Number of Nodes  |     50     |      4     |\n"
         "|   Processors per Node |      8     |      8     |\n"
         "|       Walltime(H:M:S) |  48:00:00  |  04:00:00  |\n"
         "|         Memory Limit  |    44 Gb   |    44 Gb   |"),
    ],
    "getting-started/ssh-keys.md": [
        ("    Host wheeler\n```bash\nhostname wheeler.alliance.unm.edu\nuser CHANGEME\nport 22\n```\n"
         "    Host hopper\n```bash\nhostname hopper.alliance.unm.edu\nuser CHANGEME\nport 22\n```\n"
         "    Host xena\n```bash\nhostname xena.alliance.unm.edu\nuser CHANGEME\nForwardX11 yes\nport 22\n```",
         "```\nHost hopper\n    hostname hopper.alliance.unm.edu\n    user CHANGEME\n    port 22\n\n"
         "Host easley\n    hostname easley.alliance.unm.edu\n    user CHANGEME\n    ForwardX11 yes\n    port 22\n```"),
        ("you can just type `ssh xena`.", "you can just type `ssh easley`."),
    ],
    "software/conda-environments.md": [
        ("environment on Wheeler to run", "environment on Hopper to run"),
        ("log in to Wheeler using `ssh`", "log in to Hopper using `ssh`"),
        # 2026-09-01 knowledge-store reconciliation: the anaconda3 module is
        # retired (only miniconda3 exists — observed module avail, both
        # clusters); base-env limitation and interactive-session guidance from
        # the ticket-derived python-conda-environment-slurm runbook.
        ("load the anaconda software module with the command:\n\n`module load anaconda3`",
         "load the conda software module with the command:\n\n`module load miniconda3`\n\n"
         "!!! warning \"anaconda3 is retired, and the module only gives you `base`\"\n\n"
         "    Old scripts that call `module load anaconda3` no longer work — that\n"
         "    module has been retired; use `miniconda3` instead. Loading the module\n"
         "    provides only conda's *base* environment, which does **not** include\n"
         "    numpy, scipy, or other analysis packages: a Python `ModuleNotFoundError`\n"
         "    right after loading the module means you need to create (and activate)\n"
         "    your own environment, as shown below."),
        ("We use `conda` to create new environments and install/upgrade packages within environments.",
         "Build and test environments from an interactive compute session rather than a\n"
         "login node — for example `srun --ntasks=1 --cpus-per-task=4 --time=01:00:00 --pty bash`\n"
         "first ([interactive jobs](../running-jobs/submitting-jobs.md)); package installs are\n"
         "exactly the kind of heavier work login nodes are not meant for.\n\n"
         "We use `conda` to create new environments and install/upgrade packages within environments."),
        ("Remember to include the lines below in your PBS script when working with Anaconda environments:\n\n"
         "```bash\n# load anaconda software module\nmodule load anaconda3",
         "Remember to include the lines below in your Slurm batch script when working with conda environments:\n\n"
         "```bash\n# load conda software module\nmodule load miniconda3"),
    ],
    "software/pytorch.md": [
        ("### SSH in to Xena\nTo connect to the Xena machine,",
         "### SSH in to the cluster\nTo connect to a CARC cluster (Hopper in this example),"),
        ("ssh $USERNAME@xena.alliance.unm.edu", "ssh $USERNAME@hopper.alliance.unm.edu"),
        ("Navigate to Systems > JupyterHub Cluster Links > Xena",
         "Navigate to Systems > JupyterHub Cluster Links > Hopper"),
        ("I will choose a Xena server with 2 GPU's.",
         "I will choose a server option with GPUs."),
        ("Example:\nXena 1 hour, 2 GPUs, 16 cores, 60 GB RAM",
         "Example:\n1 hour, 2 GPUs, 16 cores, 60 GB RAM"),
    ],
    "software/getting-r.md": [
        ("yourusername@wheeler-sn$", "yourusername@hopper$"),
        ("These are all of the currently available R modules installed on Wheeler.",
         "These are the R modules available on the cluster."),
        ("direct your browser to https://wheeler.alliance.unm.edu:8000 and log in",
         "direct your browser to https://hopper.alliance.unm.edu and log in"),
        ("R session running on Wheeler through JupyterHub",
         "R session running on the cluster through JupyterHub"),
        # 2026-09-01 knowledge-store reconciliation: the r-3.x centos7 Spack
        # tree is gone; current clusters serve r/4.x Lmod modules (observed
        # module avail, Hopper 2026-07-25), and anaconda3 is retired.
        ("module avail r-", "module avail r/"),
        ("----------------------- /opt/spack/share/spack/modules/linux-centos7-x86_64 ------------------------\n"
         "   ...\n"
         "   r-3.4.1-gcc-4.8.5-python2-gzeg24m\n"
         "   r-3.4.1-gcc-4.8.5-python2-zpkgqap\n"
         "   r-3.4.1-intel-17.0.4-mkl-python2-67zsm3b\n"
         "   r-3.4.1-intel-17.0.4-mkl-python2-gygkoab\n"
         "   r-3.4.2-intel-18.0.2-python2-xsxuxwx\n"
         "   r-3.4.3-gcc-4.8.5-python2-gk66fni\n"
         "   r-3.4.3-gcc-4.8.5-python2-qv6gwz6\n"
         "   r-3.4.3-gcc-6.1.0-python2-lyqiytq\n"
         "   r-3.4.3-gcc-7.3.0-python2-zhxbajj\n"
         "   r-3.4.3-intel-18.0.1-python2-3l4dkgz\n"
         "   r-3.4.3-intel-18.0.1-python2-lr24ix6\n"
         "   r-3.4.3-intel-18.0.2-python2-q3covk7\n"
         "   r-3.5.0-gcc-4.8.5-python2-khqxja7\n"
         "   r-3.5.0-gcc-7.3.0-python2-rvq3qk5\n"
         "   r-3.5.0-intel-18.0.2-python2-mkl-r6lx6yy\n"
         "   r-3.5.3-gcc-7.3.0-python2-ziiolp5\n"
         "   r-3.6.0-gcc-4.8.5-python2-i4uimtp\n"
         "   r-3.6.0-gcc-7.3.0-python2-7akol5t",
         "-------------- /opt/spack/share/spack/lmod/linux-rocky8-x86_64/Core --------------\n"
         "   ...\n"
         "   r/4.2.0-vq7z\n"
         "   r/4.2.2-oemu\n"
         "   r/4.3.0-g353\n"
         "   r/4.4.0-fyqw\n"
         "   r/4.4.0-ytj2 (D)"),
        ("Will load R-3.6.0 that has been compiled with GCC-7.3.0.",
         "```\nyourusername@hopper$ module load r/4.4.0\n```\n\n"
         "This will load R 4.4.0 — plain `module load r` loads the cluster's default R version."),
        ("in your PBS script, but we will get to that later.",
         "in your Slurm batch script, but we will get to that later."),
        ("module load anaconda3", "module load miniconda3"),
    ],
    "software/jupyterhub-mpi.md": [
        ("wheeler-sn.alli", "hopper.alli"),
    ],
    "software/matlab-deep-learning.md": [
        ("These tools can make use of GPUs, which are available for use on the Xena cluster.",
         "These tools can make use of GPUs, which are available on the CARC clusters "
         "— see the [current systems](../systems/overview.md)."),
        ("It is highly reccommended to use the dualGPU partition and request two GPUs.\n"
         "The commands below will show you how to use both the single and dual GPU partitions.",
         "It is highly recommended to request two GPUs when available.\n"
         "The commands below show both single- and dual-GPU requests."),
        ("Once logged into Xena with X11 fowarding", "Once logged in with X11 forwarding"),
        ("--partition singleGPU --x11", "--x11"),
        ("--partition dualGPU --x11", "--x11"),
        ("xena:~$ ssh xena-01", "hopper:~$ ssh $NODE   # the compute node assigned to you"),
        ("xena:~$", "hopper:~$"),
        ("xena-01:~$", "node:~$"),
    ],
    "software/matlab-gpu.md": [
        ("1. [Using a single GPU on Xena](#1)", "1. [Using a single GPU](#1)"),
        ("2. [Using Multiple GPUs on a single Xena node](#2)",
         "2. [Using multiple GPUs on a single node](#2)"),
        ("## Using a single GPU on Xena <a name=\"1\"></a>",
         "## Using a single GPU <a name=\"1\"></a>"),
        ("## Using Multiple GPUs on a single Xena node <a name=\"2\"></a>",
         "## Using multiple GPUs on a single node <a name=\"2\"></a>"),
        ("utilize a GPU on xena.", "utilize a GPU."),
        ("interactive session on a xena compute node.",
         "interactive session on a GPU compute node."),
        ("That will print something that looks like this on Xena:",
         "That will print something like this:"),
        ("Xena contains some nodes with two GPUs.",
         "Some CARC nodes contain multiple GPUs."),
        ("PBS script version:\n```bash\nxena:~$ qsub gpu_matlab.pbs\n```\n\n"
         "Slurm script version:\n```bash\nxena:~$ sbatch gpu_matlab.sh\n```",
         "```bash\nhopper:~$ sbatch gpu_matlab.sh\n```"),
        ("When using the `--partition dualGPU` flag on xena, you must also set "
         "`--cpus-per-task 2` and `-G 2`",
         "When requesting two GPUs, you must also set `--cpus-per-task 2` and `-G 2`"),
        ("For this partition, we ask for two CPUs and two GPUs.",
         "We ask for two CPUs and two GPUs."),
        ("#SBATCH --partition dualGPU\n", ""),
        ("from the xena head node", "from the head node"),
        ("xena:~$", "hopper:~$"),
    ],
    "software/alphafold.md": [
        ("Xena is the machine at CARC that has GPU resources, so you will need to "
         "use xena if you hope to run using the gpus.",
         "GPU nodes are available on the current CARC clusters — see the "
         "[systems overview](../systems/overview.md)."),
        ("Choose one of the scripts below, in this case we will be using Hopper.",
         "We will use the Hopper script below."),
    ],
    "software/parallel-matlab.md": [
        ("In order to submit a PBS script that takes advantage of MATLAB Parallel "
         "Server you first need to set up a new cluster profile specific to Wheeler.",
         "In order to submit a batch script that takes advantage of MATLAB Parallel "
         "Server you first need to set up a cluster profile."),
        ("wheeler:~$ srun --pty bash", "hopper:~$ srun --pty bash"),
        ("Now simply import the wheeler cluster profile availble in the root matlab folder:",
         "Now simply import the cluster profile available in the root MATLAB folder:"),
        ("/opt/local/MATLAB/wheeler-normal.settings",
         "/opt/local/MATLAB/<cluster>-normal.settings"),
        ("using the `wheeler` cluster profile", "using the imported cluster profile"),
        ("across two nodes on Wheeler while timing", "across two nodes while timing"),
    ],
    "software/matlab-parallel-server.md": [
        ("for example, wheeler.alliance.unm.edu or xena.alliance.unm.edu.",
         "for example, hopper.alliance.unm.edu."),
        ("Specify the path to the matlab installation on the compute nodes: "
         "/opt/local/MATLAB/R2019a (or 2020a) for the Xena cluster, and "
         "/opt/local/MATLAB/R2019a for the Wheeler cluster.",
         "Specify the path to the MATLAB installation on the compute nodes "
         "(shown by `module show matlab` on the cluster)."),
        ("running on the wheeler cluster", "running on the cluster"),
        ("ssh username@wheeler.alliance.unm.edu", "ssh username@hopper.alliance.unm.edu"),
    ],
    "software/gurobi-r.md": [
        ("There are modules for both Gurobi and R on the wheeler cluster.",
         "There are modules for both Gurobi and R on the CARC clusters."),
        ("username@wheeler-sn:~$", "username@hopper:~$"),
        # 2026-09-01: the r-3.x centos7 Spack tree is gone; r/4.x Lmod modules
        # are current (observed module avail, Hopper 2026-07-25).
        ("module load r-3.6.0-gcc-7.3.0-python2-7akol5t", "module load r"),
    ],
    "software/tensorflow.md": [
        ("benchmarks run on the Xena system at CARC using",
         "benchmarks run on a previous CARC GPU system using"),
        ("Xena has nodes with single GPU and dual GPU.",
         "That system had nodes with a single GPU and dual GPUs."),
    ],
    "software/tensorflow-multi-gpu.md": [
        ("here are benchmarks run on the (legacy) Xena system at CARC using",
         "here are benchmarks run on a previous CARC GPU system using"),
        ("The old Xena cluster had nodes with both single- and dual-GPU configurations.",
         "That system had nodes with both single- and dual-GPU configurations."),
    ],
    "software/dask-scikit-learn.md": [
        ("go to https://wheeler.alliance.unm.edu:8000 where",
         "go to https://hopper.alliance.unm.edu where"),
    ],
    "software/r-packages.md": [
        ("The actual call to Torque, our job scheduler, will be explained in more "
         "depth later, but for now to request an interactive node type the "
         "following at the command prompt on Wheeler:",
         "The actual call to Slurm, our job scheduler, is explained in more depth "
         "later; for now, to request an interactive node type the following at "
         "the command prompt:"),
    ],
    "software/paraview.md": [
        ("matches the same one that is installed on Wheeler and Hopper clusters.",
         "matches the same one that is installed on the CARC clusters."),
    ],
    "tutorials/simcov.md": [
        ("running the SimCov immunology model on the Wheeler cluster.",
         "running the SimCov immunology model on CARC systems."),
        ("Load Wheeler modules and set", "Load the required modules and set"),
        ("A wheeler PBS script is provided for you.",
         "A sample batch script is provided by the developers."),
        ("already be in the wheeler_simcov_run.pbs.",
         "already be in the repository's sample submission script."),
    ],
    "tutorials/gatk.md": [
        ("with 4 nodes on wheeler takes about 5.5 hours",
         "with 4 nodes takes about 5.5 hours"),
        ("Alternatively, you can load these as modules if you are on Wheeler "
         "(Xena only has Samtools now), but",
         "Alternatively, you can load these as modules, but"),
    ],
    "tutorials/stacks.md": [
        ("Stacks can easily be run on Wheeler with installed modules,",
         "Stacks can easily be run on CARC systems with installed modules,"),
        ("This can often be run on a single node on Wheeler, as",
         "This can often be run on a single node, as"),
        ("you will almost certainly be running this on Wheeler (low resource use), "
         "which has recent versions of all three installed:",
         "you will almost certainly be running this on a CARC cluster, which has "
         "recent versions of all three installed:"),
    ],
    "tutorials/psmc.md": [
        ("Wheeler will work for some samples, but nodes",
         "Standard nodes will work for some samples, but nodes"),
    ],
    "tutorials/beast.md": [
        ("## Running BEAST on Wheeler", "## Running BEAST on CARC systems"),
    ],
    "tutorials/orca.md": [
        ("Taos uses Slurm", "CARC clusters use Slurm"),
        ("an Orca job on Taos named", "an Orca job named"),
        ("scratch_dir=/taos/scratch/$USER/", "scratch_dir=/carc/scratch/$USER/"),
    ],
    "tutorials/mpi-casa.md": [
        ("/users/sbruzew/xena-scratch/casa-blah-blah/bin/casa",
         "/path/to/casa/bin/casa"),
        ("/users/sbruzew/xena-scratch/casa-blah-blah/bin/mpicasa",
         "/path/to/casa/bin/mpicasa"),
    ],
}

# Regex fixes for multi-line regions (applied with re.sub, DOTALL):
LEGACY_FIXES_RE = {
    "systems/resource-limits.md": [
        (r"## Xena Configuration.*?## Hopper Configuration",
         "## Hopper Configuration"),
    ],
    "software/alphafold.md": [
        (r"### Xena Script ###.*?### Hopper Script ###",
         "### Hopper Script ###"),
    ],
    "tutorials/orca.md": [
        (r"### Submitting an Orca script on Wheeler.*?### Submitting on Orca script on Taos",
         "### Submitting an Orca batch script"),
    ],
    "software/r-packages.md": [
        (r"```\nyourusername@wheeler-sn\$ qsub -I.*?prologue running on host: wheeler272\n```",
         "```\nyourusername@hopper$ srun --time=01:00:00 --ntasks=8 --pty bash\n```"),
    ],
    "tutorials/metabarcoding.md": [
        (r"[ \t]*# To install QIIME2 on the Wheeler, Xena, or Hopper clusters, "
         r"use the following command:\n([ \t]*)module load miniconda3\n[ \t]*\n"
         r"[ \t]*# To do a similar installation on the Taos cluster, use the "
         r"following command instead:\n[ \t]*module load miniconda3-4\.10\.3-gcc-10\.2\.0-gu6ytpa\n[ \t]*\n",
         "\\1# Load the conda module:\n\\1module load miniconda3\n\n"),
    ],
    "systems/storage.md": [
        (r"This PBS script that will first copy an input file.*?rm -r \$TEMP_DIR\n```",
         "This Slurm script first copies an input file (large_input_data.dat) to "
         "the compute node, runs the calculation (\"run_my_program\"), and then "
         "copies all results back into the submission directory:\n"
         "\n"
         "```bash\n"
         "#!/bin/bash\n"
         "#SBATCH --nodes=1\n"
         "#SBATCH --ntasks=8\n"
         "#SBATCH --time=1:00:00\n"
         "#SBATCH --job-name=local_storage\n"
         "\n"
         "# Define a directory on the node-local disk, create it once the job\n"
         "# has started, move data there, then cd to it and run\n"
         "TEMP_DIR=/tmp/$USER/$SLURM_JOB_ID\n"
         "mkdir -p \"$TEMP_DIR\"\n"
         "cp -r $SLURM_SUBMIT_DIR/large_input_data.dat \"$TEMP_DIR\"\n"
         "cd $TEMP_DIR\n"
         "\n"
         "# Now run my program\n"
         "run_my_program\n"
         "\n"
         "# The job has finished, so move data back to where it came from\n"
         "cp -r $TEMP_DIR/* $SLURM_SUBMIT_DIR\n"
         "\n"
         "# Finally clean up the temporary directory\n"
         "rm -r $TEMP_DIR\n"
         "```"),
    ],
}

LIST_ITEM_RE = re.compile(r"^\s*(\d+\.|[-*+])\s")


def fence_tab_indented_code(md: str, default_lang: str = "bash") -> str:
    """Convert top-level tab-indented code runs into fenced blocks with a
    sniffed language, so they get syntax highlighting and consistent styling.
    Runs inside lists, existing fences, and 4-space-indented output blocks
    (nbconvert) are left untouched."""

    def is_code_line(l: str) -> bool:
        if not l.strip():  # whitespace-only lines never *start* a run
            return False
        return bool(re.match(r"^[ ]{0,3}\t", l) or re.match(r"^ {8,}\S", l))

    def dedent(l: str) -> str:
        l = re.sub(r"^[ ]{0,3}\t", "", l, count=1)
        return re.sub(r"^ {8}", "", l, count=1) if not l.startswith("\t") and re.match(r"^ {8,}", l) else l

    def sniff(text: str) -> str:
        if re.search(r"^\s*(import |from \w+ import |def |class )|print\(", text, re.MULTILINE):
            return "python"
        if re.search(r"library\(|\s<-\s|%>%|install\.packages", text):
            return "r"
        return default_lang

    lines = md.splitlines()
    out, i, fence, last_nonblank = [], 0, None, ""
    while i < len(lines):
        line = lines[i]
        marker = line.lstrip()[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (marker if fence is None else fence)
            out.append(line)
            last_nonblank = line
            i += 1
            continue
        if fence:
            out.append(line)
            i += 1
            continue
        if is_code_line(line) and not LIST_ITEM_RE.match(last_nonblank):
            j, block = i, []
            while j < len(lines) and (is_code_line(lines[j]) or not lines[j].strip()):
                block.append(lines[j])
                j += 1
            while block and not block[-1].strip():
                block.pop()
            if not block:  # degenerate run: emit as-is, guarantee progress
                out.append(line)
                i += 1
                continue
            code = [dedent(b) if b.strip() else "" for b in block]
            lang = sniff("\n".join(code))
            out += [f"```{lang}", *code, "```"]
            i += len(block)
            last_nonblank = "```"
            continue
        out.append(line)
        if line.strip():
            last_nonblank = line
        i += 1
    return "\n".join(out)


def externalize_links(md: str) -> str:
    """Make external links open in new tabs: append {target=_blank} to
    [text](http...) links, add target=_blank into existing attr blocks, and
    patch raw HTML anchors. Internal/relative and mailto: links are left
    untouched; fenced code blocks are skipped. Idempotent."""
    out, fence = [], None
    for line in md.splitlines():
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in ("```", "~~~"):
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            out.append(line)
            continue
        if fence:
            out.append(line)
            continue
        # external md links with an existing attr block: ensure target=
        def attr_sub(m):
            attrs = m.group(3)
            if "target=" in attrs:
                return m.group(0)
            return f"{m.group(1)}{attrs.rstrip()} target=_blank }}"
        line = re.sub(r"((?<!\!)\[[^\]]*\]\((https?://[^)\s]+)\)\{)([^}]*)\}",
                      attr_sub, line)
        # external md links without an attr block
        line = re.sub(r"((?<!\!)\[[^\]]*\]\((https?://[^)\s]+)\))(?!\{)",
                      r"\1{target=_blank}", line)
        # raw HTML anchors to external URLs
        line = re.sub(r'(<a\s+)(?![^>]*\btarget=)([^>]*href="https?://[^"]*")',
                      r'\1target="_blank" \2', line)
        out.append(line)
    return "\n".join(out)


# Verification: retired system names may only appear on the sanctioned legacy
# pages below. "Burrows-Wheeler" (the alignment algorithm) is not the cluster.
LEGACY_RE = re.compile(
    r"\b(Taos|Gibbs|Xena)\b"
    r"|(?<!Burrows-)(?<!Burroughs-)(?<!Burrough-)\bWheeler\b",
    re.IGNORECASE)
LEGACY_OK = {
    "systems/cluster-specifications.md",  # the legacy reference page
    "running-jobs/pbs-to-slurm.md",       # scheduler transition guide
    "software/r-pbs-jobs.md",             # deprecated, points at replacements
    "systems/overview.md",                # pointer to the legacy reference
    "systems/index.md",                   # lists the legacy reference page
    "about/ai-agents.md",                 # tells agents these systems are retired
    "log.md",                             # history (documents the retirement)
}


def check_legacy_mentions() -> int:
    """After migration: fail if a retired system name survives in the content
    of any page outside the sanctioned legacy set (LEGACY_OK). Frontmatter is
    skipped — provenance must keep the true names of upstream source files."""
    bad = 0
    for path in sorted(DOCS.rglob("*.md")):
        rel = str(path.relative_to(DOCS))
        if rel in LEGACY_OK or rel.split("/")[0] == "assets":
            continue
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
            if m:
                text = text[m.end():]
        for i, line in enumerate(text.splitlines(), 1):
            if LEGACY_RE.search(line):
                print(f"LEGACY MENTION: {rel}:+{i}: {line.strip()[:100]}", file=sys.stderr)
                bad += 1
    return bad


def sh(cmd, cwd=None) -> str:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False).stdout.strip()


def ensure_repo(path: Path, url: str):
    if not (path / ".git").exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", url, str(path)], check=True)
    # need full history for per-file last_modified
    if (path / ".git" / "shallow").exists():
        subprocess.run(["git", "-C", str(path), "fetch", "--unshallow", "-q"], check=False)


def last_modified(repo_dir: Path, rel: str) -> str:
    out = sh(["git", "log", "-1", "--format=%cI", "--", rel], cwd=repo_dir)
    return out or GENERATED_AT


def yq(s: str) -> str:
    """YAML-safe double-quoted scalar."""
    return json.dumps(s, ensure_ascii=False)


def frontmatter(p: Page, repo_dir: Path, repo_url: str) -> str:
    lines = ["---",
             f"title: {yq(p.title)}",
             f"description: {yq(p.description)}",
             f"type: {p.type}"]
    if p.tags:
        lines.append("tags:")
        lines += [f"  - {t}" for t in p.tags]
    if p.status:
        lines.append(f"status: {p.status}")
    if p.stale_after:
        lines.append(f"stale_after: {yq(p.stale_after)}")
    lines += ["generated:",
              f"  by: {yq(GENERATED_BY)}",
              f"  at: {yq(GENERATED_AT)}"]
    if p.src:
        src_url = f"{repo_url}/blob/master/{urllib.parse.quote(p.src)}"
        lines += ["sources:",
                  f"  - id: {p.repo}",
                  f"    resource: {yq(src_url)}",
                  f"    title: {yq('UNM-CARC ' + ('QuickBytes' if p.repo == 'quickbytes' else 'webinfo') + ': ' + p.src)}",
                  "    author: \"team:unm-carc\"",
                  f"    last_modified: {yq(last_modified(repo_dir, p.src))}"]
    lines.append("---")
    return "\n".join(lines) + "\n"


def convert_notebook(src: Path, slug: str) -> str:
    """Convert an .ipynb to markdown; move extracted files into the image dir."""
    outdir = Path("/tmp/nbmd") / slug
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    subprocess.run([sys.executable, "-m", "nbconvert", "--to", "markdown",
                    f"--output-dir={outdir}", f"--output={slug}", str(src)], check=True)
    md = (outdir / f"{slug}.md").read_text(encoding="utf-8")
    extracted = outdir / f"{slug}_files"
    if extracted.exists():
        target = IMG_DIR / f"{slug}_files"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(extracted, target)
        md = md.replace(f"{slug}_files/", f"../assets/images/quickbytes/{slug}_files/")
    return md


def normalize_body(md: str, p: Page, image_names: set, asset_map: dict, link_map: dict) -> str:
    # Drop a leading H1/H2 title; we re-insert a clean H1 from the mapping.
    lines = md.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and re.match(r"^#{1,2}\s+\S", lines[0]):
        lines.pop(0)
    body = "\n".join(lines).strip("\n")

    # Rewrite image references (markdown + HTML) by basename.
    def img_sub(m):
        pre, path = m.group(1), m.group(2)
        base = urllib.parse.unquote(path.split("/")[-1].split("?")[0])
        if base in image_names:
            return f"{pre}../assets/images/quickbytes/{urllib.parse.quote(base)}"
        return m.group(0)

    body = re.sub(r"(!\[[^\]]*\]\()\s*([^)\s]+)", img_sub, body)
    body = re.sub(r"(<img[^>]*\bsrc=[\"'])([^\"']+)", img_sub, body)

    # Rewrite links to bundled downloadable assets by basename.
    def asset_sub(m):
        pre, path = m.group(1), m.group(2)
        base = urllib.parse.unquote(path.split("/")[-1].split("?")[0])
        if base in asset_map and not path.startswith(("http://", "https://", "#")):
            return f"{pre}../assets/files/{asset_map[base]}"
        return m.group(0)

    body = re.sub(r"((?<!\!)\[[^\]]*\]\()\s*([^)\s]+)", asset_sub, body)

    # Rewrite inter-QuickByte links (local relative or GitHub blob URLs).
    def link_sub(m):
        pre, path = m.group(1), m.group(2)
        raw = urllib.parse.unquote(path.split("?")[0])
        base = raw.split("#")[0].split("/")[-1]
        frag = "#" + raw.split("#")[1] if "#" in raw else ""
        if base in link_map:
            target = link_map[base]
            here = str(Path(p.dest).parent)
            rel = os.path.relpath(target, here).replace(os.sep, "/")
            return f"{pre}{rel}{frag}"
        return m.group(0)

    body = re.sub(r"((?<!\!)\[[^\]]*\]\()\s*([^)\s]+)", link_sub, body)

    # Fence top-level tab-indented code runs for syntax highlighting.
    body = fence_tab_indented_code(body, p.code_lang)

    # External links open in new browser tabs.
    body = externalize_links(body)

    # Surgical per-page fixes.
    for old, new in PATCHES.get(p.dest, []):
        body = body.replace(old, new)

    # Legacy purge: retire Wheeler/Taos/Gibbs/Xena and PBS-as-current wording.
    for old, new in LEGACY_FIXES.get(p.dest, []):
        body = body.replace(old, new)
    for pat, repl in LEGACY_FIXES_RE.get(p.dest, []):
        body = re.sub(pat, repl, body, flags=re.DOTALL)

    # Build the final document.
    out = [f"# {p.title}", ""]
    notes = []
    if p.note:
        notes.append(p.note)
    for n in notes:
        kind = "warning" if p.status in ("deprecated", "draft") else "note"
        title = "Legacy content" if "retired" in n else "Please note"
        out.append(f'!!! {kind} "{title}"')
        out += [f"    {line}" for line in n.splitlines()]
        out.append("")
    out.append(body)
    return "\n".join(out).rstrip() + "\n"


def video_embed(vid: str, title: str) -> str:
    return (f'<iframe class="carc-video" '
            f'src="https://www.youtube-nocookie.com/embed/{vid}" '
            f'title={json.dumps(title)} loading="lazy" '
            f'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; '
            f'picture-in-picture; web-share" '
            f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>')


def video_section(p: Page) -> str:
    if not p.videos:
        return ""
    head = "## Video walkthrough" + ("s" if len(p.videos) > 1 else "")
    parts = [f"\n{head}\n"]
    for vid, title in p.videos:
        parts.append(f"**{title}** — from the "
                     f"[CARC video tutorials](../training/videos.md):\n")
        parts.append(video_embed(vid, title) + "\n")
    return "\n".join(parts)


def provenance_footer(p: Page, repo_url: str, repo_dir: Path) -> str:
    if not p.src:
        return ""
    date = last_modified(repo_dir, p.src)[:10]
    url = f"{repo_url}/blob/master/{urllib.parse.quote(p.src)}"
    return (f"\n<p class=\"carc-provenance\" markdown>Migrated from "
            f"[UNM-CARC QuickBytes]({url}){{target=_blank}} (last source update {date}). "
            f"Spotted a problem? [Open an issue or pull request]({QB_URL}){{target=_blank}}.</p>\n")


def write_index(section: str, pages_by_dest: dict):
    name, blurb = SECTIONS[section]
    lines = [f"# {name}", "", blurb, ""]

    def entry(fname: str) -> str:
        p = pages_by_dest[f"{section}/{fname}"]
        suffix = " *(legacy)*" if p.status == "deprecated" else ""
        return f"* [{p.title}]({fname}) - {p.description}{suffix}"

    if section == "software":
        for group, files in SOFTWARE_GROUPS:
            lines += [f"## {group}", ""]
            lines += [entry(f) for f in files]
            lines.append("")
    else:
        ordered = [d for d in pages_by_dest if d.startswith(section + "/")]
        lines += [entry(d.split("/", 1)[1]) for d in ordered]
        lines.append("")
    if section == "about":
        lines += ["* [Documentation update log](../log.md) - Chronological history of changes to this documentation bundle.", ""]
    (DOCS / section / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    ensure_repo(QB_DIR, QB_URL)
    ensure_repo(WEBINFO_DIR, WEBINFO_URL)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy images (Images/ dir + every root-level png/jpeg/jpg/gif).
    image_names = set()
    img_src = []
    imgdir = QB_DIR / "Images"
    if imgdir.exists():
        img_src += sorted(imgdir.iterdir())
    img_src += sorted(QB_DIR.glob("*.png")) + sorted(QB_DIR.glob("*.jpeg")) + \
               sorted(QB_DIR.glob("*.jpg")) + sorted(QB_DIR.glob("*.gif"))
    for f in img_src:
        if f.is_file():
            shutil.copy2(f, IMG_DIR / f.name)
            image_names.add(f.name)

    # 2. Copy downloadable assets.
    asset_map = {}
    for src, dest in FILE_ASSETS:
        s = QB_DIR / src
        if s.exists():
            d = FILES_DIR / dest
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)
            asset_map[Path(src).name] = dest
    # workshop slide decks
    ws = QB_DIR / "workshop_slides"
    if ws.exists():
        for f in sorted(ws.glob("*.pdf")):
            d = FILES_DIR / "workshops" / f.name
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)
            asset_map[f.name] = f"workshops/{f.name}"

    # 3. Link map: source basename -> docs-relative dest (also html twins).
    link_map = {}
    for p in PAGES:
        if p.src:
            base = Path(p.src).name
            link_map[base] = p.dest
            if base.endswith(".md"):
                link_map[base[:-3] + ".html"] = p.dest

    pages_by_dest = {p.dest: p for p in PAGES}

    # 4. Migrate.
    migrated, skipped, frozen_kept = [], [], []
    for p in PAGES:
        if p.repo == "hand":
            continue
        if p.frozen and (DOCS / p.dest).exists():
            frozen_kept.append(p.dest)  # curated in-repo; never overwrite
            continue
        repo_dir = QB_DIR if p.repo == "quickbytes" else WEBINFO_DIR
        repo_url = QB_URL if p.repo == "quickbytes" else WEBINFO_URL
        src = repo_dir / p.src
        if not src.exists():
            skipped.append(p.src)
            continue
        if p.notebook:
            slug = Path(p.dest).stem
            raw = convert_notebook(src, slug)
        else:
            raw = src.read_text(encoding="utf-8", errors="replace")
        body = normalize_body(raw, p, image_names, asset_map, link_map)
        doc = (frontmatter(p, repo_dir, repo_url) + "\n" + body
               + video_section(p) + provenance_footer(p, repo_url, repo_dir))
        dest = DOCS / p.dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(doc, encoding="utf-8")
        migrated.append(p.dest)

    # 5. Section indexes (OKF §8: no frontmatter, heading + bullet listings).
    for section in SECTIONS:
        write_index(section, pages_by_dest)

    print(f"Migrated {len(migrated)} pages; copied {len(image_names)} images, "
          f"{len(asset_map)} downloadable assets.")
    if frozen_kept:
        print(f"Kept {len(frozen_kept)} frozen (curated) page(s): {', '.join(frozen_kept)}")
    if skipped:
        print("MISSING SOURCES:")
        for s in skipped:
            print(f"  - {s}")

    bad = check_legacy_mentions()
    if bad:
        print(f"ERROR: {bad} retired-system mention(s) outside the sanctioned "
              f"legacy pages — extend LEGACY_FIXES or LEGACY_OK.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
