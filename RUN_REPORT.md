# v1 Build & First Run Report

**Built**: 2026-05-10. Autonomous build session.
**Stack**: Python 3.13, uv, LiteLLM → OpenAI gpt-4o-mini.
**Time from `uv init` to working 3-column comparison**: ~30 minutes of wall-clock work.

## What was built

Everything in [PLAN.md](PLAN.md) sections 1–6, plus [README.md](README.md) and [wiki/SCHEMA.md](wiki/SCHEMA.md). Specifically:

- ✅ uv project + LiteLLM smoke test through OpenAI
- ✅ `crawler/youtube.py` — ingests YouTube transcripts via `youtube-transcript-api`, pulls metadata via `yt-dlp`
- ✅ `crawler/web.py` — fetches static pages, BeautifulSoup→markdown extraction
- ✅ 14 raw documents in `wiki/raw/` (1 YouTube transcript + 13 IRS pages)
- ✅ `scripts/distill.py` — LLM-driven raw→topic distillation with citations
- ✅ 9 distilled topic pages in `wiki/topics/taxes/`
- ✅ `wiki/SCHEMA.md` — layer-3 conventions written against the 9 distilled examples
- ✅ `agents/tax-advisor/` — personality + skills + glob + 30-LOC agent runner
- ✅ `dashboard/runners.py` — bare / stuffed / agentic
- ✅ `dashboard/store.py` — SQLite run log
- ✅ `dashboard/app.py` — Streamlit 3-column UI (untested visually; CLI harness covers same logic)
- ✅ `scripts/run_comparison.py` — CLI harness that writes `runs/<timestamp>.md`

## Test 1 — YouTube ingestion

Input URL: `https://www.youtube.com/watch?v=GCygktDbU3Q`

- **Result**: ✅ Ingested cleanly. 3,419 lines of timestamped transcript at `wiki/raw/youtube/GCygktDbU3Q.md`.
- **Title resolved**: "Oral Argument on birthright citizenship: Trump v. Barbara" (Supreme Court of the United States, April 2026, 128.5 minutes).
- **Note**: Topic-orthogonal to the v1 vertical slice (S179 / S-corp tax), so it stays in `wiki/raw/` without a corresponding `wiki/topics/` distillation. Demonstrates the raw/topics separation: raw can hold anything; agents only see what's distilled into topics + globbed.

## Test 2 — Tax query through 3 runners

Query: `i have a liquor store in cobb county in acworth ga, it is based on S-corp where me and my wife are on payroll, how can i lower my tax burden`

| Runner | Prompt tokens | Completion tokens | Latency | Quality (subjective) |
|---|---:|---:|---:|---|
| bare | 44 | 576 | 8.4s | Generic 10-point list, includes "consult a tax professional," no specific figures, no citations |
| stuffed | 5,944 | 610 | 5.0s | Decent — cites wiki paths, S-corp mechanics correct, but unranked, also says "consult a tax professional" |
| agentic | 7,050 | 574 | 8.0s | Ranked by $-impact, concrete dollar figures ($31,300 SUV cap, $66k 401k limit), citations on every claim, honest-boundaries section, no "consult a CPA" deflection |

Full outputs at [runs/20260510T191849Z.md](runs/20260510T191849Z.md).

### Visible-delta evidence (the v1 thesis test)

The thesis: **bare model regresses to internet-mean, agentic container steers it away.** What we observed:

- **Bare**'s item #8: `"Consult a Tax Professional"`. Exactly the predicted regression-to-mean.
- **Agentic**'s opening: `"Here are several strategies to lower your tax burden as an S-corp owner of a liquor store. ## Strategies, ranked by likely $ impact — 1. Balance Salary and Distributions ... [wiki: taxes/s-corp/distributions-vs-payroll]"`. No deflection. Direct. Cited. Ranked.
- **Stuffed** sits in the middle: pulls some specific facts from the wiki dump, but no ranking, no honest-boundaries, and still ends with "consult a tax professional."

The persona's refusal-posture instruction (`"Do not open with 'consult a tax professional.' Give the answer first."`) was load-bearing — the steering held in the agentic column and didn't in the stuffed column despite both having access to the same wiki content. **This is the proof the harness matters more than the corpus.**

### Token-cost view

- Bare: 620 total tokens / call.
- Stuffed: 6,554 total tokens / call (~10x).
- Agentic: 7,624 total tokens / call (~12x).

For OpenAI gpt-4o-mini at $0.15 / 1M input + $0.60 / 1M output, that's:
- Bare: $0.0006 / call
- Stuffed: $0.0012 / call
- Agentic: $0.0014 / call

Cheap enough that the 3-runner comparison is essentially free at the per-query level.

## What worked

1. **The persona refusal-posture instruction.** One sentence in `personality.md` was the difference between "consult a tax professional" and a ranked dollar-impact list.
2. **Wiki citations.** Every concrete agentic claim links to a topic file. Easy to audit which fact came from which IRS page.
3. **3-layer separation pays off.** Raw stays raw (the SCOTUS transcript sits there harmlessly). Topics are the agent's surface. Schema captures conventions. Each layer is independently editable.
4. **LiteLLM was zero friction.** Single dependency, single env var, works.

## What didn't work / known issues

1. **Stale year figures.** Wiki has 2023 401(k) limits because IRS raw pages don't carry 2025 numbers in the sections we crawled. The agent cited them confidently. Fix: add a "tag year-specific dollar figures with `(YYYY)` and flag if not current year" rule to `personality.md`. Not done in this build.
2. **Tesla CyberTruck page returns 403.** Anti-bot. Real-world hurdle. The plan called this out — Playwright/Firecrawl are the path.
3. **Two IRS URLs 404'd.** QBI deduction and depreciation FAQ. The IRS reorganizes URLs without redirects. Need a fallback strategy (e.g., search → first IRS hit) for production.
4. **`wiki/raw/web/*.md` has nav cruft at the top.** The `<li>` tags from IRS site navigation come through. The distillation step strips this fine, but the raw file looks ugly. Acceptable for v1.
5. **State/local content is empty.** No GA / Cobb County tax info crawled. The agent's honest-boundaries section correctly flags this gap. v2: targeted county/state crawlers.

## What this validates about the plan

- **Vertical-slice approach was right.** Going wide on crawlers first would have wasted hours; the narrow IRS-only crawl + S179/S-corp focus produced a working demo fast.
- **Karpathy's 3-layer wiki maps cleanly onto our directory structure.** No friction, easy to reason about.
- **`wiki/SCHEMA.md` written after 9 examples** (not before) gave us a real schema. A schema written first would have been fictional.
- **Logging every run to SQLite** makes the dashboard a real evaluation lab over time, not just a demo.

## Suggested next steps

1. **Fix the 401(k) limits.** Add a current-year-figures rule to the persona, re-distill the affected topics with a current-year fact-check pass. ~30 min.
2. **Add Anthropic provider.** When the user has a Claude API key, the dashboard turns from 1×3 (one model × three runners) into a real (model × runner) matrix. Already supported by LiteLLM with no code change — just env var.
3. **Add Augusta-rule + QBI topic pages.** The agent's `skills.md` already lists these as "not in wiki — verify before acting." Two more crawl + distill cycles (~15 min each).
4. **Cobb County / Georgia liquor-store crawler.** That's the post-S179 vertical slice in the plan. Will exercise the same pipeline against messier, harder-to-find sources.
5. **Try the dashboard live.** `uv run streamlit run dashboard/app.py` — visual confirmation of the 3-column layout. The CLI harness already covers the underlying logic.
