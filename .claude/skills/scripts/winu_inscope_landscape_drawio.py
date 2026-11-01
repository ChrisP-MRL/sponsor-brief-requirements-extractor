"""Redraw the Winu application landscape (in-scope capabilities by ISA-95 level)
from output/Winu_Application_Landscape_Tables_A4_v3.xlsx.
Single diagram sized for A4 portrait in Word: one band per level (L4 at the top), level header
strip on each band, capabilities in a 4-column grid. Writes .drawio and a high-resolution .png."""
import sys, html, openpyxl
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]  # workbook path, output path stem (no extension)
wb = openpyxl.load_workbook(src, data_only=True)
LEVELS = {"L4": ("LEVEL 4", "Business Planning & Logistics"),
          "L3": ("LEVEL 3", "Manufacturing Operations Management"),
          "L2": ("LEVEL 2", "Monitoring & Supervising"),
          "L1": ("LEVEL 1", "Sensing & Local Control")}
TITLE = "Winu application landscape: capabilities within MinRes scope"
KEYS = ["L4", "L3", "L2", "L1"]  # top to bottom
STYLE = {"In Scope": ("#f8cecc", "#b85450"), "Partial": ("#fff2cc", "#d6b656")}
NORM = {"Yes": "In Scope", "In Scope": "In Scope", "Partial": "Partial"}  # v3 uses Yes/No
data = {}
for sh in LEVELS:
    rows = [(r[0], NORM.get(r[2])) for r in wb[sh].iter_rows(min_row=3, values_only=True)]
    rows = [r for r in rows if r[1] in STYLE]
    rows.sort(key=lambda r: r[1] != "In Scope")  # In Scope first, workbook order kept
    data[sh] = rows
USED = {sc for v in data.values() for _, sc in v}
LEGEND = [t for t in [("In Scope", "In Scope"), ("Partial", "Partial (clarify / interface only)")] if t[0] in USED]

COLS, BW, BH, GX, GY, PAD = 4, 196, 46, 8, 6, 10
LEFT, TOP, LABH, BANDGAP = 20, 50, 30, 12
BAND_FILL, BAND_LINE, LAB_FILL, LAB_LINE = "#f5f5f5", "#999999", "#dae8fc", "#6c8ebf"
GRIDW = COLS * BW + (COLS - 1) * GX
BANDW = PAD + GRIDW + PAD

