"""Cross-reference resolver for entity graph.

Supports two kinds of edges:

- Frontmatter (structural): roles, jurisdictions, linked_topics, domains.
- Body refs (contextual): [[role:slug]], [[jur:path]], [[topic:path]], [[person:slug]].

The runtime resolves these into concrete file paths and loads the referenced
entity's overview.md or persona.md plus its wiki/ directory.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

ENTITIES_DIR = Path(__file__).resolve().parent
REPO_ROOT = ENTITIES_DIR.parent

REF_RE = re.compile(r"\[\[(role|jur|topic|person):([^\]]+)\]\]")


@dataclass(frozen=True)
class Ref:
    kind: str  # role | jur | topic | person
    slug: str  # the slash-path or slug after the colon

    @property
    def dir(self) -> Path:
        mapping = {"role": "roles", "jur": "jurisdictions", "topic": "topics", "person": "people"}
        return ENTITIES_DIR / mapping[self.kind] / self.slug

    @property
    def main_file(self) -> Path:
        return self.dir / ("persona.md" if self.kind == "person" else "overview.md")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter_dict, body)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 4 :].lstrip("\n")
    return fm, body


def refs_in_body(body: str) -> list[Ref]:
    return [Ref(kind, slug) for kind, slug in REF_RE.findall(body)]


def refs_in_frontmatter(fm: dict) -> list[Ref]:
    """Pull structural refs out of frontmatter."""
    out: list[Ref] = []
    for role_entry in fm.get("roles", []) or []:
        slug = role_entry.get("role") if isinstance(role_entry, dict) else role_entry
        if slug:
            out.append(Ref("role", slug))
    for slug in [fm.get("jurisdictions", {}).get("primary") if isinstance(fm.get("jurisdictions"), dict) else None]:
        if slug:
            out.append(Ref("jur", slug))
    for slug in fm.get("linked_topics", []) or []:
        out.append(Ref("topic", slug))
    return out


def load_entity_content(ref: Ref, max_chars: int = 25000) -> str | None:
    """Load main file + wiki contents. Returns None if entity doesn't exist."""
    if not ref.main_file.exists():
        return None
    chunks: list[str] = [ref.main_file.read_text(encoding="utf-8")]
    wiki_dir = ref.dir / "wiki"
    if wiki_dir.exists():
        for f in sorted(wiki_dir.rglob("*.md")):
            chunks.append(f"\n### {f.relative_to(REPO_ROOT)}\n\n{f.read_text(encoding='utf-8')}")
    text = "\n\n".join(chunks)
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n[... truncated at {max_chars} chars]"
    return text


def resolve_all(persona_path: Path) -> dict[Ref, str]:
    """Given a persona.md path, return all resolvable refs (frontmatter + body) -> content."""
    text = persona_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    refs = list({*refs_in_frontmatter(fm), *refs_in_body(body)})
    out: dict[Ref, str] = {}
    for r in refs:
        c = load_entity_content(r)
        if c is not None:
            out[r] = c
    return out
