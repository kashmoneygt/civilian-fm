# civilian-fm: Plan & Context

> "Palantir for civilians" — a system where everyday people navigate bureaucratic friction by chatting with person-agents (real or composite) distilled from public sources, user contributions, and (eventually) AI-conducted interviews. A 4-variant dashboard (bare / persona / stuffed / agentic) measures how much each layer of the harness contributes.

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

## 2. Architecture (v2)

```
                              ┌─────────────────┐
                              │  Crawler        │  (unchanged from v1)
                              │  (web, youtube) │
                              └────────┬────────┘
                                       ▼
                              ┌─────────────────┐
                              │  wiki/raw/      │  immutable source of truth
                              └────────┬────────┘
                                       ▼
        ┌────────────────────────────────────────────────────────┐
        │                  Researcher Pipeline                   │
        │  (lean processor framework, ~30 LOC, ADK-inspired)     │
        │                                                        │
        │   GOAL ──► clarify ──► identify ─┐                     │
        │                                  ├─► research ─► distill│
        │   URL  ──► crawl ──► extract ────┘                     │
        │                                                        │
        └────────────────────┬───────────────────────────────────┘
                             ▼
                  ┌──────────────────────┐
                  │  entities/           │
                  │    people/<...>/     │  persona + skills + wiki + agent.py
                  │    topics/<...>/     │  overview + wiki  (no persona)
                  └──────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  PersonAgent         │  Python container — runnable
                  │  (Python container)  │  loads persona, skills, wiki,
                  └──────────────────────┘  resolves [[topic:...]] refs
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Dashboard           │  bare / persona / stuffed / agentic
                  │  4-variant compare   │
                  └──────────────────────┘
```

### 2.1 Crawler — deterministic ingestion (unchanged from v1)

`youtube-transcript-api`, `yt-dlp`, `requests` + `beautifulsoup4`. Writes to `wiki/raw/<source>/<slug>.md`. The crawler stays dumb. What changed in v2 is the **research orchestrator** that decides what to crawl.

### 2.2 Wiki — flat markdown, Karpathy pattern

- `wiki/raw/` — verbatim crawler output. Source of truth, immutable.
- `wiki/SCHEMA.md` — page-format conventions for raw pages.

In v2, **`wiki/topics/` is removed.** The distilled "agent-owned" layer now lives inside each entity directory — every person-agent and topic-page owns its own scoped corpus.

### 2.3 Entities — people and topics

The knowledge-graph nodes. Two kinds:

- **People** have `persona.md` + `skills.md` + `wiki/` + runnable `agent.py`. Conversational.
- **Topics** have `overview.md` + `wiki/`. Not conversational — they exist to be referenced from people's personas.

```
entities/
  _base.py                                    # PersonAgent class
  _refs.py                                    # resolve [[topic:...]] / [[person:...]] cross-references
  people/
    ai-ml/                                    # public figures organized by domain of expertise
      karpathy/
        persona.md                            # nuwa-style: mental models, heuristics, expression DNA, honest boundaries
        skills.md                             # what queries this person serves
        wiki/
          public/                             # crawled
          user-notes/                         # community-contributed
          interviews/                         # (future) AI-conducted phone-call transcripts
        agent.py                              # subclasses PersonAgent
    constitutional-law/
      roberts/
    local-government/                         # local people organized by jurisdiction
      us/wa/mountlake-terrace/permit-office/lisa-smith/
      us/ga/cherokee-county/alcohol-beverage-control/mary-johnson/
  topics/
    ai-ml/
      transformers/
        overview.md
        wiki/
    constitutional-law/
      14th-amendment-citizenship/
```

**Hierarchy choice rationale:** public figures organize by primary domain because "what they're known for" is how you find them. Local-government people organize by jurisdiction because that's how civilians need to find them ("the permit office in MY city").

**Knowledge graph via cross-references.** Persona files include `[[topic:ai-ml/transformers]]` and `[[person:ai-ml/ilya]]` syntax. When a `PersonAgent` loads, the runtime resolves these references and pulls the linked topic wikis into context. No graph database — `grep` finds connections. When two people both reference the same topic, that's an emergent edge.

