---
title: "MATLAB on GPUs"
description: "Accelerate MATLAB computations with the L40S and H100 GPUs on Easley, interactively or in Slurm batch jobs, on one GPU or several."
type: Guide
tags:
  - MATLAB
  - GPU
stale_after: "2027-08-31T00:00:00Z"
sources:
  - id: quickbytes-pr-276
    resource: "https://github.com/UNM-CARC/QuickBytes/pull/276"
    title: "UNM-CARC QuickBytes PR #276: Using GPUs on Easley with MATLAB.md (tested on Easley)"
    author: "human:hfricke"
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/Using%20GPUs%20on%20Xena%20with%20MATLAB.md"
    title: "UNM-CARC QuickBytes: Using GPUs on Xena with MATLAB.md"
    author: "team:unm-carc"
    last_modified: "2022-05-25T09:46:08-06:00"
---

# MATLAB on GPUs

MATLAB's Parallel Computing Toolbox can run array operations on a GPU. On CARC,
the GPU nodes are on [Easley](../systems/overview.md): the `l40s` partition
(NVIDIA L40S) and the `h100` partition (NVIDIA H100). Request GPUs with
`--gres=gpu:<type>:<count>`, for example `--gres=gpu:l40s:1`.

This page covers using a single GPU interactively, running the same work as a
Slurm batch job, and spreading work across several GPUs on one node.

## Using a single GPU

### Start MATLAB on a GPU node

Request an interactive session with one GPU:

```bash
easley-sn:~$ srun --partition l40s --gres=gpu:l40s:1 --pty bash
```

Once a node is allocated, load MATLAB and start it:

```bash
easley055:~$ module load matlab/R2024b
easley055:~$ matlab
```

### Identify and select the GPU

Check how many GPUs MATLAB can see:

```matlab
>> gpuDeviceCount("available")

ans =

     1
```

This means you have access to a single GPU. To see its details, run:

```matlab
>> gpuDeviceTable

ans =

  1x5 table

    Index        Name         ComputeCapability    DeviceAvailable    DeviceSelected
    _____    _____________    _________________    _______________    ______________

      1      "NVIDIA L40S"          "8.9"               true              false
```

You can tell MATLAB which GPU to use by passing its index from that table. If
you don't, MATLAB uses the lowest-numbered GPU the first time you need one.

```matlab
>> gpuDevice(1)
```

MATLAB prints the selected GPU's properties, including its name, memory, and
compute capability. Running `gpuDeviceTable` again shows `DeviceSelected` is
now `true`:

```matlab
>> gpuDeviceTable

ans =

  1x5 table

    Index        Name         ComputeCapability    DeviceAvailable    DeviceSelected
    _____    _____________    _________________    _______________    ______________

      1      "NVIDIA L40S"          "8.9"               true              true
```

### Move arrays to and from the GPU

