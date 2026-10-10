"""Shared helpers for the OKF bundle and agent-surface scripts.

Every script in scripts/ reads site settings (site_name, site_description,
site_url, repo_url, edit_uri, nav) from zensical.toml, so the same scripts
serve any Zensical + OKF v0.2 site without per-site edits. Requires
Python 3.11+ (tomllib); on older interpreters `pip install tomli`.

Shared with UNM-CARC/dust-2026 and UNM-CARC/foss — keep the three copies in
step when changing link-rewriting behaviour.
"""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from typing import Iterator

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"(`+)(?:.*?)\1")
# ](target) or ](target "title") — covers links, images, and nested badges
MD_LINK_RE = re.compile(r"(\]\()(<[^>]+>|[^)\s]+)((?:\s+\"[^\"]*\")?\))")
# [id]: target   (reference-style definitions)
REF_DEF_RE = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s*)(\S+)")
# src="..." / href="..." in raw HTML
HTML_ATTR_RE = re.compile(r"(\b(?:src|href)=\")([^\"]+)(\")")

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "//", "#")


def load_config(root: Path = ROOT) -> dict:
    with open(root / "zensical.toml", "rb") as fh:
        return tomllib.load(fh)["project"]


def site_url(cfg: dict) -> str:
    return (cfg.get("site_url") or "/").rstrip("/") + "/"


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter dict or None if absent, body). Raises ValueError on bad YAML."""
    if not text.startswith("---"):
        return None, text
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise ValueError(f"unparseable YAML frontmatter: {e}") from e
    return (data if isinstance(data, dict) else {}), text[m.end():]


def frontmatter(path: Path) -> dict:
    try:
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return fm or {}


def page_url(base: str, rel: str) -> str:
    """docs-relative .md path -> pretty URL (use_directory_urls)."""
    rel = str(rel).replace("\\", "/")
    if rel == "index.md":
        return base
    if rel.endswith("/index.md"):
        return base + rel[: -len("index.md")]
    return base + rel[: -len(".md")] + "/"


def repo_branch(cfg: dict) -> str:
    """Branch named in edit_uri ("edit/main/docs/" -> "main"); default main."""
    parts = str(cfg.get("edit_uri", "")).strip("/").split("/")
    return parts[1] if len(parts) >= 2 and parts[0] in ("edit", "blob") else "main"


def raw_source_url(cfg: dict, rel: str) -> str | None:
    """Raw GitHub URL of docs/<rel> on the configured branch, or None if the
    repo is not on github.com. Sandboxed agents often reach
    raw.githubusercontent.com when they cannot reach the documentation host."""
    repo = str(cfg.get("repo_url", "")).rstrip("/")
    if not repo.startswith("https://github.com/"):
        return None
    owner_repo = repo[len("https://github.com/"):]
    return (f"https://raw.githubusercontent.com/{owner_repo}/{repo_branch(cfg)}"
            f"/docs/{str(rel).replace(chr(92), '/')}")


def is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES)


def nav_pages(nav: list, trail: tuple = ()) -> Iterator[tuple[tuple, str | None, str]]:
    """Walk a Zensical nav. Yields (section trail, label or None, target)
    where target is a docs-relative .md path or an external URL."""
    for item in nav:
        if isinstance(item, str):
            yield trail, None, item
        elif isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, str):
                    yield trail, label, value
                elif isinstance(value, list):
                    yield from nav_pages(value, trail + (label,))


def iter_body_lines(body: str) -> Iterator[tuple[int, str, bool]]:
    """Yield (line number, line, in_code) for a Markdown body."""
    fence = None
    for i, line in enumerate(body.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
                yield i, line, True
                continue
            if marker == fence:
                fence = None
                yield i, line, True
                continue
        yield i, line, fence is not None


def _sub_outside_inline_code(line: str, fn) -> str:
    """Apply fn to the parts of a line that are not inside `inline code`."""
    out, pos = [], 0
    for m in INLINE_CODE_RE.finditer(line):
        out.append(fn(line[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(fn(line[pos:]))
    return "".join(out)


def rewrite_link_targets(body: str, fn) -> str:
    """Call fn(target) -> new target for every link/image/src/href target in
    the Markdown body, skipping fenced code and inline code."""
    def repl_md(m):
        raw = m.group(2)
        bracketed = raw.startswith("<") and raw.endswith(">")
        target = raw[1:-1] if bracketed else raw
        new = fn(target)
        if bracketed:
            new = f"<{new}>"
        return m.group(1) + new + m.group(3)

    def repl_ref(m):
        return m.group(1) + fn(m.group(2))

    def repl_html(m):
        return m.group(1) + fn(m.group(2)) + m.group(3)

    def fix(segment: str) -> str:
        segment = MD_LINK_RE.sub(repl_md, segment)
        return HTML_ATTR_RE.sub(repl_html, segment)

    lines = []
    for _, line, in_code in iter_body_lines(body):
        if in_code:
            lines.append(line)
            continue
        line = REF_DEF_RE.sub(repl_ref, line)
        lines.append(_sub_outside_inline_code(line, fix))
    out = "\n".join(lines)
    return out + ("\n" if body.endswith("\n") else "")


def iter_link_targets(body: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, target) for every link target outside code."""
    for lineno, line, in_code in iter_body_lines(body):
        if in_code:
            continue
        m = REF_DEF_RE.match(line)
        if m:
            yield lineno, m.group(2)
        stripped = INLINE_CODE_RE.sub("", line)
        for m in MD_LINK_RE.finditer(stripped):
            t = m.group(2)
            yield lineno, (t[1:-1] if t.startswith("<") and t.endswith(">") else t)
        for m in HTML_ATTR_RE.finditer(stripped):
            yield lineno, m.group(2)


def split_target(target: str) -> tuple[str, str]:
    """'a/b.md#frag' -> ('a/b.md', '#frag'); keeps ?query with the suffix."""
    for sep in ("#", "?"):
        if sep in target:
            idx = target.index(sep)
            return target[:idx], target[idx:]
    return target, ""


def absolutize(target: str, src_rel: str, base: str) -> str:
    """Resolve a relative link in docs/<src_rel> to an absolute site URL."""
    if not target or is_external(target) or target.startswith("/"):
        return target
    path, suffix = split_target(target)
    if not path:
        return target
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), path))
    if resolved.startswith(".."):
        return target
    if resolved.endswith(".md"):
        return page_url(base, resolved) + suffix
    return base + resolved + suffix
