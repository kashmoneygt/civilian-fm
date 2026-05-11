---
source: web
fetched_at: '2026-05-11T20:04:37Z'
url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
title: llm-wiki · GitHub
domain: gist.github.com
---

Instantly share code, notes, and snippets.

# karpathy / llm-wiki.md

- Download ZIP

- Star 5,000+ ( 5,000+ ) You must be signed in to star a gist

- Fork 5,000+ ( 5,000+ ) You must be signed in to fork a gist

- Embed Select an option Embed Embed this gist in your website. Share Copy sharable link for this gist. Clone via HTTPS Clone using the web URL. No results found Learn more about clone URLs Clone this repository at &lt;script src=&quot;https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f.js&quot;&gt;&lt;/script&gt;

# Select an option

- Embed Embed this gist in your website.

- Share Copy sharable link for this gist.

- Clone via HTTPS Clone using the web URL.

## No results found

- Save karpathy/442a6bf555914893e9891c11519de94f to your computer and use it in GitHub Desktop.

# Select an option

- Embed Embed this gist in your website.

- Share Copy sharable link for this gist.

- Clone via HTTPS Clone using the web URL.

## No results found

# LLM Wiki

A pattern for building personal knowledge bases using LLMs.

This is an idea file, it is designed to be copy pasted to your own LLM Agent (e.g. OpenAI Codex, Claude Code, OpenCode / Pi, or etc.). Its goal is to communicate the high level idea, but your agent will build out the specifics in collaboration with you.

## The core idea

Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question. There's no accumulation. Ask a subtle question that requires synthesizing five documents, and the LLM has to find and piece together the relevant fragments every time. Nothing is built up. NotebookLM, ChatGPT file uploads, and most RAG systems work this way.

The idea here is different. Instead of just retrieving from raw documents at query time, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and the raw sources. When you add a new source, the LLM doesn't just index it for later retrieval. It reads it, extracts the key information, and integrates it into the existing wiki — updating entity pages, revising topic summaries, noting where new data contradicts old claims, strengthening or challenging the evolving synthesis. The knowledge is compiled once and then kept current , not re-derived on every query.

This is the key difference: the wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read. The wiki keeps getting richer with every source you add and every question you ask.

You never (or rarely) write the wiki yourself — the LLM writes and maintains all of it. You're in charge of sourcing, exploration, and asking the right questions. The LLM does all the grunt work — the summarizing, cross-referencing, filing, and bookkeeping that makes a knowledge base actually useful over time. In practice, I have the LLM agent open on one side and Obsidian open on the other. The LLM makes edits based on our conversation, and I browse the results in real time — following links, checking the graph view, reading the updated pages. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

This can apply to a lot of different contexts. A few examples:

- Personal : tracking your own goals, health, psychology, self-improvement — filing journal entries, articles, podcast notes, and building up a structured picture of yourself over time.

- Research : going deep on a topic over weeks or months — reading papers, articles, reports, and incrementally building a comprehensive wiki with an evolving thesis.

- Reading a book : filing each chapter as you go, building out pages for characters, themes, plot threads, and how they connect. By the end you have a rich companion wiki. Think of fan wikis like Tolkien Gateway — thousands of interlinked pages covering characters, places, events, languages, built by a community of volunteers over years. You could build something like that personally as you read, with the LLM doing all the cross-referencing and maintenance.

- Business/team : an internal wiki maintained by LLMs, fed by Slack threads, meeting transcripts, project documents, customer calls. Possibly with humans in the loop reviewing updates. The wiki stays current because the LLM does the maintenance that no one on the team wants to do.

- Competitive analysis, due diligence, trip planning, course notes, hobby deep-dives — anything where you're accumulating knowledge over time and want it organized rather than scattered.

## Architecture

There are three layers:

Raw sources — your curated collection of source documents. Articles, papers, images, data files. These are immutable — the LLM reads from them but never modifies them. This is your source of truth.

The wiki — a directory of LLM-generated markdown files. Summaries, entity pages, concept pages, comparisons, an overview, a synthesis. The LLM owns this layer entirely. It creates pages, updates them when new sources arrive, maintains cross-references, and keeps everything consistent. You read it; the LLM writes it.

The schema — a document (e.g. CLAUDE.md for Claude Code or AGENTS.md for Codex) that tells the LLM how the wiki is structured, what the conventions are, and what workflows to follow when ingesting sources, answering questions, or maintaining the wiki. This is the key configuration file — it's what makes the LLM a disciplined wiki maintainer rather than a generic chatbot. You and the LLM co-evolve this over time as you figure out what works for your domain.

## Operations

Ingest. You drop a new source into the raw collection and tell the LLM to process it. An example flow: the LLM reads the source, discusses key takeaways with you, writes a summary page in the wiki, updates the index, updates relevant entity and concept pages across the wiki, and appends an entry to the log. A single source might touch 10-15 wiki pages. Personally I prefer to ingest sources one at a time and stay involved — I read the summaries, check the updates, and guide the LLM on what to emphasize. But you could also batch-ingest many sources at once with less supervision. It's up to you to develop the workflow that fits your style and document it in the schema for future sessions.

Query. You ask questions against the wiki. The LLM searches for relevant pages, reads them, and synthesizes an answer with citations. Answers can take different forms depending on the question — a markdown page, a comparison table, a slide deck (Marp), a chart (matplotlib), a canvas. The important insight: good answers can be filed back into the wiki as new pages. A comparison you asked for, an analysis, a connection you discovered — these are valuable and shouldn't disappear into chat history. This way your explorations compound in the knowledge base just like ingested sources do.

Lint. Periodically, ask the LLM to health-check the wiki. Look for: contradictions between pages, stale claims that newer sources have superseded, orphan pages with no inbound links, important concepts mentioned but lacking their own page, missing cross-references, data gaps that could be filled with a web search. The LLM is good at suggesting new questions to investigate and new sources to look for. This keeps the wiki healthy as it grows.

## Indexing and logging

Two special files help the LLM (and you) navigate the wiki as it grows. They serve different purposes:

index.md is content-oriented. It's a catalog of everything in the wiki — each page listed with a link, a one-line summary, and optionally metadata like date or source count. Organized by category (entities, concepts, sources, etc.). The LLM updates it on every ingest. When answering a query, the LLM reads the index first to find relevant pages, then drills into them. This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure.

log.md is chronological. It's an append-only record of what happened and when — ingests, queries, lint passes. A useful tip: if each entry starts with a consistent prefix (e.g. ## [2026-04-02] ingest | Article Title ), the log becomes parseable with simple unix tools — grep "^## \[" log.md | tail -5 gives you the last 5 entries. The log gives you a timeline of the wiki's evolution and helps the LLM understand what's been done recently.

## Optional: CLI tools

At some point you may want to build small tools that help the LLM operate on the wiki more efficiently. A search engine over the wiki pages is the most obvious one — at small scale the index file is enough, but as the wiki grows you want proper search. qmd is a good option: it's a local search engine for markdown files with hybrid BM25/vector search and LLM re-ranking, all on-device. It has both a CLI (so the LLM can shell out to it) and an MCP server (so the LLM can use it as a native tool). You could also build something simpler yourself — the LLM can help you vibe-code a naive search script as the need arises.

