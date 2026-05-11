# v2 First Vertical — Run Report

**Date**: 2026-05-11
**Vertical**: Mountlake Terrace WA building-permit office
**Stack**: Python 3.13, uv, LiteLLM → OpenAI gpt-4o-mini, DuckDuckGo search

## What was built

Per PLAN.md Section 5 v2 build order:

- ✅ `entities/_base.py` — `PersonAgent` Python container (60 LOC)
- ✅ `entities/_refs.py` — cross-reference resolver for `[[role:]] / [[jur:]] / [[topic:]] / [[person:]]` (90 LOC)
- ✅ `researcher/pipeline.py` — lean processor framework (20 LOC of framework)
- ✅ `researcher/search.py` — DDGS wrapper (30 LOC)
- ✅ `researcher/llm.py` — LiteLLM completion + JSON-mode helper (30 LOC)
- ✅ Processors: `clarify`, `identify`, `research`, `distill`, `answer`, `crawl_url`, `extract_entities` (~50-150 LOC each)
- ✅ `researcher/pipelines.py` — `GOAL_PIPELINE` (URL_PIPELINE in script form)
- ✅ `scripts/research.py` — CLI for goal-mode and URL-mode
- ✅ `dashboard/runners.py` — 4 variants (bare / persona / stuffed / agentic)
- ✅ `scripts/run_comparison.py` — 4-variant CLI

Total new code: ~750 LOC across 15 files. No framework, no abstractions beyond what was needed.

## Test 1 — Goal pipeline end-to-end

**Input**: `"i want a building permit for a deck in Mountlake Terrace WA"`

| Stage | Time | Output |
|---|---:|---|
| clarify | 2s | extracted action + subject + kind |
| identify | 2s | role + jurisdiction + 6 search queries (LLM produced these) |
| research | 48s | 16 web pages crawled across 6 search queries |
| distill | 48s | persona.md + skills.md + role stub + jurisdiction stub |
| answer | 8s | initial response in agent voice |

**Total**: ~108 seconds, ~$0.03 in OpenAI calls.

**Output structure created:**

```
entities/
  people/mountlake-terrace-permit-office/
    persona.md         # nuwa 12-section schema, thin-source-adapted
    skills.md          # auto-generated link-following rules
    wiki/public/       # 16 raw crawl files
  roles/mountlake-terrace-permit-specialist/
    overview.md
  jurisdictions/us/wa/mountlake-terrace/
    overview.md
```

The persona's frontmatter declares the role edge + jurisdiction primary + domains. Body uses `[[jur:us/wa/mountlake-terrace]]` cross-reference. Both stubs were auto-created so the reference resolves at runtime.

## Test 2 — 4-variant comparison

Query: `"do I need a building permit for a 60 sq ft deck attached to my house? If yes, what are the typical fees and how long does processing take?"`

| Variant | Prompt tokens | Completion tokens | Elapsed | Quality (subjective) |
|---|---:|---:|---:|---|
| bare | 40 | 349 | 10.4s | Hedges. "Depends on local codes." Ends with "contact local authorities." Classic mean. |
| persona | 625 | 105 | 4.4s | Commits ("yes you need a permit"). 4-6 week timing. Hedges on fees ("check fee schedule"). First-person voice. |
| stuffed | 33,591 | 212 | 6.6s | Specifics: $50-$300 fees, 2-week revisions, 4-6 week residential. Generic helper voice, cites wiki path. |
| agentic | 34,497 | 141 | 3.2s | Specifics + first-person voice + `[[source:]]` citations. Offers to help with applications. |

Full outputs at [runs/v2-mountlake-terrace-permit-office-20260511T170616Z.md](runs/v2-mountlake-terrace-permit-office-20260511T170616Z.md).

### Visible-delta findings

The 4 variants give a clean attribution of where the lift comes from:

- **bare → persona**: gives the model a voice and refusal posture. Removes the "consult local authorities" hedge. But without a corpus, persona alone can't answer fee questions specifically.
- **persona → stuffed**: knowledge alone (no curated voice) gives specifics ($50-$300, 4-6 weeks) but loses first-person delivery and uses ad-hoc citations.
- **stuffed → agentic**: same knowledge, but the persona organizes it into in-character delivery with structured citations.

**The right column attribution**: persona contributes voice and refusal posture; knowledge contributes specifics; **both are required** for the win. This is exactly the 4-variant decomposition Appendix D predicted.

Cost: stuffed/agentic are ~25x more expensive than bare/persona (~$0.005 per query vs $0.0002). Cheap enough to run the full comparison on every test query.

## Content discipline check (Section 2.7)

- **Uniqueness test**: persona's mental models avoid bare-LLM-generates content. "Encourage applicants to schedule inspections through the online Permit Portal" is specific to MLT's process, not a generic permit fact.
- **Density**: persona.md came in at ~2.8k characters (~700 tokens) — well under the 25k char person budget. The 16 raw sources stayed in `wiki/public/` and got loaded as needed.
- **Honest boundaries**: present, though early generations had the LLM invent a "8 sources, 4 mention by name" statistic. Fixed by tightening the prompt; second-run honest-boundaries are grounded.
- **Selective resolution**: skills.md uses `[[jur:...]]` link-following rules. (Caveat: some links it generated point at imagined jurisdictions like "Mountlake Terrace Zoning Code" rather than real entity slugs — future fix.)

