# erichubbard.io

Two-page portfolio site. Static HTML, one stylesheet, no build step, no dependencies.

Everything GitHub Pages serves lives under `docs/`. Anything outside it is source and
tooling that stays private to the repo.

```
docs/index.html                     About / résumé
docs/work/index.html                Work index, 3 entries
docs/work/wbr-exec-brief/index.html Case study (complete)
docs/work/wbr-exec-brief/deck/      Synthetic sample deck + preview.svg
docs/styles.css                     Everything (design tokens at the top)
docs/assets/                        Photo, deck preview, generated résumé PDF
docs/robots.txt, docs/sitemap.xml   Served at the site root

assets/eric-hubbard-resume-scrubbed.docx   Résumé source of truth (not served)
tools/make_charts.py                One-off chart generator (see below)
tools/make_resume_pdf.py            One-off résumé typesetter (see below)
```

The split matters: this repo is public, so every tracked file is readable on github.com
whether or not Pages serves it. `docs/` controls what the *site* exposes, not what the
*repo* exposes. Keep genuinely private notes untracked — `HANDOFF.md` is in `.gitignore`
for exactly this reason.

## Editing

Open the file, edit the HTML, commit. There is nothing to install and nothing to run.
Colours, type scale and spacing are all tokens at the top of `styles.css`.

The four charts in the sample deck are finished SVG committed into the HTML. The
site does not generate anything at load or deploy time. `tools/make_charts.py`
wrote them, and is kept only so the synthetic series can be changed later:

```bash
python3 tools/make_charts.py    # rewrites the <!-- CHART:name --> blocks in place
```

It needs no dependencies. Every mark is `currentColor` at some opacity, so the
charts follow the page theme instead of carrying a palette of their own.

`tools/make_resume_pdf.py` typesets the scrubbed `.docx` into `assets/eric-hubbard-resume.pdf`.
It is the one thing here with a dependency, kept out of the site entirely:

```bash
python3 -m venv .venv && .venv/bin/pip install reportlab
.venv/bin/python tools/make_resume_pdf.py
```

It refuses to run if it finds a phone number in the `.docx`, warns if the output
spills past two pages, and uses only the base-14 PDF fonts so nothing is embedded
(the file is ~8 KB).

## Before launch

- [x] Headshot is in place at `assets/headshot.jpeg`.
- [ ] Register `erichubbard.io`.
- [ ] `styles.css` pulls Barlow and Barlow Condensed from Google Fonts via `@import`,
      which breaks the "no external requests" convention below. Either self-host both
      families under `assets/fonts/` and drop the `@import`, or relax the convention.
- [ ] Nothing links to `assets/eric-hubbard-resume.pdf` yet. Add the download link to
      `index.html` if the résumé should be reachable from the site.

The résumé PDF is already generated and scrubbed: phone removed, location softened
to "North Idaho". `assets/eric-hubbard-resume-scrubbed.docx` is the source of truth;
edit it and re-run the generator (below) rather than editing the PDF.

## Deploying to GitHub Pages

Live at https://ehubb20.github.io/erichubbard.io/ — a *project* site, so it is served
from a subpath until a custom domain is attached. Every internal link is relative, so
the subpath works; the canonical and `og:url` tags still point at `erichubbard.io`.

1. Repo → Settings → Pages → Source: **Deploy from a branch**, branch `main`,
   folder **`/docs`**. (Branch deploys only allow `/` or `/docs`, not an arbitrary folder.)
2. Push to `main`; Pages rebuilds on its own. There is no build step.
3. For `erichubbard.io`: register the domain, add a `CNAME` file in `docs/` containing
   `erichubbard.io`, then point DNS at GitHub — four apex `A` records
   (185.199.108–111.153) plus `www` CNAME → `ehubb20.github.io`. Check the current
   addresses in GitHub's docs before relying on them.
4. Settings → Pages → **Enforce HTTPS** once the certificate provisions.

## Conventions worth keeping

- **No client names, employer names, account identifiers, colleague names,
  hostnames or schema names anywhere under `docs/work/`.** Employers appear only in the
  experience section on the home page.
- Every figure in `docs/work/` is synthetic and labelled as such.
- The deck sample carries `noindex` as a page-level meta tag, not just a `robots.txt`
  rule, so it stays out of search results even when served from a subpath where
  `robots.txt` is ignored. Keep it that way.
- No external requests: no CDN fonts, no analytics, no embeds. Keeps the site fast and
  dependency-free. `styles.css` currently breaks this with a Google Fonts `@import` —
  see the launch checklist above.
