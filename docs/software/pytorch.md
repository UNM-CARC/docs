---
title: "PyTorch on CARC GPUs"
description: "Use CARC's shared PyTorch 2.5.1 conda environment on Easley's L40S and H100 GPUs from Slurm jobs or JupyterHub, or build your own environment."
type: Guide
tags:
  - Python
  - GPU
  - Machine learning
  - PyTorch
stale_after: "2027-08-31T00:00:00Z"
sources:
  - id: quickbytes-pr-275
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/275"
    title: "UNM-CARC QuickBytes PR #275: PyTorch on Easley (tested on Easley)"
    author: "human:hfricke"
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/PyTorch_1.9_Xena.md"
    title: "UNM-CARC QuickBytes: PyTorch_1.9_Xena.md"
    author: "team:unm-carc"
    last_modified: "2023-09-20T15:19:14-06:00"
---

# PyTorch on CARC GPUs

CARC maintains a shared, pre-built PyTorch conda environment on Easley, so most
users don't need to install PyTorch at all. This page shows how to use it from
a Slurm job and from JupyterHub, and how to build your own environment if you
need a different version.

Easley's GPU partitions are `l40s` (NVIDIA L40S) and `h100` (NVIDIA H100).
Request GPUs with `--gres=gpu:<type>:<count>`. See the
[systems overview](../systems/overview.md) for current hardware.

## Log in to Easley

```bash
ssh $USERNAME@easley.alliance.unm.edu
```

Replace `$USERNAME` with your CARC username. You won't see any characters
while you type your password. See [Logging in](../getting-started/logging-in.md)
if you have trouble connecting.

## Use the shared PyTorch environment

Load Miniconda and activate the shared environment:

```bash
module load miniconda3/latest
source activate /projects/shared/conda/envs/pytorch-2.5.1
```

Your prompt now shows the environment name:

```text
(pytorch-2.5.1) [username@easley ~]$
```

!!! note "Use `source activate`"
    Use `source activate` rather than `conda activate` in your shell and in
    Slurm scripts. `conda activate` needs shell initialization that isn't
    reliably set up on CARC nodes.

## Test PyTorch on a GPU

This Slurm script requests two L40S GPUs and prints how many GPUs PyTorch can
see. Save it as `gputest.sh`:

```bash
#!/bin/bash
#SBATCH --job-name gputest
#SBATCH --partition l40s
#SBATCH --gres=gpu:l40s:2
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --time 00:05:00
#SBATCH --output gputest.out
#SBATCH --error gputest.err

module load miniconda3/latest
source activate /projects/shared/conda/envs/pytorch-2.5.1
python3 -c "import torch; print(torch.cuda.device_count())"
```

Submit it:

```bash
sbatch gputest.sh
```

When it finishes, `gputest.out` contains:

```text
2
```

`gputest.err` holds a short notice from Miniconda about conda-forge licensing.
It appears every time the module loads and isn't an error.

## Use PyTorch in JupyterHub

1. Go to [easley.alliance.unm.edu/jupyter](https://easley.alliance.unm.edu/jupyter){target=_blank}
   and log in with your CARC username and password. See
   [JupyterHub](../interactive/jupyterhub.md) for more about CARC's
   JupyterHub.
2. If you are logged in without being asked to choose a server, open the
   **Control Panel** (upper right), click **Stop My Server**, then
   **Start Server**.
3. Choose a server option with a GPU: `8 hours, 16 cores, 55GB RAM, 1 L40s GPU`,
   `8 hours, 48 cores, 165GB RAM, 3 L40s GPU`, or
   `8 hours, 32 cores, 500GB RAM, 1 H100 GPU`.
4. Create a notebook with the **Python [conda env:conda-pytorch-2.5.1]**
   kernel and run:

    ```python
    import torch
    torch.cuda.device_count()
    ```

    The output is the number of GPUs in the option you chose: `1` for a
    1-GPU server, `3` for the 3-GPU server.

## Build your own environment

If you need a different PyTorch version, or packages the shared environment
doesn't have, create your own:

```bash
module load miniconda3/latest
conda create -n my-pytorch-env python=3.11 pytorch torchvision pytorch-cuda -c pytorch -c nvidia -y
source activate my-pytorch-env
```

This installs PyTorch 2.5.1 built for CUDA 12.4, which runs on Easley's GPUs.
To use it in JupyterHub, register it as a kernel as described in
[Conda environments in JupyterHub](conda-jupyterhub.md).

!!! warning "Don't `pip install torch` without choosing a CUDA version"
    A plain `pip install torch` currently installs a build for CUDA 13, which
    needs a newer NVIDIA driver than Easley has. It installs without complaint,
    but the first GPU operation fails with
    `RuntimeError: The NVIDIA driver on your system is too old (found version 12080)`.

??? tip "Optional: keep environments and package caches in your home directory"
    A `~/.condarc` file controls where conda puts environments and its package
    cache, and which channels it searches. To keep both under your home
    directory and prefer conda-forge, create `~/.condarc` with your preferred
    editor (for example `nano ~/.condarc`) containing the following, with
    `$USERNAME` replaced by your CARC username:

    ```yaml
    auto_activate_base: false
    channels:
      - conda-forge
      - defaults
    envs_dirs:
      - /users/$USERNAME/.conda/envs
    pkgs_dirs:
      - /users/$USERNAME/.conda/pkgs
    ```

    Check it with `cat ~/.condarc`. See
    [Conda channels and pip](conda-channels-pip.md) for more about channels.

*Every command and script on this page was tested on Easley on November 16, 2026.*

<p class="carc-provenance" markdown>Curated from [QuickBytes PR #275](https://github.com/UNM-CARC/QuickBytes/pull/275){target=_blank} (tested on Easley) and the earlier [QuickByte](https://github.com/UNM-CARC/QuickBytes/blob/master/PyTorch_1.9_Xena.md){target=_blank}. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
