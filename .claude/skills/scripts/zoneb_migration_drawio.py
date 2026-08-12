# -*- coding: utf-8 -*-
"""Build the Zone B Orica -> JKTech migration diagram as a Draw.io file.

Source of content: output/DnB_Vendor_Capability_Overlap.html, Zone B (the shared
capability domains). Zones A and C appear only as the two footer blocks.

Scope: surface only. Underground capability is deliberately excluded, which drops
the "Underground production & development design" domain (SHOTPlus(TM) Underground
vs 2DRing / 2DFace) and the BlastIQ(TM) Underground product from the two rows that
carried it. That leaves 11 contested domains, not the source document's 12.

Brand rules applied from .claude/rules/MINRES_Content_Guidelines.html:
  Century Gothic throughout; MinRes Red #CE372F for the title and the red accent
  bar; Dark Teal #00444C for column headers and the Zone A footer; Teal/Wine/Coral
  100-200 shades as band backgrounds; Brown 100 #F1EDE7 for the Zone C block.
Page is A4 landscape (1169 x 826 px at 96dpi) with 30px margins.
"""
from xml.sax.saxutils import escape

CG = "Century Gothic"
cells = []
_id = [1]


def add(value, style, x, y, w, h, parent="1"):
    _id[0] += 1
    cells.append(
        '        <mxCell id="n%d" value="%s" style="%s" vertex="1" parent="%s">\n'
        '          <mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry" />\n'
        '        </mxCell>\n'
        % (_id[0], escape(value, {'"': '&quot;'}), escape(style, {'"': '&quot;'}),
           parent, x, y, w, h))


# ---------------------------------------------------------------- column grid
XA, WA = 30, 222      # capability domain
XB, WB = 256, 248     # move from - Orica
XR, WR = 504, 36      # arrow gutter
XC, WC = 540, 248     # move to - JKTech
XD, WD = 792, 347     # what to check
RIGHT = 1139

# ---------------------------------------------------------------- header
add("", "rounded=0;whiteSpace=wrap;html=1;fillColor=#CE372F;strokeColor=none;", 30, 28, 8, 56)
add("Zone B — Moving surface Drill &amp; Blast software from Orica to JKTech",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=17;fontStyle=1;fontColor=#CE372F;"
    "align=left;verticalAlign=top;" % CG, 50, 25, 720, 26)
add("These 11 contested surface domains are the <b>entire scope</b> of a move — "
    "<b><font color=\"#CE372F\">underground is out of scope.</font></b> Beyond Zone B, 7 domains "
    "stay Orica-only and 4 are JKTech-only additions.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=9;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, 50, 51, 720, 32)
add("Prepared for: <b>Manager Drill &amp; Blast</b><br>"
    "Source: DnB_Vendor_Capability_Overlap — Zone B, surface only<br>"
    "Draft — analyst interpretation, not vendor-confirmed",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontColor=#5C5C5C;align=right;"
    "verticalAlign=top;" % CG, 780, 28, 359, 48)

# ---------------------------------------------------------------- column heads
CH = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#00444C;strokeColor=none;fontFamily=%s;"
      "fontSize=9;fontStyle=1;fontColor=#FFFFFF;align=left;verticalAlign=middle;"
      "spacingLeft=8;" % CG)
add("CAPABILITY DOMAIN", CH, XA, 90, WA, 24)
add("MOVE FROM — Orica today", CH, XB, 90, WB, 24)
add("MOVE TO — JKTech target", CH, XC, 90, WC, 24)
add("WHAT TO CHECK BEFORE YOU MOVE&#160;&#160;&#160;"
    "<font color=\"#B0EDF3\" style=\"font-size:7.5px\">GAIN = better&#160;&#183;&#160;GAP = "
    "something is lost</font>", CH, XD, 90, WD, 24)
add("", "rounded=0;html=1;fillColor=#00444C;strokeColor=none;", XR, 90, WR, 24)

# ---------------------------------------------------------------- row styling
B1 = {"fill": "#E3F2F4", "ink": "#00444C", "bar": "#3F939C"}   # Teal family
B2 = {"fill": "#F4D9DD", "ink": "#8B2E45", "bar": "#8B2E45"}   # Wine family
B3 = {"fill": "#F9E5E3", "ink": "#CE372F", "bar": "#CE372F"}   # Coral family

