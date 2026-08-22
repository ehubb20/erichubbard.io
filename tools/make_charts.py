#!/usr/bin/env python3
"""Generate the inline SVG charts for the synthetic sample deck.

One-off generator, NOT a build step: it writes finished SVG into
work/wbr-exec-brief/deck/index.html at the <!-- CHART:name --> anchors and the
result is committed. The site never runs this. Re-run it only if you want to
change the synthetic series.

    python3 tools/make_charts.py

Charts are monochrome — every mark is currentColor at some opacity — so they
follow the page's light/dark theme with no palette of their own.
"""

import pathlib
import re

W = 860
INK = "currentColor"

WEEKS = ["05-17", "05-24", "05-31", "06-07", "06-14", "06-21", "06-28",
         "07-05", "07-12", "07-19", "07-26", "08-02", "08-09"]

GMV = [742_000, 815_400, 903_100, 868_700, 1_012_300, 1_145_900, 1_079_400,
       1_238_600, 1_321_000, 1_254_700, 1_398_200, 1_166_200, 1_847_300]

UNITS = [2410, 2630, 2880, 2790, 3120, 3470, 3310, 3690, 3910, 3760, 4120, 3834, 5412]

# Channel shares drift over the window; the final week is pinned to the exact
# figures quoted on the Channel Mix slide.
SHARES = [(.402, .351, .244, .003), (.399, .353, .245, .003), (.396, .350, .251, .003),
          (.394, .349, .254, .003), (.391, .351, .255, .003), (.389, .348, .260, .003),
          (.387, .350, .260, .003), (.386, .347, .264, .003), (.385, .349, .263, .003),
          (.386, .346, .265, .003), (.384, .348, .265, .003), (.383, .350, .264, .003)]
CHANNELS = ["eBay", "Backmarket", "Amazon", "Walmart"]
LAST_WEEK = (712_540, 645_180, 484_900, 4_680)

IN_STOCK = [31.2, 32.8, 33.5, 34.1, 35.9, 36.4, 35.8, 37.2, 38.0, 37.6, 38.9, 37.9, 41.7]
DAYS_SUPPLY = [14, 13, 12, 12, 11, 10, 10, 9, 8, 8, 7, 6, 5]

TRAFFIC = [392_000, 405_000, 421_000, 410_000, 438_000, 447_000, 431_000,
           452_000, 466_000, 458_000, 471_000, 414_752, 478_210]
CONVERSION = [.31, .32, .33, .33, .34, .35, .35, .36, .36, .36, .37, .33, .40]


def channel_series():
    """Per-week dollars per channel, with the last week pinned to exact values."""
    out = []
    for gmv, share in zip(GMV[:-1], SHARES):
        out.append(tuple(round(gmv * s) for s in share))
    out.append(LAST_WEEK)
    return out


def money(v):
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    return f"${round(v/1000)}k"


def axis_label(x, y, text, anchor="end", size=9.5, op=0.5):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="ui-monospace, Menlo, monospace" font-size="{size}" '
            f'fill="{INK}" opacity="{op}">{text}</text>')


def week_axis(x0, plot_w, n, y):
    """Every other week label, so 13 ticks don't collide on a narrow deck."""
    parts = []
    step = plot_w / n
    for i, wk in enumerate(WEEKS):
        if i % 2 and i != n - 1:
            continue
        cx = x0 + step * (i + 0.5)
        parts.append(axis_label(cx, y, wk, anchor="middle", size=9, op=0.45))
    return "".join(parts)


def gridlines(x0, x1, ticks, fmt):
    parts = []
    for val, y in ticks:
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" '
                     f'stroke="{INK}" stroke-opacity="0.12" stroke-width="1"/>')
        parts.append(axis_label(x0 - 8, y + 3.2, fmt(val)))
    return "".join(parts)


def frame(title, body, height):
    return (f'<svg viewBox="0 0 {W} {height}" role="img" aria-label="{title}" '
            f'style="max-width:{W}px">'
            f'<title>{title}</title>'
            f'<text x="0" y="12" font-family="ui-monospace, Menlo, monospace" '
            f'font-size="10" letter-spacing="1.4" fill="{INK}" opacity="0.5">'
            f'{title.upper()}</text>{body}</svg>')


# --------------------------------------------------------------------------- #

