---
title: "Storage and compute usage policies"
description: "Storage quotas, per-cluster partition and walltime limits, Slurm fairshare policy, and the job time-limit extension policy."
type: Policy
tags:
  - Policy
  - Storage
  - Slurm
stale_after: "2027-08-31T00:00:00Z"
generated:
  by: "claude/fable-5"
  at: "2026-09-01T00:00:00Z"
sources:
  - id: webinfo
    resource: "https://github.com/UNM-CARC/webinfo/blob/master/resource_limits.md"
    title: "UNM-CARC webinfo: resource_limits.md"
    author: "team:unm-carc"
    last_modified: "2023-04-21T16:04:29-06:00"
  - id: knowledge-store
    resource: "https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store"
    title: "CARC knowledge store: kb/facts/easley.md, kb/facts/hopper.md, kb/policies/job-time-limit-extension-policy.md"
    author: "team:unm-carc"
    last_modified: "2026-07-25T00:00:00Z"
---

# Storage and compute usage policies

The partition limits and quota numbers on this page reflect direct
observation of the clusters on 2026-07-25. On the clusters themselves,
`sinfo`, `scontrol show partition <name>`, and `quotas` always show the
current values.

## Storage quotas

| Storage tier | Path | Size quota | File-count quota | Available on | Backed up |
| ------------ | ---- | ---------- | ---------------- | ------------ | --------- |
| Home | `/users/<username>` | 100 GB soft / 200 GB hard | — | both clusters | yes |
| Project storage | `/projects/...` | 250 GB default allocation | — | both clusters | yes |
| Center-wide user scratch | `/carc/scratch/users/<username>` | 100 GB | 22,460 (soft) | both clusters | no |
| Center-wide project scratch | `/carc/scratch/projects/...` | 1 TB | 625,000 | both clusters | no |
| Easley-local user scratch | `/easley/scratch/users/<username>` | 1 TB | 100,000 soft / 120,000 hard | Easley only | no |
| Easley-local project scratch | `/easley/scratch/projects/...` | 5 TB soft / 6 TB hard | 500,000 soft / 600,000 hard | Easley only | no |

Once you exceed a soft limit we will ask you to reduce your usage; you
cannot write beyond a hard limit. Note that the file-count limits are
real quotas too — millions of tiny files will hit them long before the
byte quota. Hopper has no machine-local scratch tier; see
[storage and backups](storage.md) for the full layout, and files on
Easley-local scratch are deleted automatically after 180 days without
access. To purchase additional storage please see our
[pricing spreadsheet](https://carc.unm.edu/research/premium-research-computing-services.html){target=_blank}.

The `quotas` command shows your quota usage. The number in an automated
quota warning email covers only one group — you can be near your
personal limit while project groups you belong to have plenty of room,
and vice versa — so check the full `quotas` breakdown before deleting
data. If the reported usage doesn't match any files you can actually
find, see [troubleshooting](../faq/troubleshooting.md#disk-quota-exceeded)
before deleting anything else.

## Compute usage policy

To ensure that all research and class projects get their fair share of the clusters and to prevent any one group from using a disproportionate amount of resources, we utilize Slurm’s built-in job accounting and fairshare system.
The cluster is a limited resource and Fairshare allows us to ensure everyone gets a fair opportunity to use it regardless of how big or small the group is.
Your compute resource allocation is shared among everyone in the slurm account you select.

For more on Slurm accounts see [Slurm accounting](../running-jobs/slurm-accounting.md).
Note that your slurm account is not the same as your CARC login account.

To see the predicted start time of your job based on your fairshare score, use the following command:
`squeue --start --job <job_id>`

## Partition limits

### Easley

| Partition | Max walltime | Notes |
| --------- | ------------ | ----- |
| general (default) | 2 days | Community CPU partition |
| bigmem | 2 days | Two large-memory nodes (~2 TB RAM each) |
| h100 | 2 days | 2× NVIDIA H100 per node; [group-gated](../faq/troubleshooting.md#my-job-wont-start) |
| l40s | 2 days | 4× NVIDIA L40S per node; [group-gated](../faq/troubleshooting.md#my-job-wont-start) |
| interactive | 4 hours | Interactive sessions, elevated scheduling priority |
| debug | 1 hour | Short test jobs |
| scavenger | 2 days | Idle reserved nodes; jobs are preemptible |
| liulab | 7 days | Lab-restricted |

A job on `general` that does not request `--time` gets a **default of 8
hours**, not the maximum, and a job that does not request memory gets
`DefMemPerCPU` — about **3.7 GB per requested CPU** on `general`
(`bigmem` and the GPU partitions set their own, higher values). Check
`scontrol show partition <name>` for the partition you use.

### Hopper

| Partition | Max walltime | Notes |
| --------- | ------------ | ----- |
| general (default) | 2 days | 10 community CPU nodes |
| debug | 4 hours | 2 nodes; per-user QOS limits apply |
| condo | 2 days | Group-restricted mixed CPU/GPU (A100, V100) nodes |
| bugs, pcnc, pathogen, tc, gold, fishgen, neuro-hsc, pna, geodef, insar | 7 days | Lab-restricted |
| cup-ecs, tid, biocomp, chakra | 7 days | Lab-restricted, GPU (A100/V100) |
| quark, toadpole | 10 days | Lab-restricted, GPU (A100) |

Hopper's `general` partition uses `DefMemPerCPU=2938` (about **2.9 GB
per requested CPU** when `--mem` is unset). Access to the condo and lab
partitions is restricted to their owning groups — check with your PI if
you expect access to one.

## Job time limits and extensions

Walltime limits vary **partition by partition on both clusters** — from
1 hour on Easley's `debug` to 10 days on some Hopper lab partitions —
so never assume a blanket 48-hour limit; check your partition's limit in
the tables above or with `scontrol show partition <name>`.

If a specific, already-running job needs more time than you requested:

- **One-time courtesy extension** — [open a ticket](../support/help.md)
  with the job ID(s); support staff may extend a specific running job as
  a one-off courtesy.
- **Permanent or repeated increases** — changing a user's or project's
  runtime limits, or extending jobs as a pattern rather than a one-off,
  requires a written proposal justifying the increase, reviewed by the
  CARC director. Shared partitions keep their default limits to stay
  fair across all users, so anything beyond a single courtesy extension
  goes through the same justification-and-review process as any other
  allocation change.

<p class="carc-provenance" markdown>Originally migrated from [UNM-CARC webinfo](https://github.com/UNM-CARC/webinfo/blob/master/resource_limits.md){target=_blank}; partition tables, quotas, and the extension policy reconciled 2026-09-01 against cluster state observed 2026-07-25 ([CARC knowledge store](https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store){target=_blank}). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
