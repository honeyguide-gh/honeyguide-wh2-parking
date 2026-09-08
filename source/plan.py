"""Marked-up floor plans for the revised WH2 layout, one sheet per scheme.

Colour convention: OSHA 1910.22(b) aisle marking, ANSI Z535.1 safety colours,
normal 5S practice.
  yellow            traffic lanes, lead-in lines            100 mm
  white             vehicle stands, equipment positions      75 mm
  blue              cold chain and staging                   75 mm
  green             pedestrian walkway                       75 mm
  black-yellow 45   door swing, low headroom, keep clear
  red-white 45      fire point and electrical panel
"""
import math, os
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
from shapely import affinity
from wh2 import (Flagship as F, HALL, WORKSHOP, FACILITIES, EQUIP, GATE,
                 east_wall_u, WALL_T)
import schemes as S

SCALE = 56.0
SHEET_W, SHEET_H = 594.0, 420.0
OX, OY = 86.7, 46.0                 # sheet position of site (0, 9120)

C = dict(yellow="#F5C400", white="#FFFFFF", blue="#1F6FB2", green="#2E9B5B",
         red="#C8102E", ink="#141310", faint="#6E6A5E", slab="#8C877B",
         wall="#3A3730", veh="#101010", vehfill="#D9D5CB", eq="#4A5560")


def p(u, v):
    return (OX + u / SCALE, OY + (9120.0 - v) / SCALE)


def pts(coords):
    return " ".join(f"{a:.2f},{b:.2f}" for a, b in (p(x, y) for x, y in coords))


def shp(g, **kw):
    if g.is_empty:
        return ""
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    att = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
    return "\n".join(f'<polygon points="{pts(list(q.exterior.coords))}" {att}/>'
                     for q in gs)


def rect(a, b, c, d, **kw):
    return shp(box(a, b, c, d), **kw)


def line(u0, v0, u1, v1, col, w, dash=None):
    a, b = p(u0, v0), p(u1, v1)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}"'
            f' stroke="{col}" stroke-width="{w/SCALE:.3f}"{d}/>')


def txt(u, v, s, size=2.6, col=C["ink"], rot=0, anchor="middle", weight="600",
        ls=0.0):
    a = p(u, v)
    tr = f' transform="rotate({rot} {a[0]:.2f} {a[1]:.2f})"' if rot else ""
    return (f'<text x="{a[0]:.2f}" y="{a[1]:.2f}" font-size="{size}" '
            f'font-family="Helvetica, Arial, sans-serif" font-weight="{weight}" '
            f'fill="{col}" letter-spacing="{ls}" text-anchor="{anchor}"{tr}>{s}</text>')


def stxt(x, y, s, size=3.0, col=C["ink"], anchor="start", weight="400", ls=0.0):
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
            f'font-family="Helvetica, Arial, sans-serif" font-weight="{weight}" '
            f'fill="{col}" letter-spacing="{ls}" text-anchor="{anchor}">{s}</text>')


def defs():
    return f'''<defs>
 <pattern id="hz" width="3.0" height="3.0" patternTransform="rotate(45)"
          patternUnits="userSpaceOnUse">
  <rect width="3.0" height="3.0" fill="{C['yellow']}"/>
  <rect width="1.5" height="3.0" fill="#111"/></pattern>
 <pattern id="fire" width="3.0" height="3.0" patternTransform="rotate(45)"
          patternUnits="userSpaceOnUse">
  <rect width="3.0" height="3.0" fill="#fff"/>
  <rect width="1.5" height="3.0" fill="{C['red']}"/></pattern>
 <pattern id="wall" width="1.5" height="1.5" patternTransform="rotate(45)"
          patternUnits="userSpaceOnUse">
  <rect width="1.5" height="1.5" fill="#4C4840"/>
  <rect width="0.45" height="1.5" fill="#2A2822"/></pattern>
 <marker id="arw" markerWidth="6" markerHeight="6" refX="5" refY="3"
         orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="{C['yellow']}"/></marker>
</defs>'''


