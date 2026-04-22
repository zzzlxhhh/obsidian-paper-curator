# AGENTS.md — LLM Wiki (Obsidian Vault)

> This file describes the structure, conventions, and workflows for AI agents working in this repository.
> This is an **Obsidian vault** used to build and maintain a personal knowledge base (wiki) with LLM assistance.

---

## Project Overview

This repository implements the **LLM Wiki pattern**: instead of treating documents as a passive RAG corpus, the LLM incrementally builds and maintains a persistent, interlinked wiki. Knowledge is compiled once, kept current, and compounds over time.

- **Human role**: curate sources, ask questions, direct analysis, review updates.
- **LLM role**: summarize sources, create and update wiki pages, maintain cross-references, detect contradictions, and keep the index/log current.
- **Obsidian role**: the IDE for browsing the wiki (graph view, backlinks, search, canvas).

Core concept documents:
- `README.md` / `README.en.md` — project overview and human contributor guidelines.

---

## Technology Stack

- **Platform**: [Obsidian](https://obsidian.md/) (desktop knowledge base application)
- **Format**: Markdown (`.md`) with Obsidian-flavored wikilinks (`[[Page Name]]`)
- **Configuration**: JSON files under `.obsidian/`
- **Plugins**: 
  - [Dataview](https://github.com/blacksmithgu/obsidian-dataview) — metadata queries and dynamic tables (`.obsidian/plugins/dataview/`)
  - [Marp Slides](https://github.com/samuele-cozzi/obsidian-marp-slides) — slide generation from markdown (`.obsidian/plugins/marp-slides/`)

---

## Directory Structure

```
LLMwiki/
├── .agents/
│   └── skills/                 # Modular agent capabilities. Each subdirectory is a reusable
│                                 skill containing a SKILL.md that defines a standard operating
│                                 procedure for a specific task.
│                                 Current skills: paper-injest, paper-lint, paper-query.
├── Clippings/                  # Inbox for raw web clippings, article excerpts, and quick notes
│   │                           # awaiting processing. Humans drop content here; agents process
│   │                           # and then archive to _processed/.
│   └── _processed/             # Archive of clippings that have been ingested into the wiki.
│                                 Preserved for reference, no longer part of active workflows.
├── concepts/                   # Shared knowledge nodes. Cross-cutting concept pages that
│                                 aggregate definitions, variants, and related ideas from
│                                 multiple sources. These are the "hubs" of the wiki graph.
│                                 Examples: "KV Cache", "PPO", "Reward Hacking".
├── LintLog/                    # Output directory for lint reports. Agents write detailed
│                                 diffs and findings here during health-check passes.
├── papers/                     # Topic-organized paper notes. Subdirectories are research
│                                 areas containing structured summaries of individual papers.
├── queries/                    # Archived Q&A records from user queries (read-only after
│                                 creation). User-managed; excluded from retrieval/indexing.
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
└── README.md / README.en.md    # Human-facing project overview (Chinese and English).

```

### Page type conventions

| Page type | Where it lives | Description |
|---|---|---|
| Paper notes | `papers/<topic>/` | Structured summary of a single paper: background, problem, method, experiments, and positioning vs. related work. |
| Concept pages | `concepts/` | Cross-source shared concepts that gather definitions and variants from multiple papers into a standalone entry. |
| Index pages | Root or topic root | Navigation pages that list and summarize all pages under a topic or the entire vault. |
| Log entries | `log.md` | Timeline records of operations, not knowledge content. Used for audit and traceability. |
| Raw clippings | `Clippings/` | Unprocessed raw content waiting to be summarized and linked into the wiki. |
| Query archives | `queries/` | Archived question–answer pairs. Read-only after creation; excluded from wiki retrieval and indexing to prevent contamination. |

---

## Workflows

| Skill | Trigger | Core Responsibilities | Key Outputs / Locations |
|---|---|---|---|
| **paper-injest** | Processing, digesting, or organizing papers from `Clippings/`; ingesting new sources. | Extract structured knowledge; generate paper summary pages (background, challenges, solution, experiments, positioning); auto-classify into topic subdirectories; create/update `concepts/` pages; maintain the Dataview metadata table. | `papers/<topic>/`, `concepts/`, `index.md`, `log.md` |
| **paper-query** | Asking questions about papers, concepts, or relationships in the wiki; requesting comparisons, synthesis, or analysis. | Hierarchical retrieval (semantic overview → structured knowledge → raw sources → external augmentation); synthesize cited answers; archive Q&A to `queries/` only. Never write query results back into wiki pages, `index.md`, or `log.md`. | Answer text; read-only archive in `queries/`. |
| **paper-lint** | Requesting a lint, audit, or health-check of the wiki. | Auto-repair structural issues (orphan pages, broken wikilinks, missing concept pages, missing cross-references); write detailed reports. | Report files in `LintLog/` |
