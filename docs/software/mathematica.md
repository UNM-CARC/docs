---
title: "Mathematica on Easley"
description: "Derive exact beam-deflection formulas with Mathematica, then run the examples across CPUs, nodes, and a GPU on Easley."
type: Tutorial
tags:
  - Mathematica
  - Wolfram Language
  - Slurm
  - Easley
  - GPU
  - Scientific computing
generated:
  by: "process:codex"
  at: "2026-09-29T00:00:00Z"
---

# Mathematica on Easley

Mathematica combines symbolic mathematics with numerical computing. This
tutorial derives **exact beam-deflection formulas**, distributes the
derivations across CPUs and nodes, and evaluates many load combinations on a
GPU.

The distinguishing feature is the workflow: solve differential equations with
symbolic parameters, manipulate the resulting formulas, and then evaluate them
numerically in the same language. MATLAB, Julia, and R also have symbolic
tools; this example highlights Mathematica's built-in symbolic solver.

## Files and setup

Download [the complete example archive](../assets/files/mathematica/mathematica-examples.tar.gz),
extract it, and work in that directory on Easley. Keep it on a filesystem
accessible from compute nodes.

```bash
wget https://carc.unm.edu/docs/assets/files/mathematica/mathematica-examples.tar.gz
tar -xzf mathematica-examples.tar.gz
cd mathematica-examples
module load mathematica/15.0.1
chmod +x math-kernel.sh
```

The archive includes the three Slurm scripts, Wolfram Language inputs, and the
shared launcher. Run the jobs below one at a time.

The examples use `neutrino.phys.unm.edu`; please substitute the fully
qualified hostname of your Mathematica license server. The shared
`math-kernel.sh` launcher contains:

```bash
#!/bin/bash
# Use the same license server for the controller and every worker.
# Replace neutrino.phys.unm.edu with your license server's FQDN.
exec math -pwfile <(printf '!neutrino.phys.unm.edu\n') "$@"
```

The Bash inline file supplies the license information without creating a
persistent license file. `"$@"` forwards the kernel's arguments. Both the
controller and parallel workers use this launcher, so each gets the same
server. See Wolfram's [kernel documentation](https://reference.wolfram.com/language/ref/program/WolframKernel.html){target=_blank}
for `-pwfile` details.

## The example: derive a beam-deflection formula

For a simply supported beam, the small-deflection model is:

```text
rigidity × y''''(x) = load × (x/length)^n
```

Here, `y(x)` is downward deflection, `length` is the beam length, `load` is
the load-intensity scale, and `rigidity` is the flexural rigidity (`E × I`).
The ends have zero deflection and zero bending moment. Setting `n = 0` gives a
uniform load; `n = 1` gives a linearly increasing load.

The shared `beam-model.wl` input derives the formula without assigning
numerical values to these parameters:

```wolfram
(* Simply supported beam: load (x/length)^power, constant flexural rigidity. *)
Clear[beamDeflection, x, length, load, rigidity];
beamDeflection[power_Integer] := Module[{y},
    Factor[DSolveValue[{
        rigidity y''''[x] == load (x/length)^power,
        y[0] == 0, y[length] == 0,
        y''[0] == 0, y''[length] == 0
    }, y[x], x]]
];
```

`DSolveValue` solves the differential equation and its boundary conditions.
`Factor` simplifies the resulting polynomial. For a uniform load, the exact
midpoint deflection is:

```text
5 × load × length^4 / (384 × rigidity)
```

This formula describes a family of beams and loads rather than one numerical
case.

## Multiple CPUs on one node

`parallel.wl` launches two local workers and gives them the definition from
`beam-model.wl`. `ParallelTable` derives midpoint formulas for load powers 0,
1, 2, and 3. It also prints each worker's hostname and license server.