def building():
    o = []
    t = WALL_T
    outer = Polygon([(-t, -t), (23120 + t * 0.75, -t),
                     (25400 + t * 0.75, 9120 + t), (-t, 9120 + t)])
    o.append(shp(outer, fill="url(#wall)"))
    o.append(shp(WORKSHOP.buffer(0), fill="url(#wall)"))
    o.append(shp(WORKSHOP, fill="#7E7A6E"))
    o.append(shp(HALL, fill=C["slab"]))
    for gu in range(3000, 25400, 3000):
        vmax = 9120.0
        if gu > 23120:
            vmax = (gu - 23120) / 2280 * 9120
            o.append(line(gu, vmax, gu, 9120, "#807B70", 55))
        else:
            o.append(line(gu, 0, gu, 9120, "#807B70", 55))
    for gv in range(3000, 9120, 3000):
        o.append(line(0, gv, east_wall_u(gv), gv, "#807B70", 55))
    # gate
    o.append(rect(-t - 20, GATE[0], 20, GATE[1], fill="#EDEBE5",
                  stroke=C["wall"], stroke_width=0.2))
    o.append(txt(-900, 8300, f"GATE {int(GATE[1]-GATE[0])} x "
                 f"{int(GATE[2])} CLEAR", 2.5, C["ink"], rot=-90))
    return "\n".join(o)


def facilities():
    o = []
    for f in FACILITIES:
        if f.key == "weigh":
            o.append(shp(f.poly, fill="none", stroke=C["blue"],
                         stroke_width=100 / SCALE))
            continue
        col = "#6E6A5F" if f.h > 1500 else "#9A958A"
        o.append(shp(f.poly, fill=col, stroke=C["wall"], stroke_width=0.2))
    # 600 working strips, drawn as a light green edge
    for f in FACILITIES:
        w = f.clearance()
        if not w.is_empty:
            o.append(shp(w, fill=C["green"], opacity="0.12"))
    LABPOS = {"weigh": (8100, 8880, 0, C["blue"]),
              "crates": (14966, 430, 0, "#F2F0EA"),
              "office": (3680, 1780, 0, "#F2F0EA"),
              "wash": (12390, 430, 0, "#F2F0EA"),
              "fridge1": (8385, 430, 0, "#2C2A24"),
              "fridge2": (10355, 430, 0, "#2C2A24"),
              "fridge3": (7815, 2370, -90, "#2C2A24")}
    for f in FACILITIES:
        x0, y0, x1, y1 = f.poly.bounds
        lu, lv, rot, col = LABPOS.get(f.key, ((x0+x1)/2, (y0+y1)/2, 0, C["ink"]))
        o.append(txt(lu, lv, f.name.upper(), 2.6, col, rot=rot))
    for key, label, a, b, c, d, h, role in EQUIP:
        fill = "#EDEAE2" if role == "hole" else C["eq"]
        o.append(rect(a, b, c, d, fill=fill, stroke="#20242A",
                      stroke_width=0.18))
    o.append(txt(8100, 7480, "TWO PLATFORM SCALES 900 x 900", 2.4, C["blue"]))

    o.append(txt(-1850, 100, "BENCH 3000 x 600", 2.3, "#F2F0EA"))
    o.append(txt(-3240, 2500, "TOOLS AND PLANT", 2.2, "#F2F0EA", rot=-90))
    o.append(txt(-1799, 5100, "WORKSHOP", 3.0, C["ink"]))
    return "\n".join(o)


def stand(v, show=True):
    o = []
    pad = 110.0
    bay = box(-F.X_ROOF - pad, F.Y_ROOF_R - pad, F.X_ROOF + pad, F.Y_NOSE + pad)
    bay = affinity.translate(affinity.rotate(bay, v.hdg, origin=(0, 0)), v.u, v.v)
    o.append(shp(bay, fill="none", stroke=C["white"], stroke_width=75 / SCALE))
    o.append(shp(v.doors_poly(), fill="url(#hz)", opacity="0.92"))
    a = math.radians(v.hdg)
    ux, uy = -math.sin(a), math.cos(a)
    px, py = -uy, ux
    nu, nv = v.nose()
    o.append(line(nu + px * 690 - ux * 25, nv + py * 690 - uy * 25,
                  nu - px * 690 - ux * 25, nv - py * 690 - uy * 25,
                  C["yellow"], 210))
    o.append(line(nu - ux * (F.LENGTH + 1400), nv - uy * (F.LENGTH + 1400),
                  nu - ux * 350, nv - uy * 350, C["yellow"], 95))
    return "\n".join(o)


