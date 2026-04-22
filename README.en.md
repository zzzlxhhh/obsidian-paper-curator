# LLM Wiki — Paper Reading & Personal Knowledge Base

> A personal wiki powered by **Kimi CLI + Obsidian**. Let the LLM do the tedious work of organizing and linking — you just read and think.

---

## What This Is

Ever felt this way about reading papers?

- You bookmark 100 papers. Your bookmarks folder becomes their graveyard. You never open them again.
- You take notes in Obsidian, but never organize them. The graph view is a mess.
- You want bidirectional links and concept connections, but the sheer effort of maintenance drains all your energy.
- Your so-called "personal knowledge base" becomes a **performative art piece** — the graph looks cool, but you never actually use it.

The real pain of tools like Obsidian isn't capture. It's **curation**. Humans are terrible at the boring work of cross-referencing, contradiction detection, and concept classification. So the idea is simple: **LLMs don't get tired, bored, or forgetful. Let them do it.**

This project is an **LLM Wiki** built on Kimi CLI + Obsidian:

- Clip a paper or blog post with Obsidian Web Clipper.
- Feed it to Kimi CLI. It reads, summarizes, extracts concepts, and builds cross-references automatically.
- You browse the results in Obsidian, ask questions, and think.

Knowledge stops being isolated islands scattered across bookmarks, and becomes a living web woven by the LLM.

---

## Why Not Traditional RAG?

Traditional RAG re-discovers knowledge from scratch on every query. The LLM retrieves fragments, pieces them together, and the answer vanishes into chat history. Nothing accumulates.

This project follows the **knowledge compounding** approach: the LLM writes each new source into the wiki, updates related concept pages, and strengthens connections. When you query, it reads already-curated pages — not raw documents.

**The wiki is a persistent, self-growing artifact.**

---

## The Three Skills: The Core of the System

The entire workflow is driven by three Agent Skills. They are not independent tools — they form a closed loop:

```
        New Paper / Article
                ↓
    ┌───────────────────┐
    │   paper-injest    │  Ingest: read clipping → structured note → update concepts
    └─────────┬─────────┘
                ↓
    ┌───────────────────┐
    │   paper-query     │  Query: answer complex questions from the curated wiki
    └─────────┬─────────┘
                ↓
    ┌───────────────────┐
    │   paper-lint      │  Maintain: check link health, fix structural issues
    └─────────┬─────────┘
                ↓
        Back to injest
```

### paper-injest: Automated Ingestion & Structuring

**What you do**: Drop an Obsidian Web Clipper `.md` file into `Clippings/`.

**What the LLM does**:
- **Duplicate prevention**: Reads `log.md` ingest history, compares against the `Clippings/` directory, and only processes genuinely new files. Archives processed clippings to `Clippings/_processed/`.
- **Full-text constraint**: Must read the entire paper before analysis begins. No skipping sections, no hallucination.
- **Knowledge unit decomposition**: Breaks the paper into Background / Challenges / Solution / Positioning / Key Concepts / Experiments, routed to the appropriate output targets.
- **Positioning discipline** (core feature): Instead of letting the LLM invent its own critique, it **faithfully captures the paper's own Related Work section**
  - Must contain two parts: a detailed list grouped by the paper's original categories + a high-level Summary Table
  - For each related work entry, records three things: objective description, limitation identified by this paper, and how this paper claims to address it
- **Automatic topic classification**: Assigns multi-label tags from 10 canonical topics (e.g., `video-generation`, `inference-optimization`). The primary topic determines the file path `papers/<topic>/`.
- **Concept page decision rules**: General background knowledge (e.g., KV Cache) → create/update shared `concepts/` pages; paper-specific proper nouns (e.g., a custom module name) → described only within the paper page.
- **Auto-backfill**: After creating a new paper page, scans the entire wiki for `(external)` references to this paper and upgrades them to internal links `[[...]]`.
- **Dataview index maintenance**: Maintains `papers/papers-index.md` with an auto-updating sortable table by author, year, venue, and topics.
- **Linking discipline**: Every background concept on first mention must be a wikilink `[[...]]`; never duplicate content that already lives on a concept page.

**Core value**: One ingest can trigger creation or updates across 10–15 wiki pages. You never manually create concept pages, links, or indexes.

---

### paper-query: Layered Retrieval & Intelligent Querying

**What you do**: Ask anything about ingested papers or concepts, from simple "What RLHF papers do we have?" to complex "What are the core differences between GRPO and PPO?"

**What the LLM does**:
- **Four-layer retrieval architecture** (core feature), progressively deepening only when necessary:
  - **L1 Semantic Overview**: Reads `index.md` + Grep keywords + scans directories to build a knowledge map. Answers navigation-style questions immediately.
  - **L2 Structured Knowledge**: Reads candidate `papers/` and `concepts/` pages in full, with transitive expansion (follows relevant wikilinks). Answers concept definitions and paper summaries.
  - **L3 Raw Evidence**: Dives into `Clippings/` original sources for exact numbers, direct quotes, and table results. Only activated when summary pages lack granularity.
  - **L4 External Augmentation**: When wiki coverage is insufficient, supplements with LLM parametric knowledge or Web search; web sources must be labeled `[External: <URL>]`.
