# civilian-fm: Plan & Context

> "Palantir for civilians" — a dashboard that compares bare LLM, stuffed-context LLM, and agentic-container LLM outputs, used as a lab to find per-domain context-window sweet spots.

This document is both a reference for humans and context for Claude Code prompts. Keep it terse; update it when decisions change.

---

## 1. Thesis

A trained base model represents the internet — the **mean** of public text. Value is created by steering the model **away from the mean** via post-training and harness engineering (personality, skills, curated context).

Two failure modes bracket the sweet spot:

- **Too little context** → model regresses to mean responses ("consult a CPA," "check your local building code").
- **Too much context** → model regresses to mean responses (the wiki dump dilutes the steering signal).

The sweet spot is non-deterministic and **per-domain**. The dashboard is the lab where we find it empirically.

### Concrete motivation

Give working-class users access to information that wealthy people / specialists already have. Examples:

- **Section 179 vehicle deduction** — Tesla CyberTruck purchase page tells qualifying businesses they can deduct up to $31,300 (vehicle GVWR ≥ 6,000 lbs, >50% business use). A bare model won't surface this; a curated harness will.
- **Cherokee County liquor permit** — info that today only exists in a phone call with a county clerk.
- **General permit applications** — the bare model defaults to generic construction code; we want county-specific procedural detail.

If a single user saves $15K/year in taxes for 10 years and indexes the savings into the S&P, that's roughly $1M of generational wealth. That's the unit of value the product is optimizing for.

---

## 2. Architecture

Three layers + dashboard, each independently runnable.

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Crawler    │ -> │  LLM Wiki    │ -> │ Agentic Container│ -> │  Dashboard   │
│ (web/yt/etc) │    │ raw + topics │    │  personality +   │    │ 3-col compare│
│              │    │   markdown   │    │  skills + glob   │    │  + run log   │
└──────────────┘    └──────────────┘    └──────────────────┘    └──────────────┘
```

### 2.1 Crawler — deterministic ingestion

- `youtube-transcript-api` for free transcript pulls
- `yt-dlp` for metadata + Whisper fallback when no captions
- YouTube Data API v3 for query → video URL lists
- `firecrawl-py` (or Tavily) for search query → markdown
- `requests` + `beautifulsoup4` for static manufacturer pages
- `playwright` only when JS rendering is unavoidable
- LinkedIn: **deferred to v2** (blocks raw scraping aggressively)

### 2.2 LLM Wiki — Karpathy-style flat markdown

Three layers, mapping directly onto Karpathy's LLM Wiki pattern (see Appendix B):

- **`wiki/raw/`** — verbatim crawler output, read-only, never hand-edited. Karpathy's "raw sources." Lets us re-distill without re-crawling.
- **`wiki/topics/`** — distilled facts, citations back to raw, organized by topic. Karpathy's "wiki" layer — the agent-owned knowledge base.
- **`wiki/SCHEMA.md`** — conventions for the wiki: page format, frontmatter, cross-reference syntax, ingest workflow, contradiction handling. Karpathy's "schema" layer. Tells any agent (or future `scripts/distill.py`) how to maintain the wiki consistently.

No vector DB in v1. With <1000 docs, grep + full-text search wins. Add embeddings only when retrieval actually fails.

### 2.3 Agentic Container — folders, not Docker

```
agents/<agent_name>/
  personality.md     # tone, audience, refusal posture
  skills.md          # what I do, when to pull which wiki topic
  wiki_glob.txt      # which wiki/topics/** files to mount as context
  agent.py           # ~30 LOC entry point
