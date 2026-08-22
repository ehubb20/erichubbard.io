# erichubbard.io

Two-page portfolio site. Static HTML, one stylesheet, no build step, no dependencies.

```
index.html                          About / résumé
work/index.html                     Work index, 3 entries
work/wbr-exec-brief/index.html      Case study (complete)
work/wbr-exec-brief/deck/           Synthetic sample deck + preview.svg
style.css                           Everything
assets/                             Photo + résumé PDF
tools/make_charts.py                One-off chart generator (see below)
```

## Editing

Open the file, edit the HTML, commit. There is nothing to install and nothing to run.
Colours, type scale and spacing are all tokens at the top of `style.css`.

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

- [ ] `assets/eric.jpg`: square, ~400×400, plain background. Then in `index.html`
      replace the `.photo-placeholder` div with
      `<img src="/assets/eric.jpg" alt="Eric Hubbard">`.
- [ ] Register `erichubbard.io`.

The résumé PDF is already generated and scrubbed: phone removed, location softened
to "North Idaho". `assets/eric-hubbard-resume-scrubbed.docx` is the source of truth;
edit it and re-run the generator (below) rather than editing the PDF.

## Deploying to Cloudflare Pages

1. Push this directory to a GitHub repo.
2. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git.
3. Build settings: **framework preset `None`**, build command **empty**,
   output directory **`/`**. There is no build step.
4. Custom domains → add `erichubbard.io` and `www.erichubbard.io`.
5. Web Analytics → enable for the domain. It is cookieless, so the site needs no
   consent banner. Do not add Google Analytics.

## Conventions worth keeping

- **No client names, employer names, account identifiers, colleague names,
  hostnames or schema names anywhere under `work/`.** Employers appear only in the
  experience section on the home page.
- Every figure in `work/` is synthetic and labelled as such.
- The deck sample carries `noindex`, so it should be read via the case study, not
  found cold in search results.
- No external requests: no CDN fonts, no analytics scripts beyond Cloudflare's,
  no embeds. Keeps the site fast and dependency-free.
