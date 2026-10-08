#!/usr/bin/env python3
"""Check every extracted item's evidence against its recorded page, and repair off-by-one/two page errors.

Usage: python -I verify_pages.py <extract_dir> <pages_dir> [--fix]

For each item in items_*.json: score = share of the evidence's significant words (or verbatim quote) found on the
recorded PDF page. Items scoring below 0.30 are searched on pages -3..+3; if a neighbour scores at least 0.60
and 0.25 better, --fix moves the item to that page. Everything else low-scoring is only reported (paraphrases of
inferred notes often score low legitimately). A log is written to <extract_dir>/verify_log.txt.
"""
import glob
import json
import re
import sys
from pathlib import Path

STOP = set("the a an of and or to in for on at by is are be as with that this shall will any all from it its their "
           "contractor company works work not may must which than into under".split())


def toks(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP and len(w) > 2}


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t.lower())).strip()


def score(item, text):
    ev = item.get("evidence") or ""
    quoted = re.findall(r'"([^"]{8,})"', ev)
    if quoted:
        return 1.0 if all(norm(q) in norm(text) for q in quoted) else 0.0
    t = toks(ev + " " + (item.get("title") or ""))
    return len(t & toks(text)) / len(t) if t else 1.0


def main(extract_dir, pages_dir, fix):
    cache = {}

    def page(n):
        if n not in cache:
            f = Path(pages_dir) / f"page_{n:04d}.txt"
            cache[n] = f.read_text(encoding="utf-8") if f.exists() else ""
        return cache[n]

    log, moved, low = [], 0, 0
    for fn in sorted(glob.glob(str(Path(extract_dir) / "items_*.json"))):
        items = json.load(open(fn, encoding="utf-8"))
        changed = False
        for it in items:
            pg = it["pdf_page"]
            s0 = score(it, page(pg))
            if s0 >= 0.30:
                continue
            best = max(((score(it, page(p)), p) for p in range(max(1, pg - 3), pg + 4) if p != pg), default=(0, pg))
            if best[0] >= 0.60 and best[0] - s0 >= 0.25:
                log.append(f"{Path(fn).name}: p{pg} -> p{best[1]} ({s0:.2f} -> {best[0]:.2f}) {it['title'][:70]}")
                if fix:
                    it["pdf_page"] = best[1]
                    changed = True
                moved += 1
            else:
                low += 1
                log.append(f"{Path(fn).name}: p{pg} REVIEW score {s0:.2f} {it['title'][:70]}")
        if changed:
            json.dump(items, open(fn, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    (Path(extract_dir) / "verify_log.txt").write_text("\n".join(log), encoding="utf-8")
    print(f"{moved} page corrections {'applied' if fix else 'proposed'}; {low} low-score items left for review (see verify_log.txt)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], "--fix" in sys.argv)
