---
name: paper-query
description: >
  Hierarchically answer questions by querying the Obsidian wiki knowledge base.
  Trigger when the user asks a question about papers, concepts, or relationships
  stored in the wiki; requests a comparison between papers or methods; asks for a
  synthesis across multiple pages; or seeks analysis, connections, or summaries of
  ingested knowledge. Uses a tiered retrieval strategy: semantic overview first,
  then structured knowledge, then raw sources, then external augmentation as needed.
---

# Paper Query Skill

Answer user questions through a **layered, adaptive retrieval pipeline**. Start with
high-level wiki structure, progressively deepen into raw sources only when the
question demands specificity, and optionally augment with external knowledge when
wiki coverage is incomplete.

## Goal

Transform a user question into:
1. A **targeted, cited answer** grounded in the most appropriate depth of evidence.
2. A **persisted query record** under `queries/<topic>/` that preserves the refined
   question and full answer for future reference.
3. Optionally, a **new wiki page** capturing the synthesis if the answer reveals
   comparisons, novel connections, or cross-cutting analysis worth preserving.

---

## Retrieval Layers

```
Layer 1  Semantic Overview    ──►  index.md, directory structure, page titles
         (always run)               └─► Fast landscape mapping

Layer 2  Structured Knowledge ──►  papers/<topic>/*.md, concepts/*.md
         (selective)                  └─► Deep understanding of processed content

Layer 3  Raw Evidence         ──►  Clippings/*.md, Clippings/_processed/*.md
         (conditional)                └─► Exact quotes, numbers, citations

Layer 4  External Augmentation ──►  LLM parametric knowledge, web search
         (fallback)                   └─► Fill gaps, verify recency, broaden context
```

**Constraint:** Do not skip Layer 1. Every query begins there. All deeper layers are
invoked **only if** the preceding layer is insufficient.

---

## Query Workflow

### Phase 0: Classify the Question (Implicit)

Before opening any file, form a quick mental model of what the question likely needs:

| Question archetype | Likely required layers | Example |
|---|---|---|
| **Navigation / inventory** | L1 only | "What papers do we have on RLHF?" |
| **Concept definition** | L1 → L2 | "What is GRPO and how does it work?" |
| **Paper summary** | L1 → L2 | "Summarize the key idea of [[Paper X]]." |
| **Fact / number / quote** | L1 → L2 → L3 | "What exact F1 score did they report on GLUE?" |
| **Comparison / trend** | L1 → L2 → (L3) → L4 | "How does X compare to Y? Is there newer work?" |
| **Contradiction / gap** | L1 → L2 → L3 → L4 | "Why do these two papers disagree on Z?" |

This is a planning heuristic, not a rigid rule. Re-evaluate after each layer.

---

### Phase 1: Semantic Overview (Layer 1) — ALWAYS

**Goal:** Build a mental map of where relevant knowledge lives without reading full pages.

1. **Read `index.md`** in full.
2. **Grep for keywords** across the vault (`papers/`, `concepts/`, `Clippings/`)
   to discover pages whose titles or summaries match the query.
3. **Scan directory listings** (`papers/*`, `concepts/*`, `Clippings/*.md`) for
   relevant filenames.
4. **Compile a candidate list** with one-line relevance notes:
   - Relevant topic directories
   - Relevant concept pages
   - Relevant paper pages
   - Relevant clipping filenames

**Stop criterion for simple navigation questions:**
If the user only asked "what do we have on X?" or "list papers about Y", answer
immediately from the candidate list with wikilinks. No further layers needed.

---

### Phase 2: Structured Knowledge (Layer 2) — USUALLY

**Goal:** Understand the processed, summarized content of the wiki.

1. **Read every candidate page** identified in Phase 1 **in full**.
   - Start with concept pages (they provide shared definitions).
   - Then read paper pages (they provide specific contributions and positioning).
2. **Transitive expansion:** If a read page contains `[[...]]` wikilinks that look
   highly relevant, read those pages too.
3. **Build an internal evidence board:** For each relevant page, note:
   - Key claims
   - Methods / architectures
   - Experimental highlights (high-level)
   - Positioning against other work
   - Open questions or contradictions mentioned

**Sufficiency check — ask yourself:**
- Does the user’s question ask for a specific number, verbatim quote, or fine-grained
  experimental detail that is NOT present in the paper/concept summary pages?
- Does the answer feel like a high-level synthesis that is already well-supported?