def veh_art(v):
    o = [shp(v.body(), fill=C["vehfill"], stroke=C["veh"], stroke_width=0.2,
             opacity="0.94"),
         shp(v.canopy(), fill="#C4BFB3", stroke=C["veh"], stroke_width=0.16),
         shp(v.doors_poly(), fill="none", stroke=C["veh"], stroke_width=0.16,
             stroke_dasharray="1.1 0.8")]
    a = math.radians(v.hdg)
    ux, uy = -math.sin(a), math.cos(a)
    px, py = -uy, ux
    nu, nv = v.nose()
    bu, bv = nu - ux * 760, nv - uy * 760
    o.append(f'<polygon points="{pts([(nu-ux*240, nv-uy*240),(bu+px*320, bv+py*320),(bu-px*320, bv-py*320)])}" fill="#2B2924" opacity="0.85"/>')
    return "\n".join(o)


def label(v):
    a = math.radians(v.hdg)
    ux, uy = -math.sin(a), math.cos(a)
    cu = v.u - ux * (F.Y_BOX_R + 250)
    cv = v.v - uy * (F.Y_BOX_R + 250)
    return (shp(box(cu - 560, cv - 470, cu + 560, cv + 470), fill="#1B1A16",
                opacity="0.6") +
            txt(cu, cv + 210, v.label, 6.2, "#FFFFFF", weight="700"))


def zones(s):
    o = []
    o.append(rect(GATE[0], 0, GATE[1], 900, fill="url(#hz)", opacity="0.95"))
    o.append(rect(150, 8100, 1350, 8970, fill="url(#fire)", opacity="0.95"))
    o.append(txt(750, 7900, "FIRE POINT", 2.2, C["red"]))
    o.append(rect(17500, 150, 18700, 1010, fill="url(#fire)", opacity="0.95"))
    o.append(txt(18100, 1250, "PANEL", 2.2, C["red"]))
    if s["key"] in ("diag", "waves"):
        o.append(line(9000, 3900, 23500, 3900, C["yellow"], 100))
        o.append(txt(16000, 3300, "AISLE 2440 CLEAR", 2.8, C["yellow"]))
    if s["key"] in ("streets", "both"):
        o.append(line(8000, 3663, 24000, 3663, C["yellow"], 100))
        o.append(line(8000, 4611, 24000, 4611, C["yellow"], 100))
        o.append(txt(16000, 4180, "WALKWAY 1098 CLEAR", 2.8, C["yellow"]))
    return "\n".join(o)


def dim_h(u0, u1, v, s, off=0.0):
    a, b = p(u0, v), p(u1, v)
    y = a[1] + off
    return (f'<line x1="{a[0]:.2f}" y1="{y:.2f}" x2="{b[0]:.2f}" y2="{y:.2f}" '
            f'stroke="{C["ink"]}" stroke-width="0.17"/>'
            + "".join(f'<line x1="{q[0]:.2f}" y1="{y-1.3:.2f}" x2="{q[0]:.2f}" '
                      f'y2="{y+1.3:.2f}" stroke="{C["ink"]}" stroke-width="0.17"/>'
                      for q in (a, b))
            + f'<text x="{(a[0]+b[0])/2:.2f}" y="{y-1.0:.2f}" font-size="2.5" '
              f'font-family="Helvetica, Arial, sans-serif" fill="{C["ink"]}" '
              f'text-anchor="middle">{s}</text>')


def dim_v(v0, v1, u, s, off=0.0):
    a, b = p(u, v0), p(u, v1)
    x = a[0] + off
    return (f'<line x1="{x:.2f}" y1="{a[1]:.2f}" x2="{x:.2f}" y2="{b[1]:.2f}" '
            f'stroke="{C["ink"]}" stroke-width="0.17"/>'
            + "".join(f'<line x1="{x-1.3:.2f}" y1="{q[1]:.2f}" x2="{x+1.3:.2f}" '
                      f'y2="{q[1]:.2f}" stroke="{C["ink"]}" stroke-width="0.17"/>'
                      for q in (a, b))
            + f'<text x="{x-1.1:.2f}" y="{(a[1]+b[1])/2:.2f}" font-size="2.5" '
              f'font-family="Helvetica, Arial, sans-serif" fill="{C["ink"]}" '
              f'text-anchor="middle" transform="rotate(-90 {x-1.1:.2f} '
              f'{(a[1]+b[1])/2:.2f})">{s}</text>')


