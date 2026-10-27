#!/usr/bin/env python3
"""Check built compatibility routes after postbuild_agent_surface.py."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
site = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site"
redirects = json.loads((ROOT / "tutorial-redirects.json").read_text())
for old, new in redirects.items():
    old_url, new_url = old.removesuffix(".md") + "/", new.removesuffix(".md") + "/"
    route = site / old_url / "index.html"
    html = route.read_text()
    match = re.search(r'location.replace\((".*?")\+location.search\+location.hash\)', html)
    assert match, f"Missing query/anchor-preserving redirect: {old}"
    href = json.loads(match[1])
    for base in ("https://carc.unm.edu/docs/", "https://unm-carc.github.io/docs/"):
        assert urljoin(base + old_url, href + "?transfer=1#before-you-start") == (
            base + new_url + "?transfer=1#before-you-start"), old
    assert (site / new_url / "index.html").is_file(), new
    assert (site / old_url / "index.md").read_bytes() == (site / new_url / "index.md").read_bytes(), old
print(f"Checked {len(redirects)} HTML and Markdown compatibility routes on both hosts.")
