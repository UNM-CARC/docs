#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt from the docs/ OKF bundle.

llms.txt      — linked outline of the site (llmstxt.org convention): every
                concept page with its frontmatter description, grouped by the
                nav sections in zensical.toml, with absolute URLs. Each entry
                also names the page's Markdown twin (URL + `index.md`) and its
                raw source on GitHub, so an agent that can reach only one host
                still finds the content.
llms-full.txt — the entire corpus concatenated as Markdown, frontmatter
                included, relative links rewritten to absolute URLs, so an
                agent can ingest the whole bundle in one file.

Site name, description, URL, repository, and page order all come from
zensical.toml. Both files are written into docs/ so the static build ships
them at the site root; CI regenerates them and fails if the committed copies
drift.

Usage: python3 scripts/gen_llms_txt.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_common import (DOCS, absolutize, frontmatter, is_external,  # noqa: E402
                        load_config, nav_pages, page_url, raw_source_url,
                        repo_branch, rewrite_link_targets, site_url,
                        split_frontmatter)


def main() -> int:
    cfg = load_config()
    base = site_url(cfg)
    name = cfg.get("site_name", "Documentation")
    desc = cfg.get("site_description", "").strip()

    raw_root = raw_source_url(cfg, "")
    branch = repo_branch(cfg)
    lines = [
        f"# {name}",
        "",
        f"> {desc} The source repository is an Open Knowledge Format (OKF "
        "v0.2) bundle: every page carries YAML frontmatter with type, "
        "provenance (generated/sources), and lifecycle (status/stale_after) "
        "fields.",
        "",
        "Every page below is listed with three addresses that all return the "
        "same content: the rendered HTML page, its Markdown twin (page URL + "
        "`index.md`, served as text/markdown with the OKF frontmatter), and "
        "the raw source file on GitHub. Fetch whichever your tool is allowed "
        "to reach; many sandboxes permit github.com and "
        "raw.githubusercontent.com but not every documentation host.",
        "",
        "```",
        f"Site page        {base}<path>/",
        f"Markdown twin    {base}<path>/index.md",
    ]
    if raw_root:
        lines += [f"Raw source       {raw_root}<path>.md      (branch {branch}; a moving target)",
                  "",
                  f"Content page     /running-jobs/slurm-intro/  ->  {raw_root}running-jobs/slurm-intro.md",
                  f"Section listing  /running-jobs/              ->  {raw_root}running-jobs/index.md"]
    lines += ["```", ""]
    full = [
        f"# {name} — full corpus",
        "",
        "Each page below begins with its canonical URL followed by its "
        "original Markdown, OKF frontmatter included. Relative links have "
        "been rewritten to absolute URLs.",
        "",
    ]

    # section -> subsection -> outline lines, in nav order; empty groups are
    # never rendered. Top-level single pages (other than Home) share a group.
    groups: dict[str, dict[str | None, list[str]]] = {}

    def add(trail: tuple, line: str):
        section = trail[0] if trail else "Other pages"
        sub = " / ".join(trail[1:]) or None
        groups.setdefault(section, {}).setdefault(sub, []).append(line)

    seen: set[str] = set()
    n = 0
    for trail, label, target in nav_pages(cfg.get("nav", [])):
        if is_external(target):
            add(trail, f"- [{label or target}]({target}): External resource.")
            continue
        rel = target.replace("\\", "/")
        if rel in seen or not (DOCS / rel).exists():
            continue
        seen.add(rel)
        if rel.endswith("index.md") or rel == "log.md":
            continue  # OKF §8 listings and the §9 log are not concept pages
        fm = frontmatter(DOCS / rel)
        url = page_url(base, rel)
        title = fm.get("title") or label or Path(rel).stem.replace("-", " ").title()
        summary = str(fm.get("description", "")).strip()
        suffix = ""
        if fm.get("status") == "deprecated":
            suffix = " (deprecated; kept for history)"
        elif fm.get("status") == "draft":
            suffix = " (draft)"
        raw = raw_source_url(cfg, rel)
        alt = f" Markdown twin: {url}index.md" + (f" Raw source: {raw}" if raw else "")
        add(trail, f"- [{title}]({url}): {summary}{suffix}{alt}")
        text = (DOCS / rel).read_text(encoding="utf-8")
        _, body = split_frontmatter(text)
        head = text[: len(text) - len(body)]
        body = rewrite_link_targets(body, lambda t, r=rel: absolutize(t, r, base))
        full += [f"---8<--- {url}", "", (head + body).rstrip(), ""]
        n += 1

    # Safety net: a page that exists in docs/ but is missing from the nav is
    # still listed (under its directory's section) and reported, so a new
    # page never silently disappears from the index. Fix by adding it to nav.
    section_of_dir = {}
    for trail, _label, target in nav_pages(cfg.get("nav", [])):
        if not is_external(target) and target.endswith("index.md") and trail:
            section_of_dir[str(Path(target).parent).replace("\\", "/")] = trail[0]
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(DOCS).as_posix()
        if (rel in seen or rel.split("/")[0] == "assets"
                or rel.endswith("index.md") or rel == "log.md"):
            continue
        print(f"warning: {rel} is not in the zensical.toml nav; add it "
              "(listed at the end of its section for now)", file=sys.stderr)
        fm = frontmatter(path)
        url = page_url(base, rel)
        title = fm.get("title") or Path(rel).stem.replace("-", " ").title()
        summary = str(fm.get("description", "")).strip()
        raw = raw_source_url(cfg, rel)
        alt = f" Markdown twin: {url}index.md" + (f" Raw source: {raw}" if raw else "")
        section = section_of_dir.get(str(Path(rel).parent).replace("\\", "/"), "Other pages")
        groups.setdefault(section, {}).setdefault(None, []).append(
            f"- [{title}]({url}): {summary}{alt}")
        text = path.read_text(encoding="utf-8")
        _, body = split_frontmatter(text)
        head = text[: len(text) - len(body)]
        body = rewrite_link_targets(body, lambda t, r=rel: absolutize(t, r, base))
        full += [f"---8<--- {url}", "", (head + body).rstrip(), ""]
        n += 1

    for section, subs in groups.items():
        lines += [f"## {section}", ""]
        for sub, entries in subs.items():
            if sub:
                lines += [f"### {sub}", ""]
            lines += entries + [""]

    log = DOCS / "log.md"
    if log.exists():
        body = rewrite_link_targets(log.read_text(encoding="utf-8"),
                                    lambda t: absolutize(t, "log.md", base))
        full += [f"---8<--- {base}log/", "", body.rstrip(), ""]
    full_text = "\n".join(full).rstrip() + "\n"
    nbytes = len(full_text.encode("utf-8"))
    ktok = max(1, round(nbytes / 4 / 1000))

    lines += ["## Meta", "",
              f"- [Full corpus in one file]({base}llms-full.txt): every page's Markdown with "
              f"frontmatter, links made absolute; about {nbytes // 1024} KB, roughly {ktok},000 "
              "tokens. Prefer it over fetching pages one at a time.",
              f"- [Documentation update log]({base}log/): dated history of changes to this bundle.",
              f"- [For AI agents]({base}about/ai-agents/): endpoints, trust signals, and how to "
              "answer questions from this corpus; includes what to do if you cannot fetch this site.",
              f"- [Sitemap]({base}sitemap.xml) and [robots.txt]({base}robots.txt)."]
    if raw_root:
        lines.append(f"- [Source repository]({cfg.get('repo_url')}): the bundle itself; "
                     f"`docs/` mirrors the site paths one to one.")
    lines.append("")

    (DOCS / "llms.txt").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    (DOCS / "llms-full.txt").write_text(full_text, encoding="utf-8")
    print(f"llms.txt: {n} pages indexed; llms-full.txt: "
          f"{(DOCS / 'llms-full.txt').stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