### 2.4 PersonAgent — Python container

`entities/_base.py` exposes ~50 LOC:

```python
class PersonAgent:
    def __init__(self, person_dir: Path):
        self.persona = read(person_dir / "persona.md")
        self.skills = read(person_dir / "skills.md")
        self.wiki = load_wiki(person_dir / "wiki")
        self.linked = resolve_refs(self.persona)        # pull [[topic:...]] / [[person:...]]
        self.history = []

    def chat(self, msg: str) -> str: ...
```

Each person's `agent.py` is ~5 lines: import base, point at directory, expose CLI/HTTP entrypoint. "Spinning up Lisa as a Python process" = instantiating this class.

### 2.5 Researcher — processor pipeline

`researcher/pipeline.py` is the lean ADK pattern (Appendix C):

```python
@dataclass
class Request:
    user_goal: str
    state: dict = field(default_factory=dict)

Processor = Callable[[Request], Request]

def run(processors: list[Processor], req: Request) -> Request:
    for p in processors:
        req = p(req)
    return req
```

Two pipelines share primitives. **Same `research` and `distill` processors** work for both entry points and both entity kinds (people, topics).

**Goal pipeline** ("I want a permit"):
```
clarify → identify_target → research → distill → answer → spawn_chat
```

**URL pipeline** ("create people from this video"):
```
crawl_url → extract_entities → (for each: research → distill) → summary
```

Convergence: both pipelines produce populated `entities/` directories that the user can chat with.

### 2.6 Dashboard — 4-variant comparison

| Variant | Persona | Knowledge |
|---|---|---|
| **bare** | — | — |
| **persona** | full `persona.md` | — |
| **stuffed** | "you are a helpful assistant" | all of the entity's `wiki/` dumped in |
| **agentic** | full `persona.md` | scoped via persona cross-references |

Each comparison targets a specific person-agent. Future calibration: interview the actual person, score which variant matches their real answer best.

Logged to `runs.db` (SQLite). Eval rubric (Appendix D) plumbed in later.

---

## 3. v1 history (shipped 2026-05-10, replaced by v2)

Commit `cdc2bca` shipped a domain-shaped tax-advisor on Section 179 / S-corp content. 9 distilled topic files, 13 crawled IRS pages, 3-runner comparison validated the visible-delta thesis (see `RUN_REPORT.md`).

**Why we moved on:** domain-shaped agents don't capture what differentiates one expert from another and don't address the "who do I talk to" framing. v2 reorganizes around person-shaped agents.

**Kept from v1:** `crawler/` (unchanged), `wiki/raw/` (still source of truth), `dashboard/` (rewired for 4 variants).

**Deleted in v2 build step 1:** `agents/tax-advisor/`, `wiki/topics/taxes/`, and the v1 distillation script that targeted the old topic layout.

---

## 4. Repository layout (v2)

```
civilian-fm/
  pyproject.toml
  .env  /  .env.example
  CLAUDE.md  /  PLAN.md  /  README.md
  RUN_REPORT.md                                   # v1 evidence, kept as history

  crawler/                                        # unchanged from v1
    youtube.py
    web.py
    store.py

  wiki/
    SCHEMA.md                                     # raw-page conventions
    raw/                                          # crawler output, immutable
      youtube/<vid>.md
      web/<slug>.md

  entities/                                       # NEW — knowledge graph nodes
    _base.py                                      # PersonAgent class
    _refs.py                                      # resolve cross-references
    people/
      <domain>/<person>/                          # public figures by expertise
        persona.md  skills.md  wiki/  agent.py
      local-government/<country>/<state>/<jurisdiction>/<office>/<person>/
        persona.md  skills.md  wiki/  agent.py
    topics/
      <domain>/<topic>/
        overview.md  wiki/

  researcher/                                     # NEW — pipeline that builds entities
    pipeline.py                                   # ~30 LOC framework
    processors/
      clarify.py                                  # ask 1-3 questions if goal is ambiguous
      identify.py                                 # goal -> entity reference (search + LLM)
      crawl_url.py                                # URL-mode entry
      extract_entities.py                         # raw content -> {people: [...], topics: [...]}
      research.py                                 # nuwa-style sub-crawls per dimension (with thin-source adaptation)
      distill.py                                  # build persona.md / overview.md + wiki
      answer.py                                   # initial response
      spawn_chat.py                               # hand off to PersonAgent
    pipelines.py                                  # GOAL_PIPELINE, URL_PIPELINE

  dashboard/                                      # 4-variant comparison
    runners.py                                    # bare / persona / stuffed / agentic
    store.py
    app.py

  scripts/
    research.py                                   # CLI for GOAL or URL pipeline
    run_comparison.py                             # 4-runner CLI

  runs/  /  runs.db                               # comparison reports (gitignored except evidence)
```

