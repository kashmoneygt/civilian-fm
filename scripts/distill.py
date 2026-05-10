"""Distill raw wiki pages into topic pages.

Usage: uv run python -m scripts.distill

Reads TOPIC_SPECS, loads raw source files for each topic, prompts an LLM to extract
structured facts with citations back to the raw paths, writes wiki/topics/<path>.md.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path

import litellm
import yaml
from dotenv import load_dotenv

load_dotenv()

REPO = Path(__file__).resolve().parent.parent
RAW = REPO / "wiki" / "raw"
TOPICS = REPO / "wiki" / "topics"
MODEL = os.getenv("DISTILL_MODEL", "gpt-4o-mini")


# Each topic: (output relative path under wiki/topics, raw file basenames to consult, focus prompt)
TOPIC_SPECS: list[tuple[str, list[str], str]] = [
    (
        "taxes/section-179/overview.md",
        ["irs-gov--publications-p946.md"],
        "Section 179 deduction: 2025 dollar limits and phase-out, what property qualifies, how it interacts with bonus depreciation. The reader is a small-business S-corp owner.",
    ),
    (
        "taxes/section-179/heavy-vehicles.md",
        ["irs-gov--publications-p946.md"],
        "Section 179 specifically for vehicles >6,000 lb GVWR vs passenger autos. Cover the SUV cap and the >6,000 lb rule. Quote any dollar figures verbatim from the source.",
    ),
    (
        "taxes/s-corp/reasonable-compensation.md",
        [
            "irs-gov--businesses-small-businesses-self-employed-paying-yourself.md",
            "irs-gov--businesses-small-businesses-self-employed-s-corporation-employees-shareholders-a.md",
        ],
        "S-corp reasonable compensation rules: why owner-employees must take W-2 salary, how distributions vs salary works, IRS scrutiny on under-compensation. Quote any IRS phrasing verbatim.",
    ),
    (
        "taxes/s-corp/distributions-vs-payroll.md",
        [
            "irs-gov--businesses-small-businesses-self-employed-paying-yourself.md",
            "irs-gov--businesses-small-businesses-self-employed-s-corporations.md",
        ],
        "S-corp tax mechanics: pass-through, distributions don't pay FICA, payroll does. The strategic angle: balance reasonable salary vs distributions to minimize SE/FICA tax.",
    ),
    (
        "taxes/retirement/solo-401k.md",
        ["irs-gov--retirement-plans-one-participant-401k-plans.md"],
        "Solo 401(k) for owner-only or owner+spouse businesses. Annual contribution limits (current year), employee deferral + employer profit-sharing, how S-corp owners use it.",
    ),
    (
        "taxes/retirement/sep-ira.md",
        ["irs-gov--retirement-plans-plan-sponsor-simplified-employee-pension-plan-sep.md"],
        "SEP-IRA for small businesses including S-corps. Contribution limits (current year), employer-only contributions, why an S-corp might pick SEP over solo 401k.",
    ),
    (
        "taxes/strategies/hire-family.md",
        ["irs-gov--businesses-small-businesses-self-employed-family-help.md"],
        "Hiring spouse and children in an S-corp. FICA exemptions for children under 18 only apply to sole props/partnerships — S-corp gets full FICA. Spouse on payroll mechanics.",
    ),
    (
        "taxes/strategies/business-travel.md",
        [
            "irs-gov--newsroom-heres-what-taxpayers-need-to-know-about-business-related-travel-deductions.md",
            "irs-gov--forms-pubs-about-publication-463.md",
        ],
        "Business travel deductions: ordinary and necessary, away-from-home rules, what qualifies, common pitfalls. S-corp owner perspective.",
    ),
    (
        "taxes/strategies/business-expenses-overview.md",
        [
            "irs-gov--forms-pubs-about-publication-535.md",
            "irs-gov--businesses-small-businesses-self-employed-deducting-business-expenses.md",
        ],
        "What counts as a deductible business expense (ordinary + necessary). S-corp specific examples relevant to retail (liquor store).",
    ),
]


PROMPT_TEMPLATE = """You are distilling raw IRS / tax-policy source material into a focused wiki page for a Section 179 / S-corp tax-strategy advisor.

The reader is a small-business S-corp owner trying to lower their tax burden legally. Your output will be loaded into the agent's context window — every line must earn its place.

## Hard rules

1. **Cite every claim** by including a `[source: <basename>.md]` reference inline with the fact. Use the basenames provided. Never cite something that wasn't in the sources.
2. **Quote dollar figures and IRS phrasing verbatim** when material (in quotation marks). Don't paraphrase the rule, paraphrase only the *explanation*.
3. **If sources don't cover the topic**, say so explicitly with a `> not in sources` line rather than fabricating. Better to ship a 60-point honest page than a 90-point fabricated one.
4. **Structure**: H1 title, then a 1-2 sentence summary, then `## Key facts` (bullets), then `## How it applies to an S-corp owner` (bullets), then `## Limits and gotchas`, then `## Sources` (list of source basenames).
5. **No filler**. No "consult a tax professional" sentences. No throat-clearing. Facts only.

## Topic focus

{focus}

## Sources

{sources}

Output only the markdown file content. Begin with the H1.
"""


def _read_raw(basenames: list[str]) -> str:
    chunks = []
    for name in basenames:
        path = RAW / "web" / name
        if not path.exists():
            chunks.append(f"### {name}\n[MISSING: file not found in wiki/raw/web/]")
            continue
        text = path.read_text(encoding="utf-8")
        chunks.append(f"### {name}\n\n{text}")
    return "\n\n---\n\n".join(chunks)


def distill_topic(spec: tuple[str, list[str], str]) -> Path:
    rel_path, basenames, focus = spec
    sources_block = _read_raw(basenames)

    prompt = PROMPT_TEMPLATE.format(focus=focus, sources=sources_block)
    resp = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    body = resp.choices[0].message.content.strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    out_path = TOPICS / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fm = {
        "topic": rel_path.replace(".md", ""),
        "sources": basenames,
        "distilled_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "distill_model": resp.model,
    }
    yaml_block = yaml.safe_dump(fm, sort_keys=False).strip()
    out_path.write_text(f"---\n{yaml_block}\n---\n\n{body}\n", encoding="utf-8")
    return out_path


def main() -> None:
    for spec in TOPIC_SPECS:
        try:
            path = distill_topic(spec)
            print(f"OK  {path.relative_to(REPO)}")
        except Exception as e:
            print(f"ERR {spec[0]}: {e}")


if __name__ == "__main__":
    main()
