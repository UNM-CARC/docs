# Documentation update log

## 2026-10-10

* **Update**: [History of CARC computing](about/history.md) now has a "Capacity over time" chart and table under The machines: total peak performance, CPU cores, memory and storage of every machine in service each year from 1995 to 2026, built by `scripts/build_capacity_timeline.py` (many inputs are estimates, listed under the chart). Tyson Swetnam's start date as Director is now Jul 1, 2026.

* **Creation**: Added the [Web archive of the old center websites](about/web-archive.md) (draft): ten browsable snapshots of the HPCERC, AHPCC, Alliance Supercluster, HPC@UNM and first CARC websites (1998–2016), about 820 pages rebuilt from Internet Archive captures by `scripts/build_web_archive.py`. Pages keep their original HTML with an archive banner; links and images point at the local copies, and anything not saved points at the nearest Wayback Machine capture. The history page links to it.

* **Creation**: Added [History of CARC computing](about/history.md) (draft), a sourced record of every supercomputer in the Galles Building machine room from Roadrunner and Los Lobos (1999–2000) through the HPC@UNM machines on the machine-room wall plaques (Pequin, Poblano, Ristra, Hammer, Yenta, Vista Azul, Delphi, Rio Bravo) to Easley. It covers install and retirement dates, manufacturers, grants, peak performance and costs (estimates and unknowns are marked), a timeline, past directors and associate directors, and the PIs who contributed hardware. The plaque photo and 17 logos and photos from Internet Archive snapshots of the old AHPCC, HPCERC, Alliance, HPC@UNM and CARC sites are in `assets/images/history/`; those snapshots also supplied the 1995–1998 IBM SP and SGI Origin machines, the 2000–2007 leadership and the 2008 and 2015 system tables.

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
