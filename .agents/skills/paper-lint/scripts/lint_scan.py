#!/usr/bin/env python3
"""
Wiki lint scanner: builds the link graph and produces a structured report.

Outputs JSON to stdout containing:
- pages: list of all markdown pages with metadata
- orphan_pages: pages with zero inbound links
- broken_links: wikilinks pointing to non-existent targets
- high_freq_missing_concepts: frequently linked terms without a concepts/ page
- page_graph: outbound and inbound links per page
"""

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    ".obsidian",
    ".agents",
    "LintLog",
    "_processed",
    "_assets",
}

# Files to exclude
EXCLUDE_FILES = {"index.md", "log.md", "README.md", "README.en.md", "AGENTS.md"}

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def should_exclude(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    for part in rel.parts:
        if part.startswith(".") or part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_FILES:
        return True
    return False


def extract_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    raw = m.group(1)
    data = {}
    key = None
    for line in raw.splitlines():
        if ":" in line and not line.strip().startswith("-"):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            data[key] = val
        elif key and line.strip().startswith("-"):
            val = line.strip()[1:].strip().strip('"').strip("'")
            if key not in data:
                data[key] = []
            if isinstance(data[key], list):
                data[key].append(val)
    return data


def extract_wikilinks(text: str) -> list:
    # Remove code blocks to avoid false positives
    clean = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    clean = re.sub(r"`[^`]+`", "", clean)
    matches = WIKILINK_RE.findall(clean)
    # Normalize: strip whitespace, lowercase for comparison
    return [m.strip() for m in matches]


def main():
    root = Path.cwd()
    if len(sys.argv) > 1:
        root = Path(sys.argv[1]).resolve()
        os.chdir(root)

    pages = {}
    all_links = Counter()

    for md_path in root.rglob("*.md"):
        if should_exclude(md_path, root):
            continue

        rel = str(md_path.relative_to(root)).replace("\\", "/")
        text = md_path.read_text(encoding="utf-8")
        fm = extract_frontmatter(text)
        links = extract_wikilinks(text)
        title = fm.get("title", md_path.stem)

        pages[rel] = {
            "path": rel,
            "filename": md_path.name,
            "title": title,
            "frontmatter": fm,
            "outbound_links": links,
            "outbound_count": len(links),
        }
        for lk in links:
            all_links[lk] += 1

    # Build inbound link map
    inbound = {p: [] for p in pages}
    for src, info in pages.items():
        for lk in info["outbound_links"]:
            # Try exact match, then case-insensitive, then filename match
            targets = []
            for tgt, tinfo in pages.items():
                if lk == tinfo["title"] or lk == tinfo["filename"].replace(".md", ""):
                    targets.append(tgt)
                elif lk.lower() == tinfo["title"].lower():
                    targets.append(tgt)
            if not targets:
                # Try partial match on path
                for tgt, tinfo in pages.items():
                    if lk.lower() in tinfo["filename"].lower():
                        targets.append(tgt)
                        break
            for tgt in set(targets):
                inbound[tgt].append(src)

    # Orphan pages: 0 inbound from other wiki pages
    orphan_pages = [p for p, srcs in inbound.items() if len(srcs) == 0]

    # Broken links: links pointing to nothing
    existing_titles = {info["title"] for info in pages.values()}
    existing_names = {info["filename"].replace(".md", "") for info in pages.values()}
    broken_links = []
    seen_broken = set()
    for src, info in pages.items():
        for lk in info["outbound_links"]:
            key = (src, lk)
            if key in seen_broken:
                continue
            if lk in existing_titles or lk in existing_names:
                continue
            # Check case-insensitive
            if lk.lower() in {t.lower() for t in existing_titles}:
                continue
            if lk.lower() in {n.lower() for n in existing_names}:
                continue
            seen_broken.add(key)
            broken_links.append({"source": src, "link": lk})

    # High-frequency linked terms without a concepts/ page
    concept_pages = {p for p in pages if p.startswith("concepts/")}
    concept_titles = {
        pages[p]["title"] for p in concept_pages
    } | {
        pages[p]["filename"].replace(".md", "") for p in concept_pages
    }
    high_freq_missing = []
    for term, count in all_links.most_common(50):
        if count < 2:
            continue
        if term in concept_titles:
            continue
        # Skip if there is already a page with this name somewhere else
        if term in existing_titles or term in existing_names:
            continue
        high_freq_missing.append({"term": term, "count": count})

    report = {
        "vault_root": str(root),
        "total_pages": len(pages),
        "pages": pages,
        "orphan_pages": orphan_pages,
        "orphan_count": len(orphan_pages),
        "broken_links": broken_links,
        "broken_count": len(broken_links),
        "high_freq_missing_concepts": high_freq_missing[:20],
        "inbound_links": inbound,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
