#!/usr/bin/env python3
"""Rebuild the old UNM research-computing center websites from Wayback captures.

Reads the raw Internet Archive material staged in ``.wayback/`` (see its
INDEX.md; git-ignored, exists only on the machine that fetched it; it was moved
out of ``.cache/`` because ``zensical build --clean`` deletes that folder) and writes a
browsable static archive to ``docs/about/web-archive/<snapshot>/``.

Each snapshot is one era of one site (for example AHPCC 2000-2001). For every
URL captured in the era's date window, the capture nearest the era's anchor
date is kept. Pages are copied byte-for-byte except for:

* link, image, frame and background URLs, which are rewritten to point at the
  local copy when one exists (in this snapshot, or in the nearest other
  snapshot), and otherwise at the Wayback Machine capture nearest the page's
  own capture date;
* stylesheets and scripts, which were never downloaded, so they load from the
  Wayback Machine (``cs_`` / ``js_`` modes);
* a small banner injected after ``<body>`` naming the capture date and linking
  back to the Wayback copy and to the archive index.

Personal home directories (``/~user``), intranet and timesheet pages, and SSH
host-key listings are left out. Each snapshot also gets a generated
``archive-contents.html`` listing every page it holds.

Usage: python3 scripts/build_web_archive.py   (rebuilds the output from scratch)
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".wayback"
OUT = ROOT / "docs" / "about" / "web-archive"
WAYBACK = "https://web.archive.org/web/"

# Old hostnames that served the same content as another host.
HOST_ALIASES = {"arc.unm.edu": "ahpcc.unm.edu"}
# These hostnames shared one web server (and largely one document tree), so an
# image or page missing under one name is looked up under the others.
SIBLINGS = ("ahpcc.unm.edu", "hpcerc.unm.edu", "alliance.unm.edu", "hpc.unm.edu",
            "carc.unm.edu")
# Spacer images were too small to fetch; serve a local transparent GIF instead.
SPACER_RE = re.compile(r"/(clearpixel|clpxl|clear|trans|spacer|pixel|blank|shim|dot_clear)\.gif$", re.I)
SPACER_GIF = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c"
                           "00000000010001000002024401003b")
# From 2015 the AHPCC and HPCERC hostnames served the CARC site.
CARC_TAKEOVER_TS = "2015"


@dataclass
class Era:
    slug: str
    title: str
    hosts: tuple[str, ...]
    start: str  # inclusive timestamp prefix
    end: str  # inclusive timestamp prefix
    anchor: str  # preferred capture date, YYYYMMDD
    blurb: str
    pages: dict = field(default_factory=dict)  # key -> Page
    images: dict = field(default_factory=dict)  # out relpath -> source file
    _image_slots: dict = field(default_factory=dict)  # lower-cased relpath -> source
    dirs: dict = field(default_factory=dict)  # lower-cased dir -> first spelling

    def image_slot(self, out: str, src) -> str:
        """Reserve an output path for an image, avoiding case-only clashes."""
        base = out = fold_dirs(out, self.dirs)
        n = 2
        while self._image_slots.get(out.lower(), src) != src:
            stem, dot, ext = base.rpartition(".")
            out = f"{stem}_{n}.{ext}" if dot else f"{base}_{n}"
            n += 1
        self._image_slots[out.lower()] = src
        self.images.setdefault(out, src)
        return out


ERAS = [
    Era("hpcerc-1998", "HPCERC", ("hpcerc.unm.edu",), "1998", "2000",
        "19990125", "The earliest captures of hpcerc.unm.edu (the High Performance Computing, "
        "Education & Research Center), which shared its pages with AHPCC."),
    Era("hpcerc-2002", "HPCERC", ("hpcerc.unm.edu",), "2001", "2003",
        "20020715", "HPCERC after its 2002 redesign, with machine pages for Los Lobos, "
        "Roadrunner, BlackBear, Vista Azul and the Access Grid."),
    Era("ahpcc-2000", "AHPCC", ("ahpcc.unm.edu",), "1999", "200106",
        "20000817", "The Albuquerque High Performance Computing Center in the Los Lobos "
        "and Roadrunner era."),
    Era("ahpcc-2002", "AHPCC", ("ahpcc.unm.edu",), "200107", "2008",
        "20020601", "The AHPCC site after its 2001 reorganisation into the Computing/ "
        "section, through its 2003 rename to HPC@UNM."),
    Era("alliance-2000", "Alliance Supercluster", ("alliance.unm.edu",), "1999", "2000",
        "20000903", "alliance.unm.edu as the home of the NCSA Alliance Linux "
        "supercluster (Roadrunner) run by AHPCC."),
    Era("alliance-2002", "alliance.unm.edu", ("alliance.unm.edu",), "2001", "2003",
        "20020101", "alliance.unm.edu once it served the AHPCC and HPCERC site, "
        "with the Alliance account and user-guide pages."),
    Era("alliance-2006", "alliance.unm.edu", ("alliance.unm.edu",), "2004",
        "2011", "20060906", "Later captures of alliance.unm.edu, which by then served "
        "the HPC@UNM site."),
    Era("hpc-2004", "HPC@UNM", ("hpc.unm.edu",), "2003", "2005",
        "20040301", "The Center for High Performance Computing at UNM before its move "
        "to Plone."),
    Era("hpc-2010", "HPC@UNM and CARC", ("hpc.unm.edu",), "2006", "2014",
        "20100801", "The Plone site on hpc.unm.edu, retitled UNM Center for Advanced "
        "Research Computing around 2010, in the Encanto, Nano and Xena era."),
    Era("carc-2015", "CARC", ("carc.unm.edu",),
        "2013", "2016", "20150925", "The first Center for Advanced Research Computing "
        "site, also served under the old AHPCC and HPCERC hostnames."),
]

EXCLUDE = re.compile(r"/~|intranet|timesheet|staff_information|ssh-known-hosts|"
                     r"search_form", re.I)


@dataclass
class Page:
    key: str
    url: str  # original URL as captured (after host takeover rewrite)
    ts: str
    src: Path
    wayback: str
    out: str = ""  # path relative to the era directory
    title: str = ""


# --------------------------------------------------------------------- urls

def canon_host(host: str) -> str:
    host = (host or "").lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return HOST_ALIASES.get(host, host)


def url_key(url: str) -> str | None:
    """Canonical form used to match links to captures."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return None
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    path = re.sub(r"/(index\.html?|index_html|default\.html?|view)$", "/", path, flags=re.I)
    return f"{canon_host(parts.netloc)}{path}" + (f"?{parts.query}" if parts.query else "")


