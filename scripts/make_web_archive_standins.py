#!/usr/bin/env python3
"""Draw stand-in icons for images the Wayback Machine never captured.

build_web_archive.py uses these, by file name, only when the original image is
missing from every capture. They imitate the late-1990s/2000s originals (nav
tabs, bullets, LaTeX2HTML navigation buttons, Plone document icons) so pages
read as intended without pretending to be the real files. Needs Pillow.

Usage: python3 scripts/make_web_archive_standins.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "web_archive_standins"
MAROON, ORANGE, NAVY, WHITE, GREY = (128, 0, 0), (230, 140, 30), (20, 50, 120), (255, 255, 255), (150, 150, 150)


def font(size, bold=True):
    for name in ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "Arial Bold.ttf", "Arial.ttf"):
        for base in ("/usr/share/fonts/truetype/dejavu/", "/Library/Fonts/", "/System/Library/Fonts/Supplemental/", ""):
            try:
                return ImageFont.truetype(base + name, size)
            except OSError:
                pass
    return ImageFont.load_default()


def save(img, name):
    img.convert("P", palette=Image.ADAPTIVE, colors=64).save(OUT / name, transparency=None) \
        if name.endswith(".gif") else img.convert("RGB").save(OUT / name, quality=90)


def button(text, w, h, bg, fg=WHITE, size=11, border=None):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    if border:
        d.rectangle([0, 0, w - 1, h - 1], outline=border)
    f = font(size)
    tw, th = d.textbbox((0, 0), text, font=f)[2:]
    d.text(((w - tw) / 2, (h - th) / 2 - 1), text, font=f, fill=fg)
    return img


def disc(size, color, bg=WHITE):
    img = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, size - 2, size - 2], fill=color)
    hl = tuple(min(255, c + 110) for c in color)
    d.ellipse([size * .3, size * .25, size * .5, size * .45], fill=hl)
    return img


def arrow(w, h, color, direction="right", bg=WHITE):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    pts = {"right": [(2, 2), (w - 3, h / 2), (2, h - 3)], "left": [(w - 3, 2), (2, h / 2), (w - 3, h - 3)],
           "up": [(2, h - 3), (w / 2, 2), (w - 3, h - 3)], "down": [(2, 2), (w / 2, h - 3), (w - 3, 2)]}[direction]
    d.polygon(pts, fill=color)
    return img


def pictogram(kind):
    img = Image.new("RGB", (16, 16), WHITE)
    d = ImageDraw.Draw(img)
    if kind == "print":
        d.rectangle([4, 1, 11, 6], outline=(60, 60, 60), fill=WHITE)
        d.rectangle([1, 6, 14, 11], fill=(110, 110, 110))
        d.rectangle([4, 10, 11, 14], outline=(60, 60, 60), fill=WHITE)
    elif kind == "link":
        d.rectangle([1, 5, 10, 14], outline=NAVY)
        d.line([7, 8, 14, 1], fill=NAVY, width=2)
        d.polygon([(9, 1), (14, 1), (14, 6)], fill=NAVY)
    elif kind == "pdf":
        d.polygon([(2, 1), (10, 1), (14, 5), (14, 15), (2, 15)], fill=WHITE, outline=(80, 80, 80))
        d.rectangle([2, 8, 14, 13], fill=(200, 20, 20))
        d.text((3, 7), "PDF", font=font(6), fill=WHITE)
    elif kind == "rss":
        d.rounded_rectangle([0, 0, 15, 15], 3, fill=(240, 120, 20))
        d.ellipse([3, 10, 6, 13], fill=WHITE)
        d.arc([-5, 3, 10, 18], 270, 360, fill=WHITE, width=2)
        d.arc([-9, -1, 14, 22], 270, 360, fill=WHITE, width=2)
    elif kind == "folder":
        d.polygon([(1, 4), (6, 4), (7, 6), (15, 6), (15, 14), (1, 14)], fill=(235, 190, 70), outline=(150, 110, 20))
    elif kind == "mail":
        d.rectangle([1, 3, 14, 12], fill=WHITE, outline=(80, 80, 80))
        d.line([1, 3, 7.5, 9, 14, 3], fill=(80, 80, 80))
    elif kind == "text":
        d.polygon([(3, 1), (10, 1), (13, 4), (13, 15), (3, 15)], fill=WHITE, outline=(80, 80, 80))
        for y in (6, 8, 10, 12):
            d.line([5, y, 11, y], fill=GREY)
    elif kind == "ical":
        d.rectangle([1, 2, 14, 14], fill=WHITE, outline=(80, 80, 80))
        d.rectangle([1, 2, 14, 5], fill=(200, 20, 20))
    return img


def main():
    OUT.mkdir(exist_ok=True)
    tabs = {"home_tab.gif": "Home", "research_tab.gif": "Research", "sitemap_tab.gif": "Site Map",
            "intranet_tab.gif": "Intranet", "education_tab.gif": "Education", "computing_tab.gif": "Computing",
            "help_desk_tab.gif": "Help Desk"}
    for name, label in tabs.items():
        save(button(label, 92, 20, MAROON), name)
        save(button(label, 92, 20, ORANGE), name.replace(".gif", "_hi.gif"))
    save(disc(15, MAROON), "ahpcc_bullet.gif")
    save(disc(15, NAVY), "hpcerc_bullet.gif")
    save(disc(9, MAROON), "list_bullet.jpg")
    save(disc(7, (60, 60, 60)), "dot.gif")
    save(Image.new("RGB", (8, 8), (200, 0, 0)), "redsquare.gif")
    save(arrow(9, 9, MAROON), "arrow-right.gif")
    save(arrow(7, 7, (200, 0, 0)), "arrow-right-red-lil.gif")
    save(arrow(10, 10, (200, 0, 0)), "home_redarrow2.gif")
    for n in (3, 4, 5):
        save(arrow(10, 10, MAROON), f"a_arrowline_{n}.gif")
    for d, nm in (("up", "spnavup.gif"), ("left", "spnavleft.gif"), ("right", "spnavright.gif"),
                  ("up", "nc_up.gif"), ("down", "nc_down.gif")):
        save(arrow(12, 12, NAVY, d), nm)
    # LaTeX2HTML navigation buttons (the generated proposal pages use these)
    for name, label, w in (("next_motif.gif", "next", 37), ("up_motif.gif", "up", 26),
                           ("previous_motif.gif", "previous", 63)):
        save(button(label, w, 24, (210, 210, 210), (0, 0, 0), 10, (90, 90, 90)), name)
        save(button(label, w, 24, (225, 225, 225), GREY, 10, (170, 170, 170)), name.replace(".gif", "_gr.gif"))
    for kind, names in (("print", ["print_icon.gif", "icon-print.gif"]), ("link", ["link_icon.gif"]),
                        ("pdf", ["pdf_icon.gif"]), ("rss", ["rss.gif"]), ("folder", ["folder_icon.gif"]),
                        ("mail", ["icon-email.gif", "mail_icon.gif"]), ("text", ["text.gif"]),
                        ("ical", ["icon_export_ical.png", "icon_export_vcal.png"])):
        for nm in names:
            pictogram(kind).save(OUT / nm)
    save(button("Search", 52, 20, (200, 200, 200), (0, 0, 0), 10, (110, 110, 110)), "search.gif")
    save(button("Go", 28, 20, (200, 200, 200), (0, 0, 0), 10, (110, 110, 110)), "gobuttonp.gif")
    print(len(list(OUT.iterdir())), "stand-ins in", OUT)


if __name__ == "__main__":
    main()