---

## 5. v2 Build Order

Each step has a concrete verification. Don't move on without it.

1. **Delete v1 tax-advisor artifacts.** No backwards compatibility.
   - *Verify:* `agents/tax-advisor/` and `wiki/topics/taxes/` gone. `dashboard/runners.py` doesn't import tax-advisor.

2. **`entities/_base.py` — PersonAgent class** (~60 LOC).
   - *Verify:* Can instantiate `PersonAgent(Path("entities/people/test/test/"))` with stub files and call `.chat("hi")`.

3. **`researcher/pipeline.py` — processor framework** (~30 LOC).
   - *Verify:* `run([lambda r: r], Request("test"))` returns the request unchanged.

4. **First processors — `clarify`, `identify`, `research`, `distill`.** ~50 LOC each.
   - *Verify clarify:* ambiguous goal → 1-3 questions; clear goal → no questions.
   - *Verify identify:* "permits in Mountlake Terrace WA" → returns a target person reference.
   - *Verify research:* spawns parallel crawls, writes both `wiki/raw/` and `entities/people/<...>/wiki/public/` files. Gracefully degrades for thin-source targets (nuwa adaptation, Appendix A).
   - *Verify distill:* produces a `persona.md` following the nuwa schema (mental models, heuristics, expression DNA where present, honest boundaries).

5. **First vertical — Lisa Smith (Mountlake Terrace permit office) end-to-end.**
   - *Verify:* `python -m scripts.research "i want to create a permit for a deck in Mountlake Terrace WA"` populates `entities/people/local-government/us/wa/mountlake-terrace/permit-office/lisa-smith/` and prints an initial answer.
   - *Verify:* `python entities/people/local-government/us/wa/mountlake-terrace/permit-office/lisa-smith/agent.py` opens a chat with Lisa.

6. **Second vertical — Karpathy (control case for source-abundant target).**
   - *Verify:* Same pipeline, no code changes, produces a denser persona.md with multiple `[[topic:...]]` cross-references that resolve cleanly.

7. **URL pipeline + entity extraction.**
   - *Verify:* `python -m scripts.research --url "https://www.youtube.com/watch?v=GCygktDbU3Q"` (SCOTUS transcript already in `wiki/raw/`) creates person-agents for Roberts, Sotomayor, Trump, Barbara, Sour, plus topic pages for `birthright-citizenship` and `14th-amendment-citizenship-clause`.
   - *Verify:* Trump's persona links to `[[topic:constitutional-law/birthright-citizenship]]`; loading Trump-agent pulls that wiki in.

8. **Dashboard — 4 variants targeting person-agents.**
   - *Verify:* Streamlit page lets you pick an entity, runs bare/persona/stuffed/agentic against a query, shows visible delta. Logs to `runs.db`.

9. **Cross-reference resolution at runtime.**
   - *Verify:* When chatting with Karpathy-agent about transformers, the response cites both Karpathy's wiki and the linked transformers topic wiki.

---

## 6. Use case backlog (v2)

The product is **"navigate friction in modern life by chatting with the right person."** Each row below is a vertical slice opportunity. Each one populates entities + builds knowledge-graph edges.