def variants(key: str | None):
    """The key itself, then the same path on sibling hosts, then with a slash added."""
    if not key:
        return []
    host, _, rest = key.partition("/")
    out = [key]
    if not rest.endswith("/") and "?" not in rest and "." not in rest.rsplit("/", 1)[-1]:
        out.append(f"{key}/")
    if host in SIBLINGS:
        out += [f"{h}/{v.partition('/')[2]}" for v in list(out) for h in SIBLINGS if h != host]
    return out


def safe_segment(seg: str) -> str:
    seg = unquote(seg)
    seg = re.sub(r"[^A-Za-z0-9._-]+", "_", seg).strip("_")
    return seg or "_"


def page_outpath(key: str) -> str:
    path, _, query = key.partition("?")
    host, _, path = path.partition("/")
    segs = [safe_segment(s) for s in path.split("/")]
    last = segs.pop() if segs else ""
    if query:
        last = f"{last or 'index'}_q_{safe_segment(query)}"
    if not last or last == "_":
        name = "index.html"
    elif re.search(r"\.html?$", last, re.I):
        name = last
    elif "." in last[-6:] and not query:
        name = last + ".html"  # .php, .asp, .shtml, .png/view leftovers ...
    else:
        segs.append(last)
        name = "index.html"
    return "/".join(segs + [name])


