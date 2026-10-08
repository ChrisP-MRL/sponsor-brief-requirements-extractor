#!/usr/bin/env python3
"""Validation checks for a FLOC data.json (see references/validation_checklist.md).

Usage: python -I validate.py <data.json> [pages_dir] [--sample 0.10] [--seed 42]
Importable: run_checks(data, pages_dir=None, sample=0.10, seed=42) -> (results, spot_rows, derived)

derived contains per-FLOC links, page ranges and the hyperlink target used by build_workbook.py so the
workbook and the checks always agree.
"""
import json
import random
import re
import sys
from pathlib import Path
from urllib.parse import quote

SCOPE_TYPES = {"Scope", "Area/Facility", "Work Package", "Exclusion", "Provisional Sum"}
STOP = set("the a an of and or to in for on at by is are be as with that this shall will any all from it its their "
           "contractor company works work not may must which than into under".split())


def pdf_url(pdf_file, page):
    p = Path(pdf_file).resolve()
    return "file:///" + quote(p.as_posix(), safe="/:") + f"#page={page}"


def printed_to_int(label):
    if label is None:
        return None
    label = str(label)
    if label.isdigit():
        return int(label)
    roman = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
    t = 0
    s = label.lower()
    for i, ch in enumerate(s):
        if ch not in roman:
            return None
        v = roman[ch]
        t += -v if i + 1 < len(s) and roman.get(s[i + 1], 0) > v else v
    return t


def derive(data):
    """Links, ancestors and page ranges."""
    src = {s["source_id"]: s for s in data["sources"]}
    flocs = {f["floc_id"]: f for f in data["flocs"]}
    children = {}
    for f in data["flocs"]:
        children.setdefault(f["parent_id"], []).append(f["floc_id"])
    links = []  # (floc_id, source_id, role)
    for f in data["flocs"]:
        if f["primary_source"]:
            links.append((f["floc_id"], f["primary_source"], "Primary"))
        for sid in f["supporting_sources"]:
            links.append((f["floc_id"], sid, "Supporting"))
    own_pages = {}
    for fid, sid, _ in links:
        if sid in src:
            own_pages.setdefault(fid, []).append(src[sid]["pdf_page"])

    ranges = {}

    def rng(fid):
        pages = list(own_pages.get(fid, []))
        printed = []
        for c in children.get(fid, []):
            r = rng(c)
            if r:
                pages += [r[0], r[1]]
        ranges[fid] = (min(pages), max(pages)) if pages else None
        return ranges[fid]

    for root in children.get(None, []):
        rng(root)

    def ancestors(fid):
        out = []
        while fid:
            out.append(fid)
            fid = flocs[fid]["parent_id"]
        return out[::-1]

    return {"src": src, "flocs": flocs, "children": children, "links": links, "ranges": ranges,
            "ancestors": ancestors}


def toks(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP and len(t) > 2]


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()