LEGEND = [
    ("hz", "Black / yellow hatch", "Door swing. Keep clear. 1988 mm headroom."),
    ("yellow", "Yellow 100 mm", "Lead-in line and traffic lane edge."),
    ("white", "White 75 mm", "Vehicle stand outline and stand number."),
    ("blue", "Blue 100 mm", "Weighing and loading zone, cold chain."),
    ("green", "Green tint", "600 mm working strip at every fitting."),
    ("fire", "Red / white hatch", "Fire point and electrical panel."),
]


def wrap(t, n):
    w, out, cur = t.split(), [], ""
    for x in w:
        if len(cur) + len(x) + 1 > n:
            out.append(cur); cur = x
        else:
            cur = (cur + " " + x).strip()
    if cur: out.append(cur)
    return out


def panel(s, y0):
    o = []
    x = 30.0
    inside = [v for v in s["vehicles"] if not v.name.startswith("W")]
    o.append(f'<line x1="{x}" y1="{y0-8}" x2="{SHEET_W-30}" y2="{y0-8}" '
             f'stroke="#DCD8CE" stroke-width="0.5"/>')
    n_flag = len([v for v in inside if v.kind != "farm" and v.u > 0])
    n_farm = len([v for v in inside if v.kind == "farm"])
    facts = [("Flagships inside", f"{n_flag}" + (f" + {n_farm} farm" if n_farm else "")),
             ("Plus the workshop bay", "1"),
             ("Every vehicle opens",
              ("both doors, the five inside" if s["key"] == "drawn" else
               "both doors" if any(len(v.doors) == 2 for v in inside)
               else "1 door, in place")),
             ("Street pitch", f"{S.PITCH:.0f} mm"),
             ("Clearance at fittings", "600 mm minimum"),
             ("Walkway between rows" if s["key"] in ("streets", "both")
              else "Drive aisle",
              f"{s['aisle']:.0f} mm" if s["aisle"] else "none"),
             ("Any vehicle, any order",
              "yes" if s["key"] in ("diag", "waves") else
              ("blocked at the gate" if s["key"] == "drawn" else "no, fixed order")),
             ("Tightest point driving out",
              "see notes" if s["key"] == "drawn"
              else f"{s.get('tight', 0):.0f} mm")]
    cy = y0 + 4
    for k, v in facts:
        o.append(stxt(x, cy, k.upper(), 2.4, C["faint"], ls=0.7))
        o.append(stxt(x + 74, cy, v, 3.2, C["ink"], anchor="end", weight="700"))
        cy += 7.4
    x2 = x + 96
    o.append(stxt(x2, y0 + 4, "FLOOR MARKING SCHEDULE", 2.9, C["ink"],
                  weight="700", ls=0.8))
    cy = y0 + 12
    for kind, nm, desc in LEGEND:
        if kind in ("hz", "fire"):
            o.append(f'<rect x="{x2}" y="{cy-3.4}" width="9" height="4.6" '
                     f'fill="url(#{kind})"/>')
        elif kind == "green":
            o.append(f'<rect x="{x2}" y="{cy-3.4}" width="9" height="4.6" '
                     f'fill="{C["green"]}" opacity="0.25" stroke="#CCC" '
                     f'stroke-width="0.2"/>')
        else:
            o.append(f'<rect x="{x2}" y="{cy-3.4}" width="9" height="4.6" '
                     f'fill="{C[kind]}" stroke="#BBB" stroke-width="0.2"/>')
        o.append(stxt(x2 + 13, cy, nm, 2.8, C["ink"], weight="600"))
        o.append(stxt(x2 + 13, cy + 3.7, desc, 2.5, C["faint"]))
        cy += 9.4
    x3 = x2 + 150
    o.append(stxt(x3, y0 + 4, "DAILY SEQUENCE", 2.9, C["ink"], weight="700", ls=0.8))
    cy = y0 + 12
    for i, ln in enumerate(s["sequence"]):
        for j, w in enumerate(wrap(f"{i+1}.  {ln}", 46)):
            o.append(stxt(x3 + (0 if j == 0 else 6), cy, w, 2.6,
                          C["ink"] if j == 0 else C["faint"]))
            cy += 3.9
        cy += 1.4
    x4 = x3 + 132
    o.append(stxt(x4, y0 + 4, "NOTES", 2.9, C["ink"], weight="700", ls=0.8))
    cy = y0 + 12
    for n in s["notes"]:
        for j, w in enumerate(wrap(n, 42)):
            o.append(stxt(x4 + (0 if j == 0 else 4), cy, w, 2.6,
                          C["ink"] if j == 0 else C["faint"]))
            cy += 3.9
        cy += 2.0
    return "\n".join(o)