S_DOM = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D1D1D1;fontFamily=%s;"
         "fontSize=9;fontColor=#00444C;align=left;verticalAlign=middle;spacingLeft=7;"
         "spacingRight=5;" % CG)
S_O = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#E0F7F9;strokeColor=#B0EDF3;fontFamily=%s;"
       "fontSize=9;fontColor=#00444C;align=left;verticalAlign=middle;spacingLeft=7;"
       "spacingRight=6;" % CG)
S_J = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#F9E5E3;strokeColor=#F3C5BF;fontFamily=%s;"
       "fontSize=9;fontColor=#8B2E45;align=left;verticalAlign=middle;spacingLeft=7;"
       "spacingRight=6;" % CG)
S_J3 = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#EFEFEF;strokeColor=#A5A5A5;dashed=1;"
        "fontFamily=%s;fontSize=9;fontColor=#424242;align=left;verticalAlign=middle;"
        "spacingLeft=7;spacingRight=6;" % CG)
S_CHK = ("text;whiteSpace=wrap;html=1;fontFamily=%s;fontSize=8;fontColor=#000000;align=left;"
         "verticalAlign=middle;spacingLeft=6;" % CG)


def dom(name, sub):
    return ("<b>%s</b><br><font color=\"#5C5C5C\" style=\"font-size:7.5px\">%s</font>"
            % (name, sub))


def tag(kind, text):
    if kind == "GAIN":
        return "<b><font color=\"#1D4347\">GAIN</font></b> — " + text
    if kind == "GAP":
        return "<b><font color=\"#CE372F\">GAP</font></b> — " + text
    if kind == "LIC":
        return "<b><font color=\"#8B2E45\">LICENSING</font></b> — " + text
    return text


def band_head(y, label, st):
    add("", "rounded=0;html=1;fillColor=%s;strokeColor=none;" % st["bar"], XA, y, 5, 22)
    add(label,
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;fontFamily=%s;"
        "fontSize=10;fontStyle=1;fontColor=%s;align=left;verticalAlign=middle;spacingLeft=8;"
        % (st["fill"], CG, st["ink"]), XA + 5, y, RIGHT - XA - 5, 22)


def row(y, h, d, s, o, j, chk, st, third=False):
    add(dom(d, s), S_DOM, XA, y, WA, h)
    add(o, S_O, XB, y, WB, h)
    add("", "shape=singleArrow;html=1;direction=east;dy=0.5;dx=13;fillColor=%s;strokeColor=none;"
        % st["bar"], XR + 4, y + h / 2.0 - 9, WR - 8, 18)
    add(j, S_J3 if third else S_J, XC, y, WC, h)
    add(chk, S_CHK, XD, y, WD, h)


RH, GAP = 44, 2

# ---------------------------------------------------------------- wave 1
y = 120
band_head(y, "WAVE 1&#160;&#160;·&#160;&#160;DIRECT SWAP — function is matched on both sides", B1)
y += 24