```wolfram title="parallel.wl"
workers = ToExpression[Environment["SLURM_CPUS_PER_TASK"]] - 1;
launcher = FileNameJoin[{Directory[], "math-kernel.sh"}];

LaunchKernels[KernelConfiguration["Local",
    "KernelCommand" -> ("\"" <> launcher <> "\""),
    "KernelCount" -> workers]];
If[Length[Kernels[]] != workers, Print["Worker launch failed"]; Exit[1]];

Print["Workers: ", ParallelEvaluate[{$KernelID, $MachineName}]];
Print["Worker license servers: ", ParallelEvaluate[$LicenseServer]];
Get["beam-model.wl"];
DistributeDefinitions[beamDeflection];
midpoints = ParallelTable[
    Factor[beamDeflection[n] /. x -> length/2], {n, 0, 3}];
Print["Midpoint formulas (load powers 0 through 3): ",
    ToString[midpoints, InputForm]];
CloseKernels[];
Exit[];
```

`mathematica_multicpu.sbatch` contains:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-multicpu
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=3
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=%x-%j.out

module load mathematica/15.0.1
cd "$SLURM_SUBMIT_DIR"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

srun ./math-kernel.sh -script parallel.wl
```

Submit it with:

```bash
sbatch mathematica_multicpu.sbatch
```

Three CPUs provide one for the controller and two for workers. The thread
settings limit each worker's math libraries to one thread. To request more
workers, increase `--cpus-per-task`; the input reserves one CPU for the
controller. Available licenses also limit the worker count.

The output includes two workers on the same node and these four exact formulas:

```text
{5 load length^4/(384 rigidity),
 5 load length^4/(768 rigidity),
 89 load length^4/(23040 rigidity),
 13 load length^4/(5120 rigidity)}
```

## Multiple nodes

`distributed.wl` performs the same four derivations with one worker on each
of two nodes. It uses Slurm to start the workers and Mathematica's WSTP
protocol to connect them to the controller.

```wolfram title="distributed.wl"
nodes = StringSplit[RunProcess[
    {"scontrol", "show", "hostnames", Environment["SLURM_JOB_NODELIST"]},
    "StandardOutput"]];
launcher = FileNameJoin[{Directory[], "math-kernel.sh"}];

links = Table[LinkCreate[LinkProtocol -> "TCPIP"], {Length[nodes]}];
processes = Table[
    StartProcess[{
        "srun", "--exact", "--nodes=1", "--ntasks=1", "--cpus-per-task=1",
        "--nodelist=" <> nodes[[i]],
        "--output=worker-%j-%N.out", "--error=worker-%j-%N.err",
        launcher, "-subkernel", "-noinit", "-wstp",
        "-linkmode", "Connect", "-linkprotocol", "TCPIP",
        "-linkname", First[links[[i]]]
    }],
    {i, Length[nodes]}
];

TimeConstrained[LaunchKernels[links], 90, Exit[1]];
If[Length[Kernels[]] != Length[nodes], Exit[1]];

Print["Workers: ", ParallelEvaluate[{$KernelID, $MachineName}]];
Print["Worker license servers: ", ParallelEvaluate[$LicenseServer]];
Get["beam-model.wl"];
DistributeDefinitions[beamDeflection];
midpoints = ParallelTable[
    Factor[beamDeflection[n] /. x -> length/2], {n, 0, 3}];
Print["Midpoint formulas (load powers 0 through 3): ",
    ToString[midpoints, InputForm]];

