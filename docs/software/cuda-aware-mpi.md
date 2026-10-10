---
title: "CUDA-aware MPI"
description: "Pass GPU device pointers directly to MPI calls with the CUDA-aware OpenMPI/UCX stack, and fix the mixed-environment segfault."
type: Guide
tags:
  - MPI
  - GPU
  - CUDA
generated:
  by: "claude/fable-5"
  at: "2026-09-01T00:00:00Z"
sources:
  - id: knowledge-store
    resource: "https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store"
    title: "CARC knowledge store: kb/ticket-solutions/fix-cuda-aware-mpi-segfault.md (staff-reviewed, fix confirmed by the reporting user)"
    author: "team:unm-carc"
    last_modified: "2026-07-25T00:00:00Z"
---

# CUDA-aware MPI

CARC provides a CUDA-aware OpenMPI build with a matching UCX (including the
`cuda_copy`/`cuda_ipc` transports), so multi-GPU MPI codes can pass **device
(GPU) pointers directly** to `MPI_Send`/`MPI_Recv` and friends — no staging
copy through host memory required.

## The symptom: device-pointer MPI segfaults

Your OpenMPI reports CUDA support, but calling `MPI_Send`/`MPI_Recv` on a
device pointer crashes with a segmentation fault. The common workaround —
an extra `cudaMemcpy` to a host staging buffer before each MPI call — works
but costs performance and a code change you shouldn't need.

This is usually an **environment problem, not a missing feature**.

## 1. Confirm the CUDA-aware stack exists

Check the module listing for the OpenMPI and UCX versions built against
CUDA:

```bash
module spider openmpi
module spider ucx
```

Look for an OpenMPI/UCX pair built with CUDA support and load them
together. (See [environment modules](../running-jobs/modules.md) for module
basics.)

## 2. Fix the usual cause: a mixed runtime environment

The segfault is most often caused by an unrelated OpenMPI or UCX install
appearing earlier in `PATH`/`LD_LIBRARY_PATH` and shadowing the CUDA-aware
stack — for example one pulled in by a conda environment or a personal
install. Explicitly put the matched UCX ahead of everything else, loaded
together with the matching OpenMPI module:

```bash
export UCX_HOME=<path to the CUDA-aware UCX install>
export PATH=$UCX_HOME/bin:$PATH
export LD_LIBRARY_PATH=$UCX_HOME/lib:$UCX_HOME/lib/ucx:$LD_LIBRARY_PATH
```

## 3. Verify

Re-run with direct device-pointer `MPI_Send`/`MPI_Recv` calls — with no
`cudaMemcpy` staging workaround — and confirm the segfault is gone.

## Still segfaulting?

If the crash continues after you've confirmed that a single, matched
OpenMPI/UCX stack is loaded (no environment mixing), it may be an
application-side pointer bug or a genuine gap in the CUDA-aware build —
[open a ticket](../support/help.md) with your module list, the exact MPI
call, and the backtrace.

<p class="carc-provenance" markdown>Distilled from a staff-reviewed, user-confirmed support-ticket resolution in the [CARC knowledge store](https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store){target=_blank}. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