- **Citation discipline**: Every factual claim must be traceable to a source via `[[Page Name]]`; contradictions must be surfaced explicitly.
- **Query record persistence**: Every query is automatically archived to `queries/<topic>/<YYYY-MM-DD>-<Short Title>.md`
  - The H1 heading is a **refined restatement** of the user's question, not a verbatim copy
  - Records which layers were used, all sources consulted, and the full synthesized answer
- **Synthesis沉淀**: If a query yields cross-paper comparisons, novel connections, or contradiction clarifications, automatically evaluates whether to write a standalone synthesis page back into the wiki.

**Core value**: Querying isn't a one-off chat. Good analyses are persisted as new wiki pages and query archives, becoming the foundation for future queries. Knowledge compounds.

---

### paper-lint: Structural Health Check & Auto-Repair

**What you do**: Say "lint the wiki".

**What the LLM does**:
- **Python script scan**: Runs `lint_scan.py` to generate a full link graph JSON, counting orphan pages, broken links, and high-frequency missing concepts.
- **Orphan page repair**: Not blindly forcing backlinks, but categorically — paper pages get added to `index.md` and backlinked from related concept pages; concept pages get added to `index.md` and cross-linked with related concepts; empty drafts/duplicates are flagged for human review instead.
- **Broken link repair**: Target exists under different name → correct wikilink; missing concept → create target page; paper not yet ingested → downgrade to `Title (external)`; unknown target → remove and record.
- **High-frequency missing concepts**: Only creates `concepts/<Term>.md` for terms linked ≥3 times that are clearly reusable background knowledge; `count == 2` only if obviously general.
- **Missing cross-references**: Scans paper pages for plain-text mentions of existing concepts and converts them to `[[Concept]]`; never creates speculative links to non-existent pages.
- **Complete diff report**: Every modification generates a timestamped report at `LintLog/YYYY-MM-DD-HHMMSS-lint-report.md` with reasons, context, and `+/-` diffs.
- **Idempotency guarantee**: Running lint twice on an unchanged wiki should find zero new issues.

**Core value**: The larger the wiki, the more likely it is to fall apart. Lint ensures every page is reachable via links, every concept has a home, and every link is valid — keeping the graph healthy over time.

---

## Full Workflow

```
Paper / Article (HTML / PDF)
    ↓
Obsidian Web Clipper → Clippings/
    ↓
paper-injest: auto-generates structured notes + concept pages + cross-references + Dataview index
    ↓
Browse the graph in Obsidian, ask follow-up questions
    ↓
paper-query: answers complex questions from the wiki, auto-archives to queries/, persists new analysis
    ↓
(Periodically) paper-lint: scans link health, auto-fixes structural issues, outputs LintLog report
    ↓
Back to injest, loop forever
```

Sources aren't limited to papers. Any high-quality technical content works: arXiv HTML, blog posts, documentation, great forum threads.

---

## Quick Directory Overview

```
LLMwiki/
├── .agents/skills/         # Agent skill definitions
│   ├── paper-injest/       # Paper ingestion skill
│   │   └── references/
│   │       └── paper-template.md
│   ├── paper-query/        # Intelligent querying skill
│   └── paper-lint/         # Structural maintenance skill
│       └── scripts/
│           └── lint_scan.py
├── Clippings/              # Inbox for web clippings (pending processing)
│   └── _processed/         # Archive of processed clippings (read-only)
├── concepts/               # Cross-paper concept pages (e.g., KV Cache, PPO)
├── papers/                 # Topic-organized paper notes
│   ├── papers-index.md     # Dataview metadata table
│   ├── LLM Inference/
│   └── Reinforcement Learning/
├── queries/                # Query archives (organized by topic, read-only after creation)
│   ├── reinforcement-learning/
│   └── ...
├── LintLog/                # Lint report archive
├── raw/                    # Original PDFs / images (read-only, immutable)
├── index.md                # Vault-wide index and catalog
├── log.md                  # Audit log (chronological, append-only)
└── AGENTS.md               # Agent conventions and workflows
```

---

## Core Principles

- **Humans read the wiki; the LLM writes it.** All summaries, links, and organization are done by the LLM.
- **raw/ is sacred.** Original sources are read-only and never modified or deleted.
- **One ingest, many updates.** A single paper may trigger creation or updates across 10–15 wiki pages.
- **Query results get filed back.** Good comparisons, analyses, and new discoveries shouldn't disappear into chat history.
- **Structure health is automated.** Lint runs periodically so the wiki doesn't decay over time.
- **Queries are archived.** Every question and its answer is automatically saved to `queries/`, forming a traceable Q&A knowledge base.
