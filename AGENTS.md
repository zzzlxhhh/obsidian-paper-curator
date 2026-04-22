<!-- From: E:\LLMwiki\AGENTS.md -->
# AGENTS.md — LLM Wiki (Obsidian Vault)

> This file describes the structure, conventions, and workflows for AI agents working in this repository.
> This is an **Obsidian vault** used to build and maintain a personal knowledge base (wiki) with LLM assistance.

---

## Project Overview

This repository implements the **LLM Wiki pattern**: instead of treating documents as a passive RAG corpus, the LLM incrementally builds and maintains a persistent, interlinked wiki. Knowledge is compiled once, kept current, and compounds over time.

- **Human role**: curate sources, ask questions, direct analysis, review updates.
- **LLM role**: summarize sources, create and update wiki pages, maintain cross-references, detect contradictions, and keep the index/log current.
- **Obsidian role**: the IDE for browsing the wiki (graph view, backlinks, search, canvas).

Core concept document:
- `LLM wiki (Readme first to build this obsidian repo).md` — the original pattern description.

---

## Technology Stack

- **Platform**: [Obsidian](https://obsidian.md/) (desktop knowledge base application)
- **Format**: Markdown (`.md`) with Obsidian-flavored wikilinks (`[[Page Name]]`)
- **Configuration**: JSON files under `.obsidian/`

---

## Directory Structure

```
LLMwiki/
├── .agents/
│   └── skills/                 # Modular agent capabilities. Each subdirectory is a reusable
│                                 skill (e.g. paper-ingest) containing a SKILL.md that defines
│                                 a standard operating procedure for a specific task.
├── Clippings/                  # Inbox for raw web clipplings, article excerpts, and quick notes
│   │                           # awaiting processing. Humans drop content here; agents process
│   │                           # and then archive to _processed/.
│   └── _processed/             # Archive of clippings that have been ingested into the wiki.
│                                 Preserved for reference, no longer part of active workflows.
├── concepts/                   # Shared knowledge nodes. Cross-cutting concept pages that
│                                 aggregate definitions, variants, and related ideas from
│                                 multiple sources. These are the "hubs" of the wiki graph.
│                                 Examples: "KV Cache", "PPO", "Reward Hacking".
├── papers/                     # Topic-organized paper notes. Each subdirectory is a research
│   │                           # area containing structured summaries of individual papers.
│   ├── LLM Inference/          # Papers on LLM inference optimization.
│   └── Reinforement Learning/  # Papers on reinforcement learning.
├── raw/                        # Cold storage for immutable source files (PDFs, images,
│                                 datasets, original article exports). Agents READ ONLY — never
│                                 modify, delete, or overwrite files in this directory.
├── AGENTS.md                   # This file: agent guidelines and conventions.
├── index.md                    # Content-oriented catalog of all wiki pages. Updated after
│                                 every ingest. Lists pages with wikilinks, one-line summaries,
│                                 and metadata (category, date, source count).
├── log.md                      # Chronological, append-only audit log of all operations
│                                 (ingests, queries, lint passes). Uses consistent prefixes
│                                 for quick scanning.

```

### Page type conventions

| Page type | Where it lives | Description |
|---|---|---|
| Paper notes | `papers/<topic>/` | Structured summary of a single paper: background, problem, method, experiments, and positioning vs. related work. |
| Concept pages | `concepts/` | Cross-source shared concepts that gather definitions and variants from multiple papers into a standalone entry. |
| Index pages | Root or topic root | Navigation pages that list and summarize all pages under a topic or the entire vault. |
| Log entries | `log.md` | Timeline records of operations, not knowledge content. Used for audit and traceability. |
| Raw clippings | `Clippings/` | Unprocessed raw content waiting to be summarized and linked into the wiki. |

---

## Workflows

### 1. Ingest

When a new source arrives:

1. Read the source (from `raw/` or as user-provided text).
2. Discuss key takeaways with the user.
3. Write a summary page in the wiki (under `papers/<topic>/` or `Clippings/`).
4. Update `index.md` with the new page and any affected categories.
5. Update or create relevant `concepts/` pages and establish cross-references.
6. Append an entry to `log.md`.

A single source may touch 10–15 wiki pages.

### 2. Query

When the user asks a question:

1. Read `index.md` first to locate relevant pages.
2. Read those pages and synthesize an answer with citations.
3. If the answer is valuable (comparison, analysis, new connection), file it back into the wiki as a new page and update `index.md`.

### 3. Lint

Health-check the wiki on request:

- Look for contradictions between pages.
- Identify stale claims superseded by newer sources.
- Find orphan pages with no inbound links.
- Spot important concepts that lack their own `concepts/` page.
- Flag missing cross-references.
