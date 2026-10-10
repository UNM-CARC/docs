---
title: "Web archive of the old center websites"
description: "Browsable copies of the HPCERC, AHPCC, Alliance Supercluster, HPC@UNM and early CARC websites, 1998 to 2016, rebuilt from Internet Archive captures with working local links and images."
type: Reference
tags:
  - About
  - History
status: draft
generated:
  by: "process:claude-code"
  at: "2026-10-10T00:00:00Z"
sources:
  - id: internet-archive
    resource: "https://web.archive.org/web/2000/http://www.ahpcc.unm.edu/"
    title: "Internet Archive captures of hpcerc.unm.edu, ahpcc.unm.edu, alliance.unm.edu, hpc.unm.edu and carc.unm.edu, 1998–2016"
    author: "team:internet-archive"
  - id: build-script
    resource: "scripts/build_web_archive.py"
    title: "Script that rebuilds the archive from the staged Wayback captures"
    author: "team:unm-carc"
---

# Web archive of the old center websites

!!! note "Archived pages, not current information"

    These are copies of web pages as they were between 1998 and 2016.
    Accounts, machines, people, phone numbers and policies on them are long
    out of date. For the story of the machines, see the
    [History of CARC computing](history.md).

Before it was CARC, the center ran websites under its earlier names: the
High Performance Computing, Education & Research Center (**HPCERC**), the
Albuquerque High Performance Computing Center (**AHPCC**) with its NCSA
Alliance Linux supercluster site, and **HPC@UNM**.
None of those sites survive on UNM servers. The Internet Archive's
Wayback Machine captured many of their pages, and this section rebuilds
them from those captures so they can be browsed again from CARC's own
site.

## Snapshots

Each snapshot is one era of one site. Open a snapshot's name for its home
page, or its page count for a list of every page it holds.

<!-- archive-table:start -->
| Snapshot | Pages | What it shows |
| --- | --- | --- |
| [HPCERC, 1998–2000](web-archive/hpcerc-1998/index.html) | [3](web-archive/hpcerc-1998/archive-contents.html) | The earliest captures of hpcerc.unm.edu (the High Performance Computing, Education & Research Center), which shared its pages with AHPCC. |
| [HPCERC, 2002–2003](web-archive/hpcerc-2002/index.html) | [35](web-archive/hpcerc-2002/archive-contents.html) | HPCERC after its 2002 redesign, with machine pages for Los Lobos, Roadrunner, BlackBear, Vista Azul and the Access Grid. |
| [AHPCC, 1999–2001](web-archive/ahpcc-2000/index.html) | [141](web-archive/ahpcc-2000/archive-contents.html) | The Albuquerque High Performance Computing Center in the Los Lobos and Roadrunner era. |
| [AHPCC, 2001–2003](web-archive/ahpcc-2002/index.html) | [150](web-archive/ahpcc-2002/archive-contents.html) | The AHPCC site after its 2001 reorganisation into the Computing/ section, through its 2003 rename to HPC@UNM. |
| [Alliance Supercluster, 2000](web-archive/alliance-2000/index.html) | [4](web-archive/alliance-2000/archive-contents.html) | alliance.unm.edu as the home of the NCSA Alliance Linux supercluster (Roadrunner) run by AHPCC. |
| [alliance.unm.edu, 2001–2003](web-archive/alliance-2002/index.html) | [79](web-archive/alliance-2002/archive-contents.html) | alliance.unm.edu once it served the AHPCC and HPCERC site, with the Alliance account and user-guide pages. |
| [alliance.unm.edu, 2004–2006](web-archive/alliance-2006/index.html) | [62](web-archive/alliance-2006/archive-contents.html) | Later captures of alliance.unm.edu, which by then served the HPC@UNM site. |
| [HPC@UNM, 2003–2005](web-archive/hpc-2004/index.html) | [121](web-archive/hpc-2004/archive-contents.html) | The Center for High Performance Computing at UNM before its move to Plone. |
| [HPC@UNM and CARC, 2006–2013](web-archive/hpc-2010/index.html) | [148](web-archive/hpc-2010/archive-contents.html) | The Plone site on hpc.unm.edu, retitled UNM Center for Advanced Research Computing around 2010, in the Encanto, Nano and Xena era. |
| [CARC, 2015–2016](web-archive/carc-2015/index.html) | [76](web-archive/carc-2015/archive-contents.html) | The first Center for Advanced Research Computing site, also served under the old AHPCC and HPCERC hostnames. |
<!-- archive-table:end -->

## How the copies were made

- **Source.** Pages and images were downloaded from the Wayback Machine in
  October 2026 (the home page once a year, plus every page whose address
  matched keywords about machines, people, accounts, documentation and
  news). Within a snapshot, each page is the capture nearest that
  snapshot's reference date, so neighbouring pages can be a few months
  apart.
- **Unchanged content.** Each page's HTML is kept byte for byte as it was
  captured. Only addresses were changed, and a small yellow banner was
  added at the top naming the capture date with a link to the original
  Wayback copy.
- **Links.** A link to a page that was saved goes to the local copy, in the
  same snapshot or the nearest other one. A link to a page that was not
  saved, or to any outside site, goes to the Wayback Machine's capture
  nearest the date of the page you are on.
- **Images.** Images that were downloaded are served locally. Small
  icons the Internet Archive never saved (navigation tabs, bullets,
  arrows) were redrawn in the period style; each one is labelled as a
  modern recreation in its alt text and tooltip, and the page banner says
  so. Grey boxes mark other images that were never archived. The rest,
  and all stylesheets and scripts, load from the Wayback Machine, so some
  pages look plainer when the Internet Archive cannot be reached.
- **Left out.** Personal home directories (`/~user`), intranet and
  timesheet pages, and SSH host-key listings.

To rebuild after adding captures, run `python3 scripts/build_web_archive.py`
with the staged captures in `.wayback/` (kept out of `.cache/`, which
`zensical build --clean` empties). Corrections and missing
pages are welcome; see [contributing](contributing.md).
