---
name: paper-lint
description: >
  Health-check and auto-repair the Obsidian wiki. Trigger when the user asks to
  lint, audit, health-check, or scan the wiki for quality issues. Fixes structural
  issues: orphan pages with no inbound links, broken wikilinks, missing concept
  pages for frequently-linked terms, and missing cross-references. Automatically
  fixes repairable issues and writes a detailed report with diffs to the LintLog/
  directory.
---

# Paper Lint Skill

Audit the wiki for structural quality issues, auto-fix what can be fixed safely,
and produce a timestamped report in `LintLog/`.

## Goal

1. A **structurally sound** graph where every page is reachable via links.
2. A **LintLog report** documenting every issue found, every fix applied, and any
   remaining items that need human review.

## Lint Workflow

Execute the steps below in order. Do not skip steps.

### Step 1: Scan

1. Ensure `LintLog/` exists at the vault root. Create it if missing.
2. Run the scanner:
   ```bash
   python .agents/skills/paper-lint/scripts/lint_scan.py
   ```
3. Read `index.md` to understand current scope.
4. Parse the JSON output. Record:
   - `total_pages`, `orphan_count`, `broken_count`, `high_freq_missing_concepts`

### Step 2: Fix Orphan Pages

An orphan page has **zero inbound links** from other wiki pages.

- Read each orphan page.
- **Paper page** (`papers/<topic>/`): Add to `index.md` under its topic, and add a
  backlink from at least one related `concepts/` page (create a "See Also" or
  "Referenced By" section if needed).
- **Concept page** (`concepts/`): Add to `index.md` under "Concepts", and link it
  from 1–2 related concept pages.
- **Synthesis page**: Link it from every source page it draws on.
- If the page is an empty draft or duplicate, **do not force a link**. Record it
  in the report under "Human Review" with recommendation to delete or merge.

### Step 3: Fix Broken Links

For each `broken_links` entry:

- **Target exists under a different name**: Correct the wikilink text to match
  the actual page title or filename.
- **Target is a missing concept** that appears in `high_freq_missing_concepts`:
  Create the concept page (see Step 4) and update the link.
- **Target is a paper not yet ingested**: Replace `[[Title]]` with plain text
  `Title (external)` to follow wiki convention.
- **Target is ambiguous / unknown**: Remove the wikilink and record in report.

### Step 4: Create Missing Concept Pages

Review `high_freq_missing_concepts` from the scan.

- For each term with `count >= 3`:
  - Judge whether it is a **reusable, cross-paper concept** (e.g., "KV Cache",
    "Policy Gradient") or a paper-specific proper noun.
  - If reusable, create `concepts/<Term>.md` with:
    - YAML frontmatter: `tags: [concept]`
    - A concise definition.
    - A "Referenced By" section listing source pages.
  - Update all pages that mention the term to use `[[Term]]` on first mention.
- For `count == 2`, create only if it is clearly general background knowledge.

### Step 5: Add Missing Cross-References

Scan paper pages for terms that have existing concept pages but appear as plain
text. Add `[[Concept Name]]` on first mention. Do **not** create speculative links
to non-existent pages.

### Step 6: Record Diffs

For every file modified or created, record a concise diff for the report:
- **New file**: frontmatter + first paragraph + "..."
- **Modification**: 2 lines of context around each change, with `+` / `-`
- **Deletion**: file path + reason only

### Step 7: Generate LintLog Report

Create `LintLog/YYYY-MM-DD-HHMMSS-lint-report.md`.

```markdown
---
tags: [lint-report]
date: YYYY-MM-DD
---

# Lint Report: YYYY-MM-DD HH:MM:SS

## Summary
- Pages scanned: <N>
- Orphans fixed: <N>
- Broken links fixed: <N>
- Concept pages created: <N>
- Cross-references added: <N>
- Human review required: <N>

## Fixes Applied

### Orphan Pages
| Page | Action |
|------|--------|
| [[Page]] | Added to index.md + backlinked from [[Concept]] |

### Broken Links
| Source | Broken Link | Fix |
|--------|-------------|-----|
| `papers/...` | `[[Bad]]` | Corrected / Removed / Created target |

### Concept Pages Created
| Concept | Linked From |
|---------|-------------|
| [[Term]] | [[Paper1]], [[Paper2]] |

### Cross-References Added
| Page | Links Added |
|------|-------------|
| [[Paper]] | [[Concept1]], [[Concept2]] |

## Diff Log

### `path/to/file.md`
```diff
- old line
+ new line
```

## Remaining for Human Review
- <item>
```

### Step 8: Update Root Log

Append to `log.md`:
```markdown
## [YYYY-MM-DD] lint | structural
- Scanned: <N> pages
- Fixed: <N> issues (see [[LintLog/YYYY-MM-DD-HHMMSS-lint-report]])
- Review needed: <N>
```

## Quality Standards

- **Minimal diffs**: Only touch lines necessary to fix the issue.
- **No orphaned fixes**: Every new concept page must be linked from at least one
  existing page before the lint run ends.
- **Idempotent**: Running lint twice on an unchanged wiki should find zero new issues.

## Directory Conventions

```
obsidian-paper-curator/
├── LintLog/                # Timestamped lint reports (created by this skill)
├── concepts/               # May be modified: new pages added
├── papers/<topic>/         # May be modified: links added
├── index.md                # May be modified: orphan pages added to catalog
└── log.md                  # Appended with lint entry
```

Do not modify files in `Clippings/`, `raw/`, or `.obsidian/`.
