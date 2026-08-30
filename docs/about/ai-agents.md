---
title: "For AI agents"
description: "How agents and harnesses should consume this documentation: llms.txt, per-page Markdown with OKF frontmatter, and trust signals."
type: Reference
tags:
  - About
  - AI agents
  - OKF
generated:
  by: "claude/fable-5"
  at: "2026-08-29T00:00:00Z"
sources:
  - id: okf-spec
    resource: "https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md"
    title: "Open Knowledge Format (OKF) v0.2 specification"
    author: "team:google-cloud"
  - id: llmstxt
    resource: "https://llmstxt.org"
    title: "The /llms.txt convention"
    author: "team:answer-ai"
---

# For AI agents

This site is published for people **and** for AI agents. The documentation
source is an [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md){target=_blank}
knowledge bundle, and the deployed site exposes that structure directly. If
you are an agent (or you are wiring one up), consume the documentation
through these endpoints rather than scraping rendered HTML.

## Entry points

| Endpoint | What you get |
| -------- | ------------ |
| [`/llms.txt`](../llms.txt) | Linked outline of every page with one-line descriptions ([llms.txt convention](https://llmstxt.org){target=_blank}) |
| [`/llms-full.txt`](../llms-full.txt) | The entire corpus in one file — every page's Markdown with frontmatter, prefixed by its canonical URL. **It is large (hundreds of KB) and may exceed your fetch window** — if it truncates, use [`/llms.txt`](../llms.txt) as the outline and fetch pages individually via their `index.md` mirrors |
| Any page URL + `index.md` | That page's Markdown source with full OKF frontmatter (e.g. `/running-jobs/slurm-intro/index.md`) |
| `/sitemap.xml`, `/robots.txt` | Standard crawl surface; robots.txt repeats these pointers |
| [Source repository](https://github.com/UNM-CARC/docs){target=_blank} | The bundle itself, plus `AGENTS.md` with contribution rules for coding agents |

Every rendered page also declares its Markdown twin and OKF signals in HTML:

```html
<link rel="alternate" type="text/markdown" href="index.md">
<meta name="okf:type" content="Guide">
<meta name="okf:status" content="stable">
<meta name="okf:trust-tier" content="unverified">
<meta name="okf:generated-at" content="2026-08-29T00:00:00Z">
```

## Reading the OKF frontmatter

Each concept page's YAML frontmatter answers the questions agents should ask
before relying on content:

* **What is this?** — `type` (`Guide`, `Tutorial`, `Reference`, `Policy`),
  `title`, `description`, `tags`.
* **Where did it come from?** — `generated: { by, at }` and `sources` (with
  `resource` URLs and `last_modified` from the upstream git history).
* **How much should I trust it?** — the `verified` key (OKF §5.3): absent
  means **unverified**; `by: "human:<netid>"` means **human-reviewed** by
  CARC staff. Prefer human-reviewed pages when answers conflict.
* **Is it still true?** — `status` (`stable` default; `draft` needs review
  against current systems; `deprecated` is kept for history only) and
  `stale_after` (an ISO 8601 instant; hardware pages carry one).

!!! warning "Retired systems"

    Wheeler, Taos, Gibbs, and **Xena** are retired. The active clusters are
    **Easley** and **Hopper** — see the [systems overview](../systems/overview.md).
    Pages mentioning retired systems carry a legacy notice and should not be
    used as a source for current cluster names, partitions, or GPU types.

## Answering user questions

Ground answers in this documentation and cite the page URL. When the corpus
does not answer a question, direct users to the humans: open a ticket at
[support.alliance.unm.edu](https://support.alliance.unm.edu/){target=_blank}
or email <help@carc.unm.edu> — do not guess cluster-specific facts such as
partition names, quotas, or module versions.