def image_outpath(key: str) -> str:
    path, _, query = key.partition("?")
    host, _, path = path.partition("/")
    segs = [safe_segment(s) for s in path.split("/") if s]
    if not segs:
        segs = ["image"]
    if query:
        segs[-1] += "_q_" + safe_segment(query)
    return "_img/" + "/".join(segs)


def fold_dirs(out: str, seen: dict) -> str:
    """Reuse the first spelling of each directory that differs only in case.

    macOS file systems are case-insensitive, so /About/ and /about/ would land in
    one folder there while links (and git, and Linux web servers) keep them apart.
    """
    parts = out.split("/")
    for i in range(1, len(parts)):
        prefix = "/".join(parts[:i])
        first = seen.setdefault(prefix.lower(), prefix)
        parts[:i] = first.split("/")
    return "/".join(parts)


def relpath(target: str, start: str) -> str:
    """Relative URL from file ``start`` to file ``target`` (both era-relative)."""
    t, s = target.split("/"), start.split("/")[:-1]
    i = 0
    while i < len(s) and i < len(t) - 1 and s[i] == t[i]:
        i += 1
    return "/".join([".."] * (len(s) - i) + t[i:]) or "./"


def ts_distance(a: str, b: str) -> float:
    def d(x):
        x = (x + "0101")[:8]
        try:
            return datetime.strptime(x, "%Y%m%d").timestamp()
        except ValueError:
            return datetime.strptime(x[:4] + "0101", "%Y%m%d").timestamp()
    return abs(d(a) - d(b))


def wayback(ts: str, url: str, mode: str = "") -> str:
    return f"{WAYBACK}{ts}{mode}/{url}"


def human_date(ts: str) -> str:
    return datetime.strptime(ts[:8], "%Y%m%d").strftime("%-d %B %Y")


# ------------------------------------------------------------------ loading

def load():
    rows = [json.loads(line) for line in open(CACHE / "manifest.jsonl")]
    images: dict[str, list[tuple[str, Path]]] = {}
    for r in rows:
        if r.get("kind") == "img" and r.get("status") == "200":
            key = url_key(r["orig"])
            src = CACHE / r["dest"]
            if key and src.exists():
                images.setdefault(key, []).append((r["ts"], src))

    # Images fetched later for pages that referenced them (extra/, see its
    # fetch script); missing-images.json holds the capture date each was asked for.
    extra = CACHE / "extra"
    if (extra / "results.jsonl").exists():
        asked = {m["key"]: m["ts"] for m in json.load(open(extra / "missing-images.json"))}
        for line in open(extra / "results.jsonl"):
            r = json.loads(line)
            src = extra / r.get("file", "")
            if r.get("status") == "ok" and src.is_file():
                ts = (re.search(r"/web/(\d{8,14})", r.get("from", "")) or [None, asked[r["key"]]])[1]
                images.setdefault(r["key"], []).append((ts, src))

    seen = set()
    for r in rows:
        if r.get("kind") != "html" or r.get("status") != "200":
            continue
        src = CACHE / r["dest"]
        if not src.exists() or (r["dest"]) in seen:
            continue
        seen.add(r["dest"])
        url, ts = r["orig"], r["ts"]
        parts = urlsplit(url)
        host = canon_host(parts.netloc)
        if host in ("ahpcc.unm.edu", "hpcerc.unm.edu") and ts >= CARC_TAKEOVER_TS:
            host = "carc.unm.edu"
        url = urlunsplit(("http", host, parts.path or "/", parts.query, ""))
        if EXCLUDE.search(parts.path or "") or src.stat().st_size < 400:
            continue
        key = url_key(url)
        for era in ERAS:
            if host in era.hosts and era.start <= ts[:len(era.start)] and \
                    ts[:len(era.end)] <= era.end:
                cur = era.pages.get(key)
                if cur is None or ts_distance(ts, era.anchor) < ts_distance(cur.ts, era.anchor):
                    era.pages[key] = Page(key, url, ts, src, r["wayback"])
                break

    for era in ERAS:
        # Compare lower-cased: macOS file systems are case-insensitive, and the
        # old sites had both /About/ and /about/.
        used: dict[str, str] = {}
        for page in sorted(era.pages.values(), key=lambda p: p.key):
            base = out = fold_dirs(page_outpath(page.key), era.dirs)
            n = 2
            while used.get(out.lower(), page.key) != page.key:
                out = re.sub(r"(\.html?)$", rf"_{n}\1", base)
                n += 1
            used[out.lower()] = page.key
            page.out = out
    return images