def run_checks(data, pages_dir=None, sample=0.10, seed=42):
    d = derive(data)
    src, flocs, children, links = d["src"], d["flocs"], d["children"], d["links"]
    n_pages = data["meta"]["pdf_page_count"]
    res = []

    def add(name, status, count, detail):
        res.append({"check": name, "status": status, "count": count, "detail": detail})

    ids = [f["floc_id"] for f in data["flocs"]]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    add("Duplicate FLOC IDs", "PASS" if not dup else "FAIL", len(dup), ", ".join(dup[:15]) or "None")
    sids = [s["source_id"] for s in data["sources"]]
    dups = sorted({i for i in sids if sids.count(i) > 1})
    add("Duplicate Source IDs", "PASS" if not dups else "FAIL", len(dups), ", ".join(dups[:15]) or "None")

    orphan = [f["floc_id"] for f in data["flocs"] if f["parent_id"] is not None and f["parent_id"] not in flocs]
    roots = [f["floc_id"] for f in data["flocs"] if f["parent_id"] is None]
    add("Orphan FLOC nodes (parent missing) / single root", "PASS" if not orphan and len(roots) == 1 else "FAIL",
        len(orphan) + (0 if len(roots) == 1 else abs(len(roots) - 1)),
        f"orphans: {orphan[:10]}; roots: {roots}")
    gaps = [f["floc_id"] for f in data["flocs"] if f["parent_id"] in flocs and f["level"] != flocs[f["parent_id"]]["level"] + 1]
    add("Hierarchy level gaps", "PASS" if not gaps else "FAIL", len(gaps), ", ".join(gaps[:15]) or "None")
    deep = [f["floc_id"] for f in data["flocs"] if not 1 <= f["level"] <= 5]
    add("Levels within 1-5", "PASS" if not deep else "FAIL", len(deep), ", ".join(deep) or "None")

    nosrc = [f["floc_id"] for f in data["flocs"] if not f["primary_source"] and not f["assumption"]]
    assum = [f["floc_id"] for f in data["flocs"] if not f["primary_source"] and f["assumption"]]
    add("FLOCs with no Source ID (not marked Assumption)", "PASS" if not nosrc else "FAIL", len(nosrc),
        ", ".join(nosrc[:15]) or "None")
    add("FLOCs marked 'No source - Assumption' (listed in Gaps_and_RFIs)", "PASS" if not assum else "WARN", len(assum),
        ", ".join(assum[:15]) or "None")

    prim_counts = {}
    for fid, sid, role in links:
        if role == "Primary":
            prim_counts[fid] = prim_counts.get(fid, 0) + 1
    multi = [k for k, v in prim_counts.items() if v > 1]
    add("FLOCs with more than one Primary reference", "PASS" if not multi else "FAIL", len(multi), ", ".join(multi) or "None")
    missing_prim = [f["floc_id"] for f in data["flocs"] if f["floc_id"] not in prim_counts and not f["assumption"]]
    add("FLOCs with no Primary reference (not Assumption)", "PASS" if not missing_prim else "FAIL", len(missing_prim),
        ", ".join(missing_prim[:15]) or "None")

    unknown = [(f, s) for f, s, _ in links if s not in src]
    add("Links pointing to unknown Source IDs", "PASS" if not unknown else "FAIL", len(unknown), str(unknown[:5]) or "None")

    linked_src = {s for _, s, _ in links}
    mapped_src = {s["source_id"] for s in data["sources"] if s.get("mapped_floc")}
    orphan_scope = [s["source_id"] for s in data["sources"]
                    if s["item_type"] in SCOPE_TYPES and s["source_id"] not in linked_src and s["source_id"] not in mapped_src]
    orphan_other = [s["source_id"] for s in data["sources"]
                    if s["item_type"] not in SCOPE_TYPES and s["source_id"] not in linked_src and s["source_id"] not in mapped_src]
    add("Unmapped scope-type items (Scope/Area/Work Package/Exclusion/Provisional Sum)",
        "PASS" if not orphan_scope else "FAIL", len(orphan_scope), ", ".join(orphan_scope[:20]) or "None")
    add("Source IDs linked to no FLOC - other item types (pricing, commercial, HSE etc.; informational)",
        "INFO", len(orphan_other), "Expected for non-scope evidence; review Source_Register filter 'Linked FLOC IDs' = blank")

    dflt = [s["source_id"] for s in data["sources"] if s.get("mapped_by") == "default"]
    add("Sources mapped by a fallback ('default') rule rather than a specific rule (review the FLOC choice)", "INFO", len(dflt),
        "Filter Source_Register 'Mapping basis' = default")
    oob = [s["source_id"] for s in data["sources"] if not 1 <= s["pdf_page"] <= n_pages]
    add(f"Page numbers outside document ({n_pages} pages)", "PASS" if not oob else "FAIL", len(oob), ", ".join(oob[:15]) or "None")

    # offset / pdf-vs-printed confusion
    parts = data["meta"]["parts"]

    def part_off(pg):
        for p in parts:
            if p["pdf_from"] <= pg <= p["pdf_to"]:
                return p.get("offset")
        return None

    mix, off_bad = [], []
    for s in data["sources"]:
        pr = printed_to_int(s.get("printed_page"))
        off = part_off(s["pdf_page"])
        if pr is None or off is None:
            continue
        if off != 0 and pr == s["pdf_page"]:
            mix.append(s["source_id"])
        if s.get("printed_page_basis") == "detected" and abs((s["pdf_page"] - pr) - off) > 2 and not re.fullmatch(r"[ivxlc]+", str(s["printed_page"]), re.I):
            off_bad.append(s["source_id"])
    add("PDF page equals printed page where a non-zero offset applies (possible swap)", "PASS" if not mix else "WARN",
        len(mix), ", ".join(mix[:15]) or "None")
    add("Detected printed page inconsistent with the part's PDF-to-printed offset", "PASS" if not off_bad else "WARN",
        len(off_bad), ", ".join(off_bad[:15]) or "None")
    nolabel = [s["source_id"] for s in data["sources"] if s.get("printed_page") in (None, "")]
    add("Sources with no printed page label (PDF page only)", "PASS" if not nolabel else "INFO", len(nolabel),
        ", ".join(nolabel[:15]) or "None")

    # parent range covers children
    bad_rng = []
    for f in data["flocs"]:
        r = d["ranges"].get(f["floc_id"])
        for c in children.get(f["floc_id"], []):
            rc = d["ranges"].get(c)
            if rc and (not r or rc[0] < r[0] or rc[1] > r[1]):
                bad_rng.append(f["floc_id"])
    add("Parent page range does not cover child pages", "PASS" if not bad_rng else "FAIL", len(set(bad_rng)),
        ", ".join(sorted(set(bad_rng))[:15]) or "None")

    # hyperlink resolution
    badlink = []
    for s in data["sources"]:
        url = pdf_url(data["meta"]["pdf_file"], s["pdf_page"])
        m = re.search(r"#page=(\d+)$", url)
        if not m or int(m.group(1)) != s["pdf_page"] or not 1 <= s["pdf_page"] <= n_pages:
            badlink.append(s["source_id"])
    pdf_exists = Path(data["meta"]["pdf_file"]).exists()
    add("Hyperlinks resolve to the stated page (target page param = PDF page, within document)",
        "PASS" if not badlink else "FAIL", len(badlink), ", ".join(badlink[:15]) or "None")
    add("Hyperlink target file exists at stated path", "PASS" if pdf_exists else "WARN", 0 if pdf_exists else 1,
        data["meta"]["pdf_file"])

    # scope-status consistency
    badstat = [f["floc_id"] for f in data["flocs"] if f["scope_status"] not in ("In scope", "Excluded", "Provisional")]
    add("Scope status values valid", "PASS" if not badstat else "FAIL", len(badstat), ", ".join(badstat[:15]) or "None")
    if data.get("resolve_errors"):
        add("Spec hooks that matched no source (resolve_spec.py)", "FAIL", len(data["resolve_errors"]),
            " | ".join(data["resolve_errors"][:5]))
    else:
        add("Spec hooks that matched no source (resolve_spec.py)", "PASS", 0, "None")

    # spot-check: 10% of FLOC->source links re-read against page text
    spot = []
    if pages_dir and Path(pages_dir).exists():
        rnd = random.Random(seed)
        k = max(1, round(len(links) * sample))
        pick = rnd.sample(links, min(k, len(links)))
        fails = 0
        for fid, sid, role in sorted(pick):
            s = src.get(sid)
            if not s:
                continue
            txt = (Path(pages_dir) / f"page_{s['pdf_page']:04d}.txt")
            page_text = txt.read_text(encoding="utf-8") if txt.exists() else ""
            ev = s.get("evidence") or ""
            quoted = re.findall(r'"([^"]{8,})"', ev) + re.findall(r"“([^”]{8,})”", ev)
            if quoted:
                ok = all(norm(q) in norm(page_text) for q in quoted)
                score = 1.0 if ok else 0.0
                how = "verbatim quote"
            else:
                t = set(toks(ev))
                score = (len(t & set(toks(page_text))) / len(t)) if t else 0.0
                ok = score >= 0.6
                how = "paraphrase keyword overlap"
            fails += 0 if ok else 1
            spot.append({"floc_id": fid, "source_id": sid, "role": role, "pdf_page": s["pdf_page"],
                         "method": how, "score": round(score, 2), "result": "PASS" if ok else "REVIEW",
                         "evidence": ev})
        add(f"Spot-check: {len(spot)} sampled FLOC-to-source links ({int(sample*100)}%) re-read against page text",
            "PASS" if fails == 0 else "WARN", fails, "Automated text match; reviewer should still read 'REVIEW' rows against the PDF")
    else:
        add("Spot-check against page text", "WARN", 0, "pages_dir not supplied; run with the extract_pages.py output folder")
    return res, spot, d


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    pages = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    r, sp, _ = run_checks(data, pages)
    for x in r:
        print(f"[{x['status']:4}] {x['check']}: {x['count']}  {x['detail'][:120]}")