def chart_gmv():
    H, x0, top, bot = 250, 64, 34, 44
    plot_w, plot_h = W - x0 - 8, H - top - bot
    hi = 2_000_000
    step = plot_w / len(GMV)
    bw = step * 0.6

    ticks = [(v, top + plot_h - plot_h * v / hi) for v in (0, 500_000, 1_000_000, 1_500_000, 2_000_000)]
    p = [gridlines(x0, W - 8, ticks, money)]

    for i, v in enumerate(GMV):
        h = plot_h * v / hi
        x = x0 + step * i + (step - bw) / 2
        y = top + plot_h - h
        last = i == len(GMV) - 1
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                 f'fill="{INK}" opacity="{0.72 if last else 0.3}"/>')
        if last:
            p.append(f'<text x="{x + bw/2:.1f}" y="{y - 7:.1f}" text-anchor="middle" '
                     f'font-family="ui-monospace, Menlo, monospace" font-size="10.5" '
                     f'fill="{INK}" opacity="0.8">$1.85M</text>')

    p.append(week_axis(x0, plot_w, len(GMV), H - 24))
    p.append(axis_label(x0, H - 6, "13 complete Mon–Sun weeks · synthetic", anchor="start", size=9, op=0.4))
    return frame("Weekly GMV, 13 weeks", "".join(p), H)


def chart_channels():
    H, x0, top, bot = 268, 64, 34, 62
    plot_w, plot_h = W - x0 - 8, H - top - bot
    hi = 2_000_000
    step = plot_w / len(GMV)
    bw = step * 0.6
    opac = [0.72, 0.5, 0.3, 0.14]

    ticks = [(v, top + plot_h - plot_h * v / hi) for v in (0, 500_000, 1_000_000, 1_500_000, 2_000_000)]
    p = [gridlines(x0, W - 8, ticks, money)]

    for i, wk in enumerate(channel_series()):
        x = x0 + step * i + (step - bw) / 2
        y = top + plot_h
        for ch, v in enumerate(wk):
            h = plot_h * v / hi
            y -= h
            if h < 0.4:
                continue
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                     f'fill="{INK}" opacity="{opac[ch]}"/>')

    p.append(week_axis(x0, plot_w, len(GMV), H - 42))

    lx = x0
    for ch, name in enumerate(CHANNELS):
        p.append(f'<rect x="{lx}" y="{H-26}" width="10" height="10" fill="{INK}" opacity="{opac[ch]}"/>')
        p.append(f'<text x="{lx+15}" y="{H-17}" font-family="ui-sans-serif, system-ui, sans-serif" '
                 f'font-size="11.5" fill="{INK}" opacity="0.7">{name}</text>')
        lx += 26 + len(name) * 7.2
    return frame("GMV by channel, 13 weeks", "".join(p), H)


