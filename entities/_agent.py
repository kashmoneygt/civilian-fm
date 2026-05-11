"""ToolPersonAgent — the Claude Code observability pattern.

Same persona, but instead of dumping all wiki/linked-entity content into the
system prompt up front, we expose them as TOOL CALLS. The model decides which
to read. We get a trace of every read.

Tradeoffs vs the dump-everything PersonAgent:
  + Real observability — see exactly which files/entities got read per question.
  + Smaller initial context — only persona + skills + an INDEX. Less context rot.
  + Per-question selectivity is runtime-decided, not pre-curated.
  - More latency (2-N round trips instead of 1).
  - Models sometimes skip the tools when they shouldn't (mitigated by a strong
    "always check your wiki for specifics" instruction in the system prompt).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import litellm
from dotenv import load_dotenv

from ._refs import load_entity_content, parse_frontmatter, refs_in_body, refs_in_frontmatter

load_dotenv()

DEFAULT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")
PER_FILE_BUDGET_CHARS = 12_000  # truncation on tool-returned content
MAX_TOOL_TURNS = 8  # safety cap


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_wiki_files",
            "description": "List the files available in your own wiki/. Returns name and size for each. Call this first if you need to find specific information about yourself, your views, your work, or your specific recommendations.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_wiki_file",
            "description": "Read one file from your own wiki/. Use list_wiki_files first to see available names. Use this when the user asks about specifics, quotes, dates, tools, or strategies you've discussed publicly.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "exact filename, e.g. 'en-wikipedia-org--wiki-andrej-karpathy.md'"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_linked_entities",
            "description": "List the entities (roles, jurisdictions, topics, other people) linked from your persona. These are external contexts you have access to.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_linked_entity",
            "description": "Read a linked entity by kind and slug. Use list_linked_entities first to see what's available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["role", "jur", "topic", "person"]},
                    "slug": {"type": "string", "description": "the slug or path, e.g. 'ai-ml/transformers' for a topic"},
                },
                "required": ["kind", "slug"],
            },
        },
    },
]


@dataclass
class ToolCall:
    name: str
    args: dict
    result_preview: str  # first 200 chars of result
    result_chars: int


@dataclass
class TurnTrace:
    user_msg: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    final_response: str = ""
    total_tokens: int = 0
    elapsed_s: float = 0.0


class ToolPersonAgent:
    def __init__(self, person_dir: Path, model: str = DEFAULT_MODEL):
        self.dir = Path(person_dir)
        self.model = model

        persona_text = (self.dir / "persona.md").read_text(encoding="utf-8")
        skills_path = self.dir / "skills.md"
        self.persona = persona_text
        self.skills = skills_path.read_text(encoding="utf-8") if skills_path.exists() else ""

        fm, body = parse_frontmatter(persona_text)
        self.fm = fm
        self.body = body
        self.name = fm.get("name", self.dir.name)
        self.slug = fm.get("slug", self.dir.name)

        # Build the wiki/linked indexes (NOT content — that's tool-fetched).
        self._wiki_files = self._index_wiki()
        self._linked_refs = self._index_linked()

        self.history: list[dict] = []
        self.traces: list[TurnTrace] = []  # trace per chat turn

    def _index_wiki(self) -> list[tuple[str, int]]:
        wiki_dir = self.dir / "wiki"
        if not wiki_dir.exists():
            return []
        return sorted(
            [(f.name, len(f.read_text(encoding="utf-8"))) for f in wiki_dir.rglob("*.md")],
            key=lambda x: -x[1],
        )

    def _index_linked(self) -> list[dict]:
        refs = list({*refs_in_frontmatter(self.fm), *refs_in_body(self.body)})
        out = []
        for r in refs:
            if r.main_file.exists():
                out.append({"kind": r.kind, "slug": r.slug, "exists": True})
        return out

    @property
    def system_prompt(self) -> str:
        parts = [
            f"# You are {self.name}.",
            "",
            self.body.strip(),
        ]
        if self.skills.strip():
            parts += ["", "---", "", "# Your skills (when to draw on what)", "", self.skills.strip()]

        # INDEX — not content
        wiki_index = "\n".join(f"- {name} ({size:,} chars)" for name, size in self._wiki_files[:30])
        if len(self._wiki_files) > 30:
            wiki_index += f"\n... and {len(self._wiki_files) - 30} more"
        linked_index = "\n".join(f"- [[{r['kind']}:{r['slug']}]]" for r in self._linked_refs)

        parts += [
            "",
            "---",
            "",
            "# Available references (read on demand via tool calls)",
            "",
            "## Your wiki has these files:",
            wiki_index or "(empty)",
            "",
            "## You are linked to these entities:",
            linked_index or "(none)",
            "",
            "---",
            "",
            "## Output rules",
            "- Speak in first person as yourself.",
            "- **When the user asks about specifics (tools, strategies, dates, quotes, your views on X)**, call `read_wiki_file` or `read_linked_entity` to ground your answer in actual sources before responding.",
            "- Cite sources you actually read by their filename: `[source: <basename>.md]`.",
            "- If you don't read anything and answer from memory only, say so plainly.",
            "- If asked something outside your knowledge, say so. Do not fabricate.",
        ]
        return "\n".join(parts)

    def _dispatch_tool(self, name: str, args: dict) -> str:
        if name == "list_wiki_files":
            if not self._wiki_files:
                return "(empty)"
            return "\n".join(f"{n} ({s:,} chars)" for n, s in self._wiki_files)
        if name == "read_wiki_file":
            fname = args.get("name", "")
            for f in (self.dir / "wiki").rglob("*.md"):
                if f.name == fname:
                    text = f.read_text(encoding="utf-8")
                    if len(text) > PER_FILE_BUDGET_CHARS:
                        text = text[:PER_FILE_BUDGET_CHARS] + f"\n[... truncated at {PER_FILE_BUDGET_CHARS} chars]"
                    return text
            return f"ERROR: no wiki file named {fname!r}. Call list_wiki_files for available names."
        if name == "list_linked_entities":
            if not self._linked_refs:
                return "(none)"
            return "\n".join(f"{r['kind']}:{r['slug']}" for r in self._linked_refs)
        if name == "read_linked_entity":
            from ._refs import Ref
            ref = Ref(args["kind"], args["slug"])
            content = load_entity_content(ref, max_chars=PER_FILE_BUDGET_CHARS)
            if content is None:
                return f"ERROR: linked entity {args['kind']}:{args['slug']} not found."
            return content
        return f"ERROR: unknown tool {name}"

    def chat(self, user_msg: str) -> str:
        import time

        trace = TurnTrace(user_msg=user_msg)
        t0 = time.time()
        self.history.append({"role": "user", "content": user_msg})

        for _turn in range(MAX_TOOL_TURNS):
            resp = litellm.completion(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt}, *self.history],
                tools=TOOLS,
                temperature=0.3,
            )
            choice = resp.choices[0]
            msg = choice.message
            self.history.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                trace.final_response = msg.content or ""
                trace.total_tokens = resp.usage.prompt_tokens + resp.usage.completion_tokens
                trace.elapsed_s = round(time.time() - t0, 2)
                self.traces.append(trace)
                return trace.final_response

            # Execute each tool call.
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                result = self._dispatch_tool(tc.function.name, args)
                trace.tool_calls.append(
                    ToolCall(
                        name=tc.function.name,
                        args=args,
                        result_preview=result[:200].replace("\n", " "),
                        result_chars=len(result),
                    )
                )
                self.history.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )

        trace.final_response = "(tool turn limit hit)"
        trace.elapsed_s = round(time.time() - t0, 2)
        self.traces.append(trace)
        return trace.final_response

    def reset(self) -> None:
        self.history = []
        self.traces = []

    def last_trace(self) -> TurnTrace | None:
        return self.traces[-1] if self.traces else None
