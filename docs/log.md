# Documentation update log

## 2026-09-29

* **Correction**: Restored the `math-kernel.sh` helper to the
  [Mathematica on Easley](software/mathematica.md) examples. Its process-based
  license file is required by the Mathematica worker-launch workflow.
* **Update**: Added the complete `parallel.wl`, `distributed.wl`, and `gpu.wl`
  sources to [Mathematica on Easley](software/mathematica.md), alongside the
  existing beam model, Slurm scripts, and downloadable archive.
* **Update**: Removed the duplicate page table of contents from
  [QuickByte Tutorials](software/index.md); its expandable sidebar groups are
  now the single navigation layer.
* **Update**: Replaced [Mathematica on Easley](software/mathematica.md) with
  the CARC beam-deflection tutorial and its complete, downloadable example
  archive: shared license launcher, Wolfram Language inputs, and single-node,
  multi-node, and GPU Slurm scripts.
* **Correction**: Restored the confirmed Easley inventory: 9 L40S nodes,
  providing 36 NVIDIA L40S GPUs (44 GPUs total with the H100 GPUs).
* **Update**: Split QuickByte Tutorials' programming-environment menu into
  Conda, JupyterHub, Julia, R, and MATLAB headings. The Conda guide now uses
  the current Miniconda name rather than the retired Anaconda module name.
* **Update**: Split the scientific tutorial categories in
  [QuickByte Tutorials](software/index.md) into Bioinformatics, Chemistry &
  materials, Computational immunology, and Astronomy in both the sidebar and
  the contents page.
* **Update**: Merged the former Software and Tutorials navigation into
  [QuickByte tutorials](software/index.md). Its scrollable contents page now
  gives each active domain tutorial a home alongside the software guides.
* **Creation**: Added [Mathematica on Easley](software/mathematica.md), a
  curated QuickByte covering interactive, serial, multicore, multinode, GPU,
  and license-server workflows with Mathematica 15.0.1 and WolframScript.
* **Update**: Refreshed the [systems overview](systems/overview.md) from
  Slurm inventory collected on September 29. It distinguishes all nodes from
  scheduled compute nodes: Easley has 65 total nodes and 4,160 CPU cores
  (63 scheduled compute nodes, 8 NVIDIA H100 GPUs, 36 NVIDIA L40S GPUs, and
  22.4 TB of compute-node RAM); Hopper has 68 total nodes and 2,176 CPU cores
  (67 scheduled compute nodes, 26 NVIDIA A100 GPUs, 2 NVIDIA V100 GPUs, and
  15.1 TB of compute-node RAM). The page now lists each cluster's
  heterogeneous node configurations, ConnectX adapters, and switch-fabric
  capacities.
* **Update**: Corrected the storage capacities in the
  [systems overview](systems/overview.md): 385 TB of GPFS scratch, 1.2 PB of
  BeeGFS working scratch, and 133 TB of NetApp enterprise storage.

## 2026-09-12

