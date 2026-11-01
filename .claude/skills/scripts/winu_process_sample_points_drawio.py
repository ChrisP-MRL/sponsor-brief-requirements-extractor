#!/usr/bin/env python3
"""Draw a simple locational diagram of the Winu MPP sample points (draw.io).

Reads the Sample_Points sheet of Winu_Process_Plant_Sample_Points.xlsx for IDs and tiers, and places each
point on a notional block flowsheet (see the workbook's Flowsheet_Basis sheet; the flowsheet is assumed).

Run: python -I -X utf8 winu_process_sample_points_drawio.py --xlsx <xlsx> --output <drawio> [--force]
"""
import argparse
import sys
from pathlib import Path
from xml.sax.saxutils import quoteattr

from openpyxl import load_workbook

TIER_COL = {"1 Essential": "#C00000", "2 Recommended": "#ED7D31", "3 Optional / survey": "#A6A6A6"}
STEP_X, STEP_Y, W, H = 175, 180, 135, 98
X0, Y0 = 60, 70

# unit id -> (label, col, row, [sample points]). Connected units are adjacent or vertically aligned so that no
# connector crosses a box or another connector.
UNITS = {
    "rom": ("ROM stockpile", 0, 0, ["SP-101"]),
    "crush": ("Primary crusher", 1, 0, ["SP-102"]),
    "cos": ("COS reclaim and SAG feed conveyor", 2, 0, ["SP-103", "SP-104"]),
    "sag": ("SAG mill and cyclones", 3, 0, ["SP-201", "SP-202", "SP-203", "SP-204"]),
    "peb": ("Oversized (pebble) crusher", 4, 0, ["SP-251"]),
    "rough": ("Rougher flotation", 3, 1, ["SP-401", "SP-402"]),
    "scav": ("Scavenger flotation", 2, 1, ["SP-403", "SP-404"]),
    "clean": ("Cleaner flotation", 1, 1, ["SP-407", "SP-408", "SP-409"]),
    "regrind": ("Regrind mill and cyclones", 0, 1, ["SP-405", "SP-406"]),
    "grav": ("Gravity gold concentrators", 4, 1, ["SP-301", "SP-302", "SP-303"]),
    "filter": ("Concentrate filter", 0, 2, ["SP-503", "SP-504"]),
    "thick": ("Concentrate thickener", 1, 2, ["SP-501", "SP-502"]),
    "split": ("HS / LS tailings split", 2, 2, ["SP-410", "SP-411"]),
    "lst": ("LST thickener", 3, 2, ["SP-601", "SP-602"]),
    "tsf": ("TSF low-sulphur cell", 4, 2, ["SP-605"]),
    "reclaim": ("TSF reclaim pond", 5, 2, ["SP-604"]),
    "prod": ("Product sampling station", 0, 3, ["SP-505"]),
    "shed": ("Concentrate shed and load-out", 1, 3, ["SP-506", "SP-507"]),
    "hscell": ("HS tailings to water-covered cell", 2, 3, ["SP-603"]),
    "pwater": ("Process water tank", 5, 3, ["SP-802"]),
    "reag": ("Reagent receipt", 0, 4, ["SP-701"]),
    "makeup": ("Reagent make-up", 1, 4, ["SP-702"]),
    "wwtp": ("Wastewater treatment", 3, 4, ["SP-804"]),
    "raw": ("Raw water (bores WINU0913 / 0925)", 4, 4, ["SP-801"]),
    "cwp": ("Clean water pond", 5, 4, ["SP-803"]),
}
R, L, B, T = (1, .5), (0, .5), (.5, 1), (.5, 0)
# (from, exit port, to, entry port, both-ways)
EDGES = [
    ("rom", R, "crush", L), ("crush", R, "cos", L), ("cos", R, "sag", L), ("sag", R, "peb", L),
    ("sag", B, "rough", T), ("sag", (.85, 1), "grav", (.15, 0)),
    ("rough", L, "scav", R), ("scav", L, "clean", R), ("clean", L, "regrind", R, True),
    ("scav", B, "split", T), ("clean", B, "thick", T),
    ("thick", L, "filter", R), ("filter", B, "prod", T), ("prod", R, "shed", L),
    ("split", R, "lst", L), ("lst", R, "tsf", L), ("tsf", R, "reclaim", L),
    ("split", B, "hscell", T), ("reclaim", B, "pwater", T),
    ("raw", T, "pwater", L), ("cwp", T, "pwater", B), ("reag", R, "makeup", L),
]
BANDS = [
    (0, "Crushing and grinding (stated: ROM, crushing, grinding, oversized crushing)"),
    (1, "Gravity and flotation (stated: gravity gold, flotation and regrind; layout assumed)"),
    (2, "Concentrate dewatering and tailings (stated: concentrate dewatering, LST thickeners, HS and LS cells)"),
    (3, "Product handling and process water (stated: product sampling, handling, reclaim; utilities)"),
    (4, "Reagents and water sources (stated)"),
]


