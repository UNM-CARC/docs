---
title: "R batch jobs with Slurm"
description: "Write and submit a Slurm script that runs an R script on Easley, line by line, using a CARC R module or your own conda R environment."
type: Guide
tags:
  - R
  - Slurm
sources:
  - id: quickbytes-pr-270
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/270"
    title: "UNM-CARC QuickBytes PR #270: R_at_CARC for Easley and Slurm"
    author: "human:hfricke"
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/R_at_CARC/PBS_job_submission.md"
    title: "UNM-CARC QuickBytes: R_at_CARC/PBS_job_submission.md"
    author: "team:unm-carc"
    last_modified: "2019-12-03T10:18:11-07:00"
---

# R batch jobs with Slurm

To run R on a cluster, you write a **Slurm script**: a short bash script that
lists the resources you want, loads R, and runs your R script. You submit it
with `sbatch`, and Slurm runs it on a compute node when resources are free.
This page builds one line by line. If you haven't set up R yet, start with
[Getting R software](getting-r.md).

## An example R script

Save this one-line R script as `my_script.R`. It prints the R version and the
node it ran on:

```r
cat("Hello from R", R.version.string, "on", Sys.info()[["nodename"]], "\n")
```

## The Slurm script

Save this as `my_slurm_script.sh` in the same directory, changing
`my_name@unm.edu` to your email address:

```bash
#!/bin/bash

#SBATCH --job-name my_r_job
#SBATCH --partition general
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 8
#SBATCH --time 48:00:00
#SBATCH --output my_r_job.out
#SBATCH --error my_r_job.err
#SBATCH --mail-type begin,end,fail
#SBATCH --mail-user my_name@unm.edu

cd $SLURM_SUBMIT_DIR

module load libdeflate/1.14-2pby r/4.5.2-pspo
export LD_LIBRARY_PATH=$LIBDEFLATE_LIB:$LD_LIBRARY_PATH

Rscript my_script.R
```

Submit it from the Easley head node:

```bash
sbatch my_slurm_script.sh
```

When it finishes, `my_r_job.out` holds the script's output:

```text
Hello from R R version 4.5.2 (2025-10-31) on easley005
```

Your node name will differ.

## What each part does

A Slurm script is a bash script with extra lines that start with `#SBATCH`.
Bash treats those lines as comments, but `sbatch` reads them as resource
requests. The first line, `#!/bin/bash`, tells the system to run the rest of
the file with bash.

| Line | Meaning |
|---|---|
| `--job-name my_r_job` | The name shown in the queue (`squeue --me`). |
| `--partition general` | Which group of nodes to run on. `general` is the default partition most users have. |
| `--ntasks 1` | Run one copy of your program. |
| `--cpus-per-task 8` | Give that one copy 8 CPU cores, which R can use through parallel packages such as `parallel` or `future`. |
| `--time 48:00:00` | The most time your job may run (here 48 hours). Slurm stops the job when it runs out. |
| `--output`, `--error` | Files for normal output and error messages. Point both at the same file if you want them combined. |
| `--mail-type`, `--mail-user` | Email you when the job begins, ends, or fails. |

Always set the time limit and the resources your job needs. For every option,
run `man sbatch` on the head node or see the
[Slurm introduction](../running-jobs/slurm-intro.md).

The rest of the script is ordinary bash:

* `cd $SLURM_SUBMIT_DIR` moves to the directory you ran `sbatch` from, so the
  script finds `my_script.R` and writes its output there.
* `module load libdeflate/1.14-2pby r/4.5.2-pspo` and the `export` line load
  CARC's R 4.5.2. Keep both: without the `export` line, R fails inside Slurm
  jobs with
  `error while loading shared libraries: libdeflate.so.0: cannot open shared object file: No such file or directory`.
* `Rscript my_script.R` runs your script. `Rscript` replaces the older
  `R CMD BATCH`.

!!! warning "One task, several CPUs"
    Request `--ntasks 1` with `--cpus-per-task` for an ordinary R script.
    If you ask for several tasks (for example `--ntasks-per-node 8`) and start
    R with `srun`, Slurm runs **8 separate copies** of your script.

## Using your own conda R environment

If you installed R into a conda environment, as described in
[Getting R software](getting-r.md), replace the two R module lines in the
script with:

```bash
module load miniconda3/latest
source activate my_r_env
```

## A longer example

The [sequential.R](../assets/files/r/sequential.R) script simulates gene trees
and compares them to a species tree. It needs the `TreeSim` and `phangorn`
packages: install them first as described in
[Installing R packages](r-packages.md). Download
[sequential_r.sh](../assets/files/r/sequential_r.sh), put both files in the
same directory, change the email address, and submit:

```bash
sbatch sequential_r.sh
```

The script saves the trees to `all_the_species_trees.pdf` and writes the mean
and median tree distances to `r_sequential.out`. The trees are random, so your
numbers will differ:

```text
null device 
          1 
[1] "mean is"
[1] 2.593317
[1] "median is"
[1] 2.511453
```

`r_sequential.err` lists the packages R loaded (`ape`, `geiger`, `phytools`,
`maps`). Those messages are normal.

*Every command and script on this page was tested on Easley on November 16, 2026.*

<p class="carc-provenance" markdown>Curated from [QuickBytes PR #270](https://github.com/UNM-CARC/QuickBytes/pull/270){target=_blank} and the earlier [PBS QuickByte](https://github.com/UNM-CARC/QuickBytes/blob/master/R_at_CARC/PBS_job_submission.md){target=_blank}. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