| If sufficient | Action |
|---|---|
| Yes — question is conceptual, comparative, or summary-level | Jump to **Phase 5** (Synthesize). |
| No — needs exact evidence, quotes, or numbers | Proceed to **Phase 3** (Raw Evidence). |

---

### Phase 3: Raw Evidence (Layer 3) — CONDITIONAL

**Goal:** Retrieve precise facts, direct quotes, tables of results, or citations
from the original clipping text.

1. **Select target clippings** from the candidate list (Phase 1) based on which
   paper pages (Phase 2) seemed most relevant but lacked the needed granularity.
2. **Read the clipping(s)** in full or use targeted search (`Grep`) within the
   clipping for specific terms (e.g., the metric name, dataset name, table caption).
3. **Extract verbatim evidence** with attribution to the clipping filename.

**Citation discipline for raw evidence:**
- When citing a fact from a clipping, use both the clipping and the derived page:
  `[[Paper Page]] (source: Clippings/_processed/<Name>.md)`.
- Prefer clipping evidence only when the structured page omits the detail.

**Sufficiency check:**
- Did the clipping contain the needed fact?
- Is the wiki itself missing coverage of a relevant paper or concept entirely?

| If sufficient | Action |
|---|---|
| Yes — raw evidence fills the gap | Jump to **Phase 5** (Synthesize). |
| No — the topic is absent, outdated, or too new in the wiki | Proceed to **Phase 4** (External Augmentation). |

---

### Phase 4: External Augmentation (Layer 4) — FALLBACK

**Goal:** Compensate for missing, stale, or incomplete wiki coverage.

**When to activate:**
- The wiki contains no relevant pages after Phase 1.
- The relevant pages are too old and the user asks about "latest" or "recent" work.
- The question is about a paper that exists in `Clippings/` but has not yet been
  ingested into `papers/` (rare — prefer ingesting first, but acceptable for quick answers).
- A contradiction in the wiki cannot be resolved internally.

**Allowed augmentation sources:**
1. **LLM parametric knowledge** — for well-established background, standard definitions,
   or widely known results. Blend it naturally; no special tag required.
2. **Web search** (`SearchWeb`, `FetchURL`) — for very recent papers, verification of
   numbers, or finding authoritative sources outside the vault.

**Transparency requirement:**
Web-sourced claims must be explicitly labeled with `[External: <URL>]`. LLM
parametric knowledge does **not** need a special tag; blend it naturally into the
answer but prefer wiki-grounded evidence when available.

If external augmentation reveals a significant gap in the wiki, **note it** in the
answer and optionally suggest that the user ingest the missing source.

---

### Phase 5: Synthesize the Answer

Compose a response that directly addresses the user's question.

**Citation discipline:**
- Every factual claim, comparison, or quoted insight must be attributed to its source
  using Obsidian wikilinks: `[[Page Name]]`.
- If the source is a clipping rather than a processed page, cite it as
  `Clippings/<Name>.md` or `Clippings/_processed/<Name>.md`.
- If multiple pages support a single point, cite all of them.
- If the wiki contains conflicting information, present both sides and note the
  contradiction explicitly.

**Answer structure (adapt to the question):**
- **Direct answer**: Start with a concise 1–3 sentence summary.
- **Reasoning / evidence**: Expand with evidence, grouped by theme or paper.
  - Use headings or bullet points to separate layers of evidence if helpful.
- **Sources** section listing all pages and clippings consulted.

---

### Phase 6: Persist the Query Record

Every query must be archived as a read-only record under `queries/`.

1. **Determine the topic folder:**
   - Look at the primary topic of the consulted papers/concepts.
   - Use the same canonical topic slugs as `paper-injest`:
     `video-generation`, `image-generation`, `language-model`,
     `reinforcement-learning`, `vision`, `multimodal`, `inference-optimization`,
     `training-systems`, `efficiency`, `alignment`.
   - If the query spans multiple topics, pick the **dominant** one or use `general/`.
   - Create `queries/<topic>/` if it does not exist.

2. **Write the query file:**
   - Filename: `<YYYY-MM-DD>-<Short Descriptive Title>.md`
   - Content structure:
     ```markdown
     ---
     date: YYYY-MM-DD
     topics: ["<primary-topic>", "<secondary>"]
     layers: ["L1", "L2", ...]
     sources:
       - "[[Page1]]"
       - "[[Page2]]"
       - "Clippings/_processed/<Name>.md"
     ---

     # <Refined Question — restated with precise language>

     <Full synthesized answer, with citations and any external annotations>

     ## Sources

     - [[Page1]]
     - [[Page2]]
     - ...
     ```