def build(xlsx: Path, out: Path):
    ws = load_workbook(xlsx, data_only=True)["Sample_Points"]
    info = {r[0]: (r[3], r[6]) for r in ws.iter_rows(min_row=5, values_only=True) if r[0]}
    placed = {s for u in UNITS.values() for s in u[3]}
    if placed != set(info):
        sys.exit(f"mismatch: missing {sorted(set(info) - placed)}, extra {sorted(placed - set(info))}")

    cells, n = [], [1]

    def nid():
        n[0] += 1
        return f"c{n[0]}"

    def vertex(label, x, y, w, h, style, tip=None):
        i = nid()
        v = quoteattr(label)
        tag = f'<object label={v} tooltip={quoteattr(tip)} id="{i}">' if tip else None
        geo = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        cell = f'<mxCell style={quoteattr(style)} vertex="1" parent="1">{geo}</mxCell>'
        cells.append(f"{tag}{cell}</object>" if tip else
                     f'<mxCell id="{i}" value={v} style={quoteattr(style)} vertex="1" parent="1">{geo}</mxCell>')
        return i

    # background bands first so they sit behind
    for row, title in BANDS:
        y = Y0 + row * STEP_Y - 36
        vertex(title, 20, y, X0 + 5 * STEP_X + W + 40 - 20, STEP_Y - 20,
               "rounded=0;whiteSpace=wrap;html=1;fillColor=#F5F8FC;strokeColor=#BFD0E6;align=left;verticalAlign=top;"
               "spacingLeft=8;fontSize=11;fontStyle=1;fontColor=#1F3864;")
    ids = {}
    for key, (label, col, row, sps) in UNITS.items():
        x, y = X0 + col * STEP_X, Y0 + row * STEP_Y
        ids[key] = vertex(label, x, y, W, H,
                          "rounded=1;whiteSpace=wrap;html=1;fillColor=#DDEBF7;strokeColor=#1F3864;fontSize=11;verticalAlign=top;spacingTop=4;")
        for k, sp in enumerate(sps):
            mx = x + 6 + (k % 3) * 42
            my = y + 46 + (k // 3) * 26
            stream, tier = info[sp]
            vertex(sp, mx, my, 40, 22,
                   f"ellipse;whiteSpace=wrap;html=1;fillColor={TIER_COL[tier]};strokeColor=none;fontColor=#FFFFFF;"
                   "fontSize=9;fontStyle=1;spacing=0;", tip=f"{sp}: {stream} ({tier})")
    for e in EDGES:
        a, (ex, ey), b, (nx, ny) = e[0], e[1], e[2], e[3]
        both = "startArrow=block;" if len(e) > 4 else ""
        i = nid()
        cells.append(f'<mxCell id="{i}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;{both}'
                     f'exitX={ex};exitY={ey};entryX={nx};entryY={ny};exitDx=0;exitDy=0;entryDx=0;entryDy=0;'
                     f'strokeColor=#1F3864;strokeWidth=1.5;" edge="1" parent="1" source="{ids[a]}" target="{ids[b]}">'
                     '<mxGeometry relative="1" as="geometry"/></mxCell>')

    # legend and title
    ly = Y0 + 5 * STEP_Y - 30
    vertex("Winu processing plant (MPP) - sample point locations (notional flowsheet; flowsheet not in the pack)",
           20, 14, 900, 28, "text;html=1;align=left;fontSize=15;fontStyle=1;fontColor=#1F3864;")
    vertex("Legend: marker = sample point, hover for stream name. Detail, methods and frequencies are on the Sample_Points sheet.",
           20, ly, 700, 22, "text;html=1;align=left;fontSize=11;")
    for k, (t, c) in enumerate(TIER_COL.items()):
        vertex(t, 20 + k * 190, ly + 26, 170, 24,
               f"ellipse;whiteSpace=wrap;html=1;fillColor={c};strokeColor=none;fontColor=#FFFFFF;fontSize=10;fontStyle=1;")

    xml = ('<mxfile host="app.diagrams.net"><diagram name="Sample points" id="sp1"><mxGraphModel dx="1400" dy="900" '
           'grid="1" gridSize="10" guides="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1100" math="0" shadow="0">'
           '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding="utf-8")
    return len(info)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    p = Path(a.output)
    if p.exists() and not a.force:
        sys.exit(f"{p} exists; use --force")
    print(f"wrote {p} with {build(Path(a.xlsx), p)} sample points")


if __name__ == "__main__":
    main()
