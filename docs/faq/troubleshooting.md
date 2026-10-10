---
title: "Troubleshooting"
description: "Diagnose the most common problems: login failures, quota errors, pending or failing jobs, and module conflicts."
type: Guide
tags:
  - FAQ
  - Support
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: carc-web
    resource: "https://carc.unm.edu/index.html"
    title: "CARC website (carc.unm.edu)"
    author: "team:unm-carc"
---

# Troubleshooting

Work through the section that matches your symptom. If nothing here fixes it,
[open a ticket](../support/help.md) with the details listed at the bottom of
that page — cluster, job ID, exact command, and full error message.

## I can't log in

1. **Check for maintenance** on the
   [cluster status monitor](https://stats.uptimerobot.com/kqt0LYLwFd){ target=_blank }
   and [UNM IT alerts](https://italerts.unm.edu/){ target=_blank }.
2. **Password or OTP problems** — reset via the steps in
   [password reset](../getting-started/password-reset.md). A fresh reset can
   take a little while to propagate (try again shortly, or reset twice), and
   if one cluster works but the other doesn't, SSH to the broken one *from*
   the working cluster's login node while you sort it out.
3. **`Permission denied (publickey)`** — your SSH key setup is incomplete or
   has wrong permissions; see [SSH keys](../getting-started/ssh-keys.md)
   (`~/.ssh` must be `700`, private keys `600`).
4. **Account exists but no access** — you may not be on an active project
   yet; ask your PI to add you in ColdFront
   ([getting started](../getting-started/overview.md)).

## "Disk quota exceeded"

You've hit a storage limit ([what the limits are](../systems/resource-limits.md)):

```bash
quotas            # show your usage against each quota
du -sh ~/* | sort -rh | head   # find what's using home space
```

Clean up, move bulk data to scratch or project space
([storage layout](../systems/storage.md)), or talk to us about
[purchasing more](https://carc.unm.edu/research/premium-research-computing-services.html){ target=_blank }.
Remember conda environments and pip caches grow quietly — `conda clean --all`
and `pip cache purge` often free gigabytes.

Two quota surprises worth knowing:

* **Files in a project directory can still count against you** — quota is
  charged by *group ownership*, not location, so files you copied into a
  project space may still bill your personal quota; see
  [storage permissions](../systems/storage-permissions.md) for finding and
  fixing ownership.
* **The warning email covers only one group** — run `quotas` for the full
  per-tier breakdown before deleting anything. If the reported usage doesn't
  match any files you can actually find, the accounting itself may be stale —
  [open a ticket](../support/help.md) instead of deleting more data.

## My job won't start

```bash
squeue -u $USER           # state and reason code
squeue --start --job <id> # predicted start time (fairshare-aware)
sinfo                     # partition and node availability
```

Common reason codes:

| Reason | Meaning | What to do |
| ------ | ------- | ---------- |
| `Priority` | Others are ahead of you (fairshare) | Wait, or request fewer/shorter resources; see [fairshare](../running-jobs/slurm-accounting.md) |
| `Resources` | Not enough free nodes for your request | Reduce cores/memory/GPUs or choose another partition |
| `QOSMax*` / limits | You've hit a partition or account limit | Check [resource limits](../systems/resource-limits.md) |
| `ReqNodeNotAvail` | Nodes down or reserved (often maintenance) | Check the [cluster status monitor](https://stats.uptimerobot.com/kqt0LYLwFd){ target=_blank } |
| `InvalidAccount` | Wrong `--account` | List yours: `sacctmgr show assoc user=$USER format=account` |

**Rejected with `uid not in group permitted to use this partition`** — the
partition is group-gated (on Easley that includes the `h100` and `l40s` GPU
partitions). Access is provisioned through a **ColdFront allocation for that
specific partition, requested by your PI** — support cannot simply add you to
the group. If no allocation exists yet, ask your PI to submit one in
[ColdFront](https://coldfront.alliance.unm.edu){ target=_blank }; after
approval, allow some time for group membership to propagate to the cluster.
Need to run something right now? The `scavenger` partition doesn't have this
gate (jobs there are preemptible). If the error persists well after an
approved allocation, [open a ticket](../support/help.md) — that's a
provisioning problem, not a normal delay.

**Stuck in `CG` (completing)** — a few minutes in `CG` after a job finishes
is normal cleanup. If it persists, `scancel` will not clear it — the job is
stuck in Slurm's own cleanup, which needs admin action — so don't keep
retrying; [open a ticket](../support/help.md) with the job ID.

## My job failed or was killed

```bash
sacct -j <id> --format=JobID,State,ExitCode,Elapsed,MaxRSS,ReqMem
seff <id>     # efficiency summary after completion
```

* **`OUT_OF_MEMORY` / `oom-kill`** (often just a bare `Killed` from your
  program) — Slurm enforces the memory your **job requested**, not what the
  node has free, so a job on a shared node can be killed while the node
  itself shows plenty of RAM. If you never set `--mem`, the default is
  proportional to the CPUs you requested (`DefMemPerCPU` — ≈3.7 GB/CPU on
  Easley `general`, ≈2.9 GB/CPU on Hopper `general`), so a small
  `--cpus-per-task` silently caps memory. Resubmit with `--mem` (or
  `--mem-per-cpu`) sized to your data's actual working set — well above the
  raw data size for tools that process in memory. For variable workloads,
  run `seff` on a smaller successful run first to calibrate. If `seff`
  shows the state was **not** `OUT_OF_MEMORY`, or memory used was well
  under what you requested, more memory is not the fix — suspect an
  application bug and [open a ticket](../support/help.md).
* **`TIMEOUT`** — raise `--time` within partition limits, or checkpoint and
  restart.
* **Immediate crash** — check the job's `.out`/`.err` files in the submit
  directory; a missing `module load` or unactivated conda environment is the
  usual culprit ([modules](../running-jobs/modules.md),
  [conda](../software/conda-environments.md)).

## Software and environment problems

* **`command not found`** — load the module first (`module spider <name>`
  to find it; [modules guide](../running-jobs/modules.md)).
* **Python `ModuleNotFoundError` after `module load miniconda3`** — the
  module provides only conda's *base* environment, which doesn't include
  numpy, scipy, or other packages: create and activate your own
  [conda environment](../software/conda-environments.md). Old scripts that
  `module load anaconda3` must switch to `miniconda3` — that module is
  retired. Build environments from an interactive job, not a login node.
* **Conda is slow or conflicts** — prefer clean per-project environments and
  the conda-forge channel; see [channels and pip](../software/conda-channels-pip.md).
* **GPU code can't see the GPU** — did you request one in the job
  (`--gres=gpu:1` or the cluster's GPU partition)? Verify with `nvidia-smi`
  inside the job; see [example Slurm scripts](../running-jobs/example-slurm-scripts.md).
* **My kernel is missing in JupyterHub** — register your environment as a
  kernel: [conda in JupyterHub](../software/conda-jupyterhub.md).

## Graphics won't display

X11 applications need forwarding enabled — `ssh -Y` and a local X server;
see [X11 forwarding](../getting-started/x11-forwarding.md). For heavier
visualization, use [ParaView client–server](../software/paraview.md) or an
[Open OnDemand](../interactive/open-ondemand.md) session instead.

## Transfers are slow or failing

Use `rsync` with resume (`rsync -avP`) rather than `scp` for large trees,
and transfer to the right storage tier — see
[transferring data](../getting-started/transferring-data.md).

A large transfer that **repeatedly hangs or times out** usually points to
client-side network stability (wireless, VPN, off-campus path) rather than
CARC. Chunk it: loop over subdirectories with separate `rsync` calls instead
of one massive invocation — reruns resume where they left off. Still stuck?
[Open a ticket](../support/help.md) noting whether it dies at the same file
or at random, wired vs. wireless, and on- vs. off-campus; support can try
reproducing the transfer to rule out a CARC-side issue.

## Still stuck?

[Open a ticket](../support/help.md) or bring it to office hours — include
your cluster, job ID, command, and the complete error text.