# ---------------------------------------------------------------- rewriting

TAG_RE = re.compile(r"<(a|area|img|frame|iframe|link|script|body|td|th|tr|table|input|"
                    r"embed|bgsound|form|base|meta|layer|ilayer)\b([^>]*)>", re.I | re.S)
ATTR_RE = re.compile(r"""(\s)(href|src|background|action|lowsrc)(\s*=\s*)("[^"]*"|'[^']*'|[^\s>]+)""",
                     re.I)
REFRESH_RE = re.compile(r"""(url\s*=\s*)([^"'>;]+)""", re.I)
BODY_RE = re.compile(r"<body\b[^>]*>", re.I)


# File names too generic to match across folders (Image1.gif, map.gif ...).
GENERIC_NAME_RE = re.compile(r"(image|img|picture|pic|photo|untitled|map|logo|banner|header|"
                             r"title|button|graphic)[-_]?\d*\.\w+$", re.I)
STANDINS = {p.name.lower(): p for p in (ROOT / "scripts" / "web_archive_standins").glob("*")}


def names_index(images) -> dict:
    """Cached images on the shared-server hosts, by lower-cased file name."""
    out: dict[str, list] = {}
    for key, caps in images.items():
        if key.partition("/")[0] in SIBLINGS:
            out.setdefault(key.partition("?")[0].rsplit("/", 1)[-1].lower(), []).extend(caps)
    return out