def line_panel(x0, y0, w, h, series, lo, hi, fmt, label, last_label):
    step = w / (len(series) - 1)
    pts = [(x0 + step * i, y0 + h - h * (v - lo) / (hi - lo)) for i, v in enumerate(series)]
    d = " ".join(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    area = d + f" L{pts[-1][0]:.1f} {y0+h:.1f} L{pts[0][0]:.1f} {y0+h:.1f} Z"

    p = [f'<text x="{x0}" y="{y0-12}" font-family="ui-monospace, Menlo, monospace" '
         f'font-size="9.5" letter-spacing="1.2" fill="{INK}" opacity="0.5">{label}</text>']
    for frac in (0, 0.5, 1):
        y = y0 + h - h * frac
        p.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+w}" y2="{y:.1f}" '
                 f'stroke="{INK}" stroke-opacity="0.12"/>')
        p.append(axis_label(x0 - 7, y + 3.2, fmt(lo + (hi - lo) * frac)))
    p.append(f'<path d="{area}" fill="{INK}" opacity="0.07"/>')
    p.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-opacity="0.65" stroke-width="1.6"/>')
    p.append(f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3.2" fill="{INK}" opacity="0.85"/>')
    p.append(f'<text x="{pts[-1][0]-4:.1f}" y="{pts[-1][1]-9:.1f}" text-anchor="end" '
             f'font-family="ui-monospace, Menlo, monospace" font-size="10.5" '
             f'fill="{INK}" opacity="0.8">{last_label}</text>')
    return "".join(p)


def chart_inventory():
    H, top = 210, 46
    pw, gap, x0 = 358, 62, 46
    ph = H - top - 42
    p = [line_panel(x0, top, pw, ph, IN_STOCK, 25, 45, lambda v: f"{v:.0f}%",
                    "IN-STOCK RATE", "41.7%"),
         line_panel(x0 + pw + gap + 16, top, pw, ph, DAYS_SUPPLY, 0, 16, lambda v: f"{v:.0f}",
                    "DAYS OF SUPPLY", "5")]
    p.append(week_axis(x0, pw, len(IN_STOCK), H - 22))
    p.append(week_axis(x0 + pw + gap + 16, pw, len(DAYS_SUPPLY), H - 22))
    p.append(axis_label(x0, H - 6,
                        "Cover has fallen every week for eight weeks while in-stock rose, so restock is not keeping pace with sell-through.",
                        anchor="start", size=9, op=0.45))
    return frame("Inventory health, 13 weeks", "".join(p), H)


def chart_traffic():
    H, x0, top, bot = 232, 64, 34, 44
    plot_w, plot_h = W - x0 - 56, H - top - bot
    hi = 500_000
    step = plot_w / len(TRAFFIC)
    bw = step * 0.6

    ticks = [(v, top + plot_h - plot_h * v / hi) for v in (0, 250_000, 500_000)]
    p = [gridlines(x0, x0 + plot_w, ticks, lambda v: f"{round(v/1000)}k")]

    for i, v in enumerate(TRAFFIC):
        h = plot_h * v / hi
        x = x0 + step * i + (step - bw) / 2
        p.append(f'<rect x="{x:.1f}" y="{top + plot_h - h:.1f}" width="{bw:.1f}" '
                 f'height="{h:.1f}" fill="{INK}" opacity="{0.55 if i == len(TRAFFIC)-1 else 0.22}"/>')

    clo, chi = 0.25, 0.45
    cpts = [(x0 + step * (i + 0.5), top + plot_h - plot_h * (v - clo) / (chi - clo))
            for i, v in enumerate(CONVERSION)]
    d = " ".join(("M" if i == 0 else "L") + f"{x:.1f} {y:.1f}" for i, (x, y) in enumerate(cpts))
    p.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-opacity="0.7" '
             f'stroke-width="1.6" stroke-dasharray="5 3"/>')
    p.append(f'<circle cx="{cpts[-1][0]:.1f}" cy="{cpts[-1][1]:.1f}" r="3.2" fill="{INK}" opacity="0.85"/>')
    for val in (0.25, 0.35, 0.45):
        y = top + plot_h - plot_h * (val - clo) / (chi - clo)
        p.append(axis_label(x0 + plot_w + 44, y + 3.2, f"{val:.2f}%"))

    p.append(week_axis(x0, plot_w, len(TRAFFIC), H - 24))
    p.append(f'<rect x="{x0}" y="{H-14}" width="10" height="9" fill="{INK}" opacity="0.35"/>')
    p.append(f'<text x="{x0+15}" y="{H-6}" font-family="ui-sans-serif, system-ui, sans-serif" '
             f'font-size="11" fill="{INK}" opacity="0.65">Traffic (left)</text>')
    p.append(f'<line x1="{x0+120}" y1="{H-9}" x2="{x0+140}" y2="{H-9}" stroke="{INK}" '
             f'stroke-opacity="0.7" stroke-width="1.6" stroke-dasharray="5 3"/>')
    p.append(f'<text x="{x0+146}" y="{H-6}" font-family="ui-sans-serif, system-ui, sans-serif" '
             f'font-size="11" fill="{INK}" opacity="0.65">Conversion rate (right)</text>')
    return frame("Traffic and conversion, 13 weeks", "".join(p), H)


CHARTS = {
    "gmv": chart_gmv,
    "channels": chart_channels,
    "inventory": chart_inventory,
    "traffic": chart_traffic,
}

if __name__ == "__main__":
    deck = pathlib.Path(__file__).resolve().parents[1] / "work/wbr-exec-brief/deck/index.html"
    html = deck.read_text()
    for name, fn in CHARTS.items():
        svg = fn()
        pattern = re.compile(
            rf"(<!-- CHART:{name} -->).*?(<!-- /CHART:{name} -->)", re.S)
        if not pattern.search(html):
            raise SystemExit(f"anchor <!-- CHART:{name} --> not found in {deck}")
        html = pattern.sub(lambda m: m.group(1) + "\n" + svg + "\n" + m.group(2), html)
        print(f"  {name}: {len(svg):,} bytes")
    deck.write_text(html)
    print(f"wrote {deck}")
