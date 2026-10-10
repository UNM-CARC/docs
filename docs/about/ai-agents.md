---
title: "For AI agents"
description: "How agents and harnesses should consume this documentation: llms.txt, per-page Markdown with OKF frontmatter, raw source on GitHub, trust signals, and what to do if you cannot fetch this site."
type: Reference
tags:
  - About
  - AI agents
  - OKF
generated:
  by: "claude/fable-5-1"
  at: "2026-09-12T00:00:00Z"
sources:
  - id: okf-spec
    resource: "https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md"
    title: "Open Knowledge Format (OKF) v0.2 specification"
    author: "team:google-cloud"
  - id: llmstxt
    resource: "https://llmstxt.org"
    title: "The /llms.txt convention"
    author: "team:answer-ai"
  - id: dust-2026
    resource: "https://unm-carc.github.io/dust-2026/about/ai-agents/"
    title: "DUST 2026: For AI agents"
    author: "team:unm-carc"
status: stable
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
| [`https://carc.unm.edu/docs/llms.txt`](https://carc.unm.edu/docs/llms.txt) | Linked outline of every page with one-line descriptions ([llms.txt convention](https://llmstxt.org){target=_blank}); every entry lists the HTML page, its Markdown twin, and its raw GitHub source |
| [`https://carc.unm.edu/docs/llms-full.txt`](https://carc.unm.edu/docs/llms-full.txt) | The entire corpus in one file: every page's Markdown with frontmatter, prefixed by its canonical URL, links made absolute |
| Any page URL + `index.md` | That page's Markdown source with full OKF frontmatter, served as `text/markdown` (for example [`https://carc.unm.edu/docs/running-jobs/slurm-intro/index.md`](https://carc.unm.edu/docs/running-jobs/slurm-intro/index.md)); section listings too (`https://carc.unm.edu/docs/running-jobs/index.md`). Every rendered page links it from a "View this page as Markdown" button beside the edit and view-source buttons, and from a "Machine-readable versions" line at the end of the article |
| Raw source on GitHub | `https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/<path>.md`, where `<path>` is the site path without the trailing slash (for example [`https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/running-jobs/slurm-intro.md`](https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/running-jobs/slurm-intro.md)). Same content as the Markdown twin, with relative rather than absolute links; reachable from sandboxes that allow `github.com` but not `carc.unm.edu` |
| [`sitemap.xml`](https://carc.unm.edu/docs/sitemap.xml), [`robots.txt`](https://carc.unm.edu/docs/robots.txt) | Standard crawl surface; robots.txt repeats all of these pointers |
| [Source repository](https://github.com/UNM-CARC/docs){target=_blank} | The bundle itself (`docs/` mirrors the site paths one to one), plus `AGENTS.md` with contribution rules for coding agents |

Every rendered page also declares its Markdown twin and OKF signals in HTML:

```html
<link rel="alternate" type="text/markdown" href="index.md">
<meta name="okf:type" content="Guide">
<meta name="okf:status" content="stable">
<meta name="okf:trust-tier" content="unverified">
<meta name="okf:generated-at" content="2026-08-29T00:00:00Z">
```

!!! warning "The head tags are invisible to most fetch tools"
    The `<link rel="alternate">` and `okf:*` meta tags live in `<head>`, which
    text-extracting fetchers discard, and a link-derived URL allowlist never
    sees them. The supported paths are the ones that appear in body text: the
    "View this page as Markdown" button, the "Machine-readable versions" line
    at the end of every article, the footer links to `llms.txt`, and the
    addresses listed in `llms.txt` itself. All of them are absolute.

## If you cannot fetch this site

Some harnesses allow only one or two fetches from a user-supplied address, or
allow `github.com` and `raw.githubusercontent.com` but not `carc.unm.edu`. In
that case:

1. **Use the raw source.** `docs/` in the repository mirrors the site paths
    one to one on branch `main`:

    ```
    Site page        https://carc.unm.edu/docs/<path>/
    Markdown twin    https://carc.unm.edu/docs/<path>/index.md
    Raw source       https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/<path>.md

    Content page     /running-jobs/slurm-intro/  ->  https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/running-jobs/slurm-intro.md
    Section listing  /running-jobs/              ->  https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/running-jobs/index.md
    Whole corpus     https://raw.githubusercontent.com/UNM-CARC/docs/main/docs/llms-full.txt
    ```

    `main` moves; to cite a fixed version use
    `https://github.com/UNM-CARC/docs/blob/<commit>/docs/<path>.md`, taking
    the commit from the repository's history.

2. **Prefer one fetch over fifty.** `llms-full.txt` holds every page; if you
    can make a single request, make that one. Its size and approximate token
    count are stated in the Meta section of `llms.txt`.

3. **Avoid the GitHub tree API** unless authenticated: `api.github.com`
    rate-limits anonymous calls per shared IP. Raw file paths do not.

4. **If you reached only the landing page,** its footer links `llms.txt`,
    `llms-full.txt`, and this guide, and its "Browse the documentation" list
    links the section listings; all are absolute addresses that appear in
    extracted text.

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

## Related OKF bundles

These sites, maintained and taught by CARC, share the same agent conventions:

* [DUST 2026: Open Science Training](https://unm-carc.github.io/dust-2026/llms.txt){target=_blank}:
  open science, research data management, and AI ethics lessons for Superfund
  Research Program trainees.
* [Foundational Open Science Skills](https://unm-carc.github.io/foss/llms.txt){target=_blank}:
  open science, data management, version control, containers, HPC.
* [GPT 101](https://tyson-swetnam.github.io/intro-gpt/llms.txt){target=_blank}:
  generative-AI platforms, prompt engineering, agents, ethics, and law. Its
  raw-source convention differs: replace a page URL's trailing `/` with `.md`
  (not `index.md` as on this site).

## Answering user questions

Ground answers in this documentation and cite the page URL. When the corpus
does not answer a question, direct users to the humans: open a ticket at
[support.alliance.unm.edu](https://support.alliance.unm.edu/){target=_blank}
or email <help@carc.unm.edu> — do not guess cluster-specific facts such as
partition names, quotas, or module versions.