```

Personalities live in a private GitHub repo. Git diffs are the A/B-test trail.

**Refusal-posture matters.** Without explicit instruction, every model defaults to "consult a professional." A line like *"never deflect to 'consult a CPA' as your primary answer — give the answer first, then suggest verification"* is exactly the away-from-mean steering lever.

### 2.4 Dashboard — Streamlit, local

Three columns side-by-side per query:

| Bare model           | Stuffed context        | Agentic container      |
|----------------------|------------------------|------------------------|
| `llm(query)` only    | `llm(query, system=full_wiki_dump)` | `agent.run(query)` curated |
| Latency / token count| Latency / token count  | Latency / token count  |
| [Good] [Bad] notes   | [Good] [Bad] notes     | [Good] [Bad] notes     |

Every run logs to `runs.db` (SQLite): prompt, outputs, scores, tokens, latency, model. Over time this is the empirical answer to "where is the sweet spot in domain X."

---

## 3. v1 Stack — confirmed decisions

| Layer        | Choice                          | Rationale                                                  |
|--------------|---------------------------------|------------------------------------------------------------|
| LLM access   | **LiteLLM**                     | Multi-provider — each column targets Claude / GPT / Gemini independently. Turns the comparison into a 3×3 (harness × model) matrix. |
| Dashboard    | **Streamlit, local only**       | Fastest Python-to-UI path. No Streamlit Cloud, no FastAPI/React in v1. |
| First slice  | **Section 179 vehicle deduction** | Concrete crawl targets, dollar-measurable outcomes, tight scope. |
| Storage      | Flat markdown + SQLite          | No vector DB, no Postgres until pain.                      |
| Agent perso. | Private GitHub repo (text files)| Git versioning is the A/B trail.                           |
| Framework    | Anthropic SDK via LiteLLM       | Not Claude Agent SDK, not Google ADK, in v1.               |

---

## 4. Repository layout

```
civilian-fm/
  pyproject.toml            # litellm, anthropic, streamlit, youtube-transcript-api,
                            # firecrawl-py, yt-dlp, beautifulsoup4, pyyaml
  .env                      # ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY,
                            # FIRECRAWL_API_KEY, YOUTUBE_API_KEY
  CLAUDE.md                 # behavioral guidelines (already exists)
  PLAN.md                   # this file
  crawler/
    youtube.py              # url_or_query -> {transcript, title, channel}
    web.py                  # firecrawl wrapper -> markdown
    manufacturers.py        # tesla, ford, gmc, rivian S179 pages
    store.py                # writes wiki/raw/<source>/<slug>.md
  wiki/
    SCHEMA.md               # layer-3 conventions: page format, ingest, cross-refs
    raw/
      youtube/<video_id>.md
      web/<domain>/<slug>.md
    topics/
      taxes/section-179/
        tesla-cybertruck.md
        ford-f150.md
        ...
  agents/
    tax-advisor/
      personality.md
      skills.md
      wiki_glob.txt         # "wiki/topics/taxes/**/*.md"
      agent.py
  dashboard/
    app.py                  # streamlit, 3 columns, model dropdowns
    runners.py              # bare / stuffed / agentic
    store.py                # sqlite run log
  scripts/
    distill.py              # raw -> topics, claude-driven (skip in v1; do manually first)