WAVE1 = [
    ("Surface / bench blast design", "Hole layout, decks, charging, initiation network",
     "SHOTPlus™ Standard&#160;·&#160;Premier&#160;·&#160;Next Gen&#160;·&#160;Design for Outcome",
     "JKSimBlast&#160;·&#160;2DBench",
     ("", "Like-for-like on function. The real difference is neutrality — SHOTPlus™ is built "
          "around Orica's own products.")),
    ("Timing, network &amp; detonation simulation", "Sequence design and on-screen firing",
     "SHOTPlus™ Premier&#160;·&#160;Next Gen SHOTPlus™",
     "2DBench&#160;·&#160;TimeHEx",
     ("GAIN", "TimeHEx adds shock and stress-wave arrival times and detonation interaction. Offset: "
              "Orica's advanced timing is tuned to Orica electronic detonators.")),
    ("Fragmentation prediction", "Predicted size distribution before firing",
     "Next Gen SHOTPlus™&#160;·&#160;Design for Outcome",
     "FragmentO&#160;·&#160;2DBench analyses&#160;·&#160;JKVBOC",
     ("", "JKMRC modelling lineage. Ask which model family each uses and what calibration data it "
          "needs from us.")),
    ("Vibration &amp; airblast prediction", "MIC, PPV, scaled distance",
     "SHOTPlus™ Premier&#160;·&#160;Next Gen SHOTPlus™",
     "2DBench analyses&#160;·&#160;TimeHEx",
     ("GAP", "MIC, PPV and scaled distance are covered; <b>airblast is not documented</b>. Offset: "
             "Orica's Monte Carlo model needs a paid site study first.")),
    ("Mine plan, CAD &amp; survey import", "Where implementations usually stall",
     "Next Gen SHOTPlus™",
     "Design Importer&#160;·&#160;JKSimBlast",
     ("", "Both say “common formats” and neither names them. Get the list from each and test "
          "it against our own exports.")),
    ("Cost &amp; powder factor in the design tool", "Pricing the shot as it is drawn",
     "BlastIQ™ Platform<br><font style=\"font-size:7.5px\">in-tool costing not documented</font>",
     "2DBench analyses&#160;·&#160;StockView",
     ("GAIN", "Volume, tonnage, powder factor and total cost inside the design module — priced "
              "against whichever supplier's catalogue we choose.")),
]
for d, s, o, j, (k, c) in WAVE1:
    row(y, RH, d, s, o, j, tag(k, c), B1)
    y += RH + GAP

# ---------------------------------------------------------------- wave 2
y += 5
band_head(y, "WAVE 2&#160;&#160;·&#160;&#160;THE SWAP LEAVES A GAP YOU MUST CLOSE", B2)
y += 24

WAVE2 = [
    ("Blast data management, records &amp; compliance", "The audit trail and statutory record",
     "BlastIQ™ Platform&#160;·&#160;Insights&#160;·&#160;Quarry&#160;·&#160;"
     "Orica Digital Solutions Platform",
     "JKBMS",
     ("GAP", "JKBMS holds designs and predictions and is positioned for statutory records. Whether "
             "<b>measured field outcomes flow back into it</b> is not stated.", False)),
    ("Field QA/QC of drilling &amp; loading", "Drilled and loaded as designed?",
     "BlastIQ™ Quarry&#160;·&#160;LOADPlus™"
     "<br><font style=\"font-size:7.5px\">captured by Orica's own loading equipment</font>",
     "Blastatistics<br><font style=\"font-size:7.5px\">third party — not JKTech's</font>",
     ("GAP", "JKTech has no field QA/QC layer of its own. Separate vendor, separate licence, separate "
             "support — and the data still comes off Orica equipment.", True)),
    ("3D visualisation", "What engineers and stakeholders see",
     "OREPro™ 3D&#160;·&#160;Next Gen SHOTPlus™",
     "2DView",
     ("GAP", "Source describes “basic” 3D display, v2.x era. Do not assume Vulcan- or "
             "Deswik-grade 3D without seeing it live.", False)),
    ("Mine-to-mill / ROM PSD to plant", "Closing the loop downstream",
     "FRAGTrack™&#160;·&#160;OREPro™ 3D Predict"
     "<br><font style=\"font-size:7.5px\">measured PSD, from real sensors</font>",
     "JK Mine-to-Mill&#160;·&#160;JKToolKit&#160;·&#160;JKVBOC"
     "<br><font style=\"font-size:7.5px\">predicted PSD, comminution research base</font>",
     ("GAP", "We trade measured PSD for modelled PSD. JK Mine-to-Mill may be consulting rather than a "
             "licensable product — confirm.", False)),
]
for d, s, o, j, (k, c, third) in WAVE2:
    row(y, RH, d, s, o, j, tag(k, c), B2, third)
    y += RH + GAP

# ---------------------------------------------------------------- wave 3
y += 5
band_head(y, "WAVE 3&#160;&#160;·&#160;&#160;PROVE IT ON OUR OWN BENCHES FIRST — the one true "
             "head-to-head", B3)
