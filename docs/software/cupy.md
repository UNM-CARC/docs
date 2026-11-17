---
title: "CuPy: NumPy on the GPU"
description: "Install CuPy on Easley with the CUDA 12 wheel, move NumPy code onto L40S and H100 GPUs, and see when the GPU is and isn't faster."
type: Guide
tags:
  - Python
  - GPU
  - CUDA
stale_after: "2027-08-31T00:00:00Z"
sources:
  - id: quickbytes-pr-261
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/261"
    title: "UNM-CARC QuickBytes PR #261: Refresh GPU benchmarks + add CuPy QuickByte (tested on Easley 2026-07-07)"
    author: "human:hfricke"
  - id: cs491-lecture-20
    resource: "https://fricke.co.uk/Teaching/CS491_591_HPC_2025_Fall/Lectures/Lecture_20-GPU_Computation.pdf"
    title: "UNM CS491/591 HPC, Lecture 20: GPU Computation"
    author: "human:gmfricke"
---

# CuPy: NumPy on the GPU

[CuPy](https://cupy.dev/){target=_blank} is a GPU array library that
implements almost all of the NumPy API and much of SciPy. A `cupy.ndarray`
lives in GPU memory and its operations run as CUDA kernels, so array-heavy
NumPy code can often move to the GPU with very few changes.

This page covers installing CuPy on Easley, basic use, and a CPU-versus-GPU
benchmark. Easley's GPU partitions are `l40s` (NVIDIA L40S) and `h100`
(NVIDIA H100); see the [systems overview](../systems/overview.md).

## Install CuPy

Create a conda environment (see [Conda environments](conda-environments.md)
for the basics):

```bash
module load miniconda3
conda create -n cupy_env python=3.11 -y
source activate cupy_env
```

Then install CuPy's CUDA 12 wheel with pip:

```bash
pip install "cupy-cuda12x[ctk]"
```

!!! warning "Don't install CuPy from conda-forge"
    `conda install -c conda-forge cupy` currently installs a build linked
    against CUDA 13, which needs a newer NVIDIA driver than Easley's GPU nodes
    have. The first GPU operation then fails with
    `cudaErrorInsufficientDriver: CUDA driver version is insufficient for CUDA runtime version`.
    The `cupy-cuda12x` wheel matches Easley's driver.

!!! note "Keep the `[ctk]` extra"
    Without `[ctk]`, CuPy imports and handles simple operations, but features
    that need other CUDA libraries fail. For example, `cupy.random` stops with
    `ImportError: Failure finding "libcurand.so.11 or libcurand.so.10"`. The
    extra installs the CUDA toolkit libraries and headers CuPy needs, so you
    don't need `module load cuda`.

## Basic use

Request a GPU and start Python in your environment:

```bash
srun --partition l40s --mem 16G --ntasks 1 --cpus-per-task 4 -G 1 --pty bash
module load miniconda3
source activate cupy_env
python3
```

```python
import numpy as np
import cupy as cp

a_cpu = np.array([1, 2, 3])
a_gpu = cp.array([1, 2, 3])
print(a_gpu)
print(type(a_gpu))
print(a_gpu.sum())
```

```text
[1 2 3]
<class 'cupy.ndarray'>
6
```

`a_gpu.sum()` runs as a CUDA kernel. To bring a result back into an ordinary
NumPy array, use `cp.asnumpy`:

```python
print(cp.asnumpy(a_gpu))
```

```text
[1 2 3]
```

Much NumPy code ports by swapping `import numpy as np` for
`import cupy as cp` and calling `cp.asnumpy()` on anything you need back on
the CPU, for example before plotting with Matplotlib, which doesn't accept
GPU arrays.

## CPU versus GPU benchmark

This script times matrix multiplication with NumPy on the CPU and CuPy on the
GPU at increasing sizes. CUDA calls return before the GPU finishes, so
`cp.cuda.Stream.null.synchronize()` makes the timer wait for the GPU.

Save it as `cupy_benchmark.py`:

```python
import time
import numpy as np
import cupy as cp

SIZES = [1000, 2000, 4000, 8000]

def bench_matmul_cpu(n):
    a = np.random.rand(n, n)
    b = np.random.rand(n, n)
    start = time.perf_counter()
    a @ b
    return time.perf_counter() - start

def bench_matmul_gpu(n):
    a = cp.random.rand(n, n)
    b = cp.random.rand(n, n)
    cp.cuda.Stream.null.synchronize()
    start = time.perf_counter()
    a @ b
    cp.cuda.Stream.null.synchronize()
    return time.perf_counter() - start

for n in SIZES:
    cpu_t = bench_matmul_cpu(n)
    gpu_t = bench_matmul_gpu(n)
    print(f"N={n}  CPU: {cpu_t:.4f}s  GPU: {gpu_t:.4f}s  speedup: {cpu_t / gpu_t:.1f}x")
```

Run it on the GPU node:

```bash
python cupy_benchmark.py
```

Output from one L40S on Easley:

```text
N=1000  CPU: 0.0560s  GPU: 0.9546s  speedup: 0.1x
N=2000  CPU: 0.0619s  GPU: 0.0141s  speedup: 4.4x
N=4000  CPU: 0.4587s  GPU: 0.1043s  speedup: 4.4x
N=8000  CPU: 3.5086s  GPU: 0.8313s  speedup: 4.2x
```

At N=1000 the GPU is slower. Every GPU operation pays a fixed cost for kernel
launch and memory allocation, and the first one in a program also loads the
CUDA math libraries. For small arrays that cost outweighs the GPU's speed, and
the N=1000 timing varies a lot from run to run. Where the crossover falls depends on the operation and the
hardware, but small workloads can run slower on a GPU, not faster.

## Going further: several GPUs with NCCL and MPI

Once code works on one GPU, you can spread it across several with
[NCCL](https://developer.nvidia.com/nccl){target=_blank} (NVIDIA Collective
Communication Library) and `mpi4py`. NCCL mirrors MPI's API (`ncclAllReduce`
for `MPI_Allreduce`, `ncclBroadcast` for `MPI_Bcast`) but works directly on
GPU memory. See also [CUDA-aware MPI](cuda-aware-mpi.md).

The [CS491/591 HPC course, Lecture 20: GPU Computation](https://fricke.co.uk/Teaching/CS491_591_HPC_2025_Fall/Lectures/Lecture_20-GPU_Computation.pdf){target=_blank}
walks through converting an MPI loop to CuPy and NCCL. One lesson from it: for
cheap per-element work, process the data in fixed-size batches rather than one
huge array per GPU. A single huge array runs out of GPU memory
(`cupy.cuda.memory.OutOfMemoryError`), and extra GPUs only pay off once the
problem is very large.

## Further reading

* [CuPy documentation](https://docs.cupy.dev/en/stable/){target=_blank}
* [CuPy and NumPy API comparison](https://docs.cupy.dev/en/stable/reference/comparison.html){target=_blank}
* [NCCL user guide](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/index.html){target=_blank}

*Every command and script on this page was tested on Easley on November 16, 2026.*

<p class="carc-provenance" markdown>Curated from [QuickBytes PR #261](https://github.com/UNM-CARC/QuickBytes/pull/261){target=_blank} (tested on Easley 2026-07-07). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