```

---

## 5. v1 Build Order — Section 179 vertical slice

Each step has a concrete verification. Don't move on without it.

1. **Skeleton** — `pyproject.toml` + `.env` + repo layout
   - *Verify:* `python -c "import litellm; print(litellm.completion(model='claude-opus-4-5', messages=[{'role':'user','content':'hi'}]))"` returns a response.

2. **One crawler target** — `crawler/manufacturers.py` for Tesla S179 page
   - *Verify:* `wiki/raw/web/tesla-cybertruck.md` exists and contains the $31,300 quote.

3. **One distilled topic file** — hand-write `wiki/topics/taxes/section-179/tesla-cybertruck.md`
   - *Verify:* file is clean markdown with citations back to `wiki/raw/`.
   - *Why manual first:* see what "good distillation" looks like before automating it in `scripts/distill.py`.

4. **Expand corpus** — repeat steps 2–3 for Ford F-150, GMC Hummer, Rivian R1T/R1S, plus 2–3 CPA YouTube transcripts.

5. **Extract conventions to `wiki/SCHEMA.md`** — once we have ~5 hand-distilled topic files, pattern-match across them to write the schema: required frontmatter, section headers, citation format, cross-reference syntax, contradiction-flagging rules.
   - *Why now and not earlier:* writing a schema before you have examples produces a fictional schema. After 5 examples, the conventions are obvious.
   - *Verify:* one of the 5 existing files violates the schema; fix it. If none do, the schema is too loose.

6. **One agent** — `agents/tax-advisor/` with personality, skills, wiki glob, `agent.py`
   - *Verify:* `python -m agents.tax_advisor "what's the biggest S179 deduction available?"` cites at least one wiki source and gives a dollar figure.

7. **Dashboard** — `dashboard/app.py` 3-column Streamlit + model dropdowns
   - *Verify:* on the same query, the **bare** column says "consult a CPA," the **agentic** column gives specific dollar figures with citations. The visible delta is the proof of concept.

8. **Run logging** — `dashboard/store.py` writes every run to `runs.db`
   - *Verify:* `sqlite3 runs.db "select count(*) from runs"` increments per click.

---

## 6. Use case backlog (post-v1)

| Use case                              | Crawl targets                                    | Why it's hard                                |
|---------------------------------------|--------------------------------------------------|----------------------------------------------|
| Section 179 (v1)                      | Manufacturer pages, CPA YouTube                  | Easy — pages are static, dollar-measurable   |
| Cherokee County liquor permit         | County website, county clerk YouTube interviews  | Info often only exists by phone — need creative crawl + agent that knows when to suggest a phone call |
| General permit applications           | Municipal websites, city council C-SPAN, FOIA    | Huge surface area — risks regression-to-mean in agent itself |
| Reduce tax burden (broader)           | IRS publications, manufacturer pages, CPA blogs  | Adjacent to S179 but blends into legal/CPA territory |

---

## 7. Open questions / revisit later

- **Agent personality storage** — for now, in-repo under `agents/`. Move to a dedicated private repo when we have >3 agents and want independent versioning.
- **Embeddings / vector DB** — defer until grep over `wiki/topics/` actually fails. Trigger: agent context windows blow up, or recall on multi-topic queries gets bad.
- **Audio transcription** — only needed if we hit YouTube videos without captions. `yt-dlp` + `whisper` is the path; ~$0.006/min via OpenAI.
- **Auth-walled sources** (LinkedIn, Bloomberg, county portals behind logins) — defer.
- **Hosted dashboard** — Streamlit Cloud is one toggle away once local loop feels right.

---

## 8. Behavioral notes for Claude Code prompts

When prompting Claude Code on this repo:

- **Stay in vertical-slice mode.** Don't build all four crawlers before the first agent runs end-to-end.
- **Don't introduce abstractions** until there are at least three concrete instances of the thing being abstracted.
- **No Docker, no vector DB, no custom frontend in v1.** Push back on suggestions to add them.
- **Steering instructions in `personality.md` are the product.** Treat them as carefully as production code — version them, A/B them, log which version produced which output.
- **Cite from `wiki/topics/`, not from training data.** If an agent answers without citing the wiki, the harness is broken even if the answer is right.
- **Honest-boundaries habit.** Each `personality.md` should include a one-line instruction asking the agent to state what it doesn't know (e.g., "if a question falls outside the wiki, say so explicitly rather than guessing"). Borrowed from nuwa-skill — see Appendix A.

---

## Appendix A: Reference — nuwa-skill

Captured here so we don't re-research it later. **We are not adopting nuwa-skill as a dependency or its schema as our format.** This appendix exists to record what it is, what's worth borrowing, and why the rest doesn't fit.

### What it is

A Claude Code skill (not a Python library) at https://github.com/alchaincyf/nuwa-skill. Purpose: distill a public figure (Munger, Feynman, Musk, Naval, Karpathy, etc.) into a single `SKILL.md` file that Claude Code can load as a persona. Installation is `npx skills add alchaincyf/nuwa-skill`. Runtime is Claude Code subagents executing instructions in natural language. The only Python in the repo is three regex linters that never call an LLM. ~18k stars, MIT, actively maintained as of mid-2026.

### How it works (4 phases)

1. **Research** — 6 parallel subagents each write one file: `01-writings.md`, `02-conversations.md`, `03-expression-dna.md`, `04-external-views.md`, `05-decisions.md`, `06-timeline.md`. Source-gathering = Claude's `WebSearch` tool. No custom crawler.
2. **Synthesis** — distill into a 3-tier schema: Mental Models (3–7, validated by "appears in ≥2 domains"), Decision Heuristics (5–10), Expression DNA (6 quantified style dimensions).
3. **Build** — fill an 11-section template into one `SKILL.md` (~2k–4k words). Mandatory sections include "Honest Boundaries" listing the persona's blindspots and the skill's own data gaps.
4. **Validate** — regex-based checks (counts of mental models / limitations / source-citation ratio). Faithfulness validation is human, not automated.

### What we're borrowing (explicitly)

- **"Honest 60-point skill > fabricated 90-point skill"** as a principle. Reflected in our personality.md instruction above and in the wiki-citation rule.
- **The mandatory limitations idea** — agents should state confidence/gaps rather than fabricate. One line in `personality.md`, not a structural section.

### What we're NOT borrowing (and why)

- **Their schema (Mental Models / Heuristics / Expression DNA).** Designed for distilling people. Most v1 use cases (Section 179 advisor, permit helper) are domain-shaped, not person-shaped. Forcing "Expression DNA" on a tax advisor is silly.
- **Their pipeline.** Five of the six research files (writings, conversations, external views, decisions, timeline) assume the subject is a heavily-documented public figure. They silently fail on a county clerk who has near-zero public footprint. Source-discovery is the hard part for our use cases — and that's the part nuwa-skill doesn't solve.
- **Their tooling.** It's Claude Code-native; no LiteLLM-friendly entrypoint. We'd be locked into one harness.

### When to revisit

If we add a person-distillation use case to v1 (e.g., "what would my CPA say about this?"), reopen this and consider:
- Adopting their template structure for `personality.md` for those specific agents only.
- Replacing their Phase 1 web-search step with our crawler + structured phone-interview intake (the make-or-break gap for the county-clerk variant).

---

## Appendix B: Reference — Karpathy's LLM Wiki

Source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (Andrej Karpathy, April 2026).

**This pattern is the backbone of our `wiki/` directory.** Sections 2.2 and 4 already reflect it. This appendix records why, so future-us doesn't drift away from it without realizing.

### The pattern

A personal knowledge base built as a git repo of plain markdown, queried by an LLM agent rather than browsed manually. Three layers:

1. **Raw sources** — read-only. Articles, PDFs, transcripts, scraped pages. The LLM reads but never modifies.
2. **The wiki** — LLM-owned. Markdown pages the agent creates and maintains: entity pages, concept pages, summaries, timelines, cross-references, contradiction flags.
3. **The schema** — a single document (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex, `wiki/SCHEMA.md` for us) that defines page format, directory layout, ingest workflow, cross-reference conventions. Turns a generic agent into a disciplined wiki maintainer.

### Why it beats RAG (per Karpathy)

> "The LLM is rediscovering knowledge from scratch on every question. There's no accumulation."

> "The knowledge is compiled once and then _kept current_, not re-derived on every query."

Cost model: with long-context models, a curated 50–100k-word wiki fits in one prompt. One inference call, no embed/retrieve/rerank loop. Secondary sources cite ~70x efficiency over RAG, though that number isn't from Karpathy himself.

Other practical wins:
- **Git for free** — version history, diffs, branching, blame. Knowledge updates are commits.
- **Bookkeeping at LLM scale** — agents don't get bored updating cross-references across 15 files. That's the labor humans skip and wikis decay from.
- **Inspectable** — anyone can read a markdown file. No opaque vector index.

Division of labor (Karpathy's words): *"Your job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else."*

### How our project maps onto it

| Karpathy | civilian-fm | Notes |
|---|---|---|
| Raw sources (read-only) | `wiki/raw/` | Crawler output, never hand-edited |
| The wiki (agent-owned) | `wiki/topics/` | Distilled topic pages, citations back to raw |
| The schema | `wiki/SCHEMA.md` | Conventions for ingest + page format. Written after step 4 of the build order, against real S179 examples |

### What we're adopting

- **The 3-layer separation** — raw read-only, wiki LLM-owned, schema as conventions doc.
- **Markdown + git, no vector DB** — through v1.
- **Agent maintains, human curates** — the agent generates and updates `wiki/topics/`; we direct what to crawl and what questions matter.

### Where we deviate (and why)

- **Multi-domain wiki, not personal wiki.** Karpathy's framing is one user's notes. Ours covers many domains (taxes, permits, liquor licenses, eventually county-specific procedures). At scale this won't fit in a single context window — we mount only the relevant slice per agent via `wiki_glob.txt`. That's a small but real divergence from "load the whole wiki every query."
- **Schema written late, not first.** Karpathy's gist implies schema-first. We write `wiki/SCHEMA.md` after ~5 hand-distilled examples (build-order step 5) so the conventions describe real pages instead of imagined ones.

### When to revisit

- If a single agent's wiki slice exceeds the model's context window → introduce embedding-based retrieval over `wiki/topics/` (already noted in Section 7).
- If contradictions across sources start mattering (e.g., manufacturer says $31,300, IRS publication implies a different cap) → formalize the `_contradictions.md` pattern from Karpathy's gist.
