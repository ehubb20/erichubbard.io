#!/usr/bin/env python3
"""Typeset assets/eric-hubbard-resume-scrubbed.docx into assets/eric-hubbard-resume.pdf.

One-off generator, NOT a build step. The .docx is the source of truth; this only
lays it out in the site's register (Helvetica base-14, so nothing is embedded and
the file stays small). Re-run it after editing the .docx.

Needs reportlab, which the site itself does not:

    python3 -m venv .venv && .venv/bin/pip install reportlab
    .venv/bin/python tools/make_resume_pdf.py

The .docx must already be scrubbed — phone removed, location softened. This
script refuses to run if it finds a phone number.
"""

import pathlib
import re
import sys
import zipfile

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, KeepTogether,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/eric-hubbard-resume-scrubbed.docx"
OUT = ROOT / "assets/eric-hubbard-resume.pdf"

INK = HexColor("#1b1b18")
SOFT = HexColor("#45453f")
MUTED = HexColor("#6e6e66")
RULE = HexColor("#c8c8be")


# ---------------------------------------------------------------- parse docx

def runs_of(para):
    """Visible text runs of a paragraph, ignoring anything in the properties block."""
    out = []
    for r in re.findall(r"<w:r>.*?</w:r>", para, re.S):
        text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", r, re.S))
        if text:
            out.append(text)
    return out


def unescape(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&apos;", "'"))


def parse(path):
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf8")
    if re.search(r"\(\d{3}\)\s*\d{3}-\d{4}|\b\d{3}-\d{3}-\d{4}\b", xml):
        sys.exit("refusing to run: the .docx still contains a phone number")

    blocks = []
    for i, p in enumerate(re.findall(r"<w:p [^>]*>.*?</w:p>|<w:p/>", xml, re.S)):
        text = unescape("".join(runs_of(p))).strip()
        if not text:
            continue
        size = re.search(r'<w:sz w:val="(\d+)"', p)
        size = int(size.group(1)) if size else None
        bold = "<w:b/>" in p
        bullet = "numPr" in p
        parts = [unescape(r).strip() for r in runs_of(p) if r.strip()]

        if i == 0:
            kind = "name"
        elif size == 26:
            kind = "subtitle"
        elif size == 18:
            kind = "contact"
        elif bullet:
            kind = "bullet"
        elif size == 21 and bold:
            kind = "role"
        elif bold and size is None and len(text) < 40 and text.isupper():
            kind = "section"
        elif blocks and blocks[-1][0] == "role":
            kind = "org"
        else:
            kind = "body"
        blocks.append((kind, text, parts))
    return blocks


# ---------------------------------------------------------------- styles

def styles():
    def s(name, **kw):
        kw.setdefault("fontName", "Helvetica")
        kw.setdefault("textColor", INK)
        return ParagraphStyle(name, **kw)

    return {
        "name": s("name", fontName="Helvetica-Bold", fontSize=21, leading=24, spaceAfter=2),
        "subtitle": s("subtitle", fontSize=11.5, leading=14, textColor=SOFT, spaceAfter=5),
        "contact": s("contact", fontSize=8.6, leading=12, textColor=MUTED, spaceAfter=2),
        "section": s("section", fontName="Helvetica-Bold", fontSize=7.8, leading=10,
                     textColor=MUTED, spaceBefore=10, spaceAfter=2.5),
        "body": s("body", fontSize=9.05, leading=11.9, textColor=SOFT, alignment=TA_JUSTIFY,
                  spaceAfter=2.5),
        "role": s("role", fontName="Helvetica-Bold", fontSize=10, leading=12.5),
        "date": s("date", fontSize=8.4, leading=12.5, textColor=MUTED, alignment=2),
        "org": s("org", fontSize=8.9, leading=11, textColor=MUTED, spaceAfter=2.5),
        "bullet": s("bullet", fontSize=9.05, leading=11.75, textColor=SOFT, spaceAfter=1.8,
                    leftIndent=11, bulletIndent=1, alignment=TA_JUSTIFY),
    }


def spaced_caps(text):
    """Letter-spacing isn't a paragraph property in reportlab, so fake it."""
    return "&nbsp;".join(text)


def build(blocks, out):
    st = styles()
    doc = BaseDocTemplate(str(out), pagesize=LETTER,
                          leftMargin=54, rightMargin=54, topMargin=48, bottomMargin=40,
                          title="Eric Hubbard · Résumé", author="Eric Hubbard",
                          subject="Business intelligence", creator="erichubbard.io")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame])])

    flow = []
    consumed = set()
    for idx, (kind, text, parts) in enumerate(blocks):
        if idx in consumed:
            continue
        esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if kind == "name":
            flow.append(Paragraph(esc, st["name"]))
        elif kind == "subtitle":
            flow.append(Paragraph(esc, st["subtitle"]))
        elif kind == "contact":
            # Runs arrive as "ehubb20@gmail.com", "|", "|   North Idaho" — strip the
            # docx's own separators so they don't double up with ours.
            cleaned = [p.strip(" | ") for p in parts]
            joined = "  ·  ".join(p for p in cleaned if p)
            flow.append(Paragraph(joined.replace("&", "&amp;"), st["contact"]))
            flow.append(Spacer(1, 4))
            flow.append(HRFlowable(width="100%", thickness=0.8, color=INK, spaceAfter=1))
        elif kind == "section":
            flow.append(Paragraph(spaced_caps(esc), st["section"]))
            flow.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=5))
        elif kind == "role":
            title = parts[0] if parts else esc
            date = parts[-1] if len(parts) > 1 else ""
            row = Table([[Paragraph(title.replace("&", "&amp;"), st["role"]),
                          Paragraph(date.replace("&", "&amp;"), st["date"])]],
                        colWidths=[doc.width * 0.68, doc.width * 0.32])
            row.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            # A role heading stranded at the foot of a page with its employer on the
            # next one reads as a mistake. Bind the heading to its org line and first
            # bullet so the group breaks as a unit.
            group = [row]
            for j in (idx + 1, idx + 2):
                if j >= len(blocks):
                    break
                k, t, _ = blocks[j]
                t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if k == "org":
                    group.append(Paragraph(t, st["org"]))
                elif k == "bullet":
                    group.append(Paragraph(t, st["bullet"], bulletText="•"))
                else:
                    break
                consumed.add(j)
            flow.append(KeepTogether(group))
        elif kind == "org":
            flow.append(Paragraph(esc, st["org"]))
        elif kind == "bullet":
            flow.append(Paragraph(esc, st["bullet"], bulletText="•"))
        else:
            flow.append(Paragraph(esc, st["body"]))

    doc.build(flow)


if __name__ == "__main__":
    if not SRC.exists():
        sys.exit(f"missing {SRC}")
    blocks = parse(SRC)
    build(blocks, OUT)
    kinds = {}
    for k, _, _ in blocks:
        kinds[k] = kinds.get(k, 0) + 1
    print(f"parsed {len(blocks)} blocks: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    pages = len(re.findall(rb"/Type\s*/Page[^s]", OUT.read_bytes()))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes, {pages} pages)")
    if pages > 2:
        print("  WARNING: a resume spilling past two pages usually wants tighter "
              "leading or fewer bullets, not a third page.")
