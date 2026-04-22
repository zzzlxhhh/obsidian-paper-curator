---
name: paper-injest
description: >
  Ingest academic paper clippings into an Obsidian wiki by extracting structured
  knowledge and cross-referencing shared background concepts. Trigger when the user
  asks to process, digest, organize, or ingest papers from the Clippings/ folder
  into the wiki. Generates a paper summary page (background, challenges, solution,
  experiment summary, positioning vs related work) auto-classified into topic
  subdirectories, creates/updates shared concept pages, and maintains a
  Dataview-powered metadata table tracking first author, affiliation, year, venue,
  and topics for all papers.
---

# Paper Ingest Skill

Process new paper clippings from `Clippings/` and integrate them into the wiki as
structured, interlinked markdown pages with automatic topic classification and
Dataview metadata tracking.

## Goal

Transform raw paper clippings into:
1. A **dedicated paper page** summarizing the work, filed under a primary topic
   subdirectory, with detailed positioning against related work.
2. **Shared concept pages** for reusable background knowledge, linked by multiple papers.
3. A **Dataview metadata table** (`papers/papers-index.md`) for querying and browsing
   papers by author, year, venue, and topics.
4. Updated `index.md` and `log.md` to reflect the new content.

## Ingest Workflow

Execute these steps in order for each paper.

### Step 1: Identify Pending Papers

**This step prevents re-reading already-ingested clippings.**

1. Read `log.md` and parse all entries with the prefix `## [YYYY-MM-DD] ingest |`.
   Extract the paper titles to build a list of **already processed** papers.
2. Scan the `Clippings/` directory for `.md` files.
   **Exclude `Clippings/_processed/` and any subdirectories starting with `_`**
   — these are reserved for other skills (e.g. `paper-query`) and must never be
   read during ingest.
3. Compare the directory listing against the processed list from `log.md`.
   Any `.md` file in `Clippings/` whose title does **not** appear in `log.md`
   is a **pending paper** requiring ingest.
4. Report the pending list to the user. If multiple papers are pending, ask the
   user which one(s) to process, or process them one at a time in alphabetical
   order.

### Step 2: Read the Paper in Full

**Hard constraint: you MUST read the entire paper before analyzing it.**

1. Read the selected clipping file from `Clippings/<Paper Title>.md` in its
   entirety. Use `ReadFile` with line offsets if the file is long, but do not
   skip sections. Continue reading until the tool reports **"End of file reached"**.
2. Extract metadata from YAML frontmatter if present:
   - `title`, `source` (URL), `author`, `published`, `created`, `tags`
3. If frontmatter is missing, infer `title` from the H1 heading or filename.

**Critical rule:** Do not begin analysis, summarization, or page creation until
you have consumed the **complete text** of the paper. No hallucination or
inference beyond what is present in the source text is permitted.

### Step 3: Analyze and Decompose

After confirming the full paper has been read, decompose it into these knowledge
units:

| Unit | Description | Output Target |
|------|-------------|---------------|
| **Background** | What problem domain does the paper sit in? What prior work does it build on? | Background concept page(s) |
| **Challenges** | What specific limitations, pain points, or gaps does the paper identify? | Paper page + concept page if general |
| **Solution** | The core technical contribution, architecture, or algorithm. | Paper page |
| **Positioning** | How does this paper criticize related work? What is its claimed advantage? | Paper page (list + summary table) |
| **Key Concepts** | New terminology, architectural patterns, or techniques introduced. | Shared concept page(s) |
| **Experiments** | Datasets, metrics, key results, comparisons. | Paper page (brief summary) |

**Decision rule for concept pages:**
- If a concept is **general background knowledge** that could be referenced by future
  papers, create or update a shared concept page under `concepts/`.
- If a concept is **paper-specific** (e.g., a custom module name unique to this work),
  describe it within the paper page only.
- When in doubt, prefer a shared concept page. It is cheap to create and prevents
  later duplication.

**Positioning discipline:**
- The Positioning section is a **structured summary of the paper's own Related Work
  section**, not an independent critique you invent.
