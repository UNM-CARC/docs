---
title: "Mathematica on Easley"
description: "Run Mathematica and WolframScript on Easley with interactive, serial, multicore, multinode, GPU, and license-server examples."
type: Tutorial
tags:
  - Mathematica
  - Wolfram Language
  - Slurm
  - Easley
  - GPU
generated:
  by: "process:codex"
  at: "2026-09-29T00:00:00Z"
sources:
  - id: quickbytes-mathematica
    resource: "https://github.com/Graviton28/QuickBytes/blob/741cae96b802cd8eab828869b9334668cb185810/mathematica_easley.md"
    title: "Graviton28 QuickBytes: mathematica_easley.md"
    author: "Graviton28"
    last_modified: "2026-09-24T22:48:46Z"
---

# Mathematica on Easley

Mathematica is a symbolic and numerical computing system built on the Wolfram Language. It can do algebra, calculus, linear algebra, statistics, optimization, and plotting in one environment, and it gives exact symbolic answers (like `x/2 - Sin[2x]/4`) as well as floating-point ones.

If you are unfamiliar with Mathematica, see the Wolfram [Mathematica page](https://www.wolfram.com/mathematica/){target=_blank} for more information. This tutorial assumes you can log in to Easley and submit [Slurm jobs](../running-jobs/slurm-intro.md), but have not used Mathematica on a cluster before. On Easley you use Mathematica through `wolframscript`, the command-line interface. There is no notebook window. You give it Wolfram Language code, run it in a Slurm job, and read the text it prints.

---

## Step 1: Load the module

```bash
module avail mathematica
```

```text
----------------------------- /opt/local/modules ------------------------------
   mathematica/15.0.1
```

```bash
module load mathematica
which wolframscript
```

```text
/opt/local/mathematica/15.0.1/Executables/wolframscript
```

Like other CARC software, run Mathematica inside a Slurm job (interactive or batch), not on the login node.

---

## Step 2: Try it interactively

Ask Slurm for a compute node first:

```bash
salloc --nodes=1 --ntasks=1 --cpus-per-task=4 --mem=8G --time=00:30:00 --partition=general
module load mathematica
```

`wolframscript -code` evaluates one expression and prints the result:

```bash
wolframscript -code 'Integrate[Sin[x]^2, x]'
```

```text
x/2 - Sin[2*x]/4
```

If your code uses `Print`, `-code` still prints the value of the *last* expression afterward, which is `Null`:

```bash
wolframscript -code 'Print[2^100]'
```

```text
1267650600228229401496703205376
Null
```

The `Null` is harmless. To suppress it, end your code with `Exit[]`:

```bash
wolframscript -code 'Print[2^100]; Exit[]'
```

```text
1267650600228229401496703205376
```

The job scripts below end their code with `Exit[]` for this reason.

Running `wolframscript` with no arguments starts an interactive session. Type expressions at the `In[n]:=` prompt and use `Quit[]` to leave:

```bash
wolframscript
```

```text
Wolfram 15.0.1 Kernel for Linux x86 (64-bit)
Copyright 1988-2026 Wolfram Research, Inc.

In[1]:= 2+2

Out[1]= 4

In[2]:= Print[Prime[100]]
541

In[3]:= Quit[]
```

Exit your interactive allocation when you're done:

```bash
exit
```

---

## Step 3: A serial job

For real work, submit a batch job. This first one uses a single CPU. Save it as `mathematica_serial.sbatch`:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-serial
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
module load mathematica

srun wolframscript -local -code '
Print["Factorization: ", Factor[x^4 - 1]];
Print["Integral: ", Integrate[x^2, {x, 0, 1}]];
Print["Linear solution: ", LinearSolve[{{2., 1.}, {1., 3.}}, {4., 7.}]];
Exit[]
'
```

The `-local` flag tells `wolframscript` to run the code on the local Wolfram Engine kernel on the compute node, and `-code` takes the Wolfram Language code between the single quotes. Here that code is three `Print` statements: a factorization, an integral, and a linear solve. Submit it:

```bash
sbatch mathematica_serial.sbatch
```

```text
Submitted batch job 1217741
```

You can watch it with `squeue --me`. Since the script doesn't set `--output`, Slurm writes the results to `slurm-<jobid>.out` in the directory you submitted from:

```bash
cat slurm-1217741.out
```

```text
Job 1217741 running on easley046
Factorization: (-1 + x)*(1 + x)*(1 + x^2)
Integral: 1/3
Linear solution: {1., 2.}
```

The factorization and the integral are exact (`1/3`). The linear solve is floating point because the matrix is written with decimal points (`2.`, `1.`).

---

## Step 4: Multiple CPUs on one node

Mathematica can run extra worker kernels alongside your main (controlling) kernel and spread work across them with functions like `ParallelTable` and `ParallelEvaluate`. Save this as `mathematica_multicpu.sbatch`:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-multicpu
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=3
#SBATCH --mem=4G
#SBATCH --time=00:05:00

module load mathematica
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

srun wolframscript -local -code '
kernel = FileNameJoin[{$InstallationDirectory, "SystemFiles", "Kernel",
    "Binaries", $SystemID, "WolframKernel"}];
workers = ToExpression[Environment["SLURM_CPUS_PER_TASK"]] - 1;

LaunchKernels[KernelConfiguration["Local",
    "KernelCommand" -> kernel, "KernelCount" -> workers]];
If[Length[Kernels[]] != workers, Print["Worker launch failed"]; Exit[1]];

Print["Workers: ", ParallelEvaluate[{$KernelID, $MachineName}]];
Print["Primes: ", ParallelTable[Prime[i], {i, 1, 20}]];
CloseKernels[];
Exit[]
'
```

Three CPUs give room for the controlling kernel plus two workers, which is why the script sets `workers` to `SLURM_CPUS_PER_TASK - 1`. It points `LaunchKernels` at the `WolframKernel` binary explicitly, so it doesn't depend on Mathematica's default parallel launcher, and it exits with an error message if the workers fail to start. The `export` line keeps math libraries to one thread each so the kernels don't compete for the same cores.

```bash
sbatch mathematica_multicpu.sbatch
```

```text
Submitted batch job 1217742
```

```bash
cat slurm-1217742.out
```

```text
Job 1217742 running on easley046
Workers: {{1, easley046}, {2, easley046}}
Primes: {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71}
```

Two workers (kernel IDs 1 and 2) both report the same machine. To use more cores, raise `--cpus-per-task`; the script always leaves one CPU for the controller.

---

## Step 5: Multiple nodes

To go beyond one node, the controller runs in the batch step and Slurm `srun` steps start one worker kernel on each allocated node. The workers talk to the controller over the network using Mathematica's WSTP protocol, so no SSH is needed. Save this as `mathematica_multinode.sbatch`:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-multinode
#SBATCH --partition=debug
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00

module load mathematica
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

wolframscript -local -code '
nodes = StringSplit[RunProcess[
    {"scontrol", "show", "hostnames", Environment["SLURM_JOB_NODELIST"]},
    "StandardOutput"]];
kernel = FileNameJoin[{$InstallationDirectory, "SystemFiles", "Kernel",
    "Binaries", $SystemID, "WolframKernel"}];

links = Table[LinkCreate[LinkProtocol -> "TCPIP"], {Length[nodes]}];
processes = Table[
    StartProcess[{
        "srun", "--exact", "--nodes=1", "--ntasks=1", "--cpus-per-task=1",
        "--nodelist=" <> nodes[[i]],
        "--output=worker-%j-%N.out", "--error=worker-%j-%N.err",
        kernel, "-subkernel", "-noinit", "-wstp",
        "-linkmode", "Connect", "-linkprotocol", "TCPIP",
        "-linkname", First[links[[i]]]
    }],
    {i, Length[nodes]}
];

TimeConstrained[LaunchKernels[links], 90, Exit[1]];
If[Length[Kernels[]] != Length[nodes], Exit[1]];

Print["Workers: ", ParallelEvaluate[{$KernelID, $MachineName}]];
Print["Primes: ", ParallelTable[Prime[i], {i, 1, 20}]];

Scan[LinkWrite[#, Unevaluated[EvaluatePacket[Quit[0]]]] &, links];
TimeConstrained[
    While[AnyTrue[processes, ProcessStatus[#] === "Running" &], Pause[0.1]],
    20, Exit[1]
];
codes = ProcessInformation[#, "ExitCode"] & /@ processes;
CloseKernels[];
If[codes =!= ConstantArray[0, Length[nodes]], Exit[1]];
Exit[]
'
```

What the script does, step by step:

1. Asks Slurm for the names of the allocated nodes (`scontrol show hostnames`).
2. Creates one network link per node, then uses `srun --nodelist=...` to start a `WolframKernel` worker on each node, telling it to connect back to its link.
3. Gives the workers 90 seconds to connect, then checks that every node has a worker.
4. Runs the same `ParallelEvaluate` and `ParallelTable` as before, now across nodes.
5. Shuts the workers down cleanly and checks their exit codes, so Slurm records them as successful.

Each worker's own messages go to `worker-<jobid>-<node>.out` and `.err` files in the submit directory, which is the first place to look if a worker fails to start.

```bash
sbatch mathematica_multinode.sbatch
```

```text
Submitted batch job 1217744
```

```bash
cat slurm-1217744.out
```

```text
Workers: {{1, easley006}, {2, easley007}}
Primes: {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71}
```

The two workers report different machines (`easley006` and `easley007`), so the work runs on two nodes.

The `debug` partition allows each user at most 2 nodes at a time. If this job stays in `PENDING` with the reason `QOSMaxNodePerUserLimit`, wait for your other `debug` jobs to finish, or run the examples one at a time.

---

## Step 6: GPU jobs

Mathematica can run computations on an NVIDIA GPU through its CUDALink package. Save this as `mathematica_gpu.sbatch`:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-gpu
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
module load mathematica

srun wolframscript -local -code '
Needs["CUDALink`"];
If[!TrueQ[CUDAQ[]], Print["CUDA unavailable"]; Exit[1]];

a = N[Table[i + j, {i, 64}, {j, 64}]];
result = CUDADot[a, Transpose[a]];

Print["Result dimensions: ", Dimensions[result]];
Print["Maximum difference from CPU: ",
    Max[Abs[Flatten[result - a.Transpose[a]]]]];
Exit[]
'
```

`--gres=gpu:1` requests one GPU. The script loads CUDALink, stops with a message if no usable GPU is found, multiplies a 64x64 matrix by its transpose on the GPU with `CUDADot`, and compares the result against the same multiplication done on the CPU.

```bash
sbatch mathematica_gpu.sbatch
```

```text
Submitted batch job 1217745
```

```bash
cat slurm-1217745.out
```

```text
You have been allocated one or more GPUs.
Job 1217745 running on easley054
Result dimensions: {64, 64}
Maximum difference from CPU: 0.
```

A difference of `0.` means the GPU and CPU answers agree exactly.

---

## Step 7: Choosing a license server

If your group has access to more than one Mathematica license server, you can pick which one a job uses by writing a one-line license file and pointing the kernel at it with `-pwfile`:

```bash
export MMA_LICENSE_SERVER=<insert-license-server-here>

WK=/opt/local/mathematica/15.0.1/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel
echo "!$MMA_LICENSE_SERVER" > mathpass_choice

"$WK" -pwfile "$PWD/mathpass_choice" -noinit -run '
Print["Using license server: ", $LicenseServer];
Print["Max processes/subprocesses: ", {$MaxLicenseProcesses, $MaxLicenseSubprocesses}];
Print[Integrate[x^2, x]];
Exit[]
'
```

Replace `<insert-license-server-here>` with the hostname of the server you want, and `MMA_LICENSE_SERVER` becomes an ordinary variable you can set in your Slurm script, so different jobs (or different users) can point at different servers without anyone changing the shared install. `$LicenseServer` and `$MaxLicenseProcesses`/`$MaxLicenseSubprocesses` in the output confirm which server and limits you actually got.

---

## Further reading

- [Wolfram Language documentation](https://reference.wolfram.com/language/){target=_blank}
- [Parallel computing in Mathematica](https://reference.wolfram.com/language/ParallelTools/tutorial/Overview.html){target=_blank}
- [CUDALink (GPU computing)](https://reference.wolfram.com/language/CUDALink/tutorial/Overview.html){target=_blank}
- [WolframScript](https://reference.wolfram.com/language/ref/program/wolframscript.html){target=_blank}
- Slurm on Easley: [Introduction to Slurm](../running-jobs/slurm-intro.md) and [Example Slurm scripts](../running-jobs/example-slurm-scripts.md)

<p class="carc-provenance" markdown>Curated from [Graviton28 QuickBytes: mathematica_easley.md](https://github.com/Graviton28/QuickBytes/blob/741cae96b802cd8eab828869b9334668cb185810/mathematica_easley.md){target=_blank}.</p>
