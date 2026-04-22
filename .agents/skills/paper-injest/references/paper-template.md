# Paper Page Template

Use this template when creating a new paper page in `papers/<primary-topic>/`.

---

## Paper Page (`papers/<primary-topic>/<Short Title>.md`)

```markdown
---
title: "<Full Paper Title>"
source: "<URL or arXiv ID>"
first_author: "<First Author Name>"
affiliation: "<First Author Institution / Lab>"
year: <YYYY>
venue: "<Conference or Journal Name>"
topics: ["<primary-topic>", "<secondary-topic>"]
ingested: "<YYYY-MM-DD>"
tags: [paper]
---

# <Short Title>

> One-line elevator pitch summarizing the core contribution.

## Background

<2-4 sentences situating the paper in its problem domain.>
<Link to shared concept pages for background knowledge:> This work builds on [[Concept A]] and [[Concept B]] to address...

## Challenges

- <Challenge 1: what specific pain point or gap does the paper identify?>
- <Challenge 2>
- <Challenge 3>

## Solution

### <Component / Sub-contribution 1>
<Description. Use sub-headings for distinct technical contributions.>

### <Component / Sub-contribution 2>
<Description.>

## Positioning

**Goal: faithfully reconstruct how the original paper discusses and positions itself
against prior work in its Related Work section.**

Do NOT invent critiques that are not present in the source text. Use the paper's
own framing, vocabulary, and comparative arguments. Organize bullets in the same
order and grouping that the paper uses (e.g., by sub-topic: algorithms, systems,
applications).

### <Sub-topic 1> (e.g. RL Algorithms for LLM Alignment)

- **[[Related Paper in Wiki]]** — <What the original paper says this work does>.
  - *Original paper's critique*: <How the original authors describe its limitation or gap>.
  - *Original paper's differentiation*: <How the original authors claim their work improves upon it>.

- **Prior Method B (external)** — <What the original paper says this work does>.
  - *Original paper's critique*: <How the original authors describe its limitation or gap>.
  - *Original paper's differentiation*: <How the original authors claim their work improves upon it>.
  - *(external — not yet in wiki; consider ingesting if cited by ≥2 papers)*

- **Baseline from Literature (external)** — <...>
  - *Original paper's critique*: <...>.
  - *Original paper's differentiation*: <...>.

### <Sub-topic 2> (e.g. Asynchronous RL Training Systems)

- **[[Related System in Wiki]]** — <...>.
  - *Original paper's critique*: <...>.
  - *Original paper's differentiation*: <...>.

- **Earlier System (external)** — <...>.
  - *Original paper's critique*: <...>.
  - *Original paper's differentiation*: <...>.

### Summary Table

After the detailed list, provide a high-level comparison table that summarizes
the landscape from the original paper's perspective.

| Method / System | Core Approach | Key Limitation (per this paper) | This Paper's Advantage |
|-----------------|--------------|--------------------------------|------------------------|
| [[Related Paper]] | <approach> | <limitation> | <advantage> |
| Method B (external) | <approach> | <limitation> | <advantage> |
| **This Paper** | **<approach>** | **—** | **—** |

## Key Concepts

- [[<Concept 1>]] — <one-line description of how this paper uses it>
- [[<Concept 2>]] — <...>
- [[<Concept 3>]] — <...>

## Experiments

<1-2 paragraphs or a small table summarizing datasets, baselines, and key results.>
<Focus on the "so what" — what do the results demonstrate about the proposed solution?>

## Connections

- <Relationship to other papers in the wiki, e.g.:
  - "Extends [[Prior Paper]] by adding X."
  - "Compared to [[Baseline Framework]], achieves Y speedup."
  - "Shares the [[Shared Concept]] approach with [[Related Paper]].">
```

### Positioning Section Rules

1. **Two-part structure (MANDATORY)**: The Positioning section MUST contain:
   - **Part A — Detailed List**: One or more sub-topic groupings, each with
     bullet entries for every related work discussed by the paper.
   - **Part B — Summary Table**: A single comparison table at the end that
     synthesizes all related works plus "This Paper" at a high level.
   Do not omit either part.
2. **Faithful to source**: Every critique and differentiation claim must be
   traceable to the original paper's Related Work section. Do not hallucinate
   comparisons the authors did not make.
3. **Preserve the paper's own structure**: If the Related Work is organized into
   subsections (e.g., "RL Algorithms", "Training Systems", "Agentic RL"), mirror
   that structure with sub-headings in Positioning.
4. **External marking**: Any related work not yet ingested into the wiki MUST be
   marked with `(external)` after its name. If the same external work is cited
   by ≥2 papers in the wiki, strongly consider ingesting it.
5. **Linking**: Use `[[...]]` for wiki-internal papers; plain text + `(external)`
   for external ones. Do NOT create broken internal links.

### Topic Tags Reference

Use one or more slugs from this list for the `topics` frontmatter field.
The **first** slug determines the file path; the rest are metadata tags.

| Slug | Use For |
|------|---------|
| `video-generation` | Text-to-video, image-to-video, video diffusion |
| `image-generation` | Text-to-image, image editing, image diffusion |
| `language-model` | LLM arch, pretraining, post-training, reasoning |
| `reinforcement-learning` | RLHF, RLVR, GRPO, PPO, agentic RL |
| `vision` | Image classification, segmentation, visual understanding |
| `multimodal` | VLM, omni-modal, cross-modal learning |
| `inference-optimization` | KV-cache, quantization, pruning, speculative decoding, sparse attention |
| `training-systems` | Distributed training, parallelism, fault tolerance |
| `efficiency` | General compression, acceleration, hardware co-design |
| `alignment` | Safety, fine-tuning, preference optimization |

---

## Dataview Index (`papers/papers-index.md`)

Create this page once. It auto-updates as new papers are added.

```markdown
---
title: "Papers Index"
tags: [index, dataview]
---

# Papers Index

Browse all ingested papers. Sort by column headers in Obsidian's live preview.

```dataview
TABLE first_author, affiliation, year, venue, topics
FROM "papers"
WHERE contains(tags, "paper")
SORT year DESC, venue ASC
```

## By Topic

```dataview
TABLE length(rows) as Count
FROM "papers"
WHERE contains(tags, "paper")
GROUP BY topics[0]
SORT Count DESC
```

## Papers with Multiple Topics

```dataview
TABLE topics
FROM "papers"
WHERE contains(tags, "paper") AND length(topics) > 1
SORT year DESC
```
```

---

## Concept Page (`concepts/<Concept Name>.md`)

Use this template when creating a new shared background concept page in `concepts/`.

```markdown
---
title: "<Concept Name>"
tags: [concept]
---

# <Concept Name>

> One-sentence definition.

## Overview

<2-4 paragraph explanation of the concept. Keep it general and reusable.>
<Include intuition, motivation, and high-level mechanics.>
<Avoid paper-specific details unless necessary for clarity.>

## Related Concepts

- [[<Related Concept 1>]] — <brief relationship note>
- [[<Related Concept 2>]] — <...>

## Referenced By

- [[<Paper A>]] — <how Paper A uses or discusses this concept>
- [[<Paper B>]] — <...>
```

---

## Linking Rules

1. **First mention in a paper page** → always use `[[Concept Name]]` wikilink.
2. **Subsequent mentions** → optionally plain text if the link would be distracting.
3. **Concept pages** → always link to related concepts and all papers that reference them.
4. **No orphan pages** → every new concept page should have at least one inbound link
   from a paper page before creation is considered complete.
5. **External references** → mark with `(external)` and consider ingesting if the same
   external paper is cited by ≥2 papers in the wiki.