- **MUST contain two parts**: (1) a **detailed list** of related work entries,
  grouped by the paper's original sub-topics; and (2) a **Summary Table** that
  synthesizes the landscape at a high level. Do not omit either part.
- Preserve the paper's original grouping and order of related work categories.
- Every critique, limitation, and differentiation claim must be directly traceable
  to something the authors wrote. Use the paper's own framing and vocabulary.
- For each related work entry, record three things from the source text:
  1. What the paper says that work does (objective description).
  2. What limitation or gap the paper identifies in that work.
  3. How the paper claims its own work addresses that limitation.

### Step 4: Determine Topic Classification

Analyze the paper's problem domain and contribution to assign **topic tags**.
A paper can have **multiple** topics, but the **first topic** determines the
file path (`papers/<primary-topic>/`).

Choose from this canonical list (or add new ones):

| Topic Slug | Description |
|------------|-------------|
| `video-generation` | Text-to-video, image-to-video, video diffusion models |
| `image-generation` | Text-to-image, image editing, image diffusion |
| `language-model` | LLM architecture, pretraining, post-training, reasoning |
| `reinforcement-learning` | RLHF, RLVR, GRPO, PPO, agentic RL, training systems |
| `vision` | Image classification, segmentation, visual understanding |
| `multimodal` | VLM, omni-modal models, cross-modal learning |
| `inference-optimization` | KV-cache, quantization, pruning, speculative decoding, sparse attention |
| `training-systems` | Distributed training, parallelism strategies, fault tolerance |
| `efficiency` | General model compression, acceleration, hardware co-design |
| `alignment` | Safety, fine-tuning, preference optimization, red-teaming |

**Multi-topic examples:**
- STA (sparse attention for video DiT): `topics: [video-generation, inference-optimization]`
- A paper on RLHF for LLM reasoning: `topics: [language-model, reinforcement-learning, alignment]`

### Step 5: Create / Update Shared Concept Pages

For each identified shared concept:

1. Check if a page already exists: `concepts/<Concept Name>.md` or search wiki.
2. **If exists**: Read it. Append or revise the content to incorporate this paper's
   perspective. Add a backlink to the new paper page.
3. **If new**: Create `concepts/<Concept Name>.md` with:
   - YAML frontmatter: `tags: [concept]`
   - A concise definition/explanation.
   - A "Referenced By" section listing papers that mention this concept.
   - Wikilinks to related concepts.

Keep concept pages **focused and atomic** — one idea per page. Prefer linking over
nesting.

### Step 6: Create the Paper Page

Create `papers/<primary-topic>/<Short Title>.md`. The `<primary-topic>` directory
is created if it does not exist.

Use the template from `references/paper-template.md` in this skill. Key sections:

- **Metadata**: YAML frontmatter MUST include:
  ```yaml
  ---
  title: "<Full Paper Title>"
  source: "<URL>"
  first_author: "<First Author Name>"
  affiliation: "<First Author Institution / Lab>"
  year: <YYYY>
  venue: "<Conference or Journal>"
  topics: ["<primary-topic>", "<secondary-topic>"]
  ingested: "<YYYY-MM-DD>"
  tags: [paper]
  ---
  ```
  Extract `first_author`, `affiliation`, `year`, and `venue` from the paper's
  author list, footnotes, and source URL. If uncertain, infer from context or mark
  with a `?` for later verification.

- **Background**: Link to shared concept pages via `[[Concept Name]]`. Do NOT repeat
  full explanations that already exist on concept pages. Summarize in 2-4 sentences
  and link out.
- **Challenges**: Bullet list of the problems the paper addresses.
- **Solution**: Detailed description of the contribution. Use sub-headings for major
  components.
- **Positioning**: Structured summary of the paper's **Related Work** section.
  This is a **mandatory** section. The goal is NOT to invent your own critique, but
  to faithfully capture **how the original authors discuss and position their work
  against prior work**. See template for format.
- **Key Concepts**: Bulleted list of `[[Concept Name]]` links introduced or heavily
  used by this paper.
