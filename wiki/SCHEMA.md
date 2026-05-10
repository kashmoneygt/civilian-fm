# wiki/SCHEMA.md

Conventions for `wiki/raw/` and `wiki/topics/`. Layer 3 of Karpathy's LLM Wiki pattern (see `PLAN.md` Appendix B). Adopted after distilling 9 topics from 13 raw IRS pages — written against real examples, not in the abstract.

## Directory structure

```
wiki/
  SCHEMA.md           # this file
  raw/
    web/<slug>.md     # crawler output, never hand-edited
    youtube/<vid>.md
  topics/
    <domain>/<subdomain>/<topic>.md
```

Topic paths are hierarchical: `taxes/section-179/heavy-vehicles.md`, `taxes/s-corp/reasonable-compensation.md`. Pick the deepest path that still groups naturally with siblings.

## Frontmatter

### Raw pages (crawler-written, immutable)

```yaml
---
source: web | youtube
fetched_at: <UTC ISO timestamp>
url: <original URL>
title: <page or video title>
# web only: domain
# youtube only: video_id, language, uploader, duration_seconds
---
```

### Topic pages (LLM-distilled or hand-written)

```yaml
---
topic: <slash path matching the file location, no .md>
sources: [<basename of each raw file consulted>]
distilled_at: <UTC ISO timestamp>
distill_model: <model id used, or "human" if hand-written>
---
```

## Topic page structure

```markdown
# <Title>

<1-2 sentence summary. No throat-clearing. State what the page covers.>

## Key facts

- <fact> [source: <basename>.md]
- <fact> [source: <basename>.md]

## How it applies to an S-corp owner   # or whichever audience this topic serves

- <actionable bullet>
- <actionable bullet>

## Limits and gotchas

- <gotcha> [source: <basename>.md]

## Sources

- <basename>.md
- <basename>.md
```

## Hard rules

1. **Every fact cites a source.** `[source: <basename>.md]` inline. No uncited claims.
2. **Quote dollar figures and IRS phrasing verbatim** in quotation marks. Paraphrase the explanation, not the rule.
3. **If sources don't cover a topic, mark it explicitly.** Use `> not in sources` lines rather than fabricating. Better an honest 60-point page than a fabricated 90.
4. **No filler.** No "consult a tax professional" deflections. No throat-clearing. Facts only.
5. **Citation basenames must exist** in `wiki/raw/web/` or `wiki/raw/youtube/`. The source is the filename, not the URL.

## Cross-references

Use `[[topic-path]]` for wiki-internal references. Example:

> Section 179 vehicles interact with [[taxes/strategies/business-vehicle]] for non-vehicle deductions.

The agent runtime resolves these as files; no special tooling required for v1.

## Contradiction handling

When two sources disagree (e.g., a state-tax site contradicts an IRS publication):

1. Present both positions with their citations.
2. Add a `> Contradiction:` callout naming which source is authoritative for the reader's situation.
3. If material, file a `wiki/topics/_contradictions/<topic-slug>.md` page.

## Ingest workflow (for `scripts/distill.py` and humans)

1. Crawler writes new file under `wiki/raw/`.
2. Add a `(topic_path, [source_basenames], focus_prompt)` entry to `TOPIC_SPECS` in `scripts/distill.py`.
3. Run `uv run python -m scripts.distill`. The script reads the named raw files into the prompt and writes the distilled topic page.
4. Spot-check the output against the raw — at least one fact's citation should be verifiable by grep'ing the raw file.
5. If the topic is reusable across multiple agents, add it to the relevant `agents/<agent>/wiki_glob.txt`.

## Verification checklist before merging a new topic

- [ ] Frontmatter present and valid YAML.
- [ ] Every fact has a `[source: ...]` inline citation.
- [ ] At least one dollar figure or IRS rule quoted verbatim.
- [ ] Sources block lists every cited basename.
- [ ] No "consult a professional" deflections.
- [ ] Page renders cleanly in any markdown viewer.