y += 24
row(y, 48, "Blast movement, ore loss &amp; dilution", "Where the ore actually ends up",
    "OREPro™ 3D&#160;·&#160;OREPro™ 3D Predict"
    "<br><font style=\"font-size:7.5px\">Vendor claim: $45.2m additional value over 14 months at one "
    "site</font>",
    "JKVBOC"
    "<br><font style=\"font-size:7.5px\">Value-based rather than grade-only, embedded physics engine, "
    "10–30 minute simulation claimed</font>",
    "<b>The only domain where two named products do the same job.</b> Run both against the same "
    "benches and the same reconciled outcomes before either business case is written.",
    B3)
y += 48 + 10

# ---------------------------------------------------------------- footers
FH = 796 - y

add("", "rounded=0;html=1;fillColor=#00444C;strokeColor=none;", 30, y, 680, FH)
add("DOES NOT MOVE&#160;&#160;·&#160;&#160;ZONE A",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=#B0EDF3;"
    "align=left;verticalAlign=top;" % CG, 42, y + 6, 656, 12)
add("<b>7 domains, 37 Orica products with no JKTech counterpart:</b> electronic &amp; wireless "
    "initiation&#160;·&#160;non-electric initiation &amp; boosters&#160;·&#160;bulk explosive "
    "systems&#160;·&#160;packaged explosives&#160;·&#160;charging and delivery fleet&#160;"
    "·&#160;field measurement and monitoring hardware&#160;·&#160;site circularity.<br>"
    "Whatever we do in software, initiation, explosives and charging stay with an explosives supplier. "
    "And <b>JKTech measures nothing of its own</b> — every prediction above has to be calibrated "
    "off Blastatistics, off Orica's sensors, or off our own data.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontColor=#FFFFFF;align=left;"
    "verticalAlign=top;" % CG, 42, y + 20, 656, FH - 24)

add("", "rounded=0;html=1;fillColor=#F1EDE7;strokeColor=none;", 714, y, 425, FH)
add("", "rounded=0;html=1;fillColor=#CE372F;strokeColor=none;", 714, y, 5, FH)
add("COMES WITH THE MOVE&#160;&#160;·&#160;&#160;ZONE C",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontStyle=1;fontColor=#CE372F;"
    "align=left;verticalAlign=top;" % CG, 728, y + 6, 403, 12)
add("<b>4 domains Orica has no commercial reason to build:</b> multi-supplier explosives catalogue "
    "(StockView — Orica, Enaex, Dyno Nobel)&#160;·&#160;open CSV interoperability "
    "(O-Pitblast, Maptek, Datamine, Minesight)&#160;·&#160;downstream comminution modelling "
    "(JKToolKit, freeware)&#160;·&#160;user-defined units of measurement.",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=8;fontColor=#000000;align=left;"
    "verticalAlign=top;" % CG, 728, y + 20, 403, FH - 24)

add("Mineral Resources Limited&#160;&#160;·&#160;&#160;Zone B migration view&#160;&#160;·&#160;"
    "&#160;Companion to DnB_Vendor_Capability_Overlap, Orica_DnB_Capability_Matrix and "
    "JKTech_DnB_Capability_Matrix",
    "text;html=1;whiteSpace=wrap;fontFamily=%s;fontSize=7;fontColor=#888888;align=left;"
    "verticalAlign=middle;" % CG, 30, 800, 1109, 12)

# ---------------------------------------------------------------- assemble
XML = (
    '<mxfile host="app.diagrams.net" agent="Claude Code" version="24.0.0" type="device">\n'
    '  <diagram name="Zone B - Orica to JKTech" id="zoneB-migration">\n'
    '    <mxGraphModel dx="1169" dy="826" grid="0" gridSize="10" guides="1" tooltips="1" '
    'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="826" '
    'math="0" shadow="0" background="#FFFFFF">\n'
    '      <root>\n'
    '        <mxCell id="0" />\n'
    '        <mxCell id="1" parent="0" />\n'
    + "".join(cells) +
    '      </root>\n'
    '    </mxGraphModel>\n'
    '  </diagram>\n'
    '</mxfile>\n')

if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    dest = os.path.join(root, "output", "DnB_ZoneB_Orica_to_JKTech_Migration.drawio")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(XML)
    print("wrote %s" % dest)
    print("content bottom = %spx of 826 ; %d cells" % (y + FH, _id[0] - 1))
