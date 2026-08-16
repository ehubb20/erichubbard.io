# erichubbard.io

Two-page portfolio site. Static HTML, one stylesheet, no build step, no dependencies.

```
index.html                          About / résumé
work/index.html                     Work index — 3 entries
work/wbr-exec-brief/index.html      Case study (complete)
work/wbr-exec-brief/deck/           Synthetic sample deck + preview.svg
style.css                           Everything
assets/                             Photo + résumé PDF
```

## Editing

Open the file, edit the HTML, commit. There is nothing to install and nothing to run.
Colours, type scale and spacing are all tokens at the top of `style.css`.

## Before launch

- [ ] `assets/eric.jpg` — square, ~400×400, plain background. Then in `index.html`
      replace the `.photo-placeholder` div with
      `<img src="/assets/eric.jpg" alt="Eric Hubbard">`.
- [ ] `assets/eric-hubbard-resume.pdf` — **scrubbed copy**: phone number removed,
      location softened to "North Idaho". Do not upload the working résumé.
- [ ] Register `erichubbard.io`.

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
- The deck sample carries `noindex` — it should be read via the case study, not
  found cold in search results.
- No external requests: no CDN fonts, no analytics scripts beyond Cloudflare's,
  no embeds. Keeps the site fast and dependency-free.