To use the GPU, data must be in a `gpuArray` object. See the
[MathWorks `gpuArray` documentation](https://www.mathworks.com/help/parallel-computing/gpuarray.html){target=_blank}
for the full reference.

Create an ordinary array (here an 8x8 magic square), then copy it to the GPU:

```matlab
>> A = magic(8);
>> B = gpuArray(A);
```

`isgpuarray` tells you where an array lives:

```matlab
>> isgpuarray(A)

ans =

  logical

   0

>> isgpuarray(B)

ans =

  logical

   1
```

To bring results back into the normal MATLAB workspace, for example before
saving them or using functions that don't support GPUs, use `gather`:

```matlab
>> C = gather(B);
>> isgpuarray(C)

ans =

  logical

   0
```

### Run functions on GPU arrays

`arrayfun` applies a function to every element of a `gpuArray` on the GPU, and
the result stays on the GPU:

```matlab
>> result = arrayfun(@sqrt, B);
>> isgpuarray(result)

ans =

  logical

   1
```

You can pass your own functions to `arrayfun` as well. MathWorks keeps a
[list of functions that support GPU arrays](https://www.mathworks.com/help/parallel-computing/gpuarray.html){target=_blank}.

## Run a GPU job with Slurm

Batch jobs avoid the mistakes that come with interactive work and free the GPU
as soon as your script finishes. This example times the same `sqrt` on the CPU
and on the GPU.

### MATLAB script

Save this as `gpu_matlab.m`. `tic` and `toc` time each version:

```matlab
gpuDevice(1);

A = magic(5000);
disp("sqrt of 5000x5000 matrix on cpu:")
tic
B = arrayfun(@sqrt, A);
toc
disp("sqrt of 5000x5000 matrix on gpu:")
C = gpuArray(magic(5000));
tic
D = arrayfun(@sqrt, C);
toc
```

### Slurm script

Save this as `gpu_matlab.sh`, replacing `<DIR>` with the directory that holds
`gpu_matlab.m`. It requests one L40S GPU, loads MATLAB, and runs the script,
writing MATLAB's output to `gpu_matlab.out`:

```bash
#!/bin/bash

#SBATCH --job-name gpu_matlab_job
#SBATCH --output gpu_matlab_job.out
#SBATCH --error gpu_matlab_job.err
#SBATCH --time 00:05:00
#SBATCH --partition l40s
#SBATCH --ntasks 1
#SBATCH --gres=gpu:l40s:1

cd <DIR>

module load matlab/R2024b
matlab -nodisplay -r gpu_matlab > gpu_matlab.out
```

### Submit the job

Submit from the Easley head node, then read the results when it finishes:

```bash
easley-sn:~$ sbatch gpu_matlab.sh
easley-sn:~$ cat gpu_matlab.out
```

After MATLAB's startup banner, `gpu_matlab.out` from a run on one L40S ends
with:

```text
sqrt of 5000x5000 matrix on cpu:
Elapsed time is 12.389680 seconds.
sqrt of 5000x5000 matrix on gpu:
Elapsed time is 0.381576 seconds.
```

Your times will vary a little from run to run.

## Using multiple GPUs on one node

Easley's `l40s` nodes have up to four L40S GPUs. MATLAB uses several GPUs the
same way it uses several CPUs: a `parpool` starts one worker per GPU, and each
worker picks up its own GPU when it works with `gpuArray` objects.

!!! note "Request one CPU per GPU"
    MATLAB uses a CPU to drive each GPU, so set `--cpus-per-task` to the same
    number as the GPU count in `--gres`. If the numbers don't match, MATLAB
    may not find or use all the GPUs you were given.

### MATLAB script

Save this as `gpu_logistic_map.m`. It builds a logistic map by iterating the
logistic equation over a set of random populations. The `parfor` loop splits
the simulations across one worker per GPU, the loop is timed, and the figure
is saved as `logistic_map.jpg`:

```matlab
N = 1000;
r = gpuArray.linspace(0,4,N);

numIterations = 1000;

numGPUs = gpuDeviceCount("available");
parpool(numGPUs);

numSimulations = 100;
X = zeros(numSimulations,N,'gpuArray');

disp("Timing execution of parfor loop:")

tic
parfor i=1:numSimulations
  X(i,:) = rand(1,N,'gpuArray');
  for n=1:numIterations
    X(i,:) = r.*X(i,:).*(1-X(i,:));
  end
end
toc

f = figure('visible','off');
plot(r,X,'.');
saveas(f,'logistic_map','jpg')

return
```

### Slurm script

Save this as `gpu_logistic_map.sh`, replacing `<DIR>` as before. It asks for
two L40S GPUs and two CPUs:

```bash
#!/bin/bash

#SBATCH --job-name gpu_logistic_map_job
#SBATCH --output gpu_logistic_map_job.out
#SBATCH --error gpu_logistic_map_job.err
#SBATCH --time 00:10:00
#SBATCH --partition l40s
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 2
#SBATCH --gres=gpu:l40s:2

cd <DIR>

module load matlab/R2024b
matlab -nodisplay -r gpu_logistic_map > gpu_logistic_map.out
```

### Submit the job

```bash
easley-sn:~$ sbatch gpu_logistic_map.sh
easley-sn:~$ cat gpu_logistic_map.out
```

After MATLAB's startup banner, `gpu_logistic_map.out` shows a pool with one
worker per GPU and the loop's run time:

```text
Starting parallel pool (parpool) using the 'Processes' profile ...
Connected to parallel pool with 2 workers.
Timing execution of parfor loop:
Elapsed time is 3.062344 seconds.
Parallel pool using the 'Processes' profile is shutting down.
```

When the job finishes, `logistic_map.jpg` is in the same directory. Copy it to
your computer or open it in [Open OnDemand](../interactive/open-ondemand.md) to
view it.

*Every command and script on this page was tested on Easley on November 16, 2026.*

<p class="carc-provenance" markdown>Curated from [QuickBytes PR #276](https://github.com/UNM-CARC/QuickBytes/pull/276){target=_blank} (tested on Easley) and the earlier [QuickByte](https://github.com/UNM-CARC/QuickBytes/blob/master/Using%20GPUs%20on%20Xena%20with%20MATLAB.md){target=_blank}. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/docs){target=_blank}.</p>
