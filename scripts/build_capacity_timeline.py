#!/usr/bin/env python3
"""Build the computing-capacity timeline on docs/about/history.md.

Sums peak FLOPS, cores, RAM and storage over every machine in service each year
and writes an inline SVG chart plus a table of the totals between the
``capacity-timeline`` markers in the history page. The per-machine figures come
from "The machines" section of that page; values the page does not give are
estimates and are flagged ``est`` below. Edit MACHINES and re-run.

Usage: python3 scripts/build_capacity_timeline.py [path/to/history.md]
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "about" / "history.md"
START, END = "<!-- capacity-timeline:start -->", "<!-- capacity-timeline:end -->"
FIRST_YEAR, LAST_YEAR = 1995, 2026

# name, first and last year in service (inclusive: in service at any time that year),
# cores, CPU peak TFLOPS, RAM TB, storage TB, set of fields that are estimates
# ("years" when the in-service span itself is assumed).
MACHINES = [
    ("IBM SP1", 1995, 1997, 32, 0.004, 0.004, 0, {"tflops", "ram"}),
    ("IBM SP2", 1997, 2000, 128, 0.034, 0.016, 0, {"tflops", "ram"}),
    ("Nambe (SGI Origin)", 1997, 2003, 8, 0.003, 0.001, 0, {"tflops"}),
    ("Roadrunner", 1999, 2003, 128, 0.063, 0.032, 0.41, set()),
    ("BlackBear", 2000, 2004, 32, 0.018, 0.008, 0, {"tflops"}),
    ("Vista", 2000, 2008, 32, 0.021, 0.016, 0, {"tflops"}),
    ("Azul", 2000, 2006, 32, 0.018, 0.016, 0, {"tflops", "years"}),
    ("Los Lobos", 2000, 2007, 512, 0.375, 0.256, 2, set()),
    ("Truchas", 2001, 2007, 24, 0.016, 0.012, 0, {"tflops", "years"}),
    ("RCDE", 2001, 2007, 64, 0.021, 0.008, 0, {"tflops", "years"}),
    ("Delphi", 2003, 2015, 8, 0.008, 0.008, 2, {"tflops", "ram"}),
    ("Rio Bravo", 2004, 2021, 10, 0.05, 0.01, 20, {"tflops"}),
    ("Pequin", 2005, 2012, 4, 0.012, 0.016, 0, set()),
    ("Poblano", 2005, 2013, 16, 0.061, 0.256, 0, {"years"}),
    ("Ristra", 2005, 2012, 192, 1.2, 0.384, 0, set()),
    ("Hammer", 2005, 2012, 32, 0.256, 0.032, 0, set()),
    ("Yenta", 2005, 2013, 32, 0.27, 0.032, 20, {"tflops", "years"}),
    ("Nano", 2007, 2016, 140, 1.288, 0.28, 0, {"ram"}),
    ("Pequeña", 2008, 2017, 176, 2.1, 0.35, 0, {"ram"}),
    ("HP X9000", 2010, 2016, 0, 0, 0, 281, {"years"}),
    ("Metropolis", 2012, 2017, 140, 0.728, 0.28, 0, {"ram"}),
    ("Galles", 2013, 2019, 400, 2.2, 0.8, 0, {"ram"}),
    ("Gibbs", 2013, 2025, 384, 3.996, 1.536, 6.3, set()),
    ("Ulam", 2014, 2017, 960, 4.2, 1.92, 0, {"ram"}),
    ("Xena", 2016, 2026, 576, 18, 9.8, 73, set()),
    ("Wheeler", 2017, 2025, 2432, 25, 14.6, 40, set()),
    ("Taos", 2018, 2025, 180, 6, 2.3, 27, {"tflops", "ram", "years"}),
    ("Hopper", 2022, 2026, 2176, 200, 10.1, 0, {"tflops", "ram"}),
    ("Hopper base storage", 2022, 2024, 0, 0, 0, 700, set()),
    ("Easley", 2025, 2026, 4160, 270, 23.3, 0, {"tflops"}),
    ("Shared storage (GPFS, BeeGFS, NetApp)", 2025, 2026, 0, 0, 0, 5120, {"years"}),
]

# Double-precision (FP64, non-tensor) GPU peak in TFLOPS, added on top of the CPU
# peak: Xena 32 Tesla K40M x 1.43; Hopper 37 A100 x 9.7; Easley 8 H100 x 34
# plus 36 L40S x 1.4. All estimates from vendor specifications.
GPU_TFLOPS = {"Xena": 45.8, "Hopper": 359, "Easley": 322}

METRICS = [  # key, panel title, unit formatter
    ("tflops", "Peak performance"),
    ("cores", "CPU cores"),
    ("ram", "Memory (RAM)"),
    ("storage", "Storage"),
]
IDX = {"cores": 3, "tflops": 4, "ram": 5, "storage": 6}


def totals() -> dict[int, dict[str, float]]:
    out = {}
    for y in range(FIRST_YEAR, LAST_YEAR + 1):
        row = {k: 0.0 for k in IDX}
        row["gpu"] = 0.0
        for m in MACHINES:
            if m[1] <= y <= m[2]:
                for k, i in IDX.items():
                    row[k] += m[i]
                row["gpu"] += GPU_TFLOPS.get(m[0], 0)
        row["total"] = row["tflops"] + row["gpu"]
        out[y] = row
    return out


def fmt(key: str, v: float) -> str:
    if key == "cores":
        return f"{v:,.0f}"
    if key == "tflops":
        if v >= 1000:
            return f"{v / 1000:.3g} PFLOPS"
        if v >= 1:
            return f"{v:.3g} TFLOPS"
        return f"{v * 1000:.3g} GFLOPS"
    # ram and storage are in TB
    if v >= 1000:
        return f"{v / 1000:.3g} PB"
    if v >= 1:
        return f"{v:.3g} TB"
    return f"{v * 1000:.3g} GB"


SERIES = {  # extra series drawn in a panel: (data key, css class, label, only where)
    "tflops": [("total", "cc-line2", "CPU + GPU", "gpu"), ("tflops", "cc-line", "CPU", None)],
}


def panel(key: str, title: str, data, x0: float, y0: float, w: float, h: float) -> str:
    years = list(data)
    series = SERIES.get(key, [(key, "cc-line", None, None)])
    pos = [data[y][k] for k, *_ in series for y in years if data[y][k] > 0]
    lo = 10 ** math.floor(math.log10(min(pos)))
    hi = 10 ** math.ceil(math.log10(max(pos)))
    pl, pr, pt, pb = 76, 78, 26, 22  # plot padding inside the panel
    px0, px1, py0, py1 = x0 + pl, x0 + w - pr, y0 + pt, y0 + h - pb

    def X(year):
        return px0 + (year - FIRST_YEAR) / (LAST_YEAR + 1 - FIRST_YEAR) * (px1 - px0)

    def Y(v):
        return py1 - (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (py1 - py0)

    parts = [f'<text class="cc-title" x="{x0 + 4}" y="{y0 + 14}">{title}</text>']
    if len(series) > 1:  # legend, right of the title
        lx = x0 + 150
        for k, cls, label, _ in reversed(series):
            parts.append(f'<line class="{cls}" x1="{lx}" x2="{lx + 16}" y1="{y0 + 10}" y2="{y0 + 10}"/>'
                         f'<text class="cc-axis" x="{lx + 20}" y="{y0 + 14}">{label}</text>')
            lx += 32 + 6.2 * len(label)
    d = 1
    while lo * d <= hi:  # one gridline per decade
        v = lo * d
        parts.append(f'<line class="cc-grid" x1="{px0}" x2="{px1}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>')
        parts.append(f'<text class="cc-axis" x="{px0 - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">'
                     f'{fmt(key, v).replace(" ", "&#160;")}</text>')
        d *= 10
    for year in range(FIRST_YEAR + 5, LAST_YEAR + 1, 10):
        parts.append(f'<text class="cc-axis" x="{X(year + 0.5):.1f}" y="{py1 + 16}" '
                     f'text-anchor="middle">{year}</text>')
    labels = []
    for k, cls, label, only in series:
        # Step line: each year's total holds from Jan 1 to Dec 31.
        path, prev = [], None
        for year in years:
            v = data[year][k]
            if v <= 0 or (only and data[year][only] <= 0):
                prev = None
                continue
            x_a, x_b, yv = X(year), X(year + 1), Y(v)
            path.append(f"{'M' if prev is None else 'L'}{x_a:.1f},{yv:.1f} L{x_b:.1f},{yv:.1f}")
            prev = v
        parts.append(f'<path class="{cls}" d="{" ".join(path)}"/>')
        last = data[LAST_YEAR][k]
        parts.append(f'<circle class="cc-dot {cls}-dot" cx="{X(LAST_YEAR + 1):.1f}" cy="{Y(last):.1f}" r="4"/>')
        labels.append([Y(last), fmt(key, last)])
    labels.sort()
    for i in range(1, len(labels)):  # keep end labels from overlapping
        labels[i][0] = max(labels[i][0], labels[i - 1][0] + 14)
    for yl, text in labels:
        parts.append(f'<text class="cc-label" x="{X(LAST_YEAR + 1) + 7:.1f}" y="{yl + 4:.1f}">{text}</text>')
    for year in years:  # hover targets with native tooltips
        vals = [(label, data[year][k]) for k, _, label, only in series
                if data[year][k] > 0 and not (only and data[year][only] <= 0)]
        if vals:
            tip = "; ".join(f"{label + ' ' if label else ''}{fmt(key, v)}" for label, v in reversed(vals))
            parts.append(f'<rect class="cc-hit" x="{X(year):.1f}" y="{py0}" '
                         f'width="{X(year + 1) - X(year):.1f}" height="{py1 - py0}">'
                         f'<title>{year}: {tip}</title></rect>')
    return "".join(parts)


def svg(data) -> str:
    W, H, gap = 760, 460, 12
    pw, ph = (W - gap) / 2, (H - gap) / 2
    cells = [(0, 0), (pw + gap, 0), (0, ph + gap), (pw + gap, ph + gap)]
    body = "".join(panel(k, t, data, x, y, pw, ph) for (k, t), (x, y) in zip(METRICS, cells))
    return (f'<svg class="cc-svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="cc-t cc-d" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="cc-t">CARC computing capacity by year, {FIRST_YEAR}–{LAST_YEAR}</title>'
            f'<desc id="cc-d">Four log-scale step charts of the total peak performance (CPU, and CPU plus GPU), CPU cores, '
            f'memory and storage of all machines in service each year. The table below the chart '
            f'gives the same totals.</desc>{body}</svg>')


STYLE = """<style>
.cc-figure{--cc-series:#ba0c2f;--cc-series2:#2a78d6;margin:1em 0}
[data-md-color-scheme="slate"] .cc-figure{--cc-series:#f2557a;--cc-series2:#3987e5}
.cc-svg{width:100%;height:auto;font-family:var(--md-text-font-family,sans-serif)}
.cc-title{font-size:13px;font-weight:600;fill:var(--md-default-fg-color)}
.cc-axis{font-size:10px;fill:var(--md-default-fg-color--light)}
.cc-label{font-size:11px;font-weight:600;fill:var(--md-default-fg-color)}
.cc-grid{stroke:var(--md-default-fg-color--lightest);stroke-width:1}
.cc-line{fill:none;stroke:var(--cc-series);stroke-width:2;stroke-linejoin:round}
.cc-line2{fill:none;stroke:var(--cc-series2);stroke-width:2;stroke-dasharray:6 3;stroke-linejoin:round}
.cc-dot{fill:var(--cc-series);stroke:var(--md-default-bg-color);stroke-width:2}
.cc-line2-dot{fill:var(--cc-series2)}
.cc-hit{fill:transparent}
.cc-hit:hover{fill:var(--md-default-fg-color--lightest)}
</style>"""


def table(data) -> str:
    years = [1995, 1997, 1999, 2000, 2003, 2005, 2008, 2010, 2013, 2015, 2016, 2017, 2020,
             2022, 2025, 2026]
    rows = ["| Year | Peak, CPU | Peak, GPU | Peak, total | CPU cores | Memory | Storage |",
            "| ---- | --------: | --------: | ----------: | --------: | -----: | ------: |"]
    for y in years:
        r = data[y]
        gpu = fmt('tflops', r['gpu']) if r['gpu'] else "–"
        rows.append(f"| {y} | {fmt('tflops', r['tflops'])} | {gpu} | {fmt('tflops', r['total'])} | "
                    f"{fmt('cores', r['cores'])} | "
                    f"{fmt('ram', r['ram'])} | {fmt('storage', r['storage']) if r['storage'] else 'unknown'} |")
    return "\n".join(rows)


def main() -> None:
    import sys
    page = Path(sys.argv[1]) if len(sys.argv) > 1 else PAGE
    data = totals()
    block = (f"{START}\n<div class=\"cc-figure\" markdown=\"0\">\n{STYLE}\n{svg(data)}\n</div>\n\n"
             f"*Totals for all machines in service at any time in each year, on log scales. "
             f"Hover a year for its value.*\n\n{table(data)}\n{END}")
    text = page.read_text(encoding="utf-8")
    if START not in text:
        raise SystemExit(f"markers {START} / {END} not found in {page}")
    head, _, rest = text.partition(START)
    _, _, tail = rest.partition(END)
    page.write_text(head + block + tail, encoding="utf-8")
    for y in (2000, 2010, 2017, 2026):
        print(y, {k: fmt(k, v) for k, v in data[y].items()})


if __name__ == "__main__":
    main()
