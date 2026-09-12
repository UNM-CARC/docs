---
title: "ORCA quantum chemistry"
description: "Run ORCA quantum chemistry calculations in parallel on CARC clusters."
type: Tutorial
tags:
  - Chemistry
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/orca_easley_hopper.md"
    title: "UNM-CARC QuickBytes: orca_easley_hopper.md"
    author: "team:unm-carc"
    last_modified: "2026-08-03T15:32:09-06:00"
---

# ORCA quantum chemistry

Both Easley and Hopper use Slurm (**S**imple **L**inux **U**tility for **R**esource **M**anagement) to submit jobs and manage resources. Below is a sample script for submitting an Orca job named `orca_submission.sh`.

### Submitting an Orca script on Easley

```bash
#!/usr/bin/bash

## Set your slurm flags here requesting resources.
#SBATCH --job-name=orca_test
#SBATCH --output=test.out
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --partition=general
#SBATCH --mem-per-cpu=6GB
#SBATCH --mail-type=begin        # send email when job begins
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-type=fail         # send email if job fails
#SBATCH --mail-user=<YourNetID>@unm.edu

module load orca/6.1.1

## Set your input and output file names
input_file=my_orca_input.inp
output_file=my_orca_output.log

# Orca needs the full path when running in parallel
full_orca_path=$(which orca)

# Run Orca
$full_orca_path $input_file > $output_file
```

Now you can simply submit your job to the queue with `sbatch orca_submission.sh`.

### Submitting an Orca script on Hopper

The Hopper version is identical — check `sinfo` for the partitions you have access to (Hopper's default is `general`, same as Easley):

```bash
#!/usr/bin/bash

## Set your slurm flags here requesting resources.
#SBATCH --job-name=orca_test
#SBATCH --output=test.out
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --partition=general
#SBATCH --mem-per-cpu=6GB
#SBATCH --mail-type=begin        # send email when job begins
#SBATCH --mail-type=end          # send email when job ends
#SBATCH --mail-type=fail         # send email if job fails
#SBATCH --mail-user=<YourNetID>@unm.edu

module load orca/6.1.1

## Set your input and output file names
input_file=my_orca_input.inp
output_file=my_orca_output.log

# Orca needs the full path when running in parallel
full_orca_path=$(which orca)

# Run Orca
$full_orca_path $input_file > $output_file
```

Now you can simply submit your job to the queue with `sbatch orca_submission.sh`.

Neither Easley nor Hopper provisions a personal top-level scratch directory by default for every user. If you need scratch space for large I/O, use your project's allocated path under `/carc/scratch/projects/` (see `storage_permissions_BeeGFS.md` for how to find your exact path, since the layout varies by project) or just run directly from `$SLURM_SUBMIT_DIR`, as the scripts above do. Contact help@carc.unm.edu if you need a dedicated scratch allocation.

*Module and paths verified against `orca/6.1.1` on both Easley and Hopper.*

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/orca_easley_hopper.md){target=_blank} (last source update 2026-08-03). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
