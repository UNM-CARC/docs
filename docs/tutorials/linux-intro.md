---
title: "Introduction to Linux"
description: "A first tour of the Linux command line for new HPC users."
type: Tutorial
tags:
  - Linux
  - New users
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: quickbytes
    resource: "https://github.com/UNM-CARC/QuickBytes/blob/master/linux_intro.md"
    title: "UNM-CARC QuickBytes: linux_intro.md"
    author: "team:unm-carc"
    last_modified: "2026-06-17T13:42:20-06:00"
---

# Introduction to Linux

If you are new to the Unix/Linux command line, you are in the right place. Rather than duplicating the excellent training materials that already exist, this page points you to the best resources for getting started, then covers the CARC-specific context you need to use any of our clusters effectively.

## Start Here: Software Carpentry

[Software Carpentry](https://software-carpentry.org/lessons/){target=_blank} is a volunteer organization that develops and maintains free, peer-reviewed tutorials for computing skills used in research. Their materials are used by universities and research institutions worldwide and are specifically designed for researchers who are new to programming and the command line.

We strongly recommend working through their **Unix Shell** lesson before using Easley:

**[The Unix Shell — Software Carpentry](https://swcarpentry.github.io/shell-novice/){target=_blank}**

This lesson covers everything you need to get started, including navigating the filesystem, creating and editing files, working with directories, redirecting output, and writing shell scripts. It takes approximately 3–4 hours to complete and requires no prior experience.

Their full lesson catalog is available at [software-carpentry.org/lessons](https://software-carpentry.org/lessons/){target=_blank} and includes tutorials on Python, R, Git, and more — all highly relevant to HPC research workflows.

## Other Useful Resources for New Users

- **[explainshell.com](https://explainshell.com/){target=_blank}** — paste any shell command and get a plain-English explanation of each part. Extremely useful when you encounter an unfamiliar command.
- **[The Linux Command Line (free book)](https://linuxcommand.org/tlcl.php){target=_blank}** — a comprehensive introduction to the Linux shell, freely available online.
- **[Git and Version Control — Software Carpentry](https://swcarpentry.github.io/git-novice/){target=_blank}** — managing your code and scripts with Git is strongly recommended for any research computing work.
- **[Programming with Python — Software Carpentry](https://swcarpentry.github.io/python-novice-inflammation/){target=_blank}** — if you plan to use Python on Easley, this is a good starting point.
- **`man <command>`** — every CARC system has built-in manual pages for every command. For example, `man ls` explains every option available for the `ls` command.

## Logging In to Easley

Once you are comfortable with the basics, log in to our main computing cluster, Easley, via SSH from your terminal:

```bash
ssh username@easley.alliance.unm.edu
```

On Mac, use the built-in Terminal app (found in Applications → Utilities). On Windows, use [MobaXterm](https://mobaxterm.mobatek.net){target=_blank}, which provides an SSH client and terminal in one.

## CARC-Specific Notes

A few things about the Easley environment that differ from a typical desktop Linux system:

**Your home directory** is at `/users/yourusername`. This is where you land when you log in. Storage here is backed up but has a quota — use it for scripts and important files, not large datasets.

**Scratch storage** for large working data is at `/easley/scratch/users/yourusername`. This is not backed up, so copy important results to your home or project directory when your job is done.

**Software is managed with modules**, not installed globally. Before using most software, you need to load it with `module load`. See the [Managing Software Modules](../running-jobs/modules.md) QuickByte for details.

**Jobs run through SLURM**, not directly on the login node. Do not run computationally intensive work on the login node — submit it as a job. See the [Intro to SLURM](../running-jobs/slurm-intro.md) QuickByte to get started.

If you have any trouble please reach out to us at help@carc.unm.edu.

*This quickbyte was validated on 6/17/2026*

<p class="carc-provenance" markdown>Migrated from [UNM-CARC QuickBytes](https://github.com/UNM-CARC/QuickBytes/blob/master/linux_intro.md){target=_blank} (last source update 2026-06-17). Spotted a problem? [Open an issue or pull request](https://github.com/UNM-CARC/QuickBytes){target=_blank}.</p>