class Rewriter:
    by_name: dict = {}
    not_archived: set = set()  # keys the Wayback Machine returned nothing for

    def __init__(self, era: Era, page: Page, images, all_pages):
        self.era, self.page, self.images, self.all_pages = era, page, images, all_pages
        self.base = page.url
        self.stats = {"local": 0, "wayback": 0, "img_local": 0, "img_wayback": 0}
        self.marked = {"recreated": 0, "missing": 0}

    def link(self, raw: str, kind: str) -> str:
        value = html.unescape(raw.strip())
        if not value or value.startswith("#") or re.match(r"(mailto|javascript|data|about):",
                                                          value, re.I):
            return raw
        try:
            absolute = urljoin(self.base, value)
        except ValueError:
            return raw
        absolute, _, frag = absolute.partition("#")
        frag = f"#{frag}" if frag else ""
        key = url_key(absolute)
        ts = self.page.ts
        if kind == "page":
            # Sibling hosts only shared a document tree before the 2003 split.
            keys = variants(key) if ts < "2004" else variants(key)[:2]
            for k in keys:
                if k in self.era.pages:
                    self.stats["local"] += 1
                    return relpath(self.era.pages[k].out, self.page.out) + frag
            for k in keys:
                if k in self.all_pages:
                    era, target = min(self.all_pages[k],
                                      key=lambda et: ts_distance(et[0].anchor, ts))
                    self.stats["local"] += 1
                    up = "../" * self.page.out.count("/")
                    return f"{up}../{era.slug}/{target.out}{frag}"
            self.stats["wayback"] += 1
            return wayback(ts, absolute) + frag
        if kind == "image":
            for k in variants(key):
                caps = self.images.get(k)
                if caps:
                    cap_ts, src = min(caps, key=lambda c: ts_distance(c[0], self.era.anchor))
                    out = self.era.image_slot(image_outpath(key), src)
                    self.stats["img_local"] += 1
                    return relpath(out, self.page.out)
            # The same file name elsewhere on the same server (sites moved their
            # image folders around), then a drawn stand-in, before giving up.
            name = key.partition("?")[0].rsplit("/", 1)[-1].lower() if key else ""
            if key and key.partition("/")[0] in SIBLINGS and name in self.by_name \
                    and not GENERIC_NAME_RE.match(name):
                cap_ts, src = min(self.by_name[name], key=lambda c: ts_distance(c[0], ts))
                out = self.era.image_slot(image_outpath(key), src)
                self.stats["img_local"] += 1
                return relpath(out, self.page.out)
            if name in STANDINS:
                out = self.era.image_slot(f"_img/standin/{name}", STANDINS[name])
                self.stats["img_standin"] = self.stats.get("img_standin", 0) + 1
                return relpath(out, self.page.out)
            if key and SPACER_RE.search(key.partition("?")[0]):
                self.era.image_slot("_img/spacer.gif", SPACER_GIF)
                self.stats["img_local"] += 1
                return relpath("_img/spacer.gif", self.page.out)
            # The Wayback Machine has no copy either: a neutral grey box rather
            # than a broken-image icon.
            if key in self.not_archived:
                out = self.era.image_slot("_img/standin/_not-archived.gif",
                                          STANDINS["_not-archived.gif"])
                self.stats["img_standin"] = self.stats.get("img_standin", 0) + 1
                return relpath(out, self.page.out)
            self.stats["img_wayback"] += 1
            return wayback(ts, absolute, "im_")
        mode = {"css": "cs_", "js": "js_"}.get(kind, "")
        return wayback(ts, absolute, mode)

    def tag(self, m: re.Match) -> str:
        name, attrs = m.group(1).lower(), m.group(2)
        if name == "base":
            href = re.search(r"""href\s*=\s*["']?([^"'\s>]+)""", attrs, re.I)
            if href:
                self.base = urljoin(self.page.url, href.group(1))
            return "<!-- base removed by archive -->"
        if name == "meta":
            if re.search(r"http-equiv\s*=\s*[\"']?refresh", attrs, re.I):
                attrs = REFRESH_RE.sub(lambda r: r.group(1) + self.link(r.group(2), "page"),
                                       attrs)
            return f"<{m.group(1)}{attrs}>"
        rel = re.search(r"""rel\s*=\s*["']?([^"'>]+)""", attrs, re.I)

        def attr(a: re.Match) -> str:
            an = a.group(2).lower()
            val = a.group(4)
            q = val[0] if val[0] in "\"'" else ""
            inner = val[1:-1] if q else val
            if an == "background" or (an in ("src", "lowsrc") and name in ("img", "input")):
                kind = "image"
            elif name == "link":
                r = rel.group(1).lower() if rel else ""
                kind = "css" if "stylesheet" in r else ("image" if "icon" in r else "page")
            elif name == "script" or (an == "src" and name in ("embed", "bgsound", "layer", "ilayer")):
                kind = "js" if name == "script" else "other"
            elif an == "action":
                kind = "other"
            else:
                kind = "page"
            new = self.link(inner, kind).replace('"', "%22")
            if kind == "image" and "_img/standin/" in new and name in ("img", "input"):
                marks.append("missing" if new.endswith("_not-archived.gif") else "recreated")
            return f'{a.group(1)}{a.group(2)}{a.group(3)}"{new}"'

        marks: list = []
        attrs = ATTR_RE.sub(attr, attrs)
        if marks:
            attrs = self.mark_standin(attrs, marks[0])
        return f"<{m.group(1)}{attrs}>"

    def mark_standin(self, attrs: str, mark: str) -> str:
        """Label a stand-in so readers don't take it for an archived original."""
        self.marked[mark] += 1
        note = ("Modern recreation, not an archived original" if mark == "recreated"
                else "Image not archived")
        alt = re.search(r"""(\salt\s*=\s*)("[^"]*"|'[^']*'|[^\s>]*)""", attrs, re.I)
        if alt:
            val = alt.group(2).strip("\"'")
            label = f"{val} ({note.lower()})" if val.strip() else note
            attrs = attrs[:alt.start()] + f' alt="{label.replace(chr(34), "&quot;")}"' + attrs[alt.end():]
        else:
            attrs = attrs.rstrip("/ ") + f' alt="{note}"' + (" /" if attrs.rstrip().endswith("/") else "")
        if not re.search(r"\stitle\s*=", attrs, re.I):
            attrs = attrs.rstrip("/ ") + f' title="{note}"' + (" /" if attrs.rstrip().endswith("/") else "")
        return attrs

    def banner(self) -> str:
        p, up = self.page, "../" * self.page.out.count("/")
        shown = re.sub(r"^https?://", "", p.url)
        return (
            '\n<div id="carc-archive-banner" style="all:initial;display:block;'
            'background:#fff8dc;border-bottom:2px solid #ba0c2f;color:#222;'
            'font:13px/1.45 Helvetica,Arial,sans-serif;padding:6px 12px;text-align:left;'
            'position:relative;z-index:2147483647">'
            f'<b style="color:#ba0c2f">CARC web archive</b> &middot; Archived copy of '
            f'<code style="font:12px monospace">{html.escape(shown)}</code> as captured by the '
            f'Internet Archive on {human_date(p.ts)}. Links to pages that were not saved '
            'here go to the Wayback Machine. '
            f'{self.standin_note()}'
            f'<a style="color:#0b5cad" href="{html.escape(p.wayback)}">Wayback copy</a> &middot; '
            f'<a style="color:#0b5cad" href="{up}archive-contents.html">All pages in this snapshot</a> &middot; '
            f'<a style="color:#0b5cad" href="{up}../">Web archive index</a></div>\n'
        )

    def standin_note(self) -> str:
        parts = []
        if self.marked["recreated"]:
            parts.append("Icons the Internet Archive did not save were redrawn for this copy "
                         "and are not originals (hover over one to see).")
        if self.marked["missing"]:
            parts.append("Grey boxes mark images that were never archived.")
        return " ".join(parts) + " " if parts else ""

    def run(self) -> bytes:
        text = self.page.src.read_bytes().decode("latin-1")
        tm = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        self.page.title = re.sub(r"\s+", " ", html.unescape(tm.group(1))).strip() if tm else ""
        text = TAG_RE.sub(self.tag, text)
        body = BODY_RE.search(text)
        if body:
            text = text[:body.end()] + self.banner() + text[body.end():]
        elif not re.search(r"<frameset", text, re.I):
            text = self.banner() + text
        return text.encode("latin-1", errors="replace")


