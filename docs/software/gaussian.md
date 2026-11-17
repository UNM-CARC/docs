---
title: "Gaussian"
description: "Run Gaussian 16 quantum chemistry jobs on Easley: load the module, write an input file, run interactively, and scale across nodes with Linda."
type: Guide
tags:
  - Chemistry
  - Gaussian
  - Slurm
stale_after: "2027-08-31T00:00:00Z"
sources:
  - id: quickbytes-pr-259
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/259"
    title: "UNM-CARC QuickBytes PR #259: Add Gaussian QuickByte (tested on Easley 2026-07-07)"
    author: "human:hfricke"
  - id: gaussian-workshop
    resource: "https://carc.unm.edu/docs/assets/files/workshops/IntermediateIntroToCARCWorkshopGaussian_1hr.pdf"
    title: "CARC Intermediate Introduction to Computing at CARC: 1 hour version with Gaussian"
    author: "team:unm-carc"
---

# Gaussian

[Gaussian](https://gaussian.com/){target=_blank} is a general-purpose
computational chemistry package for quantum chemistry calculations such as
geometry optimizations, energies, and vibrational frequencies. This page
covers loading Gaussian 16 on Easley, running a job interactively, and
submitting a batch job that runs across two nodes.

## Load Gaussian

```bash
module load gaussian/g16
```

Loading the module sets Gaussian's scratch directory for you:

```text
Gaussian scratch directory (GAUSS_SCRDIR) set to /easley/scratch/users/<your_username>/
```

## Create an input file

A Gaussian job is a plain-text `.com` input file: a route line (the
calculation to run), a title, the charge and spin multiplicity, and a
molecular geometry. You can draw a molecule in
[Avogadro](https://two.avogadro.cc/){target=_blank} and export it with
**File > Export > Molecule...** as "Gaussian Z-Matrix Input", or write a small
geometry by hand. For example, save this as `water.com`:

```text
%chk=water.chk
%mem=4GB
%nprocshared=4
# opt B3LYP/6-31G(d)

Water molecule optimization

0 1
O    0.000000    0.000000    0.000000
H    0.000000    0.757000    0.586000
H    0.000000   -0.757000    0.586000

```

* `# opt B3LYP/6-31G(d)` runs a geometry optimization (`opt`) with the B3LYP
  functional and the 6-31G(d) basis set.
* `0 1` is the molecule's charge and spin multiplicity.
* The file must end with a blank line, or Gaussian won't read the input.

## Run interactively

Gaussian must run on a compute node, not the login node. Request one, then
run the job:

```bash
srun --partition debug --ntasks 1 --cpus-per-task 4 --mem 8G --pty bash
module load gaussian/g16
g16 water.com water.log
```

Check whether it succeeded:

```bash
grep -i "normal termination" water.log
```

```text
 Normal termination of Gaussian 16 at Mon Nov 16 10:32:29 2026.
```

"Normal termination" means the job finished successfully; this small
optimization takes a few seconds. If a job fails, that line is missing and
the last lines of the log describe the error.

## Run across nodes with Linda

To use more than one node, Gaussian uses **Linda** to coordinate copies of
itself across nodes. Linda doesn't read Slurm's allocation directly, so the
batch script converts the node list in `$CARC_NODEFILE` (set by CARC once your
job starts) into the format Linda expects.

Remove the output from the interactive run first:

```bash
rm -f water.log water.chk
```

Save this as `gaussian16_linda_water.sh`:

```bash
#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
#SBATCH --job-name=g16_water

module load gaussian/g16

# To make linda print verbose messages
export GAUSS_LFLAGS="-v"

INPUT_MOLECULE=$SLURM_SUBMIT_DIR/water.com
OUTPUT_FILE=$SLURM_SUBMIT_DIR/water.log

# Reformat the SLURM provided list of compute nodes to a format Gaussian can understand
# i.e. remove duplicates and replace newlines with commas
export GAUSS_WDEF=$(cat $CARC_NODEFILE | uniq | sed -z 's/\n/,/g;s/,$/\n/')

# Tell Linda to use as many nodes as requested by the user
export GAUSS_PDEF=$SLURM_CPUS_PER_TASK
echo "Parallelizing $GAUSS_PDEF processes across $GAUSS_WDEF nodes."

# Set the memory Gaussian variable
export GAUSS_MDEF=4GB

# Run Gaussian
g16 $INPUT_MOLECULE $OUTPUT_FILE
```

Submit it and watch the queue:

```bash
sbatch gaussian16_linda_water.sh
squeue --me
```

When the job finishes, its Slurm output file shows Linda splitting the work
between the two nodes:

```text
Gaussian scratch directory (GAUSS_SCRDIR) set to /easley/scratch/users/<your_username>/
Parallelizing 4 processes across easley012,easley013 nodes.
ntsnet: using executable file /opt/local/gaussian/g16/C.01/avx2/g16/linda-exe/l302.exel
ntsnet: trying to schedule 1 worker
ntsnet: scheduled a total of 1 worker
ntsnet: starting master process on easley012
ntsnet: starting 1 worker on easley013
...
```

Your node names and the `linda-exe` programs listed will differ; what matters
is a master process on one node and a worker on the other. Check `water.log`
as before: it should end with "Normal termination of Gaussian 16."

## Further reading

* [Gaussian 16 manual](https://gaussian.com/man/){target=_blank}
* [Route-line keyword reference](https://gaussian.com/keywords/){target=_blank}
  (functionals, basis sets, job types)
* CARC workshop slides:
  [Intermediate workshop: Gaussian (1 hour)](../assets/files/workshops/IntermediateIntroToCARCWorkshopGaussian_1hr.pdf)
  and [Slurm with Gaussian and Abinit](../assets/files/workshops/IntroToCARCWorkshopSlurmGaussianAbinit.pdf).
  See [Workshops](../training/workshops.md) for more.

*Every command and script on this page was tested on Easley on November 16, 2026.*

<p class="carc-provenance" markdown>Curated from [QuickBytes PR #259](https://github.com/UNM-CARC/QuickBytes/pull/259){target=_blank} (tested on Easley 2026-07-07), based on the CARC intermediate workshop with Gaussian. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