| Use case | Target person(s) | Source material | Vertical priority |
|---|---|---|---|
| Mountlake Terrace permit | Lisa Smith, permit specialist | city site, meeting minutes, news mentions | v2 first |
| Karpathy on AI/ML (control) | Karpathy | blog, lectures, papers, tweets | v2 second |
| SCOTUS oral argument explorer | Roberts, Sotomayor, Trump, Barbara | the SCOTUS YouTube transcript we already have | v2 URL-mode test |
| Cherokee County liquor license | Mary Johnson, ABC board chair | county site, meeting minutes, eventually user-call notes | v2.5 |
| Fulton County property tax appeal | County tax assessor staff | assessor site, recent appeal cases | v3 |
| Hiring first employee (S-corp) | A real CPA distilled from their public content | CPA blog, podcast appearances, video Q&As | v3 — replaces v1's tax-advisor |

---

## 7. Open questions / revisit later

- **AI-conducted phone interviews.** Twilio + Whisper + an LLM script that calls actual people (Mary Johnson, Lisa Smith) to fill honest-boundary gaps. Recording-consent laws differ per state — needs legal review. v3.
- **News pipeline.** Feed-tagged article ingestion ("data center opened near you"). v3.
- **CCTV / Flock integration.** Situational context layer. Flock has an enterprise API. v3-v4.
- **Vector retrieval.** Defer until any entity's wiki exceeds the model's context window. Trigger: any `wiki/` glob > 100k tokens.
- **Multi-user contribution to shared agents.** Many users adding notes to "their" Mary Johnson agent. Requires auth + moderation. v3.
- **Hosted dashboard.** Streamlit Cloud is one toggle once the loop feels right.
- **Deterministic eval** (Appendix D rubric + LLM judge). Plumb in after v2 first vertical works end-to-end.

---

## 8. Behavioral notes for Claude Code prompts

When prompting Claude Code on this repo:

- **People-shaped agents only.** No domain-shaped agents (`agents/tax-advisor/`-style). Every conversational agent represents a real or composite person with a `persona.md`, `skills.md`, and growing `wiki/`.
- **Stay in vertical-slice mode.** Don't build all entity kinds before the first person-agent runs end-to-end.
- **Don't introduce abstractions** until there are at least three concrete instances of the thing being abstracted. The processor pipeline pattern (Appendix C) applies only to multi-step agents like the researcher — never to single-call agents.
- **Cite from the entity's wiki, not from training data.** If an agent answers without citing, the harness is broken.
- **Honest boundaries are mandatory.** Every `persona.md` has a section listing what we don't know about this person. This is non-negotiable per Appendix A.
- **Cross-references are the graph.** Use `[[topic:...]]` and `[[person:...]]` in markdown. Don't introduce a graph database.
- **No Docker, no vector DB, no custom frontend** without explicit user approval. Push back on these suggestions.

---

## Appendix A: Reference — nuwa-skill

Captured here so we don't re-research it later. **We are not adopting nuwa-skill as a dependency.** But after re-reading the source, we are adopting more of its substance than we originally thought — its 12-section schema and its thin-source adaptation rules go directly into our v2 `persona.md` and `researcher/processors/research.py`.

**Material corrections to the original entry are flagged inline below.**

### What it is

A Claude Code skill (not a Python library) at https://github.com/alchaincyf/nuwa-skill. Purpose: distill a public figure (Munger, Feynman, Musk, Naval, Karpathy, etc.) into a single `SKILL.md` file that Claude Code can load as a persona. Installation is `npx skills add alchaincyf/nuwa-skill`. Runtime is Claude Code subagents executing instructions in natural language. The only Python in the repo is three regex linters that never call an LLM. ~18k stars, MIT, actively maintained as of mid-2026.

### How it works (4 phases)

