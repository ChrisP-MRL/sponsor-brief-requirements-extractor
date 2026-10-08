#!/usr/bin/env python3
"""Resolve a FLOC specification (names + page/keyword hooks) against the Source Register -> data.json.

Usage: python -I resolve_spec.py <sources.json> <floc_spec.json> <config.json> <out_data.json>

floc_spec.json
{
  "project": { <node> },
  "pricing": [ {"schedule","item_no","description","unit","basis","page","kw","floc_keys":[...]} ],
  "allocation_rules": [ {"rule_id","cost_pool","description","driver","applies_to","basis","sources":[{"page","kw"}],"notes"} ],
  "rfis": [ {"topic","question","impact","priority","type","page","kw","floc_keys":[...]} ]
}
<node> = {
  "key": "short unique key (for pricing/RFI references)", "name": "...",
  "status": "In scope | Excluded | Provisional", "disciplines": [..], "responsibility": "...",
  "primary": {"page": 123, "kw": "regex matched against section/title/evidence of sources on that page"},
  "maps":   [ {"pages": [from, to], "kw": "regex on section/title/figure/suggested_area (optional)",
               "types": ["Scope", ...] (optional), "default": true (optional: fallback, applied last and
               reported for review), "any_field": true (optional: also search evidence/notes)} ],
  "assumption": false, "notes": "...", "children": [ <node> ]
}
Mapping: every source is claimed by AT MOST ONE FLOC (MECE). Rules are tried most-specific first
(keyword rules before page-only rules, then narrower page span). A node's primary source is forced onto it.
Sources claimed by no rule stay unmapped (reported by validation if they are scope-type items).
FLOC IDs are generated from config 'numbering' in tree order. Nothing is guessed: unresolved hooks
are listed under 'resolve_errors' in the output and fail validation.
"""
import json
import re
import sys

TYPE_RANK = {"Area/Facility": 0, "Work Package": 1, "Scope": 2, "Exclusion": 3, "Provisional Sum": 4,
             "Pricing Structure": 5, "Allocation Basis": 6, "Interface": 7}
CONF_RANK = {"High": 0, "Medium": 1, "Low": 2}


def haystack(s):
    return " ".join(str(s.get(k) or "") for k in ("section", "title", "evidence", "figure_table", "notes"))


def map_haystack(s):
    """Fields used by 'maps' keywords: precise (no free-text evidence/notes) to limit false claims."""
    return " ".join(str(s.get(k) or "") for k in ("section", "title", "figure_table", "suggested_area"))


def find_source(sources_by_page, page, kw):
    pool = sources_by_page.get(page, [])
    rx = re.compile(kw, re.I) if kw else None
    hits = [s for s in pool if rx is None or rx.search(haystack(s))]
    if not hits and kw:  # hook written as plain text containing regex characters, e.g. "(WBS 2900 series)"
        lit = re.compile(re.escape(kw), re.I)
        hits = [s for s in pool if lit.search(haystack(s))]
    hits.sort(key=lambda s: (TYPE_RANK.get(s["item_type"], 9), CONF_RANK.get(s["confidence"], 3), s["source_id"]))
    return hits[0] if hits else None


