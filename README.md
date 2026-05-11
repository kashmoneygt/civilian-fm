# civilian-fm

"Palantir for civilians" — a system where everyday people navigate bureaucratic friction (permits, licenses, taxes, legal, "who do I talk to?") by chatting with person-shaped agents distilled from public sources.

Two entry points (goal-mode and URL-mode) produce the same artifact: a populated `entities/people/<slug>/` directory you can chat with. A 4-variant dashboard (bare / persona / stuffed / agentic) measures how much the harness contributes.

Read [V2_RUN_REPORT.md](V2_RUN_REPORT.md) for the AHA moments documented so far (Karpathy resources, SCOTUS judicial diversity, Augusta Rule tax savings, Naval wealth framework).

---

## Setup

```bash
uv sync
cp .env.example .env       # edit; fill in OPENAI_API_KEY at minimum
```

That's it. No Docker, no vector DB, no other infrastructure.

---

## Try the pre-built agents right now

15 person-agents already exist in `entities/people/`. Pick one and chat:

```bash
# Andrej Karpathy — on AI/ML, transformers, vibe coding, Software 2.0
uv run python -m scripts.chat entities/people/andrej-karpathy

# Naval Ravikant — on wealth, leverage, specific knowledge
uv run python -m scripts.chat entities/people/naval-ravikant

# Tom Wheelwright — on tax strategy (Rich Dad advisor, author of Tax-Free Wealth)
uv run python -m scripts.chat entities/people/tom-wheelwright

# Karlton Dennis — tax YouTuber, knows the Augusta Rule
uv run python -m scripts.chat entities/people/karlton-dennis

# Justice Thomas / Kagan / Gorsuch / Barrett — distilled from Trump v. Barbara
uv run python -m scripts.chat entities/people/justice-thomas
uv run python -m scripts.chat entities/people/justice-kagan
uv run python -m scripts.chat entities/people/justice-gorsuch
uv run python -m scripts.chat entities/people/justice-barrett

# Jeff Niten — Mountlake Terrace WA City Manager (real local-government test)
uv run python -m scripts.chat entities/people/jeff-niten-mountlake-terrace

# Pace Morby — real estate creative finance (subject-to, seller financing)
uv run python -m scripts.chat entities/people/pace-morby
```

In the REPL:
- Type a message + enter
- `/info` to inspect what's loaded into the persona
- `/reset` to clear conversation history
- `/quit` or Ctrl-D to exit

Try `--model gpt-4o` for the bigger model if you want better answers (~10x cost).

---

## Build a NEW person-agent from a goal

Ask the system "I want to learn X" or "I need help with Y in [place]." The pipeline crawls, distills, and builds a runnable agent.

```bash
uv run python -m scripts.research "i want to learn how Charlie Munger thinks about investing"
```

Takes 60–180 seconds. Produces `entities/people/<discovered-person>/` plus an initial answer printed to stdout. Then chat:

```bash
uv run python -m scripts.chat entities/people/charlie-munger
```

### What happens under the hood

The goal pipeline runs these processors in order ([researcher/pipelines.py](researcher/pipelines.py)):

1. **`clarify`** — LLM call. Extracts action + subject + subject-kind from the goal.
2. **`identify`** — LLM call. Picks a target person (or jurisdiction), role, and 6–8 search queries.
3. **`research`** — DDGS search + crawler. Fetches top hits, writes to `wiki/raw/web/`.
4. **`discover_people`** — LLM call. Scans crawled pages for named individuals; picks the highest-relevance candidate. (See "AHA when this works vs not" in [V2_RUN_REPORT.md](V2_RUN_REPORT.md).)
5. **`distill`** — LLM call. Produces `persona.md` (nuwa 12-section schema) + `skills.md` + role and jurisdiction stubs.
6. **`answer`** — Instantiates the new PersonAgent and asks it the original goal.

### Real examples that produced strong AHA

```bash
uv run python -m scripts.research "andrej karpathy — i want to learn how he teaches deep learning"
uv run python -m scripts.research "tom wheelwright — i want to learn his approach to lowering taxes for small business owners"
uv run python -m scripts.research "naval ravikant — i want to understand his philosophy on wealth and startups"
uv run python -m scripts.research "i want a building permit for a deck in Mountlake Terrace WA"
```

---

## Build MULTIPLE person-agents from a URL

The URL pipeline extracts entities (people + topics) from raw content, then runs research+distill on each. Use it on transcripts, articles, or long-form videos.