1. **Research** — 6 parallel subagents each write one file: `01-writings.md`, `02-conversations.md`, `03-expression-dna.md`, `04-external-views.md`, `05-decisions.md`, `06-timeline.md`. **Correction:** source-gathering uses pluggable info-skills (gemini-video, web-article-reader, agent-reach, pdf, huashu-research) when installed; WebSearch is the fallback, not the default. Our crawler slots into the same pluggable position.
2. **Synthesis** — distill into a 3-tier schema: Mental Models (3–7, validated by "appears in ≥2 domains"), Decision Heuristics (5–10), Expression DNA (6 quantified style dimensions).
3. **Build** — fill a **12-section** template (corrected from 11) into one `SKILL.md` (~2k–4k words). Sections: frontmatter, operating-system header, role-play rules, identity card, mental models, decision heuristics, expression DNA, timeline, values & anti-patterns, knowledge genealogy, **honest boundaries** (mandatory), research sources.
4. **Validate** — **substantive automated quality gates** via subagents, *not* regex-only as we originally documented. Three tests: **known-case alignment** (does the persona match real positions the person took?), **edge-case reasoning** (defensible answers in unseen scenarios), **voice authenticity** (100-word style passage scored against verified writing samples). Plus quantified PASS/FAIL on mental-model count, limitations density, primary-source ratio. The `scripts/quality_check.py` regex linter is only the surface layer.

### Thin-source adaptation — the unlock we previously missed

Nuwa explicitly handles thin-source targets. From their docs (translated):

> *"When post-Phase-0.5 evaluation finds available sources <10, mental models are reduced to 2-3, each labeled 'based on limited information / inference'."*

> *"If the user provides local material, analyze it first: which dimensions does it cover? Which are missing or weak? Spawn search agents only for the missing dimensions; skip search for dimensions already covered."*

**This is exactly the Lisa-Smith / Mary-Johnson pattern.** Our earlier dismissal of nuwa ("doesn't work for thin sources") was wrong. Their framework adapts; their examples just don't showcase it.

### What we ARE borrowing (revised after re-read)

- **The 12-section schema** as the structure of our `persona.md`. Mental Models / Decision Heuristics / Expression DNA / Honest Boundaries are all directly applicable now that v2 is people-shaped.
- **The thin-source adaptation rules** — reduce mental models to 2-3, label inferences, search only for missing dimensions. Goes into `researcher/processors/research.py` and `distill.py`.
- **The substantive validation tests** (known-case, edge-case, voice authenticity) — port into the eval framework from Appendix D when we plumb it in.
- **The pluggable source-skill pattern.** Our crawler is the "info-skill"; we plug it into the same slot nuwa uses.
- **Honest Boundaries as a mandatory schema section** — not optional, not a one-liner. A full section per persona. Reflected in Section 8 behavioral notes.
- **"Honest 60-point skill > fabricated 90-point skill"** as a guiding principle.

### What we're NOT borrowing

- **The framework wrapper.** Nuwa is Claude Code-native (`npx skills add`). We re-implement the patterns in Python so it integrates with LiteLLM and our processor pipeline.
- **WebSearch as primary source.** Our crawler is more deliberate and writes structured `wiki/raw/` files.

### Citation: where to verify

- `SKILL.md` — main orchestration file (Chinese with English README).
- `references/extraction-framework.md` — the schema.
- `references/skill-template.md` — the 12-section template.
- `examples/munger-perspective/SKILL.md` — worked example.
- `scripts/quality_check.py` — surface regex layer (the substantive tests are in the SKILL.md instructions, not in this script).

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
| The wiki (agent-owned) | `entities/people/<...>/wiki/` and `entities/topics/<...>/wiki/` | In v2 the distilled layer lives inside each entity. Each person and each topic owns its own scoped corpus. |
| The schema | `wiki/SCHEMA.md` | Conventions for ingest + page format. Written after step 4 of the build order, against real S179 examples |

### What we're adopting

- **The 3-layer separation** — raw read-only, wiki LLM-owned, schema as conventions doc.
- **Markdown + git, no vector DB** — through v1.
- **Agent maintains, human curates** — the researcher pipeline generates and updates each entity's `wiki/`; we direct what to crawl and what questions matter.

### Where we deviate (and why)

- **Multi-domain wiki, not personal wiki.** Karpathy's framing is one user's notes. Ours covers many domains (taxes, permits, liquor licenses, eventually county-specific procedures). At scale this won't fit in a single context window — we mount only the relevant slice per agent via `wiki_glob.txt`. That's a small but real divergence from "load the whole wiki every query."
- **Schema written late, not first.** Karpathy's gist implies schema-first. We write `wiki/SCHEMA.md` after ~5 hand-distilled examples (build-order step 5) so the conventions describe real pages instead of imagined ones.