def main(sources_path, spec_path, config_path, out):
    cfg = json.load(open(config_path, encoding="utf-8"))
    sources = json.load(open(sources_path, encoding="utf-8"))
    spec = json.load(open(spec_path, encoding="utf-8"))
    by_page = {}
    for s in sources:
        by_page.setdefault(s["pdf_page"], []).append(s)
    errors, flocs, rules, keymap, counters = [], [], [], {}, {}
    num, prefix = cfg["numbering"], cfg["project_code"]

    def new_id(level, parent_id):
        if level == 1:
            return prefix
        if level == 2:
            idx = counters["_l2"] = counters.get("_l2", -1) + 1
            return f"{prefix}-{num['l2_start'] + num['l2_step'] * idx:04d}"
        n = counters[parent_id] = counters.get(parent_id, 0) + 1
        return f"{parent_id}-{n:0{3 if level == 5 else 2}d}"

    def walk(node, level, parent_id):
        fid = new_id(level, parent_id)
        rec = {"floc_id": fid, "parent_id": parent_id, "level": level, "key": node.get("key") or fid,
               "description": node["name"], "disciplines": node.get("disciplines", []),
               "responsibility": node.get("responsibility", "Not stated"),
               "scope_status": node.get("status", "In scope"), "assumption": bool(node.get("assumption")),
               "notes": node.get("notes"), "primary_source": None, "supporting_sources": []}
        if rec["key"] in keymap:
            errors.append(f"Duplicate key {rec['key']}")
        keymap[rec["key"]] = fid
        flocs.append(rec)
        p = node.get("primary")
        if p:
            s = find_source(by_page, p["page"], p.get("kw"))
            if s:
                rec["primary_source"] = s["source_id"]
            else:
                errors.append(f"{fid} {node['name']}: primary hook p{p['page']} /{p.get('kw')}/ matched no source")
        for m in node.get("maps", []):
            rules.append({"floc": fid, "a": m["pages"][0], "b": m["pages"][1],
                          "rx": re.compile(m["kw"], re.I) if m.get("kw") else None,
                          "types": set(m["types"]) if m.get("types") else None,
                          "default": bool(m.get("default")), "any": bool(m.get("any_field"))})
        for c in node.get("children", []):
            walk(c, level + 1, fid)

    walk(spec["project"], 1, None)
    rules.sort(key=lambda r: (1 if r["default"] else 0, 0 if r["rx"] else 1, r["b"] - r["a"]))
    claim, by = {}, {}
    for f in flocs:  # forced primaries
        if f["primary_source"]:
            claim.setdefault(f["primary_source"], f["floc_id"])
    for s in sources:
        if s["source_id"] in claim:
            continue
        for r in rules:
            if r["a"] <= s["pdf_page"] <= r["b"] and (r["types"] is None or s["item_type"] in r["types"]) \
                    and (r["rx"] is None or r["rx"].search(haystack(s) if r["any"] else map_haystack(s))):
                claim[s["source_id"]] = r["floc"]
                by[s["source_id"]] = "default" if r["default"] else "rule"
                break
    fmap = {f["floc_id"]: f for f in flocs}
    for s in sources:
        s["mapped_floc"] = claim.get(s["source_id"])
        s["mapped_by"] = by.get(s["source_id"], "primary" if s["source_id"] in claim else None)
        f = fmap.get(s["mapped_floc"])
        if f and s["source_id"] != f["primary_source"]:
            f["supporting_sources"].append(s["source_id"])

    def res_hooks(lst):
        ids = []
        for h in lst or []:
            s = find_source(by_page, h["page"], h.get("kw"))
            if s:
                ids.append(s["source_id"])
            else:
                errors.append(f"hook p{h['page']} /{h.get('kw')}/ matched no source")
        return ids

    pricing = []
    for k, p in enumerate(spec.get("pricing", []), 1):
        s = find_source(by_page, p["page"], p.get("kw"))
        if not s:
            errors.append(f"pricing {p.get('item_no')} p{p['page']} /{p.get('kw')}/ matched no source")
        bad = [x for x in p.get("floc_keys", []) if x not in keymap]
        if bad:
            errors.append(f"pricing {p.get('item_no')}: unknown floc keys {bad}")
        pricing.append({"pricing_id": f"PRC-{k:03d}", "schedule": p["schedule"], "item_no": p.get("item_no"),
                        "description": p["description"], "unit": p.get("unit") or "Not stated",
                        "basis": p.get("basis"), "pdf_page": p["page"], "source_id": s["source_id"] if s else None,
                        "floc_ids": [keymap[x] for x in p.get("floc_keys", []) if x in keymap],
                        "notes": p.get("notes")})
    alloc = []
    for r in spec.get("allocation_rules", []):
        alloc.append({**{k: r.get(k) for k in ("rule_id", "cost_pool", "description", "driver", "applies_to",
                                                "basis", "notes")},
                      "source_ids": res_hooks(r.get("sources"))})
    rfis = []
    for k, r in enumerate(spec.get("rfis", []), 1):
        s = find_source(by_page, r["page"], r.get("kw"))
        if not s:
            errors.append(f"RFI {k} p{r['page']} /{r.get('kw')}/ matched no source")
        rfis.append({"rfi_id": f"RFI-{k:03d}", "topic": r["topic"], "question": r["question"],
                     "impact": r.get("impact"), "priority": r.get("priority", "Medium"),
                     "source_id": s["source_id"] if s else None, "pdf_page": r["page"],
                     "floc_ids": [keymap[x] for x in r.get("floc_keys", []) if x in keymap],
                     "type": r.get("type", "Clarification")})
    meta_keys = ("project", "project_code", "client", "document_id", "document_title", "pdf_file", "pdf_page_count",
                 "currency", "workbook_version", "levels", "level_colours", "level_font_white", "parts",
                 "link_note", "numbering")
    data = {"meta": {k: cfg[k] for k in meta_keys}, "sources": sources, "flocs": flocs, "pricing": pricing,
            "allocation_rules": alloc, "rfis": rfis, "keymap": keymap, "resolve_errors": errors}
    json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(flocs)} FLOCs, {len(sources)} sources ({sum(1 for s in sources if s['mapped_floc'])} mapped), "
          f"{len(pricing)} pricing, {len(alloc)} rules, {len(rfis)} RFIs, {len(errors)} resolve errors")
    for e in errors[:40]:
        print("  ERR", e)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