def render(s):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" '
         f'height="{SHEET_H}mm" viewBox="0 0 {SHEET_W} {SHEET_H}">',
         f'<rect width="{SHEET_W}" height="{SHEET_H}" fill="#FFFFFF"/>', defs()]
    o.append(stxt(30, 16, "HONEYGUIDE GHANA LTD   WH2", 2.8, C["faint"],
                  weight="700", ls=1.6))
    o.append(stxt(30, 30, s["name"].split(" - ")[1].upper(), 8.6, C["ink"],
                  weight="700"))
    o.append(stxt(30, 38, s["tag"], 3.4, C["faint"]))
    o.append(stxt(SHEET_W - 30, 16, "v0.4.0   2 Sep 2026   1:56 at A2",
                  2.5, C["faint"], anchor="end"))
    o.append(building())
    o.append(facilities())
    o.append(zones(s))
    for v in s["vehicles"]:
        o.append(stand(v))
    for v in s["vehicles"]:
        o.append(veh_art(v))
    for v in s["vehicles"]:
        o.append(label(v))
    o.append(dim_h(0, 25400, 9120, "25400 clear at the north wall", off=-6))
    o.append(dim_h(0, 23120, 0, "23120 clear at the south wall", off=8))
    o.append(dim_v(0, 9120, 25400, "9120", off=8))
    o.append(dim_v(-198, 4698, -3398, "4896", off=-6))
    a = p(24200, 8600)
    o.append(f'<g transform="translate({a[0]:.2f} {a[1]:.2f})">'
             f'<path d="M0,-5.5 L2.8,3.6 L0,1.8 L-2.8,3.6 Z" fill="{C["ink"]}"/>'
             f'<text y="8" font-size="2.8" font-family="Helvetica, Arial" '
             f'text-anchor="middle" fill="{C["ink"]}">N</text></g>')
    o.append(panel(s, 232.0))
    o.append(stxt(30, SHEET_H - 12,
                  "Geometry read directly from Hardware Designs/Warehouse "
                  "Design.3dm saved 31 Aug 2026 18:43. All dimensions in "
                  "millimetres.", 2.4, C["faint"]))
    o.append("</svg>")
    return "\n".join(o)