3. **Refine the question:**
   - The H1 heading must **not** be a verbatim copy of the user’s casual prompt.
   - Rephrase it into a precise, self-contained question that captures intent,
     scope, and any implicit assumptions. Example:
     - User: "what about grpo vs ppo?"
     - Refined: "What are the key algorithmic differences between GRPO and PPO in
       reinforcement learning for large language models, and what advantages does
       GRPO claim over PPO?"

---

### Phase 7: Decide Whether to Create Synthesis

After archiving the query record, evaluate whether the answer also represents
**durable wiki value** deserving a standalone concept or synthesis page:

| Criterion | Action |
|---|---|
| Simple factual lookup (answer exists on one page) | Do **not** create a new page. |
| Comparison across 2+ papers or concepts | **Create** a synthesis page. |
| Novel connection not explicitly stated in any single page | **Create** a synthesis page. |
| Cross-cutting analysis that could be referenced later | **Create** a synthesis page. |
| Clarification of a contradiction or gap | **Create** a synthesis page (or update an existing concept page). |
| Answer relied heavily on external augmentation due to missing wiki coverage | Suggest ingestion; do **not** persist external-only synthesis unless the synthesis itself is novel. |

**Ask the user** if uncertain: "This analysis compares X and Y — should I save it as a
new wiki page?"

---

### Phase 8: Create the Synthesis Page (if applicable)

If the answer merits persistence:

1. **Choose a location and title:**
   - Cross-paper comparison or method analysis → `concepts/<Descriptive Title>.md`
   - Topic-specific synthesis → `papers/<topic>/<Descriptive Title>.md`
   - General wiki-level analysis → `<Descriptive Title>.md` in the vault root.

2. **Write the page:**
   - YAML frontmatter: `tags: [synthesis]` (plus any relevant topic tags).
   - A clear H1 title.
   - Body that captures the analysis, comparison, or connection.
   - Heavy use of wikilinks `[[...]]` to the source pages.
   - A "Sources" section listing all consulted pages.

3. **Update `index.md`:**
   - Add the new page under the appropriate category with a one-line summary.

4. **Update `log.md`:**
   - Append an entry:
     ```markdown
     ## [YYYY-MM-DD] query | <Question summary>
     - Layers used: L1, L2, (L3), (L4)
     - Query record: queries/<topic>/<YYYY-MM-DD>-<Short Title>.md
     - Consulted: [[Page1]], [[Page2]], ...
     - Created synthesis: [[<Descriptive Title>]] (if applicable)
     ```

---

### Phase 9: Deliver the Answer

Present the synthesized answer to the user. Mention the archived query record
(e.g., "Saved to `queries/reinforcement-learning/2026-04-22-grpo-vs-ppo.md`") so
they know it is preserved for future reference.

If a new synthesis page was created, mention it and provide the wikilink so the
user can navigate to it in Obsidian.

---

## Quality Standards

- **Grounded**: Every claim traceable to a source via `[[...]]` or labeled as external.
- **Layer-aware**: Do not read full clippings for questions answerable from summary
  pages. Do not hallucinate details when raw evidence is needed — go fetch it.
- **Complete**: Read all relevant pages at each activated layer before answering;
  do not stop at the first match.
- **Concise**: Prefer synthesis over quoting large blocks of text.
- **Linked**: The answer itself should be dense with wikilinks so the user can explore
  deeper in Obsidian.
- **Persistent**: High-value analyses (comparisons, new connections) are filed back into
  the wiki so the knowledge compounds.
- **Transparent**: Web-sourced external augmentation is flagged with `[External: <URL>]`. Contradictions are always surfaced.

---

## Directory Conventions

```
LLMwiki/
├── index.md                # Layer 1 entry point: read first
├── papers/<topic>/         # Layer 2: processed paper summaries
├── concepts/               # Layer 2: shared concept + synthesis pages
├── queries/<topic>/        # Archived question–answer pairs (read-only after creation)
├── Clippings/              # Layer 3: raw, unprocessed sources (read-only)
├── Clippings/_processed/   # Layer 3: archived raw sources (read-only)
└── log.md                  # Query audit trail
```

Treat `Clippings/` and `Clippings/_processed/` as **read-only**. Never modify or delete
clipping files during a query.