```bash
uv run python -m scripts.research --url "https://www.youtube.com/watch?v=GCygktDbU3Q"
```

Takes 5–10 minutes (it builds N person-agents). From the Trump v. Barbara SCOTUS transcript, it extracted 8 people (Trump, Barbara, 5 justices, the Solicitor General) and 6 topics (birthright citizenship, 14th Amendment, etc.) — then built person-agents for all 8.

### Other URLs to try

```bash
# A Karpathy lecture transcript → builds an agent for him + any guests
uv run python -m scripts.research --url "https://www.youtube.com/watch?v=zjkBMFhNj_g"

# A podcast transcript → builds agents for host + each guest mentioned
uv run python -m scripts.research --url "<podcast-transcript-url>"

# A news article → builds agents for the named people in the article
uv run python -m scripts.research --url "<article-url>"
```

The crawler handles YouTube (uses `youtube-transcript-api` for free captions) and static web pages (BeautifulSoup). Sites with JS rendering or anti-bot (Tesla, anything Cloudflare-fronted with bot detection) return 403 — those need Playwright/Firecrawl, not wired yet.

---

## The 4-variant comparison harness

The empirical check: does the persona actually steer the model away from the mean? Run the same query through four runners and see.

```bash
uv run python -m scripts.run_comparison entities/people/<slug> "<question>"
```

The four runners are in [dashboard/runners.py](dashboard/runners.py):

| Runner | What it loads |
|---|---|
| **bare** | No system prompt — just the user query. Mean-of-internet baseline. |
| **persona** | Just `persona.md` body. No wiki. Isolates the persona effect alone. |
| **stuffed** | Generic "be helpful" system + entire wiki dumped in. No persona. Isolates the corpus effect alone. |
| **agentic** | Full PersonAgent — persona + skills + wiki + resolved cross-references. The full harness. |

Output is written to `runs/v2-<slug>-<timestamp>.md` plus logged to `runs.db` (SQLite).

### Examples that produced AHA

```bash
# Karpathy — "what are YOUR resources?" The bare model couldn't even name his work.
uv run python -m scripts.run_comparison entities/people/andrej-karpathy \
  "If I'm a developer who wants to learn deep learning by actually building things, what specific repos, tools, or resources of yours should I use? Be concrete."

# Tax — same query across two strategists vs bare. Augusta Rule appears only in Karlton Dennis.
uv run python -m scripts.run_comparison entities/people/karlton-dennis \
  "I own a small business as an S-corp making \$400k/year. My CPA only talks about 401(k). What 2-3 non-obvious strategies should I use?"

# Wealth — Naval's framework appears verbatim only in the agentic column.
uv run python -m scripts.run_comparison entities/people/naval-ravikant \
  "I'm a software engineer making \$200k/year with \$100k saved. Everyone says diversify into index funds. Is that the best move?"
```

---

## Multi-agent comparisons (e.g., 4 SCOTUS justices on the same question)

Not via `run_comparison.py` — that's bare-vs-persona-vs-stuffed-vs-agentic for ONE agent. For "same question, different person-agents," use the chat CLI on each agent, or write a small loop. Example pattern (used to produce AHA #2):

```bash
uv run python <<'EOF'
from pathlib import Path
from entities._base import PersonAgent

QUERY = "Should the 14th Amendment's birthright citizenship clause apply to children born in the US to parents who are illegally present? What is your reasoning?"

for slug in ["justice-thomas", "justice-kagan", "justice-gorsuch", "justice-barrett"]:
    print(f"\n## {slug}\n{'='*60}")
    agent = PersonAgent(Path(f"entities/people/{slug}"))
    print(agent.chat(QUERY))
EOF
```

---

## Repo map

