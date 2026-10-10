---
title: "Installing deep learning packages"
description: "Install GPU-enabled deep learning frameworks (PyTorch, TensorFlow) into conda environments."
type: Guide
tags:
  - Python
  - GPU
  - Machine learning
status: draft
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/Install%20deep%20learning%20packages.md"
    title: "UNM-CARC QuickBytes: Install deep learning packages.md"
    author: "team:unm-carc"
    last_modified: "2021-10-15T00:00:00Z"
---

# Installing deep learning packages

!!! note "Match builds to current GPUs"
    Choose framework builds that match the GPUs on the
    [current clusters](../systems/overview.md) (A100 on Hopper; L40S and
    H100 on Easley), and check exact package versions before installing.

This step-by-step guide walks through installing deep learning and machine
learning tools in a [conda environment](conda-intro.md) on CARC systems.

## Set up the conda environment

1. Load the conda module to get the `conda` command (the old `anaconda3`
   module has been retired — use `miniconda3`):

    ```bash
    module load miniconda3
    ```

2. Create a conda environment with a name:

    ```bash
    conda create --name <env_name> python==3.6
    ```

3. Verify the environment was created:

    ```bash
    conda info --envs
    ```

4. Activate the environment:

    ```bash
    source activate <env_name>
    ```

## Install deep learning packages

Install one or more of the following, as your work requires.

=== "TensorFlow (GPU)"

    ```bash
    conda install -c anaconda tensorflow-gpu
    ```

=== "Keras (GPU)"

    ```bash
    conda install -c anaconda keras-gpu
    ```

=== "PyTorch (CPU)"

    ```bash
    conda install pytorch torchvision -c pytorch
    ```

=== "PyTorch (GPU, K40 legacy)"

    First make sure Python 3.7 is installed in your current environment:

    ```bash
    conda create -n <env_name> python==3.7
    source activate <env_name>
    ```

    Then install the K40-compatible build that CARC staged in shared storage,
    plus the matching CUDA toolkit:

    ```bash
    conda install /projects/shared/pytorch/PyTorch1.5-K40-Compatible/pytorch-1.5.0-py3.7_cuda10.1.243_cudnn7.6.3_0.tar.bz2
    conda install cudatoolkit=10.1.243
    ```

## Verify GPU access from PyTorch

Run the following Python code on a GPU node (request one first — see
[example Slurm scripts](../running-jobs/example-slurm-scripts.md)):

```python
import torch
from torch import nn, tensor
from torch.cuda import device_count

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
x = torch.rand(5, 3)
print(x)
print("Is GPU Available?", torch.cuda.is_available(),
      " CUDA device count:", torch.cuda.device_count(),
      "current_device:", torch.cuda.current_device())
x = torch.tensor([1, 2, 3], device=device)
y = torch.tensor([1, 4, 9]).to(device)
print(x, y)
print(x + y)
```

Expected output:

```text
tensor([[0.3220, 0.2174, 0.1226],
        [0.7249, 0.8111, 0.8414],
        [0.5974, 0.5169, 0.5242],
        [0.1436, 0.5150, 0.5688],
        [0.3298, 0.1289, 0.5349]])
Is GPU Available? True  CUDA device count: 1  current_device: 0
tensor([1, 2, 3], device='cuda:0') tensor([1, 4, 9], device='cuda:0')
tensor([ 2,  6, 12], device='cuda:0')
```

## Additional machine learning packages

```bash
# OpenCV
conda install -c conda-forge opencv

# numpy, pandas, matplotlib, scikit-learn
conda install numpy pandas matplotlib scikit-learn
```

## Related pages

* [PyTorch on CARC GPUs](pytorch.md)
* [TensorFlow on CARC GPUs](tensorflow.md)
* [Conda channels and pip](conda-channels-pip.md)
* [Conda environments in JupyterHub](conda-jupyterhub.md)

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/Install%20deep%20learning%20packages.md){target=_blank} (last source update 2021-10-15), then restructured with fenced code blocks and curated in this repository. Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
