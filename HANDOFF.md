# Handoff: erichubbard.io

State as of 2026-08-16. Nothing is deployed yet; the domain is not registered yet.

Note: this file and `README.md` sit at the site root, so Cloudflare Pages will serve
them at `/HANDOFF.md` and `/README.md`. Neither contains anything sensitive, and
`robots.txt` disallows both. If that still bothers you, move the site files into a
`public/` directory and set the Pages output directory to `public`.

---

## What this is

A two-page portfolio site supplementing the résumé and LinkedIn. Static HTML, one
stylesheet, no framework, no build step, no external requests.

Run it locally:

```bash
python3 -m http.server 4321 --directory .
```

## Why it exists (decided, not up for re-litigation)

These were settled deliberately. Change them if you want, but know what you're changing.

| Decision | Choice |
|---|---|
| Purpose | A **proof page**. The AI-agent claim on the résumé reads as hype in one bullet; this exists to make it believable. |
| Reader | BI/analytics **leadership hiring managers** one step up, not recruiters (the résumé handles them) and not AI/ML managers. |
| Discoverability | Indexed, own domain. LinkedIn already owns your name in search; this reclaims some of it. |
| Contact surface | Email + LinkedIn only. **No phone.** Location softened to "North Idaho". |
| Attribution | Employers appear **only** in the experience section on the home page. Case studies attribute nothing. "Gierd" stays out of titles, meta, and `/work/`. |
| Client data | Fully synthetic. Real figures never appear. |
| Scope | Ship with one case study complete; the other two are summaries carrying their own artifact, with no dead links. |

## What's built

```
index.html                       About/résumé. Headline is Eric's own wording.
work/index.html                  Three entries. #1 links out; #2 and #3 are complete
                                 summaries with artifacts and no "read more".
work/wbr-exec-brief/             Full case study. Problem, constraint, architecture,
                                 stack, seven judgment calls, outcome.
work/wbr-exec-brief/deck/        Synthetic sample deck, 12 sections, 4 charts, noindex.
style.css                        Design tokens at the top.
tools/make_charts.py             One-off chart generator. Not a build step.
tools/make_resume_pdf.py         One-off résumé typesetter. Needs reportlab.
assets/                          Scrubbed .docx (source of truth) + generated PDF.
```

**Entry 1, WBR exec brief.** Complete. Seven judgment calls: failing closed on stale
data, "source not checked" vs "no activity", never inventing an owner, the ×28 unit
correction printed on the slide with its error bar, the credential-scope bug that
returned 19 of 79 issues with an HTTP 200, filtering tracker matches on the way back,
searching by function. Says 17 configured accounts.

An **architecture section** was added 2026-08-21 from the project's own `ARCHITECTURE.md`
(source kept out of this repo; a scrubbed copy is in the session scratchpad). Trimmed on
Eric's feedback the same day to three parts: the run as a chain of artifacts with its
diagram, the build/validate/publish ordering, and the four validation layers with what
each is blind to. Plus a `The stack` block using `dl.meta.tight`.

Cut on that pass, and do not put back without asking: the orchestration decisions
(07:15 timing, schedule vs. event trigger, serial looping), the config-baked-into-image
caveat, and the `What it still doesn't do` gaps. They were accurate but the section read
long. Deliberately never ported at all: the module inventory, credentials table, account
roster, and the known gaps about credential posture.

The judgment call about tracker scope was **corrected** in that pass. The page had said
the fix was to scope by project or by the account named in the title. The architecture
doc records a later finding: project-only *under*-reports, so the real fix keeps the
broad query and re-checks each match at a word boundary client-side.

**Entry 2, three-layer architecture.** Rewritten around how the design *eroded*: two
of three scheduled jobs live in the connector directory, one bypasses the connector
layer entirely, which is why the pipeline layer has nothing to chain. Ends on "naming
an empty layer in a README is not enforcement." The diagram shows the real state, not
the intended one.

**Entry 3, returns analysis.** Synthetic chart, plus an annotated SQL header showing
the join decisions, plus the callout that one marketplace exposes buyer free-text and
the largest one does not.

## Verified

- Light and dark both render; SVGs carry their own palettes.
- No horizontal page overflow at 375px. Metric tables restack into labelled blocks;
  diagrams get a scroll container with a legibility floor rather than shrinking to 6px type.
- Leak scan of `work/` is clean. No client names, account IDs, hostnames, schema names,
  or real colleague names. Fictional names in the deck were re-picked after three landed
  within a letter or two of real ones. Re-run 2026-08-21 after the architecture section
  landed, widened to cover warehouse dataset names, vault paths, internal ticket prefixes,
  service-account identities and every script name in the source doc. Clean.
  The scan script is in the session scratchpad as `leakscan.sh`, worth keeping if the
  site grows.
- Résumé PDF: 2 pages, resolves at `/assets/eric-hubbard-resume.pdf`, no phone number.

## Blocking launch

1. **Register `erichubbard.io`.** Was available 2026-08-16; `.com` belongs to a different
   Eric Hubbard (GoDaddy placeholder since Dec 2024).
2. **`assets/eric.jpg`**: square, ~400×400, plain background. Then replace the
   `.photo-placeholder` div in `index.html` with `<img src="/assets/eric.jpg" alt="Eric Hubbard">`.
3. **Confirm the account numbers** before publishing. The architecture doc says
   *seventeen configs, fifteen live* (two churned). The site says "17 accounts, one
   config file each" and "seventeen accounts configured" are both defensible, but the
   loose phrase "covers seventeen of them" was changed to "carries seventeen account
   configurations" on 2026-08-21 because it was not. If someone asks in an interview,
   the honest answer is seventeen built, fifteen currently running.
4. **Tell your manager** you're publishing anonymized writeups of your work.
5. Push to GitHub → Cloudflare Pages (preset `None`, no build command, output `/`),
   add the domain, enable Web Analytics (cookieless, so no consent banner).

## Open threads

- **Entry 2 length.** ~330 words plus a large figure, noticeably heavier than entry 3.
  If the page reads top-heavy, give it its own detail page rather than cutting it.
- **Case study length.** Entry 1 grew with the architecture section and was then trimmed
  back. Still the longest page on the site. If it grows again, a short table of contents
  under the standfirst earns its place before more prose does.
- **Detail pages for entries 2 and 3** were deferred by design. Same template as entry 1:
  Problem / Constraint / What I built / Judgment calls / Outcome.
- **`ai-bi` as a future entry.** Roughly half yours, and it is a *leadership* artifact:
  tooling that lets a junior analyst do dashboard work unaided. The home page now leads
  with leadership and the work section has no evidence of it. That gap is worth closing.
- **Certifications** are deliberately absent from the site and present in the PDF. They
  earn their place in an ATS and undercut you next to the case studies.

## Conventions to keep

- No client names, employers, account identifiers, colleague names, hostnames or schema
  names anywhere under `work/`.
- Every figure in `work/` is synthetic and labelled as such.
- No external requests: no CDN fonts, no third-party scripts, no embeds.
- Third-party tool names (Linear, Asana, Zendesk, Amazon, eBay, BigQuery, Kestra,
  1Password) are fine and used consistently; they are public products, not client
  information. Several already appear in the home-page tools list.
- **No em dashes anywhere.** Removed site-wide 2026-08-21 at Eric's request, including in
  SVG label text, the sample deck's no-data cells (now `n/a`), the chart generator, and
  the résumé PDF's bullet glyph. Use commas, colons, semicolons, parentheses or a full
  stop. `grep -rn \u2014 --include='*.html' --include='*.css'` should return nothing.