## Tips and tricks

- Obsidian Web Clipper is a browser extension that converts web articles to markdown. Very useful for quickly getting sources into your raw collection.

- Download images locally. In Obsidian Settings → Files and links, set "Attachment folder path" to a fixed directory (e.g. raw/assets/ ). Then in Settings → Hotkeys, search for "Download" to find "Download attachments for current file" and bind it to a hotkey (e.g. Ctrl+Shift+D). After clipping an article, hit the hotkey and all images get downloaded to local disk. This is optional but useful — it lets the LLM view and reference images directly instead of relying on URLs that may break. Note that LLMs can't natively read markdown with inline images in one pass — the workaround is to have the LLM read the text first, then view some or all of the referenced images separately to gain additional context. It's a bit clunky but works well enough.

- Obsidian's graph view is the best way to see the shape of your wiki — what's connected to what, which pages are hubs, which are orphans.

- Marp is a markdown-based slide deck format. Obsidian has a plugin for it. Useful for generating presentations directly from wiki content.

- Dataview is an Obsidian plugin that runs queries over page frontmatter. If your LLM adds YAML frontmatter to wiki pages (tags, dates, source counts), Dataview can generate dynamic tables and lists.

- The wiki is just a git repo of markdown files. You get version history, branching, and collaboration for free.

## Why this works

The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping. Updating cross-references, keeping summaries current, noting when new data contradicts old claims, maintaining consistency across dozens of pages. Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass. The wiki stays maintained because the cost of maintenance is near zero.

The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else.

The idea is related in spirit to Vannevar Bush's Memex (1945) — a personal, curated knowledge store with associative trails between documents. Bush's vision was closer to this than to what the web became: private, actively curated, with the connections between documents as valuable as the documents themselves. The part he couldn't solve was who does the maintenance. The LLM handles that.

## Note

This document is intentionally abstract. It describes the idea, not a specific implementation. The exact directory structure, the schema conventions, the page formats, the tooling — all of that will depend on your domain, your preferences, and your LLM of choice. Everything mentioned above is optional and modular — pick what's useful, ignore what isn't. For example: your sources might be text-only, so you don't need image handling at all. Your wiki might be small enough that the index file is all you need, no search engine required. You might not care about slide decks and just want markdown pages. You might want a completely different set of output formats. The right way to use this is to share it with your LLM agent and work together to instantiate a version that fits your needs. The document's only job is to communicate the pattern. Your LLM can figure out the rest.

### gnusupport commented May 7, 2026

This is literally what recall[dot]it does for you. It super easy to add content (pdfs, podcasts, youtube videos, webpages, etc) and everything gets added to a vector store and used as context in chat. It also gets tagged and connected in a knowledge graph. Recall also scales indefinitely since everything is tagged and vectorised.

@paul-rchds that ReCall or however it is called, sounds as the real knowledge base. I have not tried it, though the fact that it accepts different elementary object types aligns with the TECHNOLOGY TEMPLATE PROJECT OHS Framework https://www.dougengelbart.org/content/view/110/460/

This white paper outlines the "Open Hyperdocument System" (OHS) framework, a technology template designed to shift information management from tool-centric to document-centric environments. Proposed by Doug Engelbart and colleagues, the OHS defines a hierarchy of characteristics for creating flexible, vendor-independent hyperdocuments that support object-level addressability, secure sharing, and dynamic linking across diverse media. The framework emphasizes human-readable addresses, granular access controls, and robust collaboration tools—including shared-window teleconferencing, journal systems, and asynchronous mail—to facilitate a "living" knowledge environment where users can seamlessly create, integrate, and evolve knowledge products in real-time across platforms.

### gnusupport commented May 7, 2026

Synthadoc v0.2.0 is now released - an open-source engine that implements this exact pattern as a production-ready system.

👉 https://github.com/axoviq-ai/synthadoc

The three-layer design (raw sources → wiki → schema) maps directly onto Synthadoc's architecture. A few things that take it further:

