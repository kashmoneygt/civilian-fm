# civilian-fm

"Palantir for civilians" — a system where everyday people navigate bureaucratic friction (permits, licenses, appeals, "who do I talk to?") by chatting with person-shaped agents distilled from public sources, user contributions, and (eventually) AI-conducted interviews.

**Current status:** v1 shipped and validated (see [RUN_REPORT.md](RUN_REPORT.md)), now superseded by v2. v2 plan is in [PLAN.md](PLAN.md) — building.

## Quick start

```bash
uv sync
cp .env.example .env   # fill in OPENAI_API_KEY
```

## What's in the repo right now

- [PLAN.md](PLAN.md) — current architecture and build order (v2)
- [CLAUDE.md](CLAUDE.md) — behavioral guidelines for Claude Code prompts on this repo
- [RUN_REPORT.md](RUN_REPORT.md) — v1 evidence (historical)
- `crawler/` — YouTube and web crawler (unchanged from v1)
- `wiki/raw/` — crawler output, immutable source of truth
- `dashboard/store.py` — SQLite run logger (still used in v2)

## What's being built (v2)

Per [PLAN.md](PLAN.md) Section 5:

1. `entities/_base.py` — `PersonAgent` class
2. `researcher/pipeline.py` — processor framework
3. Goal pipeline: clarify → identify → research → distill → chat
4. URL pipeline: crawl → extract entities → research each → chat
5. First vertical: Lisa Smith (Mountlake Terrace permit office)
6. Second vertical: Karpathy (source-abundant control case)
7. URL test: SCOTUS transcript already in `wiki/raw/youtube/GCygktDbU3Q.md`
8. Dashboard rewired for 4-variant comparison (bare / persona / stuffed / agentic)

## Reference appendices in [PLAN.md](PLAN.md)

- **Appendix A** — nuwa-skill (we're borrowing its 12-section schema and thin-source adaptation)
- **Appendix B** — Karpathy's LLM Wiki pattern (backbone of our entity wiki layer)
- **Appendix C** — Google ADK internals (we're borrowing the processor pipeline pattern)
- **Appendix D** — evaluation framework (rubric + LLM judge, deferred until after v2 first vertical)
