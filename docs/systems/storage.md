---
title: "Storage and backups"
description: "CARC storage spaces (home, project, scratch), the real filesystem paths, retention windows, and what is backed up."
type: Guide
tags:
  - Storage
  - Data
generated:
  by: "claude/fable-5"
  at: "2026-09-01T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/storage_and_backup.md"
    title: "UNM-CARC QuickBytes: storage_and_backup.md"
    author: "team:unm-carc"
    last_modified: "2021-03-18T12:38:03-06:00"
  - id: knowledge-store
    resource: "https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store"
    title: "CARC knowledge store: kb/facts/easley.md, kb/facts/hopper.md (observed cluster state)"
    author: "team:unm-carc"
    last_modified: "2026-07-25T00:00:00Z"
---

# Storage and backups

CARC provides two broad classes of storage:

- **Enterprise storage** is intended for safely retaining data over the
  long term. Home directories and Enterprise Project Storage are backed up.
- **Scratch storage** is temporary working space for data that is being
  actively processed or analyzed. Scratch storage is **not backed up** and
  should not be used as the only copy of important data.

For help restoring data from Enterprise Project Storage or a home directory,
email [help@carc.unm.edu](mailto:help@carc.unm.edu).

## Storage limits

| Storage type | Location | User or project limit | PI limit | Backed up? |
| ------------ | -------- | --------------------- | -------- | ---------- |
| Home directory | `/users/{username}` | 100 GB per user | — | Yes |
| Enterprise Project Storage | `/projects/...` | 500 GB per project | 2.5 TB per PI | Yes |
| CARC personal scratch (BeeGFS) | `/carc/scratch/users/{username}` | 100 GB per user | — | No |
| CARC project scratch (BeeGFS) | `/carc/scratch/projects/{PI username}/{name}` | 1 TB per project | 5 TB per PI | No |
| Easley personal scratch (IBM GPFS) | `/easley/scratch/users/{username}` | 1 TB per user | — | No |
| Easley project scratch (IBM GPFS) | `/easley/scratch/projects/{PI username}/{name}` | 5 TB per project | 25 TB per PI | No |

Run the `quotas` command to list your current quota usage and the storage
locations available to your account and projects.

## Easley scratch expiration

Easley scratch is intended only for active work. Files that have not been
accessed for 180 days are automatically deleted. This expiration policy
applies to both personal and project storage on Easley scratch. Deleted
scratch data cannot be restored from backup. Move data that must be retained
to Enterprise Project Storage or another appropriate long-term storage
location before the expiration period is reached.

!!! note "Hopper has no machine-local scratch"

    There is no `/hopper/scratch`. On Hopper your only scratch tier is
    center-wide `/carc/scratch` — a real asymmetry between the two
    clusters, not just a naming difference.

## Choosing a storage type

- Use your **home directory** for personal source code, scripts, documents,
  and other relatively small files that are difficult to reproduce.
- Use **Enterprise Project Storage** for project data that must be retained
  safely over the long term.
- Use **CARC or Easley scratch** for temporary data being actively processed
  or analyzed, especially data that can be regenerated. Move anything that
  must be retained to enterprise storage before deleting the scratch copy.
- For especially I/O-intensive work, a job can temporarily use the compute
  node's `/tmp` disk or `/dev/shm`. Both are cleared when the job ends, and
  `/dev/shm` consumes memory that would otherwise be available to the job.

Home, project, and scratch filesystems are shared resources. Poorly chosen
storage or inefficient I/O can affect other users as well as your own work.
For file-count quotas and related policy details, see
[Storage and compute usage policies](resource-limits.md).

## Finding your project space path

The project scratch paths in the storage-limits table use `{PI username}`
for the CARC username of the project's PI and `{name}` for the project space
name. Use the `quotas` command to list your current quota usage and storage
locations, and check
[ColdFront](https://coldfront.alliance.unm.edu){target=_blank} for the
project's allocation status. If a newly approved path does not exist yet,
provisioning may not have finished; email
[help@carc.unm.edu](mailto:help@carc.unm.edu) if you cannot find or access
the space.

## Example use of a node's hard drive

This Slurm script first copies an input file (large_input_data.dat) to the compute node, runs the calculation ("run_my_program"), and then copies all results back into the submission directory:

```bash
#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=1:00:00
#SBATCH --job-name=local_storage

# Define a directory on the node-local disk, create it once the job
# has started, move data there, then cd to it and run
TEMP_DIR=/tmp/$USER/$SLURM_JOB_ID
mkdir -p "$TEMP_DIR"
cp -r $SLURM_SUBMIT_DIR/large_input_data.dat "$TEMP_DIR"
cd $TEMP_DIR

# Now run my program
run_my_program

# The job has finished, so move data back to where it came from
cp -r $TEMP_DIR/* $SLURM_SUBMIT_DIR

# Finally clean up the temporary directory
rm -r $TEMP_DIR
```

## Video walkthrough

**Storage Systems** — from the [CARC video tutorials](../training/videos.md):

<iframe class="carc-video" src="https://www.youtube-nocookie.com/embed/WwsbLyl7d1A" title="Storage Systems" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<p class="carc-provenance" markdown>Originally migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/storage_and_backup.md){target=_blank}; paths, tiers, and retention reconciled 2026-09-01 against cluster state observed 2026-07-25 ([CARC knowledge store](https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store){target=_blank}). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