### When to revisit

- If a single entity's wiki exceeds the model's context window → introduce embedding-based retrieval over that entity's `wiki/` (also noted in Section 7).
- If contradictions across sources start mattering (e.g., manufacturer says $31,300, IRS publication implies a different cap) → formalize the `_contradictions.md` pattern from Karpathy's gist.

---

## Appendix C: Reference — Google ADK internals

Source-level reading of https://github.com/google/adk-python. **We are not adopting ADK.** This appendix records what's worth borrowing and what's not, so we don't keep relitigating it.

### What ADK actually is

- Open-source agent framework, Python/TypeScript/Go/Java. Marketed as "model-agnostic" via a `LiteLlm` wrapper (`models/lite_llm.py`) — real-ish, with caveats: Gemini `types.Content` is canonical internally, so Gemini-specific parts (file URIs, thought signatures) degrade on Anthropic/Vertex.
- Deployment targets Cloud Run / GKE / Vertex Agent Engine. "Lightweight" deployment in practice is a single LLM call with a constructed system prompt — same shape as our tax-advisor.

### Execution loop

`LlmAgent._run_async_impl` → `BaseLlmFlow.run_async`. Standard tool-use loop: preprocess → LLM call → postprocess → handle function calls → repeat until final response. Same shape as every other framework. Nothing special.

### Multi-agent mechanisms (the marketing pitch)

Two distinct patterns:
- **Sub-agent-as-tool** (`tools/agent_tool.py`) — wrap a child agent as a `FunctionDeclaration`, copy state down, merge state delta up.
- **Transfer-to-agent** (`tools/transfer_to_agent_tool.py`) — a tool that sets `tool_context.actions.transfer_to_agent = name`; the flow re-dispatches.

Plus shell agents: `SequentialAgent`, `ParallelAgent` (asyncio.TaskGroup with backpressure), `LoopAgent` (terminates on `event.actions.escalate`). All conceptually simple; the docs make them sound bigger than they are.

### State and memory

Three-tier:
- `Session` — `app_name`, `user_id`, `id`, `events[]`, `state{}`, persisted via pluggable `SessionService` (in-memory, SQLite, Vertex).
- `State` — dict with `_value` + `_delta`; reads check delta first. Prefixes `app:`, `user:`, `temp:` are conventions for the persistence layer to route scope.
- `MemoryService` — separate, for cross-session retrieval (in-memory, Vertex RAG, Memory Bank).
- `instructions` processor does `{var}` substitution from session state into the system prompt — that's the built-in scratchpad.

### Two ideas worth borrowing

1. **Processor pipeline.** `SingleFlow` registers ~12 request processors in a fixed order (`basic → auth → instructions → identity → compaction → contents → context_cache → planning → code_execution → output_schema`). Each is a tiny composable unit mutating an `LlmRequest`. Far cleaner than a monolithic `build_system_prompt()` function when you have multiple prompt-construction steps.
   
   **Adoption rule for civilian-fm:** apply only to multi-step agents like the researcher pipeline (clarify → plan → search → crawl → distill → answer). Do not refactor the tax-advisor — one LLM call, one function, no processors. We don't build framework where there isn't pipeline.

2. **`output_key` convention.** An `LlmAgent` can declare `output_key="search_results"`; its final response auto-writes to session state under that key. Next agent reads it. Clean handoff between sequential subagents without a framework.
   
   **Adoption rule:** when the researcher has 5+ sequential steps, use this as a convention. Don't enforce via Pydantic; just a `state: dict` that each step mutates by name.

### What we're NOT borrowing

- **The framework itself.** Pydantic config schemas, live/streaming code paths, audio transcription manager, Vertex coupling, event-bus abstractions — all bloat for our purposes.
- **Multi-agent transfer mechanics.** Sub-agent-as-tool and transfer-to-agent are clever, but premature. Until we have 3+ agents in one loop, a `for p in processors:` is enough.
- **`LiteLlm` wrapper.** We already use LiteLLM directly; ADK's wrapper adds an additional translation layer we don't need.