# ------------------------------------------------------------------- output

def contents_page(era: Era) -> str:
    rows = []
    for p in sorted(era.pages.values(), key=lambda p: (p.out != "index.html", p.out)):
        shown = re.sub(r"^https?://", "", p.url)
        rows.append(
            f'<tr><td><a href="{html.escape(p.out)}">{html.escape(p.title or shown)}</a><br>'
            f'<small>{html.escape(shown)}</small></td><td>{human_date(p.ts)}</td>'
            f'<td><a href="{html.escape(p.wayback)}">Wayback</a></td></tr>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(era.title)} - CARC web archive</title>
<style>
body{{font:15px/1.5 Helvetica,Arial,sans-serif;max-width:60rem;margin:0 auto;padding:1rem;color:#222;background:#fff}}
h1{{color:#ba0c2f;font-size:1.5rem}} a{{color:#0b5cad}} table{{border-collapse:collapse;width:100%}}
td,th{{border-bottom:1px solid #ddd;padding:.4rem;text-align:left;vertical-align:top}}
small{{color:#666;word-break:break-all}}
</style></head><body>
<p><a href="../">&larr; CARC web archive</a></p>
<h1>{html.escape(era.title)}</h1>
<p>{html.escape(era.blurb)} {len(era.pages)} pages, each the capture nearest
{human_date(era.anchor)}. <a href="index.html">Open the home page</a>.</p>
<table><tr><th>Page</th><th>Captured</th><th></th></tr>
{chr(10).join(rows)}
</table></body></html>
"""


def main() -> int:
    if not (CACHE / "manifest.jsonl").exists():
        print(f"no Wayback cache at {CACHE}", file=sys.stderr)
        return 1
    images = load()
    Rewriter.by_name = names_index(images)
    extra = CACHE / "extra" / "results.jsonl"
    if extra.exists():
        Rewriter.not_archived = {json.loads(line)["key"] for line in open(extra)
                                 if json.loads(line)["status"] == "missing"}
    all_pages: dict[str, list] = {}
    for era in ERAS:
        for p in era.pages.values():
            all_pages.setdefault(p.key, []).append((era, p))

    for era in ERAS:
        first, last = (f(p.ts for p in era.pages.values())[:4] for f in (min, max))
        era.title = f"{era.title}, {first}" + (f"–{last}" if last != first else "")

    if OUT.exists():
        shutil.rmtree(OUT)
    summary = []
    for era in ERAS:
        root = OUT / era.slug
        totals = {"local": 0, "wayback": 0, "img_local": 0, "img_standin": 0, "img_wayback": 0}
        home = next((p for p in era.pages.values() if p.out == "index.html"), None)
        for page in era.pages.values():
            rw = Rewriter(era, page, images, all_pages)
            data = rw.run()
            dest = root / page.out
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            for k, v in rw.stats.items():
                totals[k] += v
        for out, src in era.images.items():
            dest = root / out
            dest.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(src, bytes):
                dest.write_bytes(src)
            else:
                shutil.copyfile(src, dest)
        if home is None:  # no captured home page: make the contents page the entry
            (root / "index.html").write_text(contents_page(era), encoding="utf-8")
        (root / "archive-contents.html").write_text(contents_page(era), encoding="utf-8")
        summary.append({"slug": era.slug, "title": era.title, "pages": len(era.pages),
                        "images": len(era.images), "has_home": home is not None,
                        "first": min(p.ts for p in era.pages.values())[:8],
                        "last": max(p.ts for p in era.pages.values())[:8], **totals})
    update_index_table(summary)
    for s in summary:
        print(json.dumps(s))
    return 0


INDEX_MD = ROOT / "docs" / "about" / "web-archive.md"
TABLE_START, TABLE_END = "<!-- archive-table:start -->", "<!-- archive-table:end -->"


def update_index_table(summary: list[dict]) -> None:
    """Rewrite the snapshot table between the markers in web-archive.md."""
    if not INDEX_MD.exists():
        return
    eras = {e.slug: e for e in ERAS}
    lines = ["| Snapshot | Pages | What it shows |", "| --- | --- | --- |"]
    for s in summary:
        era = eras[s["slug"]]
        lines.append(
            f"| [{era.title}](web-archive/{s['slug']}/index.html) | "
            f"[{s['pages']}](web-archive/{s['slug']}/archive-contents.html) | {era.blurb} |")
    text = INDEX_MD.read_text(encoding="utf-8")
    head, _, rest = text.partition(TABLE_START)
    _, _, tail = rest.partition(TABLE_END)
    INDEX_MD.write_text(f"{head}{TABLE_START}\n{chr(10).join(lines)}\n{TABLE_END}{tail}",
                        encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
