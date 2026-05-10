# civilian-fm

"Palantir for civilians" — a comparison dashboard that runs the same query through three LLM harnesses (bare model / stuffed-context / agentic container) to find per-domain context-window sweet spots.

See [PLAN.md](PLAN.md) for the architectural rationale and [wiki/SCHEMA.md](wiki/SCHEMA.md) for the wiki layer conventions.

## Setup

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY (others optional)
```

## Usage

### Crawl a YouTube video into wiki/raw/

```bash
uv run python -m crawler.youtube "https://www.youtube.com/watch?v=<id>"
```

### Crawl a static web page

```bash
uv run python -m crawler.web "https://www.irs.gov/businesses/small-businesses-self-employed/s-corporations"
```

Some sites (Tesla, anti-bot) return 403 — skip these or add a Playwright fallback.

### Distill raw pages into topic pages

Edit `TOPIC_SPECS` in [scripts/distill.py](scripts/distill.py), then:

```bash
uv run python -m scripts.distill
```

### Run a single agent query

```bash
uv run python agents/tax-advisor/agent.py "your question"
```

### Run the 3-runner comparison from CLI

```bash
uv run python -m scripts.run_comparison "your question"
# writes runs/<timestamp>.md and logs to runs.db
```

### Run the Streamlit dashboard

```bash
uv run streamlit run dashboard/app.py
```

## Repository layout

```
civilian-fm/
  pyproject.toml
  .env / .env.example
  CLAUDE.md             # behavioral guidelines
  PLAN.md               # architecture + decisions
  README.md             # this file
  crawler/
    youtube.py          # transcript ingestion
    web.py              # static page ingestion
    store.py            # write to wiki/raw/<source>/<slug>.md
  wiki/
    SCHEMA.md           # layer-3 conventions
    raw/                # immutable crawler output
      web/<slug>.md
      youtube/<vid>.md
    topics/             # LLM-distilled topic pages
      taxes/section-179/
      taxes/s-corp/
      taxes/retirement/
      taxes/strategies/
  agents/
    tax-advisor/
      personality.md
      skills.md
      wiki_glob.txt
      agent.py
  dashboard/
    runners.py          # bare / stuffed / agentic
    store.py            # SQLite run log
    app.py              # Streamlit UI
  scripts/
    distill.py          # raw -> topics
    run_comparison.py   # CLI 3-runner harness
  runs/                 # comparison reports (markdown, gitignored)
  runs.db               # SQLite log (gitignored)
```

## Models

Default model is `gpt-4o-mini` via LiteLLM. To use a different OpenAI model, set `AGENT_MODEL=gpt-4o` in `.env` or pass as second arg to `run_comparison`. To add Anthropic/Gemini providers, set the respective `*_API_KEY` env vars — LiteLLM picks them up automatically.

## Known limits (v1)

- **No vector retrieval.** The agent reads the entire `wiki_glob` into the system prompt every call. Fine until the glob exceeds the model's context window. Trigger to add embeddings: when prompt-token count routinely > 100k.
- **Year-specific figures may be stale.** IRS pages rotate dollar figures yearly; some distilled topics carry 2023 numbers. The agent should be prompted to flag year-tagged figures explicitly — see future improvement note in `agents/tax-advisor/skills.md`.
- **Anti-bot pages are blocked.** Tesla, Cloudflare-fronted retail sites return 403 from the bare `requests` crawler. Use Playwright or Firecrawl when this matters.
- **State/local content is sparse.** No GA / Cobb County tax content in v1 — the agent's `honest boundaries` section calls this out.