```
civilian-fm/
  pyproject.toml                # deps; uv-managed
  .env                          # OPENAI_API_KEY (gitignored)
  CLAUDE.md                     # behavioral guidelines
  PLAN.md                       # v2 architecture, all design decisions, appendices on
                                #  nuwa-skill, Karpathy LLM wiki, ADK, eval framework
  V2_RUN_REPORT.md              # all 5 iterations + AHA moments documented
  README.md                     # this file

  entities/                     # the knowledge graph
    _base.py                    # PersonAgent class (~100 LOC)
    _refs.py                    # resolve [[role:]] / [[jur:]] / [[topic:]] / [[person:]]
    people/<slug>/              # FLAT; 15 person-agents currently
      persona.md                # nuwa-style: identity, mental models, heuristics,
                                #  workflows, expression DNA, honest boundaries
      skills.md                 # link-following rules per query type
      wiki/public/              # crawled raw sources for this person
    roles/<slug>/               # held by people, time-bounded
      overview.md
    jurisdictions/<path>/       # us/, us/ga/, us/wa/mountlake-terrace/, etc.
      overview.md
    topics/<domain>/<topic>/    # concepts (not built much yet)

  researcher/                   # pipeline that builds entities
    pipeline.py                 # ~20 LOC framework
    pipelines.py                # GOAL_PIPELINE composition
    search.py                   # DDGS wrapper
    llm.py                      # LiteLLM + JSON-mode helper
    processors/
      clarify.py
      identify.py
      research.py
      discover_people.py        # the named-person extractor
      distill.py                # produces persona.md + skills.md
      answer.py
      crawl_url.py              # URL-mode entry
      extract_entities.py       # URL-mode: extract people+topics from content

  crawler/                      # unchanged from v1 — used inside research/crawl_url
    youtube.py                  # transcript via youtube-transcript-api
    web.py                      # requests + BS4 + lxml
    store.py                    # writes wiki/raw/<source>/<slug>.md

  dashboard/
    runners.py                  # bare / persona / stuffed / agentic
    store.py                    # SQLite run log
    app.py                      # Streamlit UI (not currently wired to v2)

  scripts/
    research.py                 # CLI: goal mode or URL mode
    chat.py                     # CLI: interactive chat with a person-agent
    run_comparison.py           # CLI: 4-variant comparison harness

  wiki/raw/                     # crawler dumping ground (source of truth, immutable)
  runs/                         # comparison outputs (mostly gitignored; tracked evidence kept)
  runs.db                       # SQLite run log (gitignored)
```

---

## Cost notes (gpt-4o-mini, default)

- Build a new person-agent (goal mode): ~$0.02 per build (one full pipeline run, ~25 LLM calls including ~15 web crawls).
- Build multiple person-agents from a URL: ~$0.05–0.20 per URL depending on entity count.
- Chat with an agent: ~$0.003–0.01 per turn (rich-source agents have larger system prompts).
- 4-variant comparison: ~$0.05 per query.

`gpt-4o` is ~10x more expensive but tends to produce stronger answers, especially on the agentic column. Set `AGENT_MODEL=gpt-4o` in `.env` or pass `--model gpt-4o` to `chat.py`.

---

## Known issues

- **Discovery quality** — `discover_people` greedily picks top-1 candidate. Works great for famous figures (Karpathy, SCOTUS, Naval, Wheelwright); produces weak agents when the top candidate's public corpus is thin (Ben Hall traffic-lawyer case). Future fix in PLAN.md Section 6.
- **`stuffed` runner sometimes hits TPM rate limit** on big agents (45k+ token wiki). Token budgets in `entities/_base.py` cap the agentic runner; stuffed loads more aggressively.
- **Hallucinated cross-refs in `skills.md`** — distill sometimes generates `[[jur:...]]` for slugs that don't exist as entities. They silently no-op at runtime.
- **Anti-bot pages return 403** (Tesla, some Cloudflare-fronted sites). Use a different source or wait for Playwright/Firecrawl integration.

---

## What's been validated (per V2_RUN_REPORT.md)

The system steers away from the mean when:
1. Person has a **distinctive framework** (Naval's "specific knowledge", Wheelwright's "taxes as incentives")
2. Person has **signature non-obvious strategies** (Augusta Rule, Cash Balance Plan, nanoGPT, originalism)
3. Person has **rich public corpus** (books, podcasts, YouTube, papers)
4. Question matches their **actual area of strong views**

The system reverts toward the mean when:
1. Persona is composite/role-shaped instead of a named real person
2. Sources are generic Wikipedia/glossary content
3. Question is too general for the person to have a specific view
4. Context rot (45k+ token wikis dilute specific facts)

Three documented AHA moments worth reading:
- **Karpathy**: bare GPT couldn't name his work; agentic surfaced nanoGPT, AutoResearch, Zero to Hero.
- **SCOTUS**: 4 justice agents gave 4 distinct grounded-in-jurisprudence answers vs bare's one "balanced" answer.
- **Karlton Dennis**: only persona that surfaced the **Augusta Rule** — rent your home to your S-corp 14 days/year tax-free.