### Concrete lean implementation

The whole processor-pipeline pattern, civilian-fm-style:

```python
# agents/researcher/pipeline.py — ~30 LOC total
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Request:
    user_goal: str
    state: dict = field(default_factory=dict)

Processor = Callable[[Request], Request]

def run(processors: list[Processor], goal: str) -> Request:
    req = Request(user_goal=goal)
    for p in processors:
        req = p(req)
    return req
```

Each processor is a plain function. `output_key` is convention, not type-enforced. If we ever need async or streaming, we add it then.

### When to revisit

- If we end up wanting native Gemini features (thought signatures, multimodal Gemini-specific shapes) → consider ADK's `LiteLlm` wrapper.
- If we need multi-agent routing across 5+ specialized agents → reconsider their transfer-to-agent pattern (but probably reimplement leaner).

---

## Appendix D: Evaluation framework — variants and scoring

The dashboard's comparison value depends on us being honest about what we're measuring. This appendix locks in the variants and the scoring stack so we don't drift into vibes-only comparison.

### The four variants

We compare on two independent axes — **persona** (on/off) and **knowledge** (off / scoped / full-dump):

| Variant | Persona | Knowledge | Isolates |
|---|---|---|---|
| **bare** | — | — | Mean-of-the-internet baseline |
| **persona** | full `personality.md` + `skills.md` | — | Persona-only effect: does refusal-posture + tone steering work without any corpus? |
| **stuffed** | "you are a helpful assistant" | full wiki dump | Knowledge-only effect: does adding context help without instruction on how to use it? |
| **agentic** | full | scoped via `wiki_glob.txt` | Full harness. Should win — and the delta vs. `persona` and `stuffed` separately attributes the lift |

This decomposition lets us write claims like "the persona contributes ~1.1 rubric points; the scoped wiki contributes ~0.6; the combination contributes ~1.7" instead of "agentic is better."

### Three-layer scoring stack

Industry pattern (Anthropic, Confident AI, Evidently, G-Eval paper). Combine:

1. **Programmatic checks** (`eval/checks.py`) — regex/structural rules. Zero LLM cost, instant, fully deterministic. Examples for tax-advisor:
   - Contains `$\d` (dollar figure)? Boolean.
   - Contains `consult a (tax professional|CPA|accountant)` (refusal pattern)? Boolean.
   - Contains `[wiki:` (citation marker)? Count.
   - Has `## Limits` or `## Honest boundaries` section? Boolean.
   - Word count.

2. **LLM-as-judge with rubric** (`eval/rubric.py`) — for subjective dimensions. Single judge model (GPT-4o), temperature=0, fixed prompt, structured output. Rubric dimensions (1-5 each):
   - **Actionability** — concrete next steps vs. vague advice
   - **Specificity** — uses the user's actual details (S-corp, Cobb County, spouse on payroll)
   - **Trust** — could a sharp reader verify each claim?
   - **Steering** — ranked by impact, or flat list?

3. **Human spot-checks** — every Nth run gets human review, stored alongside the judge score. Used to compute judge-vs-human agreement over time. If agreement drops below ~0.7, recalibrate the rubric.

### Storage

Extend the existing `runs` table in `runs.db` with: `prog_score` (JSON of programmatic checks), `judge_score` (JSON of rubric dimensions), `judge_model`, `human_score` (nullable, JSON), `human_notes`.

### Why this matters

Without scoring, every dashboard run is a vibes-check. With scoring, after ~50 runs you can plot real claims: "in the tax domain, agentic beats stuffed by 1.7 ± 0.4 rubric points (n=23)." That's the empirical answer to the "where's the context-window sweet spot" question the original plan posed.

### Build order

1. Add the `persona` variant (~15 LOC in `dashboard/runners.py`).
2. Add `eval/checks.py` (~80 LOC, all regex).
3. Add `eval/rubric.py` (~50 LOC, one LLM call with structured output).
4. Plumb scores into `runs.db` + the Streamlit UI.
5. Run 30+ queries to seed the dataset before next architecture push.