- **Experiments**: Brief summary — datasets, baselines, key quantitative results,
  comparisons. 1-2 paragraphs or a small table. Full detail is not required.
- **Connections**: Optional — note relationships to other papers already in the wiki.

**Linking discipline:**
- Every background concept mentioned should be a wikilink `[[...]]` on first use.
- Do not duplicate concept-page content on the paper page.
- If a concept page does not exist yet, create it (Step 5) before finalizing the paper page.

### Step 7: Backfill External Links

**When a new paper page is created, check if any existing wiki pages reference it
as an external work.**

1. Search the wiki for occurrences of the new paper's title (or short title)
   adjacent to the marker `(external)`.
2. For each match found (typically in other papers' Positioning sections):
   - Replace the external reference with an internal wikilink `[[Short Title]]`.
   - Remove the `(external)` marker.
3. Record these backfills in `log.md` under the same ingest entry.

This ensures that as the wiki grows, related work references automatically upgrade
from external stubs to live internal links.

### Step 8: Update Dataview Index

Ensure `papers/papers-index.md` exists and contains a Dataview query that renders
a sortable table of all papers. The query should read:

```dataview
TABLE first_author, affiliation, year, venue, topics
FROM "papers"
WHERE contains(tags, "paper")
SORT year DESC, venue ASC
```

If `papers-index.md` does not exist, create it using the template in
`references/paper-template.md`. If it exists, no edits are typically needed —
Dataview dynamically updates the table as new paper pages are added.

### Step 9: Archive the Clipping

After the paper page is successfully created and all backfills are complete,
**move the original clipping file** from `Clippings/<Paper Title>.md` to
`Clippings/_processed/<Paper Title>.md`.

Create `Clippings/_processed/` if it does not exist.

This keeps the `Clippings/` inbox clean and ensures subsequent ingest runs only
see genuinely pending papers. The archived clipping remains readable by other
skills (e.g. `paper-query`) but is excluded from future ingest scans.

### Step 10: Update Root Index and Log

- **index.md**: Add the new paper page under its primary topic category with a
  one-line summary. Add any new concept pages under "Concepts".
- **log.md**: Append an entry:
  ```markdown
  ## [YYYY-MM-DD] ingest | <Paper Title>
  - Added paper page: [[<Short Title>]]
  - Topics: `[<primary>, <secondary>, ...]`
  - Added/updated concepts: [[Concept1]], [[Concept2]]
  - Backfilled links: [[Other Paper]] (if any)
  - Archived clipping: `Clippings/_processed/<Paper Title>.md`
  ```

## Quality Standards

- **No redundancy**: Background knowledge lives on concept pages, not duplicated
  across paper pages.
- **Dense linking**: Every paper page should have 5-15 outbound wikilinks to concepts
  and related papers.
- **Self-contained summaries**: A reader should understand the paper's contribution
  from the paper page alone, even if they follow no links.
- **Stable filenames**: Use clear, short, ASCII filenames. Avoid special characters.
  Example: `papers/video-generation/STA Fast Video.md`, `concepts/GRPO.md`.
- **Complete frontmatter**: Every paper page must have `first_author`, `affiliation`,
  `year`, `venue`, and `topics` for the Dataview table to work correctly.
- **Positioning is mandatory**: Every paper page must include a structured Positioning
  section analyzing related work limitations and this paper's advantages.

## Directory Conventions

```
LLMwiki/
├── Clippings/              # Pending papers (inbox). Read but never modify.
│   └── _processed/         # EXCLUDED from paper-injest. Reserved for other
│                           # skills (e.g. paper-query). Do not read or write.
├── papers/                 # Paper summary pages, grouped by primary topic
│   ├── papers-index.md     # Dataview table of all papers
│   ├── video-generation/
│   ├── language-model/
│   ├── reinforcement-learning/
│   └── ...
├── concepts/               # Shared background knowledge pages
├── index.md                # Wiki catalog
└── log.md                  # Chronological operation log + ingest history
```

Create `papers/`, `papers/<topic>/`, and `concepts/` as needed. The `_processed/`
subdirectory under `Clippings/` is intentionally excluded from all ingest steps.