def build(keys, title):
    els, y = [], TOP
    for k in keys:
        rows = max(1, -(-len(data[k]) // COLS))
        h = LABH + PAD + rows * (BH + GY) - GY + PAD
        els.append(("band", LEFT, y, BANDW, h))
        els.append(("lab", LEFT, y, BANDW, LABH, LEVELS[k][0], LEVELS[k][1], f"{len(data[k])} in scope"))
        for i, (name, sc) in enumerate(data[k]):
            r, c = divmod(i, COLS)
            els.append(("box", LEFT + PAD + c * (BW + GX), y + LABH + PAD + r * (BH + GY), BW, BH, name, sc))
        y += h + BANDGAP
    els.append(("legend", LEFT, y + 4))
    els.append(("title", LEFT, 14, title))
    return els, LEFT + BANDW + LEFT, y + 36

n = 2
def diagram(els, name, did, W, H):
    global n
    cells = []
    def cell(style, val, x, y, w, h):
        global n; n += 1
        cells.append(f'<mxCell id="{n}" parent="1" style="{style}" value="{html.escape(val, quote=True)}" vertex="1"><mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')
    for e in els:
        if e[0] == "band": cell(f"rounded=0;whiteSpace=wrap;html=1;fillColor={BAND_FILL};strokeColor={BAND_LINE};", "", *e[1:])
        elif e[0] == "lab":
            _, x, yy, w, h, lvl, nm, sub = e
            v = f'<b>{html.escape(lvl)}</b>&nbsp;&nbsp;&nbsp;{html.escape(nm)}&nbsp;&nbsp;&nbsp;<font style="font-size: 11px;">({sub})</font>'
            cell(f"rounded=0;whiteSpace=wrap;html=1;fillColor={LAB_FILL};strokeColor={LAB_LINE};align=left;spacingLeft=10;verticalAlign=middle;fontSize=13;fontFamily=Helvetica;", v, x, yy, w, h)
        elif e[0] == "box":
            _, x, yy, w, h, nm, sc = e; f, s = STYLE[sc]
            cell(f"rounded=1;whiteSpace=wrap;html=1;fillColor={f};strokeColor={s};fontSize=11;fontFamily=Helvetica;", nm, x, yy, w, h)
        elif e[0] == "legend":
            _, x, yy = e
            for i, (sc, lab) in enumerate(LEGEND):
                f, s = STYLE[sc]
                cell(f"rounded=1;whiteSpace=wrap;html=1;fillColor={f};strokeColor={s};", "", x + i * 250, yy, 24, 16)
                cell("text;html=1;align=left;verticalAlign=middle;fontSize=10;fontFamily=Helvetica;", lab, x + i * 250 + 30, yy - 2, 210, 20)
        elif e[0] == "title": cell("text;html=1;align=left;verticalAlign=middle;fontSize=15;fontStyle=1;fontFamily=Helvetica;", e[3], e[1], e[2], BANDW, 30)
    return (f'<diagram name="{html.escape(name)}" id="{did}"><mxGraphModel dx="1000" dy="800" grid="1" gridSize="10" page="1" pageWidth="{W}" pageHeight="{H}">'
            f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(cells)}</root></mxGraphModel></diagram>')

S = 4  # PNG scale: ~3x print resolution when pasted at page width in Word
def png(els, W, H, path):
    img = Image.new("RGB", (W * S, H * S), "white"); d = ImageDraw.Draw(img)
    F = lambda sz, b=False: ImageFont.truetype("C:/Windows/Fonts/arial%s.ttf" % ("bd" if b else ""), sz * S)
    hexc = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    ctext = lambda cx, cy, t, font: d.text((cx * S, cy * S), t, font=font, fill="black", anchor="mm")
    def wrap(text, fn, maxw):
        lns, cur = [], ""
        for wd in text.split():
            t = (cur + " " + wd).strip()
            if d.textlength(t, font=fn) / S > maxw and cur: lns.append(cur); cur = wd
            else: cur = t
        return lns + [cur]
    for e in els:
        if e[0] in ("band", "lab"):
            x, yy, w, h = e[1:5]
            f, s = (BAND_FILL, BAND_LINE) if e[0] == "band" else (LAB_FILL, LAB_LINE)
            d.rectangle([x * S, yy * S, (x + w) * S, (yy + h) * S], fill=hexc(f), outline=hexc(s), width=S)
            if e[0] == "lab":
                _, _, _, _, _, lvl, nm, sub = e
                tx, cy = x + 10, yy + h / 2
                for t, f_ in [(lvl, F(13, True)), (nm, F(13)), (f"({sub})", F(11))]:
                    d.text((tx * S, cy * S), t, font=f_, fill="black", anchor="lm"); tx += d.textlength(t, font=f_) / S + 12
        elif e[0] == "box":
            _, x, yy, w, h, nm, sc = e; f, s = STYLE[sc]
            d.rounded_rectangle([x * S, yy * S, (x + w) * S, (yy + h) * S], radius=7 * S, fill=hexc(f), outline=hexc(s), width=S)
            fn = F(11); lns = wrap(nm, fn, w - 12)
            for i, l in enumerate(lns): ctext(x + w / 2, yy + h / 2 + (i - (len(lns) - 1) / 2) * 14, l, fn)
        elif e[0] == "legend":
            _, x, yy = e
            for i, (sc, lab) in enumerate(LEGEND):
                f, s = STYLE[sc]
                d.rounded_rectangle([(x + i * 250) * S, yy * S, (x + i * 250 + 24) * S, (yy + 16) * S], radius=4 * S, fill=hexc(f), outline=hexc(s), width=S)
                d.text(((x + i * 250 + 32) * S, (yy + 8) * S), lab, font=F(10), fill="black", anchor="lm")
        elif e[0] == "title": d.text((e[1] * S, (e[2] + 15) * S), e[3], font=F(15, True), fill="black", anchor="lm")
    img.save(path, dpi=(96 * S, 96 * S))

els, W, H = build(KEYS, TITLE)
open(out + ".drawio", "w", encoding="utf-8").write('<mxfile host="app.diagrams.net">' + diagram(els, "Application landscape", "ins1", W, H) + '</mxfile>')
png(els, W, H, out + ".png")
print({k: len(data[k]) for k in KEYS}, W, H, "aspect h/w %.2f (A4 portrait text area ~1.45)" % (H / W))
