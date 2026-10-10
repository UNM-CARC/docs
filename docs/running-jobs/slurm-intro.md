---
title: "Introduction to Slurm"
description: "Slurm basics on CARC clusters: partitions, interactive jobs, and your first batch script."
type: Guide
tags:
  - Slurm
  - Jobs
  - New users
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/Intro_to_slurm.md"
    title: "UNM-CARC QuickBytes: Intro_to_slurm.md"
    author: "team:unm-carc"
    last_modified: "2026-07-06T13:37:22-06:00"
---

# Introduction to Slurm

## Getting Started

For a general introduction to Slurm — including an overview of its architecture, key commands (`sinfo`, `squeue`, `srun`, `sbatch`, `scancel`, `scontrol`), and basic job submission examples — refer to the **[official Slurm Quick Start User Guide](https://slurm.schedmd.com/quickstart.html){target=_blank}**. The guide is well-maintained and covers the core concepts you need to get up and running.

The sections below supplement that guide with information specific to CARC Easley at the University of New Mexico.

---

## CARC Easley Partitions

When you run `sinfo` on Easley, you will see output similar to the following:

```bash
[username@easley ~]$ sinfo
```

```
PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST
general*       up 2-00:00:00      2   mix- easley[005-006]
general*       up 2-00:00:00      2  drain easley[011,033]
general*       up 2-00:00:00     20    mix easley[002-003,008,017,021-024,026-027,030-031,038-042,046-048]
general*       up 2-00:00:00     24  alloc easley[001,004,007,009-010,012-016,018-020,025,028-029,032,034-037,043-045]
bigmem         up 2-00:00:00      1  drain easley049
bigmem         up 2-00:00:00      1    mix easley050
h100           up 2-00:00:00      1    mix easley054
h100           up 2-00:00:00      3  alloc easley[051-053]
l40s           up 2-00:00:00      1    mix easley055
l40s           up 2-00:00:00      2  alloc easley[056-057]
interactive    up    4:00:00      2   mix- easley[005-006]
interactive    up    4:00:00      3  drain easley[011,033,049]
interactive    up    4:00:00     23    mix easley[002-003,008,017,021-024,026-027,030-031,038-042,046-048,050,054-055]
interactive    up    4:00:00     29  alloc easley[001,004,007,009-010,012-016,018-020,025,028-029,032,034-037,043-045,051-053,056-057]
debug          up    1:00:00      2   mix- easley[005-006]
debug          up    1:00:00      3  drain easley[011,033,049]
debug          up    1:00:00     23    mix easley[002-003,008,017,021-024,026-027,030-031,038-042,046-048,050,054-055]
debug          up    1:00:00     29  alloc easley[001,004,007,009-010,012-016,018-020,025,028-029,032,034-037,043-045,051-053,056-057]
scavenger      up 2-00:00:00      2   mix- easley[005-006]
scavenger      up 2-00:00:00      3  drain easley[011,033,049]
scavenger      up 2-00:00:00     28    mix easley[002-003,008,017,021-024,026-027,030-031,038-042,046-048,050,054-055,058,060-063]
scavenger      up 2-00:00:00     30  alloc easley[001,004,007,009-010,012-016,018-020,025,028-029,032,034-037,043-045,051-053,056-057,059]
```

Key partitions you may have access to:

- **general** — The default community partition. Maximum wall time of 2 days. Use this if you are not a member of a specific condo group.
- **debug** — Short jobs only (1-hour limit). Useful for testing scripts before submitting long runs.
- **condo** — Purchased nodes available to specific research groups. If you are a member of a condo group, you likely already know your partition name. Check with your PI if you are unsure.
- **scavenger** - Whenever a purchased/reserved node is not in use, this partition grabs them and allows them to be used by the public, but be warned you will be kicked off if the owner begins a job on it.

To see detailed node information including CPU count, memory, and disk:

```bash
sinfo -N -l
```

If you omit `--partition` (or `-p`) from your job submission, your job will be submitted to the `general` partition by default.

---

## Useful `squeue` Flags

The official guide covers `squeue` basics. A few flags that are especially handy on a shared cluster:

```bash
squeue --me              # Show only your jobs
squeue -p general        # Show only jobs in the general partition
squeue -u <username>     # Show jobs for a specific user
```

---

## Canceling Jobs

```bash
scancel <JOBID>          # Cancel a specific job
scancel --me             # Cancel all of your jobs
```

---

## Notes on Resource Requests

- The more constraints you add to a job (e.g., requiring all tasks on the same node with `--ntasks-per-node`), the longer your queue time may be. Requesting resources spread across nodes often results in faster scheduling.
- Memory is specified per CPU with `--mem-per-cpu` (in MB) or for the whole job with `--mem`.
- Time limits use the format `D-HH:MM:SS` (e.g., `1-12:00:00` for 1 day and 12 hours) or `MM:SS` / `HH:MM:SS` for shorter jobs.
- If you omit `--time`, you do **not** get the partition maximum: `general` applies a default of 8 hours (`DefaultTime=08:00:00`). Check `scontrol show partition <name>` for the partition you use.
- If you omit `--mem`/`--mem-per-cpu`, memory defaults to an amount proportional to the CPUs you request (`DefMemPerCPU` — observed ≈3.7 GB per CPU on Easley's `general` partition, ≈2.9 GB on Hopper's). A small `--cpus-per-task` therefore caps your memory well below what the node physically has — the usual cause of jobs killed `OUT_OF_MEMORY` on nodes with plenty of free RAM. See [troubleshooting](../faq/troubleshooting.md#my-job-failed-or-was-killed).

---

## Additional Resources

- [Official Slurm Quick Start Guide](https://slurm.schedmd.com/quickstart.html){target=_blank}
- [CARC at UNM Documentation](https://carc.unm.edu){target=_blank}
- For help, contact the CARC support team or visit the CARC user portal.


*This quickbyte was validated on 8/3/2026.*

## Video walkthrough

**Slurm Job Scheduler** — from the [CARC video tutorials](../training/videos.md):

<iframe class="carc-video" src="https://www.youtube-nocookie.com/embed/cIRyG8C3CVk" title="Slurm Job Scheduler" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/Intro_to_slurm.md){target=_blank} (last source update 2026-07-06). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