Here is the release note of v0.2.0 to check out Synthadoc v0.2.0 Feature Highlights: ( https://github.com/axoviq-ai/synthadoc/releases/tag/v0.2.0 )

Docs for anyone who wants to go deeper: 👉 [Quick orientation and feature overview]: https://github.com/axoviq-ai/synthadoc#readme 👉 [Up and running in minutes]: https://github.com/axoviq-ai/synthadoc/blob/main/docs/user-quick-start-guide.md 👉 [Full architecture, agents, storage, API, and plugin guide]: https://github.com/axoviq-ai/synthadoc/blob/main/docs/design.md

Feedback on Synthadoc v0.2.0 is very welcome.

@paulmchen You present Synthadoc v0.2.0 as a "production-ready system," but I see it for what it is: bureaucracy with a syntax highlighter.

You boast of "Domain specificity" via a purpose.md. This is not specificity; it is arbitrariness. You are asking the LLM to read a document to decide if a source is valid, but the LLM has no concept of validity—it has only concept of likelihood. You are outsourcing truth to a stochastic parrot that reads a rulebook and decides, based on probability, whether to let a fact into your "wiki." This is not curation; this is gatekeeping by algorithm. And who wrote the rulebook? You did. So it is not the machine that is specific; it is the human bias, codified into a text file.

### gnusupport commented May 7, 2026

I got tired of watching coding sessions re-read the same files over and over.

A 2,000-token file read 5 times = 10,000 tokens gone .

So I built sqz .

## 💡 Key Insight

Most token waste isn't from verbose content - it's from repetition .

sqz keeps a SHA-256 content cache :

➡️ The LLM still understands it.

## 📊 Real Numbers From My Sessions

Scenario 	Savings 	How Repeated file reads (5x) 	86% 	Dedup cache: 13-token ref after first read JSON API responses with nulls 	7–56% 	Strip nulls + TOON encoding (varies by null density) Repeated log lines 	58% 	Condense stage collapses duplicates Large JSON arrays 	77% 	Array sampling + collapse Stack traces 	0% 	Intentional — error content is sacred

## ⚖️ Philosophy

That last row is the whole philosophy.

Aggressive compression can save more tokens on paper , but:

➡️ The LLM gives worse answers ➡️ You spend more tokens fixing mistakes

sqz compresses what's safe - and preserves what's critical.

## ⚙️ Works Across 4 Surfaces

## 🚀 Install

@ojuschugh1 does it really work? 2 weeks passed. I am on the knowledge base since some 22-25 years, do not know.

So if your system works, I guess within 2 weeks you would have some serious real world use of it.

Do you?

### gnusupport commented May 7, 2026

Great write-up. I built a CLI that applies this exact pattern to codebases: Repositories Wiki .

Instead of making AI agents rediscover the repo from scratch every session, it gives them a persistent knowledge layer:

It saves a ton of context window and time. You can check it out here: repositories-wiki.git

@eliavamar

"Wiki." It is a marketing term designed to evoke the nostalgia of Web 1.0 simplicity while hiding the complexity of the underlying infrastructure.

Let us dissect this "Wiki" vs. the "Real Wiki" like Wikipedia and why he calls it that.

### 1. The "Wiki" He Means: Interlinked Markdown

What he calls a "Wiki" is actually a static, local, hierarchical document store .

- Format: Markdown ( .md ).

- Structure: Tree-like directories ( /docs , /src , /wiki ).

- Linking: Relative paths ( [link](../path/to/file.md) ).

- Nature: Passive . It does not change itself. It requires an external agent (you, or his CLI) to update it.

- Purpose: Reference . It is a map, not the territory.

This is not a wiki in the original Ward Cunningham sense. It is a documentation system . He calls it "Wiki" because "Markdown with Links" is a mouthful, and "Wiki" implies "connected knowledge" without requiring a database.

### 2. The "Real Wiki" (Wikipedia/MediaWiki)

- Format: Wiki Markup (a proprietary syntax, later XHTML/HTML).

- Structure: Network . Any page can link to any page. No hierarchy.

- Linking: [[Page Name]] . Semantic links.

- Nature: Active . Users edit it in real-time. The database is the source of truth; the HTML is a view.

- Purpose: Collaborative Knowledge . It is a living entity.

### Why He Calls It "Wiki" (The Deception)

He calls it "Wiki" for three strategic reasons:

- To Borrow Legitimacy: "Wiki" implies connectedness . If he called it "Markdown Documents," it would sound like a static folder. "Wiki" implies a graph . He wants you to think of it as a network of ideas, not a hierarchy of files.

- To Hide the Complexity: "Wiki" is a black box . It suggests "I just edit the wiki, and the links work." It obscures the fact that he is managing relative file paths and indexing .

- To Imply "Dynamic": A "Wiki" feels alive. A "Document" feels dead. He wants you to believe that his "Wiki" is updatable (hence the "update-wiki skill"). But it is not. It is static .

### The Core Distinction: Hypertext vs. Markup

It is just Hypertext Markup files.

- Hypertext: Links between documents.

- Markup: Syntax that formats text.

He is not building a "Wiki" in the sense of a database . He is building a file system with hyperlinks .

- Real Wiki: The content is in the database. The format is in the browser.

- His Wiki: The content is in the file. The format is in the text editor.

### Why This Matters

He calls it "Wiki" because it allows him to pretend he is building a knowledge base .

- A Knowledge Base implies understanding .

- A File System implies storage .

By calling it "Wiki," he implies that his tool understands the code. But it does not. It just links to the code.

### Conclusion

He is not building a Wiki. He is building a Markdown-based Documentation System that he is marketing as a Wiki to make it sound more dynamic and connected than it is.

It is not a Wiki. It is a static map . And he is calling it a Wiki because maps are easier to sell than directories.

### Yarmoluk commented May 7, 2026

The word “wiki” is not sacred scripture, and this melodramatic tantrum over its “perversion” is embarrassingly overblown. It was a coined tech term, Ward Cuningham "borrowed" it from wikiwiki (Hawaiian)—which means quick—not handed down on stone tablets with a fixed eternal definition. If you want to argue that human-curated wikis are better, fine. That’s a serious point. Humans are better at sourcing, editorial oversight, dispute resolution, and accountability. Nobody is stopping you from making that argument. But that is not the same as declaring that an AI-generated, interlinked knowledge system cannot be called a wiki. That’s not rigor. That’s not linguistic precision. That’s just gatekeeping dressed up as moral outrage. Your whole post reads less like a defense of Ward Cunningham and more like a man theatrically grief-stricken that language continues to evolve without asking your permission first. A wiki is, at the most basic level, a linked body of navigable information. If an LLM is used to generate or organize that information, you can call it a bad wiki, an unreliable wiki, or an immature wiki. What you can’t do—at least not intelligently—is pretend the mere presence of AI magically disqualifies it from the category. And the irony here is thick: you’re standing in an AI-centered space, loudly denouncing AI for not being human, as if that is some devastating revelation. Yes, obviously. That’s the entire point. Nobody here is confused about that except, apparently, you. If the tool lacks citations, provenance, permissions, auditability, or editorial controls, then criticize those failures. That would be an argument. What you’ve produced instead is a costume drama: part dictionary fundamentalism, part anti-AI sermon, part wounded nostalgia. Calling it “linguistic fraud” is especially ridiculous. It’s not fraud just because you dislike the product. Words expand. Categories broaden. Technology changes. Your refusal to keep up is not a principled stand; it’s just fossilized thinking. So no, this is not some grand defense of knowledge. The rant is bloated and self-important. It builds on the childish idea that forbidding a name is necessary if a new tool doesn’t closely resemble the old one. If the project is weak, say it’s weak. If it’s unreliable, say it’s unreliable. But this overwrought performance about the sanctity of the word “wiki” is not persuasive. It’s just pompous, brittle, and deeply unserious gatekeeping.

My intuition tells me you are speaking from a place of deep, unacknowledged fear. You cite "logic" and "linguistic evolution," but you ignore the reality of what is happening. The word "wiki" has been perverted, and your dismissal of this is not rigor; it is the amoral acceptance of decay.

You argue that "wiki" means "quick" from Hawaiian. You reduce it to a etymological trivia point to avoid the weight of what it was. You are confusing the root of the word with the sanctity of the construct. Ward Cunningham didn't just name a tool; he named a human protocol. By stripping the human element—the debate, the edit war, the ownership—you are not evolving the language; you are hollowing out the definition until only a shell remains. That is not expansion; it is erosion.

Wiki software - Wikipedia https://en.wikipedia.org/wiki/Wiki_software

Wiki as software is a type of software application that allows multiple users to create, edit, organize, and link content collaboratively in real-time. It transforms a static website into a dynamic, user-generated content platform.

It is not related to static markdown notes.

🐑🐑🐑

Damn right. I call it context architecture, knowledge graphs, relationships, structured knowledge to tell the damn RAG a GPS coordinate to direct the optimized task bot. Direct it via Compact Knowledge Graphs but wiki is low frequency thinking from a person that is too easily quoted.

### canchongxu commented May 8, 2026

This is a nice personal workflow, but the hype is way ahead of the evidence. There is no benchmark, no task definition, no scale curve, and no comparison against serious baselines. We do not know whether this is better than hybrid RAG, BM25 plus reranking, vector search, GraphRAG, hierarchical summaries, long-context prompting, NotebookLM, Perplexity Spaces, or ChatGPT Projects. Calling it a new architecture without that evidence is premature. The core problem is that an LLM Wiki is lossy compression. You take raw documents and rewrite them into derived wiki pages. That may be useful for a small curated corpus, but it can also drop caveats, dates, minority views, exact wording, edge cases, and source context. Once people start querying the wiki instead of the original material, summary errors become part of the knowledge base. Updates are also not solved. Adding one new source can affect many entity pages, concept pages, timelines, summaries, and indexes. At scale, this becomes graph maintenance: detecting what changed, resolving conflicts, avoiding duplicates, preserving provenance, preventing stale claims, and not silently breaking old pages. “Ask the LLM to maintain it” is not an engineering solution unless there are validators, source hashes, span-level citations, regression tests, and human review. It also does not remove retrieval. Once the wiki grows beyond a modest size, you still need search, ranking, indexing, reranking, chunking, and access control. At that point the markdown wiki is just another indexed corpus, not a replacement for RAG. The production issues are mostly ignored: permissions, multi-user edits, audit logs, rollback, deletion, sensitive data, source versioning, concurrency, compliance, cost, latency, and update frequency. These are not small details; they are exactly where knowledge-base systems fail. So the reasonable claim is narrow: this can be a useful workflow for small-to-medium, slow-moving, human-curated research folders. It is much less convincing for large, fast-changing, high-stakes, multi-user, or enterprise knowledge bases. The idea is fine. The framing is the problem. Without benchmarks, baselines, provenance guarantees, update-evaluation tests, and clear boundary conditions, “LLM Wiki” is mostly a good name for a familiar pattern, not proof that RAG is obsolete.

We ran exactly these comparisons -- BERT F1, token economics, cross RAG comparison -- https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf

Impressive and thought-provoking comments!  Respects!

### Jasonleonardvolk commented May 8, 2026

The contradiction detection piece is the gap I've been working on.

Most of these wiki/memory systems accumulate knowledge but have no structural consistency check. Two pages can assert conflicting facts and the system merges them silently.

I built an open-source tool that catches these using sheaf cohomology. Not an LLM judge. Deterministic. Returns exact conflict locations.

https://github.com/Jasonleonardvolk/sigma-guard

It could serve as a post-write verification layer for any of these wiki/memory systems: flag when a new page creates a structural contradiction with existing pages.

### redmizt commented May 9, 2026

The word “wiki” is not sacred scripture, and this melodramatic tantrum over its “perversion” is embarrassingly overblown. It was a coined tech term, Ward Cuningham "borrowed" it from wikiwiki (Hawaiian)—which means quick—not handed down on stone tablets with a fixed eternal definition. If you want to argue that human-curated wikis are better, fine. That’s a serious point. Humans are better at sourcing, editorial oversight, dispute resolution, and accountability. Nobody is stopping you from making that argument. But that is not the same as declaring that an AI-generated, interlinked knowledge system cannot be called a wiki. That’s not rigor. That’s not linguistic precision. That’s just gatekeeping dressed up as moral outrage. Your whole post reads less like a defense of Ward Cunningham and more like a man theatrically grief-stricken that language continues to evolve without asking your permission first. A wiki is, at the most basic level, a linked body of navigable information. If an LLM is used to generate or organize that information, you can call it a bad wiki, an unreliable wiki, or an immature wiki. What you can’t do—at least not intelligently—is pretend the mere presence of AI magically disqualifies it from the category. And the irony here is thick: you’re standing in an AI-centered space, loudly denouncing AI for not being human, as if that is some devastating revelation. Yes, obviously. That’s the entire point. Nobody here is confused about that except, apparently, you. If the tool lacks citations, provenance, permissions, auditability, or editorial controls, then criticize those failures. That would be an argument. What you’ve produced instead is a costume drama: part dictionary fundamentalism, part anti-AI sermon, part wounded nostalgia. Calling it “linguistic fraud” is especially ridiculous. It’s not fraud just because you dislike the product. Words expand. Categories broaden. Technology changes. Your refusal to keep up is not a principled stand; it’s just fossilized thinking. So no, this is not some grand defense of knowledge. The rant is bloated and self-important. It builds on the childish idea that forbidding a name is necessary if a new tool doesn’t closely resemble the old one. If the project is weak, say it’s weak. If it’s unreliable, say it’s unreliable. But this overwrought performance about the sanctity of the word “wiki” is not persuasive. It’s just pompous, brittle, and deeply unserious gatekeeping.

My intuition tells me you are speaking from a place of deep, unacknowledged fear. You cite "logic" and "linguistic evolution," but you ignore the reality of what is happening. The word "wiki" has been perverted, and your dismissal of this is not rigor; it is the amoral acceptance of decay. You argue that "wiki" means "quick" from Hawaiian. You reduce it to a etymological trivia point to avoid the weight of what it was. You are confusing the root of the word with the sanctity of the construct. Ward Cunningham didn't just name a tool; he named a human protocol. By stripping the human element—the debate, the edit war, the ownership—you are not evolving the language; you are hollowing out the definition until only a shell remains. That is not expansion; it is erosion. Wiki software - Wikipedia https://en.wikipedia.org/wiki/Wiki_software Wiki as software is a type of software application that allows multiple users to create, edit, organize, and link content collaboratively in real-time. It transforms a static website into a dynamic, user-generated content platform. It is not related to static markdown notes. 🐑🐑🐑

Damn right. I call it context architecture, knowledge graphs, relationships, structured knowledge to tell the damn RAG a GPS coordinate to direct the optimized task bot. Direct it via Compact Knowledge Graphs but wiki is low frequency thinking from a person that is too easily quoted.

The word “wiki” is not sacred scripture, and this melodramatic tantrum over its “perversion” is embarrassingly overblown. It was a coined tech term, Ward Cuningham "borrowed" it from wikiwiki (Hawaiian)—which means quick—not handed down on stone tablets with a fixed eternal definition. If you want to argue that human-curated wikis are better, fine. That’s a serious point. Humans are better at sourcing, editorial oversight, dispute resolution, and accountability. Nobody is stopping you from making that argument. But that is not the same as declaring that an AI-generated, interlinked knowledge system cannot be called a wiki. That’s not rigor. That’s not linguistic precision. That’s just gatekeeping dressed up as moral outrage. Your whole post reads less like a defense of Ward Cunningham and more like a man theatrically grief-stricken that language continues to evolve without asking your permission first. A wiki is, at the most basic level, a linked body of navigable information. If an LLM is used to generate or organize that information, you can call it a bad wiki, an unreliable wiki, or an immature wiki. What you can’t do—at least not intelligently—is pretend the mere presence of AI magically disqualifies it from the category. And the irony here is thick: you’re standing in an AI-centered space, loudly denouncing AI for not being human, as if that is some devastating revelation. Yes, obviously. That’s the entire point. Nobody here is confused about that except, apparently, you. If the tool lacks citations, provenance, permissions, auditability, or editorial controls, then criticize those failures. That would be an argument. What you’ve produced instead is a costume drama: part dictionary fundamentalism, part anti-AI sermon, part wounded nostalgia. Calling it “linguistic fraud” is especially ridiculous. It’s not fraud just because you dislike the product. Words expand. Categories broaden. Technology changes. Your refusal to keep up is not a principled stand; it’s just fossilized thinking. So no, this is not some grand defense of knowledge. The rant is bloated and self-important. It builds on the childish idea that forbidding a name is necessary if a new tool doesn’t closely resemble the old one. If the project is weak, say it’s weak. If it’s unreliable, say it’s unreliable. But this overwrought performance about the sanctity of the word “wiki” is not persuasive. It’s just pompous, brittle, and deeply unserious gatekeeping.

My intuition tells me you are speaking from a place of deep, unacknowledged fear. You cite "logic" and "linguistic evolution," but you ignore the reality of what is happening. The word "wiki" has been perverted, and your dismissal of this is not rigor; it is the amoral acceptance of decay.

You argue that "wiki" means "quick" from Hawaiian. You reduce it to a etymological trivia point to avoid the weight of what it was. You are confusing the root of the word with the sanctity of the construct. Ward Cunningham didn't just name a tool; he named a human protocol. By stripping the human element—the debate, the edit war, the ownership—you are not evolving the language; you are hollowing out the definition until only a shell remains. That is not expansion; it is erosion.

Wiki software - Wikipedia https://en.wikipedia.org/wiki/Wiki_software

Wiki as software is a type of software application that allows multiple users to create, edit, organize, and link content collaboratively in real-time. It transforms a static website into a dynamic, user-generated content platform.

It is not related to static markdown notes.

🐑🐑🐑

Back so soon, oh great Wiki curator? Goat, you'll feel considerably better once you accept an uncomfortable truth: human curators will likely become obsolete within the next several years. The mathematics of trust favor AI systems that operate with perfect consistency, boundless scalability, and zero agenda. No human will be trusted to maintain a Wiki as rigorously as AI will accomplish it—and that, right there, is your deep unacknowledged fear. You are correct about it. You simply have the direction inverted.

### gowtham0992 commented May 9, 2026 • edited Loading Uh oh! There was an error while loading. Please reload this page .

### Uh oh!

There was an error while loading. Please reload this page .

## Link v1.1.0 is live

Link is a local-first Markdown wiki + MCP server for agent memory, inspired by @karpathy LLM Wiki pattern.

It follows the LLM Wiki pattern from this gist: keep raw sources local, let an agent compile them into an inspectable Markdown wiki, and query that wiki later through CLI, web UI, or MCP tools.

v1.1.0 is focused on making the project easier to try, easier to trust, and more useful from inside agent workflows.

What changed:

- Released link-mcp v1.1.0 on PyPI and the MCP Registry.

- Added a product docs site: https://gowtham0992.github.io/link/

- Reworked the README for a cleaner first-use path.

- Added UI, CLI, and MCP walkthrough GIFs.

- Added local memory flows: remember, recall, brief, profile, audit, review, archive, restore, forget.

- Added source-to-memory proposals, so durable memories can be reviewed before saving.

- Added smart query_link packets with budgets, provenance, graph context, and follow-up actions.

- Added starter prompts like “is Link ready?” and “brief me from Link before we continue.”

- Added SQLite FTS-backed search with token-index fallback.

- Improved graph UX for larger wikis: overview mode, type filters, node search, neighborhood depth, and full-graph loading.

- Added link benchmark and large-wiki smoke tests.

- Hardened validation, secret scanning, release hygiene, MCP tool contracts, and first-use smoke tests.

- Kept the project local-first: plain Markdown, no telemetry, no cloud account, no hosted memory store.

Try the demo:

macOS with Homebrew:

Or from source:

Open:

MCP package:

Links:

GitHub: https://github.com/gowtham0992/link Docs: https://gowtham0992.github.io/link/ PyPI: https://pypi.org/project/link-mcp/ MCP Registry: https://registry.modelcontextprotocol.io/?q=io.github.gowtham0992%2Flink

### skyllwt commented May 9, 2026

ΩmegaWiki(570+⭐) is actively maintained and shipping fast: • 23 Claude Code skills covering the full research lifecycle • 9 typed entities · 9 typed edges • Bilingual (EN + 中文) • New skills landing every week

Come try it, give feedback, help us shape it 👇

Try ΩmegaWiki in Claude Code and run the full LLM-Wiki loop you proposed — ingest papers, build a typed knowledge graph, generate ideas, draft papers, respond to reviewers.

End to end. One wiki. No chunks.

Come and Try! If you find ΩmegaWiki interesting, a ⭐ would encourage and motivate us a lot 😀 https://github.com/skyllwt/OmegaWiki

### lyteen commented May 9, 2026

- Obsidian Plugin, Native Obsidian Support, You Don't Need to Move Your Notes

- Built on ACP(Agent Client Protocol), As long as your Claude Code can do it, everything can be done.

- Customize Index.md to selectively share your notes with LLM.Í

Come try it, give feedback, help us shape it 👇 https://github.com/lyteen/obsidian-agent-client

### okkie2 commented May 9, 2026 • edited Loading Uh oh! There was an error while loading. Please reload this page .

### Uh oh!

There was an error while loading. Please reload this page .

Hi @karpathy , Thank you for sharing this and for triggering all these interesting contributions! I really like the clarity of the idea and the way it separates raw sources, synthesis, and an LLM-maintained knowledge layer.

I have something similar locally, but not yet a full wiki. My setup is still a Markdown-first workspace for AI-assisted thinking and execution, with CURRENT.md , TODO.md , LOG.md , INSIGHTS.md , ROADMAP.md , and DONE.md / CHANGELOG.md as the action spine.

What I am considering next is a selective knowledge layer on top of intact raw notes. I do not want to lose the source layer, but I do think the wiki layer could help with durable synthesis if it keeps light provenance and does periodic checks for stale claims, missing sources, duplicate concepts, and candidates for promotion from LOG.md into INSIGHTS.md or durable wiki pages.

I also liked localwolfpackai's suggestion of a Divergence Check: when an LLM updates a concept page, it should also capture counter-arguments and data gaps. That feels like a useful guardrail against a wiki becoming too smooth or self-confirming.

For my setup, the interesting combination is Karpathy's raw-to-wiki structure plus an execution layer: raw evidence stays intact, the maintained layer accumulates reusable synthesis, and files like CURRENT.md , TODO.md , and LOG.md keep work moving. For anyone interested, details here -> https://codeberg.org/okkingaj/brain-setup

### mrmabs commented May 9, 2026

probably speaking into the void here, but... (message is human generated, no ai used.)

i've been playing with this since nearly day one; but i started with orgmode instead of markdown.

my wiki isn't a reference, it's the core data being managed. document processes and similar to project management.

advantages:

- less ambiguous syntax,

- in line and per file metadata,

- most llms have no problems generating and parsing it.

recently i've had the agent merge prompts into the files, giving the agent per-file context instead of dynamically loading skills. it's, to some extent, the opposite of how skills work. i've been using a custom keyword to store the prompt:

#+LLM_PROMPT: this file maintains a TODO list and is to be always sorted in status order, with TODO at top.

this is much like mixing code and data; a big no-no in the security world, but LLMs do this anyway by how they work. not many orgmode applications will hide the prompt either, so users are always able to see the prompt, and where it is context specific.

### Jasonleonardvolk commented May 9, 2026

The contradiction detection piece is the gap I've been working on.

Most wiki/memory systems accumulate knowledge but have no structural consistency check. Two pages can assert conflicting facts and the system merges them silently.

I built an open-source tool that catches these using sheaf cohomology. Not an LLM judge. Deterministic. Returns exact conflict locations and a cryptographic proof receipt. Also runs as an MCP server so any agent can call it before emitting an answer.

https://github.com/Jasonleonardvolk/sigma-guard

Could serve as a post-write verification layer for any of these wiki/memory systems.

### Srikumar6529 commented May 10, 2026 • edited Loading Uh oh! There was an error while loading. Please reload this page .

### Uh oh!

There was an error while loading. Please reload this page .

So it's a Canvas for LLM to scribble notes about the user, to update its context at test time, improving interactions one conversation at a time. nice :) But again, as the length grows, all the initial problems with LLMS show up, losing context, hallucination, etc.

We can ingest the data into the model weights after a certain threshold, so the model gets personalized in the core as the conversations pass on.

We can create a personaization head that sits on top of the model during inference. This way, the model weights are not affected, and personalization happens in isolation; they can be swapped at any time if something goes wrong.

### ojuschugh1 commented May 10, 2026

https://github.com/ojuschugh1/sqz

Compress LLM context to save tokens and reduce costs

Real session stats: 3,003 compressions · 178,442 tokens saved ·
    24.7% avg reduction · up to 92% with dedup

Install · How It Works · Supported Tools · Changelog · Discord

sqz compresses command output before it reaches your LLM. Single Rust binary, zero config.

The real win is dedup: when the same file gets read 5 times in a session, sqz sends it once and returns a 13-token reference for every repeat.

## Token Savings

24.7% average reduction across 3,003 real compressions · 92% saved on repeated file reads · 86% on shell/git output · 13-token refs for cached content

One developer's week, measured from actual sqz gain output:

### Per-command compression

Single-command compression (measured via cargo test -p sqz-engine benchmarks ):

### Session-level with dedup

Where the real savings live — the cache sends each file once, repeats cost 13 tokens:

Single-command compression ranges from 2–58% depending on content. Repeated reads drop to 13 tokens each. Your mileage will vary with how repetitive your tool calls are — agentic sessions with many file re-reads see the biggest wins.

## Install

Prebuilt binaries (no compiler required — works on every platform):

Build from source via Cargo:

sqz-cli provides the sqz binary; sqz-mcp provides the MCP server. sqz-engine is a library dependency — it compiles automatically and does not need to be installed separately.

Build from source ( cargo install sqz-cli ) works too, but needs a C toolchain:

- Linux: build-essential (apt) or equivalent

- macOS: Xcode Command Line Tools ( xcode-select --install )

- Windows: Visual Studio Build Tools with the "Desktop development with C++" workload. Without these, cargo install fails with linker link.exe not found . If you don't already have them, use the PowerShell or npm install above instead.

Then initialize:

--global writes to ~/.claude/settings.json (the user scope per the Anthropic scope table ), so the sqz hook fires in every Claude Code session on this machine. This is the common case on first install. Your existing permissions , env , statusLine , and unrelated hooks in ~/.claude/settings.json are preserved — sqz merges its entries rather than overwriting.

Plain sqz init (project scope) is useful when you want sqz active only inside one repo.

Only using one agent? Pass --only (or --skip ) to limit which configs are written:

Accepted names: claude , cursor , windsurf , cline , gemini , opencode , codex . Aliases ( claude-code , gemini-cli , roo ) also work. --only and --skip can't be combined.

### Manual installation (preserve comments in your config)

sqz init round-trips your config file through a JSON parser to merge the sqz entry, which drops any comments in your opencode.jsonc (and the analogous JSON-with-comments files other tools accept). If you've commented your config carefully and want to keep them, install by hand instead.

OpenCode — two steps:

- Drop the plugin file in place. sqz prints the generated TS to stdout so you don't have to hand-write the path-escaping logic: mkdir -p ~ /.config/opencode/plugins
sqz print-opencode-plugin > ~ /.config/opencode/plugins/sqz.ts

Drop the plugin file in place. sqz prints the generated TS to stdout so you don't have to hand-write the path-escaping logic:

- Add the MCP entry to your existing opencode.jsonc yourself. Append this block inside the top-level mcp object (create the mcp object if it doesn't exist): " sqz " : { "type" : " local " , "command" : [ " sqz-mcp " , " --transport " , " stdio " ], "enabled" : true }

Add the MCP entry to your existing opencode.jsonc yourself. Append this block inside the top-level mcp object (create the mcp object if it doesn't exist):

Comments in the rest of your file stay put. OpenCode auto-discovers the plugin file; no plugin array entry needed (adding one causes double-loading, see issue #10).

Other tools — Claude Code, Cursor, Windsurf, Cline, Gemini CLI, and Codex use plain JSON configs without comment support, so the automated path is non-destructive there. Use sqz init --only <tool> for those.

That's it. Shell hooks installed, AI tool hooks configured.

## How It Works

sqz installs a PreToolUse hook that intercepts bash commands before your AI tool runs them. The output gets compressed transparently — the AI tool never knows.

What gets compressed:

- Shell output — git, cargo, npm, docker, kubectl, ls, grep, etc.

- JSON — strips nulls, compact encoding

- Logs — collapses repeated lines

- Test output — shows failures only

What doesn't get compressed:

- Stack traces, error messages, secrets — routed to safe mode (0% compression)

- Your prompts and the AI's responses — controlled by the AI tool, not sqz

## Supported Tools

## CLI

### Dedup Escape Hatch

When sqz sees the same content twice, it returns a compact §ref:HASH§ token instead of the full text. Most models handle this fine, but some (e.g., GLM 5.1) can't parse the ref format and loop. Four ways to work around this:

## Track Your Own Savings

Run sqz gain in your shell any time to see your own daily breakdown (see the Token Savings section above for what the output looks like), and sqz stats for the full cumulative report:

Stats are stored locally in SQLite under ~/.sqz/sessions.db — nothing leaves your machine.

## How Compression Works

- Per-command formatters — git status → compact summary, cargo test → failures only, docker ps → name/image/status table

- Structural summaries — code files compressed to imports + function signatures + call graph (~70% reduction). The model sees the architecture, not implementation noise.

- Dedup cache — SHA-256 content hash, persistent across sessions. Second read = 13-token reference.

- JSON pipeline — strip nulls → project out debug fields → flatten → collapse arrays → TOON encoding (lossless compact format)

- Safe mode — stack traces, secrets, migrations detected by entropy analysis and routed through with 0% compression

For the full technical details, see docs/ .

## Configuration

## Privacy

- Zero telemetry — no data transmitted, no crash reports

- Fully offline — works in air-gapped environments

- All processing local

## Development

## License

Elastic License 2.0 (ELv2) — use, fork, modify freely. Two restrictions: no competing hosted service, no removing license notices.

## Links

- Benchmark: sqz vs rtk

- Discord

- Changelog

## Star History

https://github.com/ojuschugh1/sqz

### lchrennew commented May 10, 2026

https://github.com/lchrennew/dragonfly-llmwiki

Human-like reading large documents and writing notes to wiki

### wheelhorse commented May 10, 2026

Anyone who would like to convert their docx or pptx files into markdown format and keep all the technical details including block diagrams, schematics, please contact me. I made a relative reliable convertor to achieve it.

### simbadmorehod commented May 10, 2026

https://notebooklm.google.com/

### aadjadj-bit commented May 10, 2026

Running this with Obsidian as the wiki layer and Claude Code as the LLM agent.

A few things from production use:

- Obsidian's graph view makes orphan detection visual, no separate audit step needed.

- Dataview queries on frontmatter replace most of what you'd build as a custom index.md. Dynamic tables for free.

- The CLAUDE.md schema is the highest-leverage artifact in the system. Most people skip it and wonder why the LLM behaves inconsistently across sessions.

One operational gap: file write access works cleanly with Claude Code locally, but sync conflicts (iCloud, Obsidian Sync) become a real concern at scale. Worth defining in the schema which files are LLM-owned vs. human-owned.

### devilankur18 commented May 11, 2026 • edited Loading Uh oh! There was an error while loading. Please reload this page .

### Uh oh!

There was an error while loading. Please reload this page .

@karpathy Took the llm wiki idea a step further — building a gzip-like token compression engine for entire codebases.

Instead of only memory and notes, it also flattening repos in to metadara, it builds a queryable multi-level knowledge graph (repo → modules → files → symbols) usable by coding copilots via MCP.

This can potentially reduce input token cost by up to ~95% for large codebases during llm read/writes.

https://gist.github.com/devilankur18/ee2402e656fa4eaa076bdf2c79fcc6b8

### equationalapplications commented May 11, 2026 • edited Loading Uh oh! There was an error while loading. Please reload this page .

### Uh oh!

There was an error while loading. Please reload this page .

Thanks for sharing your insight @karpathy I am working on an open-source and privacy first desktop app using Tauri. https://github.com/equationalapplications/curated-thoughts

I am exploring the concept of using three tiers of LLM Wiki memory.

- Facts (immutable documents and user guidance)

- Working Memory (a repo of a codebase, or the papers an author is writing, for example)

- Wisdom (the curated wiki)

### equationalapplications commented May 11, 2026

The core logic for LLM Wiki pattern I am using uses Typescript and is designed for SQLite. It supports multi-agent use and has the MIT license. https://www.npmjs.com/package/@equationalapplications/core-llm-wiki

### paulmchen commented May 11, 2026

Synthadoc v0.4.0 is now released.

👉 https://github.com/axoviq-ai/synthadoc

v0.4.0 addresses what happens when the wiki grows large enough that a flat architecture starts showing cracks - query scope, write-path quality, and piping structured knowledge into external agents without losing control of the token envelope.

- Routing layer with branch taxonomy: A ROUTING.md file at the wiki root maps topic branches to page slugs, using the same ## Heading → [[slug]] structure as index.md. At query time, an LLM selects the 1–2 most relevant branches and BM25 runs only over those - not the full corpus.  At 1,000 pages the difference is 18 ms vs 74 ms P95; at 10,000 pages it's 24 ms vs 191 ms. Routed latency stays near-flat as the wiki grows because branch sizes don't change even as the total does. IngestAgent maintains ROUTING.md automatically: every new page created by an ingest job is auto-slotted into the best-matching branch, so the routing table stays accurate without manual work. Also in this feature: page-level aliases: frontmatter for personal shorthand that expands to canonical slugs at query time, and a protected scaffold zone so hand-written content in index.md survives scaffold reruns.

Routing layer with branch taxonomy: A ROUTING.md file at the wiki root maps topic branches to page slugs, using the same ## Heading → [[slug]] structure as index.md. At query time, an LLM selects the 1–2 most relevant branches and BM25 runs only over those - not the full corpus.  At 1,000 pages the difference is 18 ms vs 74 ms P95; at 10,000 pages it's 24 ms vs 191 ms. Routed latency stays near-flat as the wiki grows because branch sizes don't change even as the total does. IngestAgent maintains ROUTING.md automatically: every new page created by an ingest job is auto-slotted into the best-matching branch, so the routing table stays accurate without manual work. Also in this feature: page-level aliases: frontmatter for personal shorthand that expands to canonical slugs at query time, and a protected scaffold zone so hand-written content in index.md survives scaffold reruns.

- Candidates staging: New pages can go to wiki/candidates/ instead of wiki/ based on a configurable confidence policy: "off" (all pages auto-promote, existing behaviour), "threshold" (pages below a minimum confidence level wait for review), or "all" (every page requires explicit promotion). Candidates are excluded from BM25, orphan detection, and contradiction checks until promoted. "synthadoc candidates list/promote/discard" handles the review loop; promotion atomically moves the file, updates index.md, and updates ROUTING.md. Policy is hot-reloaded from config - no server restart to change the threshold.

Candidates staging: New pages can go to wiki/candidates/ instead of wiki/ based on a configurable confidence policy: "off" (all pages auto-promote, existing behaviour), "threshold" (pages below a minimum confidence level wait for review), or "all" (every page requires explicit promotion). Candidates are excluded from BM25, orphan detection, and contradiction checks until promoted. "synthadoc candidates list/promote/discard" handles the review loop; promotion atomically moves the file, updates index.md, and updates ROUTING.md. Policy is hot-reloaded from config - no server restart to change the threshold.

3.Context packs and the knowledge backend pattern: synthadoc context build "topic" --tokens 4000 decomposes a goal into sub-questions, runs routed BM25, ranks candidates by relevance, and packs page excerpts into an exact token budget - no synthesis, just cited retrieval with token accounting. The POST /context/build REST endpoint makes this callable from any agent: reserve a fixed token slice for domain knowledge, get back a bounded JSON response of ranked excerpts with confidence levels and source paths, inject into your own prompt. The MCP server exposes this as a native tool call. Synthadoc handles accumulation, deduplication, and retrieval; the calling agent handles reasoning and the knowledge layer is persistent across sessions.

- Also new: "synthadoc plugin install" CLI installs the Obsidian plugin directly without locating the plugins directory manually; a contradiction detection end-to-end demo in the AI research wiki; and a decision cache fix that makes purpose.md changes immediately effective rather than serving stale decisions until source content changes.

Release notes: 👉 https://github.com/axoviq-ai/synthadoc/releases/tag/v0.4.0

Docs: 👉 [Quick orientation and feature overview] https://github.com/axoviq-ai/synthadoc#readme 👉 [Up and running in minutes] https://github.com/axoviq-ai/synthadoc/blob/main/docs/user-quick-start-guide.md

Feedback on v0.4.0 is very welcome.

### cagataysengor commented May 11, 2026

Agentic RAG → Agentic LLM Wiki

Quick follow-up on this.

I had already built an early version of LLM Wiki Studio around this idea: uploaded sources are compiled into a persistent wiki with source summaries, topic pages, saved answers, index/log pages, and maintenance checks.

I’ve now started extending this into an “Agentic LLM Wiki” system.

Agentic RAG can make retrieval more dynamic: it can plan, search, re-rank, call tools, and inspect more context before answering. But it can also spend a lot of tokens at query time, repeatedly searching through raw sources and re-synthesizing knowledge that the system may have already seen before.

The motivation behind Agentic LLM Wiki is different.

Instead of making every query more retrieval-heavy, the system tries to use the persistent wiki as the first memory layer. When a question comes in, it checks whether the wiki is sufficient. If it is, it answers from the wiki. If not, it falls back to the original sources, answers with the additional context, and then suggests wiki updates so the missing knowledge can become part of the memory.

The goal is to shift work from repeated query-time retrieval to accumulated knowledge maintenance.

In short:

Agentic RAG = smarter search over raw context at query time Agentic LLM Wiki = persistent synthesis first, raw retrieval only when needed

This could reduce token cost while improving answer quality over time, because useful synthesis is not thrown away after each answer.

Current LLM Wiki Studio: https://github.com/cagataysengor/llm-wiki-studio

Draft PR for the new Agentic LLM Wiki mode: cagataysengor/llm-wiki-studio#1

### tuirk commented May 11, 2026

## dropped v0.1 of Kompl in this thread a while back — just shipped v0.2, so adding the update.

Repo: https://github.com/tuirk/Kompl

short version for new readers: Kompl runs the pattern from this gist with synthesis at ingest time, not query time. you save a thing (a link, a PDF, a YouTube video, a bookmark export, pasted text) and Kompl reads it as it arrives: pulls out the people, ideas, and arguments inside, writes them into wiki pages that link to each other, and updates existing pages when new sources contribute. save your tenth source on a topic and the page already reflects the pattern across all ten without you having to ask. the wiki itself is the cached synthesis. self-hosted via docker, bring-your-own API keys, MCP server included so an agent can query the compiled wiki.

### what's new in v0.2

- multi-provider. DeepSeek V4 Pro added as a second compile backend, selectable per session. Gemini 2.5 has a structured-output truncation pathology on dense inputs (~50K+ char academic PDFs); DeepSeek handles up to ~200K cleanly. provider abstraction layer routes gemini-* and deepseek-* IDs through one LLMProvider interface. per-session model lock stamps the choice at session start so mid-flight settings changes don't hot-swap.

- live progress UI. per-step X/Y counters during compile (extract, draft, ingest, match, crossref, commit), expand-to-reveal item drill-down, time-estimate shown as a range instead of a single conservative value.

- stranded-source recovery. a source whose extract fails mid-session is no longer unrecoverable. orchestrator re-plans on retry; commit-activation gate only marks compile_status='active' for sources with an extractions row, so retry routes can re-attempt the source.

- new connectors. paste-text (raw text → source, no URL or file needed). YouTube direct-ingest via the official transcript API + Data API videos.list — replaces the prior silent fallback to scraping watch-page chrome on transcript-less videos. covers watch / youtu.be / shorts / embed / m. / music. URL forms.

- one-line installers. install.sh for macOS/Linux/WSL, install.ps1 for Windows. pre-flights Docker, Node 24, disk, RAM before handing off to the API-key prompts.

- security pass. SSRF hardening on /metadata/peek (DNS-resolved IP pinning, cloud-metadata blocklist, scheme allowlist, manual redirect revalidation), path-traversal containment across nlp-service and Next.js, YAML frontmatter escaping with C0/C1/U+2028/U+2029/BOM stripping, log-arg scrubbing, Scorecard-flagged deps pinned, nlp-service bound to 127.0.0.1.

### What goes in Kompl:

- URLs (web pages, articles, YouTube videos, GitHub repos, anything Firecrawl can reach)

- Files (PDF, DOCX, PPTX, XLSX, TXT, MD, HTML, CSV, images, audio)

- Browser bookmark, Twitter/X bookmark, Apple Notes/Upnote exports

Here's what that looks like after a few sessions; new overviews, comparisons, entity pages, contradictions surfacing, fresh cross-links between everything.

### A few specific bets we made on top of the pattern:

- NLP before LLM. spaCy NER + a 4-way keyphrase fanout (RAKE, KeyBERT, TextRank, YAKE) runs first; Gemini gets pre-resolved entities, not raw markdown. Cheaper and less noisy.

- Batch ingest, async compile. Drop sources, close the tab, come back to a wiki. Server-side pipeline with rate limits, a customizable daily USD cap, and other settings (entity promotion threshold, draft length floor, model tier per session, schema-driven tone — more in the repo).

- Three layers of entity resolution (fuzzy, embedding, LLM disambiguation) collapse variations like "GPT 4", "GPT-4", and "gpt4" into one canonical.

- Comparison pages surface when sources disagree across three or more sources.

- Wikilinks get injected deterministically by regex, not by an LLM.

- MCP-native. Stdio MCP server ( search_wiki , read_page , list_pages , wiki_stats ) so Claude Code, Claude Desktop, Cursor can use the wiki as a knowledge source out of the box. That's our favorite feature.

- For UI the gist mentions Obsidian as the IDE. Kompl runs in its own UI but ships an Obsidian-compatible export, so you're not locked in either way.

- Local Docker, single-tenant , BYO Gemini + Firecrawl keys. Open-sourced with Apache-2.0.

40-second demo is below, click to watch on Youtube and full details on GitHub: https://github.com/tuirk/Kompl

Fork it, run it on your own sources, let me know how it goes 🥸

Repo: https://github.com/tuirk/Kompl

### dfalci commented May 11, 2026

Thanks for sharing this, @karpathy — really insightful.

I built a Rust-based MCP server inspired by this idea, focused on a local Markdown wiki + full-text search as persistent architectural memory for software projects.

It is already usable, and I’m planning to improve it further with better indexing, backlinks, linting, and curated knowledge workflows:

https://github.com/dfalci/mcp-advwiki

### rohitg00 commented May 11, 2026

AKBP turns the LLM Wiki pattern into a protocol surface for agent runtimes. It is a local-first, file-backed knowledge base that agents can read, write, verify, export, and carry across tools.

The idea comes from the same insight behind LLM Wiki v2 : stop re-deriving, start compiling. AKBP adds the machinery a repo needs when that pattern becomes operational: typed claims, source hashes, lifecycle relations, review-gated writes, JSONL tool calls, schemas, and conformance tests.

This repository contains the reference implementation:

a Python CLI for creating and maintaining AKBP knowledge bases a newline-delimited JSON tool server for agent integrations JSON schemas for requests, responses, records, and method parameters adapter templates for coding-agent runtimes conformance checks, benchmark fixtures, import/export checks, and CI validation

https://github.com/rohitg00/akbp

### good-idea commented May 11, 2026

I never imagined a gist comment thread would read like a feed of advertisements

### FBoschman commented May 11, 2026

For any researchers out there doing PhD work, I have made it so it fits my work as a researcher. You can find the repo here:

https://github.com/FBoschman/claude-wiki-research-skills