META = {
 "drawn": dict(
   sequence=[
     "Four Flagships on the diagonal at 45 degrees, 3494 mm apart along the row.",
     "A fifth stands nose-west against the east wall, and the farm vehicle west of the crates.",
     "Five more outside: one in the workshop bay and four in the yard, doors shut.",
     "Read straight out of the Rhino model of 8 Sep: every axle centre and heading",
     "comes from the vehicle's own three wheels, nothing fitted or rounded."],
   notes=[
     "Five Flagships inside plus the farm vehicle, ten Flagships in the fleet. This is your layout as the model has it, not a redesign of it.",
     "The gate is blocked. The farm vehicle's body reaches v = 5693 and the gate opening ends at 7650, so 1957 mm is left where a Flagship needs 2028. Move it about 300 mm south and the building works: with it out of the way, all five inside vehicles drive out in any order.",
     "Both doors will not open. At 3494 mm on a 45 degree row each door passes 0.63 m2 into the next vehicle's body; both doors open needs 4600 mm at that angle, which is 1106 mm more per stand. D4 and N1's doors overlap by 0.11 m2 as well.",
     "Three vehicles stand inside a 600 mm working strip: D1 is 359 mm from Fridge 2, D2 is 279 mm from the crate rack, and the farm vehicle is 314 mm from the office. N1's body is 60 mm off the east wall.",
     "The model shows both doors open on the four yard vehicles too. Drawn here with them shut, as instructed."]),

 "diag": dict(
   sequence=[
     "Three stands on the diagonal, at 145 degrees on a 4450 mm pitch.",
     "Both doors open on all three at once. Load them together.",
     "Any of the three leaves at any time. Nobody has to be moved.",
     "Drive in forward, swing left, reverse onto the stand.",
     "The south strip is the aisle. Keep it clear."],
   notes=[
     "Three inside plus the workshop bay. This is the review's two constraints met exactly, and it is the most the shed will take with them.",
     "Four is not tight, it is impossible. The stand band is 14.9 m once the office, the third fridge and its working strip come off, and the closest two both-doors-open vehicles can ever be, at any angle, is 3950 mm. Four stands need 15.8 m.",
     "The diagonal is the right instinct: staggered 3650 mm along their axis, two vehicles with both doors open sit only 2200 mm apart across. That is the tightest packing there is.",
     "Every stand was driven out of the gate in simulation with the other two still standing, doors open. Tightest point on any of those runs is 45 mm.",
     "If the fleet grows past three inside, the loading formation has to move to the yard. See Scheme 4."]),
 "both": dict(
   sequence=[
     "Street A fills first, east to west, then street B.",
     "Both doors open on all six. Load them together.",
     "Morning: A1, A2, A3, then B3, B2, B1. That order is fixed.",
     "A vehicle that returns early cannot take its stand out of turn.",
     "The middle strip stays clear as the walkway."],
   notes=[
     "Six inside plus the workshop bay: what both doors open costs when the order stays as it is today.",
     "Both doors open changes nothing nose to tail. A door leaf is 1976 mm and the street pitch is 4170, so the leaves never meet. The cost is sideways: two rows now need 4300 mm between them instead of 3232.",
     "The price is the morning juggling the review wants rid of. Six vehicles, one fixed order, and nobody can leave out of turn.",
     "Driven and verified: the whole departure runs A1 through B1 with a tightest point of 41 mm.",
     "Take this only if loading all six at once matters more than the order they leave in."]),
 "streets": dict(
   sequence=[
     "Street A fills first, east to west, doors north over the weighing zone.",
     "Street B next, doors south over the cold line.",
     "Morning: all of A out west to east, then B out east to west.",
     "B leaves through A's lane, so A has to be clear first.",
     "The north strip stays clear for weighing and loading all day."],
   notes=[
     "Eight inside plus the workshop bay. The densest layout there is, and the reference point for what the two new constraints cost.",
     "One door open on each vehicle, and a fixed order in and out. Both of the review's constraints are broken here.",
     "Kept in the set because the difference is the whole decision: eight with one door and a fixed order, three with both doors and any order.",
     "1098 mm of walkway between the two streets, a real gap rather than a painted line.",
     "Each nose tucks 306 mm under the canopy of the vehicle ahead, which is what puts a 4476 mm vehicle on a 4170 mm pitch."]),
 "waves": dict(
   sequence=[
     "Overnight: three Flagships inside on the diagonal, the farm vehicle in the workshop bay.",
     "The other seven stand in the yard, west of the workshop, both doors open.",
     "Morning: the three inside load and leave, in any order.",
     "Three from the yard come in and take the empty stands.",
     "Repeat. Bring the second shift of operators in as the first leaves."],
   notes=[
     "Three inside plus the farm vehicle in the workshop bay, and seven in the yard: ten vehicles, both doors open on all of them, none of them blocking another.",
     "The yard is where this scheme lives or dies. Seven stands abreast with both doors open need 4285 mm of frontage each, so 30 m in one rank, or about 15 x 17 m as two ranks of four facing one aisle.",
     "The site model does not carry a yard boundary, so those figures are what the formation needs, not what the yard has. Chalk it out before committing.",
     "The turnover is the point: three go, three replace them, and the shed never has more than three loading at once. That is the constraint, not a choice.",
     "The farm vehicle is 4373 x 1813 x 1953 with no doors, so it parks in the workshop bay without a swing to allow for."]),
}


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    import sequence as Q, audit_paths as AU
    base_scale, base_ox = SCALE, OX
    for f in S.SCHEMES:
        s = f()
        s.update(META[s["key"]])
        globals()["SCALE"] = s.get("scale", base_scale)
        globals()["OX"] = s.get("ox", base_ox)
        inside = [v for v in s["vehicles"] if not v.name.startswith("W")]
        if s["key"] == "drawn":
            paths, ex = {}, []
            s["tight"] = 0
        elif s["key"] in ("diag", "waves"):
            from independent import free_to_leave
            _, _, paths = free_to_leave(inside)
            ex = [v.name for v in inside]
        else:
            ex, paths, bad = Q.solve(s, verbose=False)
        if ex:
            _, tight = AU.audit(s, ex, paths, verbose=False)
            s["tight"] = tight
        fn = f"out/plan_{s['key']}.svg"
        open(fn, "w").write(render(s))
        print("wrote", fn)
