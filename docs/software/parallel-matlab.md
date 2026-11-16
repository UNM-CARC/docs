---
title: "Parallel MATLAB batch jobs"
description: "Run parfor loops on many cores of one Easley node with MATLAB's local worker pool, interactively or as a Slurm batch job."
type: Guide
tags:
  - MATLAB
  - Parallel
  - Slurm
sources:
  - id: quickbytes-pr-277
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/277"
    title: "UNM-CARC QuickBytes PR #277: Parallel MATLAB batch submission.md (tested on Easley)"
    author: "human:hfricke"
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/Parallel%20MATLAB%20profile%20setup%20and%20batch%20submission.md"
    title: "UNM-CARC QuickBytes: Parallel MATLAB profile setup and batch submission.md"
    author: "team:unm-carc"
    last_modified: "2022-05-11T10:43:18-06:00"
---

# Parallel MATLAB batch jobs

MATLAB's Parallel Computing Toolbox can split loops across many CPU cores. On
Easley you request cores from Slurm as usual, then start a pool of MATLAB
workers on those cores. There's no cluster profile to import.

This page covers work that fits on one node. To spread MATLAB workers across
several nodes, see [MATLAB Parallel Server](matlab-parallel-server.md).

!!! note "No profile import needed"
    Older versions of this guide imported a cluster profile with
    `parallel.importProfile('/opt/local/MATLAB/<cluster>-normal.settings')`.
    You don't need that on Easley. `parpool` uses MATLAB's built-in local
    (`Processes`) profile and the cores Slurm gave you.

## Try it interactively

Start an interactive session with 16 cores:

```bash
easley-sn:~$ srun --partition general --ntasks 1 --cpus-per-task 16 --pty bash
```

Once a node is allocated, load MATLAB and start it:

```bash
easley021:~$ module load matlab/R2024b
easley021:~$ matlab
```

Start a pool the same size as the cores you requested, and time a `parfor`
loop on it:

```matlab
poolobj = parpool(16);
tic
n = 200;
A = 500;
a = zeros(1,n);
parfor i = 1:n
    a(i) = max(abs(eig(rand(A))));
end
toc
delete(poolobj);
```

## Run it as a batch job

A batch job avoids the mistakes that come with interactive work. This example
compares a regular `for` loop with a 16-worker `parfor` loop.

### MATLAB script

Save this as `parallel_matlab.m`:

```matlab
poolobj = parpool(16);

tic
n = 200;
A = 500;
a = zeros(1,n);
for i=1:n
    a(i) = max(abs(eig(rand(A))));
end
toc

tic
n = 200;
A = 500;
a = zeros(1,n);
parfor i=1:n
    a(i) = max(abs(eig(rand(A))));
end
toc
delete(poolobj);
```

### Slurm script

Save this as `parallel_matlab.sh`. Request as many `--cpus-per-task` as the
worker count you pass to `parpool`:

```bash
#!/bin/bash

#SBATCH --job-name parallel_matlab
#SBATCH --partition general
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 16
#SBATCH --time 00:10:00
#SBATCH --output parallel_matlab_job.out
#SBATCH --error parallel_matlab_job.err

cd $SLURM_SUBMIT_DIR

module load matlab/R2024b

matlab -nodisplay -r parallel_matlab > parallel_matlab.out
```

!!! tip "Match the pool to the job automatically"
    Instead of hard-coding `16` in both files, you can size the pool from
    Slurm's allocation inside the MATLAB script:
    `parpool(str2double(getenv('SLURM_CPUS_PER_TASK')))`.

### Submit the job

```bash
easley-sn:~$ sbatch parallel_matlab.sh
```

After MATLAB's startup banner, `parallel_matlab.out` shows the regular loop's
time first and the 16-worker `parfor` loop's second:

```text
Starting parallel pool (parpool) using the 'Processes' profile ...
Connected to parallel pool with 16 workers.
Elapsed time is 21.161951 seconds.
Elapsed time is 1.688252 seconds.
Parallel pool using the 'Processes' profile is shutting down.
```

Your times will vary from run to run.

If you need help with parallel MATLAB, email
[help@carc.unm.edu](mailto:help@carc.unm.edu).

*Every command and script on this page was tested on Easley on November 16, 2026.*

<p class="carc-provenance" markdown>Curated from [QuickBytes PR #277](https://github.com/UNM-CARC/QuickBytes/pull/277){target=_blank} (tested on Easley) and the earlier [QuickByte](https://github.com/UNM-CARC/QuickBytes/blob/master/Parallel%20MATLAB%20profile%20setup%20and%20batch%20submission.md){target=_blank}. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