## What worked

1. **Processor pipeline pattern** scaled cleanly from 0 to 6 processors. ~30 LOC of framework; each processor is a plain function. No premature abstraction.
2. **Cross-reference resolution at runtime** worked first-try — agentic runner pulled in linked jurisdiction wiki without code changes.
3. **Thin-source adaptation** (nuwa Appendix A) — the persona acknowledges limits ("voice approximated from generic role norms") rather than fabricating.
4. **Auto-creation of role + jurisdiction stubs** — distill creates them on demand if missing. No "entity not found" errors.
5. **DuckDuckGo search is free and adequate** for first vertical. Some result quality issues (TikTok, unrelated city pages) but the LLM ignored bad sources.

## Iteration 1 — discover_people (added 2026-05-11)

User feedback: "I was hoping our query would discover https://cityofmlt.com/587/City-Council and create an agent from a real council member."

Diagnosis: `identify` generated only procedural search queries, so `research` never visited the council page. There was no step that pivoted from "we have jurisdiction info" to "find a named person."

Fix:
1. Tightened `identify` prompt to require `person_name_hint` be a real first+last name OR null (not a role title), and to generate **people-discovery queries** alongside procedural ones.
2. Added `discover_people` processor between `research` and `distill`. It scans the crawled raw pages for named individuals, returns ranked candidates with `relevance_score`, picks the top one, and updates the target's `person_name_hint`, `person_slug`, and `role_slug` (so the persona reflects the picked person's actual role, not the goal-derived role).

Result on the same query:

```
Person candidates discovered:
  - [10] Jeff Niten     — City Manager of Mountlake Terrace
  - [ 9] Steve Woodard  — Mayor
  - [ 8] Kyoko Matsumoto Wright — Council Member
  - [ 8] Bryan Wahl     — Mayor Pro Tem
  - [ 7] Sam Doyle      — Council Member
  - [ 6] Erin Murray    — Council Member
  PICKED: Jeff Niten

Built person-agent at: entities/people/jeff-niten-mountlake-terrace
```

Jeff Niten's persona now carries:
- Real name and verified role (City Manager since April 2023)
- Concrete facts from crawled news: "$4.2M projected budget gap per year through 2030"
- "1,800 housing units under construction or planned near the light rail station"
- Council-Manager government structure (not boilerplate — specifically MLT's)
- Cited sources: heraldnet.com, theurbanist.org, cityofmlt.com

Full comparison: [runs/v2-jeff-niten-mountlake-terrace-20260511T173510Z.md](runs/v2-jeff-niten-mountlake-terrace-20260511T173510Z.md).

Interesting nuance observed in the 4-variant: on a more complex query ("...does the budget gap affect permit speed?"), **stuffed actually matched or slightly beat agentic** on factual coverage — it surfaced the $6.50 State Building Code Council fee that agentic dropped. This is exactly the Section 2.7 canary: the persona's selective resolution may be filtering out useful signal. Future iteration: tighten `skills.md` link-following rules to ensure budget-related queries actually pull the budget-gap facts the persona has.

## Known issues / next iteration targets

1. ~~No specific person identified.~~ **Fixed in iteration 1.**
2. **Hallucinated cross-references in skills.md.** The LLM invented `[[jur:Mountlake Terrace Zoning Code]]` (not a jurisdiction; that's a topic). Need to constrain skills.md generation to known entity slugs.
3. **Search result noise.** ~25% of crawls returned irrelevant pages (TikTok, generic city directory). A relevance filter (LLM-as-judge or simple heuristics) before crawling would tighten the corpus.
4. **No Karpathy vertical yet.** Build step 6 in PLAN.md — run same pipeline on a source-abundant target to verify it scales up gracefully.
5. **No URL pipeline test yet.** Build step 7 — exercise on the SCOTUS transcript we already have.
6. **Dashboard UI not yet wired.** Only the CLI comparison harness works. Streamlit app needs updating.

## Cost summary

For the full vertical (1 research run + 1 comparison run):
- Research pipeline: ~30 LLM calls (clarify, identify, distill x2, plus 16 web fetches), ~$0.03
- Comparison: 4 LLM calls, ~$0.011
- Total: **~$0.04 to build a new person-agent and run a 4-variant comparison**

Cheap enough to iterate aggressively.

## What this validates about the v2 plan

- The 3-entity graph (people + roles + jurisdictions + topics) works in practice. Cross-references resolve at runtime as designed.
- The processor pipeline pattern is the right level of abstraction — lean enough to read in one sitting, structured enough to add steps without rewriting.
- The 4-variant comparison gives empirical answers to "what's contributing what" rather than vibes.
- Content discipline matters more than architecture: tightening the persona prompt removed one hallucination class in a single iteration.

Architecture is proven. Next session: Karpathy vertical (build step 6), then URL pipeline on SCOTUS (build step 7), then dashboard UI rewire (build step 8).