* **Update**: Made the Markdown behind every page easier for AI agents to find, following the conventions of the [DUST 2026](https://unm-carc.github.io/dust-2026/about/ai-agents/){target=_blank} site: each rendered page now carries a "View this page as Markdown" button beside the edit and view-source buttons and a "Machine-readable versions" line at the end of the article (Markdown twin, raw source on GitHub, `llms.txt`, `llms-full.txt`); the site footer links `llms.txt`, `llms-full.txt`, and the agent guide; `llms.txt` is now built from the site nav and lists the Markdown twin and raw GitHub source of every page plus the corpus size; `llms-full.txt` and the per-page Markdown mirror have relative links rewritten to absolute URLs; `robots.txt` names the raw-source convention; and the [agent guide](about/ai-agents.md) explains the raw-source fallback for sandboxes that cannot reach carc.unm.edu and warns that `<head>` tags are invisible to text-extracting fetchers. Scripts now share `scripts/okf_common.py`.

## 2026-09-08

* **Update**: Linked [CARC Video Tutorials](training/videos.md) directly to the QuickBytes playlist.

## 2026-09-01

* **Update**: Reconciled the corpus against the [CARC knowledge store](https://git.repo.alliance.unm.edu/CARC/CARC-knowledge-store){target=_blank} — staff-reviewed articles distilled from real support tickets plus cluster state observed directly over SSH on 2026-07-25. Corrected stale facts: [Slurm intro](running-jobs/slurm-intro.md) now lists Easley's real partitions (debug is 1 hour, not 4; there is no Easley `condo` partition) plus the group-gated `h100`/`l40s` GPU partitions and the default time/memory behavior; [resource limits](systems/resource-limits.md) (now curated in-repo) carries observed per-cluster partition tables — the old Hopper table was a hardware generation stale — full storage quotas with file-count limits, and the job time-limit extension policy; [storage and backups](systems/storage.md) (now curated in-repo) documents the real paths (`/carc/scratch`, `/easley/scratch`, `/projects`), the 180-day Easley scratch cleanup, that Hopper has no machine-local scratch, and how to find a project's path; the retired `anaconda3` module was replaced with `miniconda3` across [conda environments](software/conda-environments.md), [getting R](software/getting-r.md), and [deep-learning packages](software/deep-learning-packages.md); [getting R](software/getting-r.md) and [Gurobi with R](software/gurobi-r.md) now show the current `r/4.x` module tree; and [modules](running-jobs/modules.md) no longer claims plain `intel` modules don't exist.
* **Creation**: Added [CUDA-aware MPI](software/cuda-aware-mpi.md) — passing GPU device pointers directly to MPI and fixing the mixed OpenMPI/UCX environment segfault, distilled from a staff-reviewed, user-confirmed ticket resolution.
* **Update**: Folded ticket-derived answers into the FAQ and guides: [troubleshooting](faq/troubleshooting.md) covers the `uid not in group permitted to use this partition` rejection and the ColdFront path to GPU-partition access, jobs stuck in `CG`, a full out-of-memory diagnosis (per-job memory enforcement, `DefMemPerCPU` defaults, calibrating with `seff`), Python `ModuleNotFoundError` after loading `miniconda3`, quota surprises (group-ownership accounting, stale warnings), hanging transfers, and password-reset propagation; the [general FAQ](faq/general.md) answers where project scratch lives, how to keep data past scratch retention, GPU-partition gating, and allocation expiration/renewal; [password reset](getting-started/password-reset.md) and [transferring data](getting-started/transferring-data.md) carry the matching tips; [getting started](getting-started/overview.md) tells PIs to keep allocations current.

* **Update**: The [agent guide](about/ai-agents.md) now cross-links the [GPT 101 generative-AI workshop](https://tyson-swetnam.github.io/intro-gpt/){target=_blank} — an OKF v0.2 bundle with the same llms.txt conventions, maintained and taught by CARC.

## 2026-08-30

* **Update**: System-status links now point straight at the live monitors — the [cluster login & website status board](https://stats.uptimerobot.com/kqt0LYLwFd), [UNM IT alerts](https://italerts.unm.edu/), [perfSONAR network performance](http://perfsonar.alliance.unm.edu), the [Easley DNS check](https://dnschecker.org/#A/easley.alliance.unm.edu), and [XDMoD usage metrics](https://xdmod.alliance.unm.edu/) — instead of the intermediary carc.unm.edu downtime page. The landing button and troubleshooting steps use the cluster status board; the support card and systems overview list all five.

* **Update**: The header logo is now a Googie starburst — the same 12-ray construction as the homepage hero's atomic bursts (alternating ray lengths, tip dots, cycling colors), in the cream/turquoise/white subset that reads on the cherry header.

* **Update**: Completed the retirement of Wheeler, Taos, Gibbs, and Xena across the corpus. The "Legacy content" admonitions are gone, and every active page now reads against the current clusters: hostnames and prompts point at Hopper, retired-only sections were removed (the Wheeler/PBS Orca variant, the Xena AlphaFold script, Xena-specific partition flags), and the historical Xena and Wheeler queue tables moved from [resource limits](systems/resource-limits.md) into the [legacy cluster reference](systems/cluster-specifications.md). The migration pipeline now enforces this: it fails if a retired system name appears outside the sanctioned legacy pages (provenance frontmatter and the changelog stay truthful).

* **Update**: Converted the remaining PBS-era material on active pages to Slurm ([storage](systems/storage.md) example script and wording, [R package installs](software/r-packages.md) interactive-session request) and fenced all file paths on the storage page. Fixed the [SSH config example](getting-started/ssh-keys.md) (now a single well-formed block covering Hopper and Easley).

* **Update**: Footer social links: removed the X/Twitter icon (account no longer exists) and pointed YouTube at the [main UNM CARC channel](https://www.youtube.com/@UNMCARC).

## 2026-08-29

* **Update**: Made the deployed site directly consumable by AI agents: every page's Markdown source (OKF frontmatter intact) is now served at its URL plus `index.md`; rendered pages advertise it via `link rel=alternate` and `okf:*` meta tags (type, status, trust tier, generated-at); `robots.txt` points crawlers at `llms.txt`, the full corpus, and the mirror convention (`scripts/postbuild_agent_surface.py`, wired into CI). Added the [For AI agents](about/ai-agents.md) guide and a repository `AGENTS.md`/`CLAUDE.md` for coding harnesses.

* **Update**: Embedded CARC YouTube recordings across the site: the [Video tutorials](training/videos.md) page now carries the full QuickBytes playlist, CARC Annual Meeting 2025 talks, and research presentations from the UNMCARC channel; ten guide pages (logging in, Slurm intro, storage, transfers, modules, conda, X11, GNU Parallel, SimCov, parallel R) embed their matching walkthrough via the migration pipeline.
* **Creation**: Rebuilt the [Workshops and slides](training/workshops.md) page (previously a stub) as a curated catalog of 33 slide decks: the Introduction to CARC series, domain-focused workshops, course guest lectures, and legacy material.

* **Update**: The Xena cluster has been retired. Removed Xena from the [Systems overview](systems/overview.md), [Facilities description](about/facilities.md), FAQ, and landing page; added it to the retired-systems list in [Cluster specifications](systems/cluster-specifications.md); marked Xena-specific GPU guides (PyTorch, MATLAB GPU/deep learning, deep-learning packages) as `status: draft` with legacy notices pending review against Hopper and Easley GPUs.
* **Update**: Annotated all code across the corpus: tab-indented QuickBytes code now renders as language-fenced blocks with syntax highlighting; restructured [Installing deep learning packages](software/deep-learning-packages.md) (now curated in-repo); annotated inline code references in [Parallel R with the future package](software/parallel-r-future.md).

* **Creation**: Added the Interactive computing section ([Open OnDemand](interactive/open-ondemand.md), [JupyterHub](interactive/jupyterhub.md)) and the FAQ section ([General FAQ](faq/general.md), [Troubleshooting](faq/troubleshooting.md)).
* **Creation**: Added [Contributing to these docs](about/contributing.md) — the OKF frontmatter contract, verification workflow, and local build instructions for CARC staff.
* **Update**: Added machine-readable `llms.txt` and `llms-full.txt` indexes generated from OKF frontmatter (`scripts/gen_llms_txt.py`, enforced in CI); moved the page table of contents into the left sidebar.

* **Initialization**: Created this documentation bundle with [Zensical](https://zensical.org){target=_blank}, structured as an Open Knowledge Format (OKF v0.2) knowledge bundle.
* **Migration**: Migrated 56 tutorials and guides from [UNM-CARC/QuickBytes](https://github.com/UNM-CARC/QuickBytes){target=_blank} and [UNM-CARC/webinfo](https://github.com/UNM-CARC/webinfo){target=_blank} with provenance frontmatter (`generated`, `sources`, per-file `last_modified` from git history). All migrated pages are unverified pending CARC staff review.
* **Creation**: Wrote the [Getting started overview](getting-started/overview.md), [Good Neighbor Use Policy](getting-started/good-neighbor-policy.md), [Systems overview](systems/overview.md), [Video tutorials](training/videos.md), [Getting help](support/help.md), [Acknowledging CARC](support/acknowledging-carc.md), [Mission and vision](about/mission.md), [Facilities description](about/facilities.md), and [Partner cyberinfrastructure](about/partners.md) pages from carc.unm.edu content.
* **Deprecation**: Marked [Cluster specifications](systems/cluster-specifications.md) (retired Wheeler, Taos, and Gibbs systems) and [R batch jobs with PBS](software/r-pbs-jobs.md) as deprecated; both are kept for history and links.
