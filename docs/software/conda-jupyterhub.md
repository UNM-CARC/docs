---
title: "Conda environments in JupyterHub"
description: "Make your conda environments available as kernels in CARC JupyterHub."
type: Guide
tags:
  - Python
  - Conda
  - Jupyter
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/Conda_JupyterHub.md"
    title: "UNM-CARC QuickBytes: Conda_JupyterHub.md"
    author: "team:unm-carc"
    last_modified: "2023-06-27T14:50:38-06:00"
---

# Conda environments in JupyterHub

Custom environments created by users can also be used on JupyterHub. This QuickByte shows you how to make python environments  accessible on JupyterHub. 

## In Terminal 

If you are creating a conda environment from scratch that you know you will want to use on JupyterHub, as you are creating the environment add the ipykernel to the packages you want included.

For example, if you were making a natural language processing libraries environment, you could create an environment like this:

``` 
module load miniconda3
conda create -n nltk nltk ipykernel
```

Alternatively, if you already have an environment created and would like it to be available on JupyterHub, then add the ipykernel. 

``` 
source activate nltk
conda install ipykernel
```

Remember that you can also access the terminal through JupyterHub. To do this click Terminal under the New dropdown menu. 

![term_Jup](../assets/images/quickbytes/JuphuB_terminal.png)

## On JupyterHub

After your environments have been modified to include the ipykernel, you can open notebooks on JupyterHub by opening a New Notebook under File and selecting the environment. 

![term_Jup](../assets/images/quickbytes/JupHub_envi.png)

*This quickbyte was validated on 7/30/2026*

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/Conda_JupyterHub.md){target=_blank} (last source update 2023-06-27). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
