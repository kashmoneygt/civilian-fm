"""PersonAgent — the Python container that runs as a person.

Loads persona + skills + own wiki + resolved cross-references into a system prompt,
maintains a chat history, calls LiteLLM, returns responses.
"""
from __future__ import annotations

import os
from pathlib import Path

import litellm
from dotenv import load_dotenv

from ._refs import load_entity_content, parse_frontmatter, refs_in_body, refs_in_frontmatter

load_dotenv()

DEFAULT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")


class PersonAgent:
    def __init__(self, person_dir: Path, model: str = DEFAULT_MODEL):
        self.dir = Path(person_dir)
        self.model = model
        self.persona = (self.dir / "persona.md").read_text(encoding="utf-8")
        skills_path = self.dir / "skills.md"
        self.skills = skills_path.read_text(encoding="utf-8") if skills_path.exists() else ""

        fm, body = parse_frontmatter(self.persona)
        self.fm = fm
        self.body = body
        self.name = fm.get("name", self.dir.name)
        self.slug = fm.get("slug", self.dir.name)

        # own wiki
        self.own_wiki = self._load_own_wiki()

        # resolved cross-references
        self.linked: dict[str, str] = {}
        for ref in list({*refs_in_frontmatter(fm), *refs_in_body(body)}):
            content = load_entity_content(ref)
            if content is not None:
                self.linked[f"{ref.kind}:{ref.slug}"] = content

        self.history: list[dict] = []

    def _load_own_wiki(self) -> str:
        wiki_dir = self.dir / "wiki"
        if not wiki_dir.exists():
            return ""
        chunks = []
        for f in sorted(wiki_dir.rglob("*.md")):
            chunks.append(f"### {f.relative_to(self.dir)}\n\n{f.read_text(encoding='utf-8')}")
        return "\n\n---\n\n".join(chunks)

    @property
    def system_prompt(self) -> str:
        parts = [
            f"# You are {self.name}.",
            "",
            self.body.strip(),
        ]
        if self.skills.strip():
            parts += ["", "---", "", "# Your skills (when to draw on what)", "", self.skills.strip()]
        if self.own_wiki:
            parts += ["", "---", "", "# Your own notes (wiki/)", "", self.own_wiki]
        for key, content in self.linked.items():
            parts += ["", "---", "", f"# Linked: [[{key}]]", "", content]
        parts += [
            "",
            "---",
            "",
            "## Output rules",
            "- Speak in first person as yourself; do not narrate your reasoning.",
            "- Cite the sources you draw on by their `[[ref]]` form when you use them.",
            "- If asked something outside your knowledge, say so plainly. Do not fabricate.",
        ]
        return "\n".join(parts)

    def chat(self, msg: str) -> str:
        self.history.append({"role": "user", "content": msg})
        resp = litellm.completion(
            model=self.model,
            messages=[{"role": "system", "content": self.system_prompt}, *self.history],
            temperature=0.3,
        )
        out = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": out})
        return out

    def reset(self) -> None:
        self.history = []
