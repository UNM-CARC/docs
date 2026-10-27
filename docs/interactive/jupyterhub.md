---
title: "JupyterHub"
description: "Run Jupyter notebooks on Hopper and Easley compute nodes through CARC JupyterHub."
type: Guide
tags:
  - Interactive
  - Jupyter
  - New users
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: carc-web
    resource: "https://carc.unm.edu/index.html"
    title: "CARC website (carc.unm.edu)"
    author: "team:unm-carc"
---

# JupyterHub

CARC runs JupyterHub portals that launch Jupyter notebook servers **on
cluster compute nodes**, so your notebooks have direct access to CARC
storage, modules, and hardware.

| Cluster | JupyterHub URL |
| ------- | -------------- |
| Hopper | [hopper.alliance.unm.edu](https://hopper.alliance.unm.edu){ target=_blank } |
| Easley | [easley.alliance.unm.edu/jupyter](https://easley.alliance.unm.edu/jupyter){ target=_blank } |

Log in with your CARC username and password. New here? Start with
[Getting started at CARC](../getting-started/overview.md).

## Starting a server

After login, JupyterHub asks for your session options (Slurm account,
resources, and duration — the exact form depends on the cluster). Your
notebook server is a [Slurm job](../running-jobs/slurm-intro.md) under the
hood, so:

* it may queue briefly until resources are available;
* it stops when its time limit is reached — save your notebooks;
* the resources you hold count against your project's
  [fairshare](../running-jobs/slurm-accounting.md), so stop your server
  (*File → Hub Control Panel → Stop My Server*) when you are done.

## Using your own environments as kernels

The default kernels cover common cases, but most research needs its own
packages. Create a [conda environment](../software/conda-environments.md) and
register it as a Jupyter kernel — the walkthrough is in
[Conda environments in JupyterHub](../software/conda-jupyterhub.md).

## Scaling beyond one node

Notebooks don't have to stay single-threaded:

* [Parallel Python with Dask and scikit-learn](../tutorials/dask-scikit-learn.md) -
  scale scikit-learn across cluster workers from a notebook.
* [MPI parallelization from JupyterHub](../tutorials/jupyterhub-mpi.md) - drive
  mpi4py/ipyparallel from a notebook session.
* For long or heavy computations, move to a
  [batch job](../running-jobs/example-slurm-scripts.md) — notebooks are for
  exploration, batch is for production runs.

## Related pages

* [Open OnDemand](open-ondemand.md) - browser access to files, shells, and other interactive apps.
* [Installing deep learning packages](../software/deep-learning-packages.md) - GPU-ready PyTorch/TensorFlow environments.
* [Getting help](../support/help.md) - stuck server or missing kernel? Open a ticket.