Scan[LinkWrite[#, Unevaluated[EvaluatePacket[Quit[0]]]] &, links];
TimeConstrained[
    While[AnyTrue[processes, ProcessStatus[#] === "Running" &], Pause[0.1]],
    20, Exit[1]
];
codes = ProcessInformation[#, "ExitCode"] & /@ processes;
CloseKernels[];
If[codes =!= ConstantArray[0, Length[nodes]], Exit[1]];
Exit[];
```

`mathematica_multinode.sbatch` contains:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-multinode
#SBATCH --partition=debug
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=%x-%j.out

module load mathematica/15.0.1
cd "$SLURM_SUBMIT_DIR"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

./math-kernel.sh -script distributed.wl
```

Submit it with:

```bash
sbatch mathematica_multinode.sbatch
```

The controller runs directly in the batch step. The input starts separate
`srun` steps for its workers; adding `srun` in front of the controller would
start duplicate controllers. Each worker uses the same shared license launcher.

Expect the same formulas as above, but worker hostnames on **two different
nodes**. Worker messages are saved in `worker-*.out` and `worker-*.err`. The
input includes a connection timeout and closes workers before exiting.

## GPU evaluation

The GPU example uses the symbolic formulas as input to a numerical calculation.
It does not run the symbolic differential-equation solver on the GPU.

`gpu.wl` derives four beam-response formulas on the CPU. It sets `length =
load = rigidity = 1` to obtain normalized response shapes, samples them at 256
positions, and combines them using 1,024 sets of load coefficients:

```wolfram
gpuResult = CUDADot[shapeMatrix, coefficients];
```

This GPU matrix multiplication produces deflection at every position for every
load combination. Superposition applies because the beam equation is linear.
The example compares the GPU result with a CPU multiplication and prints the
maximum difference. See Wolfram's [CUDADot documentation](https://reference.wolfram.com/language/CUDALink/ref/CUDADot.html){target=_blank}.

```wolfram title="gpu.wl"
Get["beam-model.wl"];
Needs["CUDALink`"];
If[!TrueQ[CUDAQ[]], Print["CUDA unavailable"]; Exit[1]];

(* Derive exact responses for four polynomial loads, then normalize the units. *)
shapes = Table[
    beamDeflection[n] /. {length -> 1, load -> 1, rigidity -> 1},
    {n, 0, 3}
];
Print["Uniform-load formula: ", ToString[shapes[[1]], InputForm]];

(* Evaluate at 256 positions for 1024 combinations of the four loads. *)
positions = N[Subdivide[0, 1, 255]];
shapeMatrix = Table[shapes /. x -> position, {position, positions}];
coefficients = N[Table[Sin[i j/100], {i, 1, 4}, {j, 1, 1024}]];

gpuResult = CUDADot[shapeMatrix, coefficients];
difference = Max[Abs[Flatten[gpuResult - shapeMatrix.coefficients]]];
Print["License server: ", $LicenseServer];
Print["Result dimensions: ", Dimensions[gpuResult]];
Print["Maximum difference from CPU: ", difference];
If[difference > 10^-10, Exit[1]];
Exit[];
```

`mathematica_gpu.sbatch` contains:

```bash
#!/bin/bash -l
#SBATCH --job-name=mathematica-gpu
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --gpus-per-node=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=%x-%j.out

module load mathematica/15.0.1
cd "$SLURM_SUBMIT_DIR"

srun ./math-kernel.sh -script gpu.wl
```

Submit it with:

```bash
sbatch mathematica_gpu.sbatch
```

Expect result dimensions `{256, 1024}` and a maximum CPU/GPU difference close
to zero. Small floating-point differences are normal. This example checks the
CPU-to-GPU workflow; a small workload may be faster on the CPU.

On first use, CUDALink may download supporting software into your Wolfram
cache, which can add startup time.

## Read the results

`sbatch` prints the job number. Check progress with:

```bash
squeue --me
```

Each job writes `mathematica-<mode>-<jobid>.out` in the submission directory.
For example:

```bash
cat mathematica-multicpu-1235085.out
```

Use your own job number. If a job reports `No valid password found`, check the
hostname in `math-kernel.sh` and license availability. If a two-node debug job
is pending with `QOSMaxNodePerUserLimit`, let your other debug jobs finish.

## Further reading

- [Wolfram Language](https://reference.wolfram.com/language/){target=_blank}
- [Parallel kernel configuration](https://reference.wolfram.com/language/ref/KernelConfiguration.html){target=_blank}
- [CUDALink](https://reference.wolfram.com/language/CUDALink/tutorial/Overview.html){target=_blank}
- [Introduction to Slurm](../running-jobs/slurm-intro.md)
