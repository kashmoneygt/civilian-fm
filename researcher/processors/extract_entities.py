"""Extract entities (people + topics) from raw content fetched by crawl_url."""
from __future__ import annotations

from ..llm import complete_json
from ..pipeline import Request

PROMPT = """The following is raw text content (transcript or article) crawled from {url}.

Extract distinct named entities. Two kinds:

1. **People** — specific named individuals. Skip generic references ("the lawyer," "the chairman" without a name).
2. **Topics** — substantive concepts, events, or legal/technical subjects that deserve their own research page.

Return JSON:

{{
  "people": [
    {{
      "name": "<full name>",
      "slug": "<lowercase kebab-case, with disambiguator if common name>",
      "role_hint": "<one phrase about what they do, if clear from text>",
      "context_in_source": "<one sentence: how do they appear in this content>",
      "search_queries": ["<2-3 web search queries that would find more about this person>"]
    }}
  ],
  "topics": [
    {{
      "name": "<topic title>",
      "slug": "<domain/sub-slug, e.g. 'constitutional-law/14th-amendment-citizenship'>",
      "description": "<one sentence>",
      "search_queries": ["<2-3 web search queries>"]
    }}
  ]
}}

Rules:
- People slugs: famous figures use first-last (e.g. "donald-trump"); common names get a disambiguator (role or jurisdiction).
- Topic slugs: domain/topic — pick the domain pragmatically.
- Limit: up to 8 people and up to 6 topics. Pick the most central to the content.

# Source content

{content}"""


def run(req: Request) -> Request:
    content = req.state.get("raw_content", "")
    if not content:
        req.state["extracted_entities"] = {"people": [], "topics": []}
        return req

    out = complete_json(
        PROMPT.format(url=req.user_url or "(no url)", content=content[:120_000]),
        temperature=0.0,
    )
    req.state["extracted_entities"] = out
    return req
