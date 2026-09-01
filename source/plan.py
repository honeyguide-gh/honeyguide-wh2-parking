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
    if s["key"] in ("rank", "rank8"):
        o.append(line(9000, 6186, 24200, 6186, C["yellow"], 100))
        o.append(txt(16800, 6360, "DRIVE AISLE 2934 CLEAR", 2.8, C["yellow"]))
    if s["key"] in ("streets", "two"):
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
    facts = [("Flagships inside", f"{len(inside)}"),
             ("Plus the workshop bay", "1"),
             ("Every vehicle opens", "1 door, in place"),
             ("Street pitch", f"{S.PITCH:.0f} mm"),
             ("Clearance at fittings", "600 mm minimum"),
             ("Walkway between rows" if s["key"] in ("streets", "two")
              else "Drive aisle",
              f"{s['aisle']:.0f} mm" if s["aisle"] else "none"),
             ("Tightest point driving out", f"{s.get('tight', 0):.0f} mm")]
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
    o.append(stxt(SHEET_W - 30, 16, "v0.3.0   31 Aug 2026   1:56 at A2",
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
 "streets": dict(
   sequence=[
     "Street A fills first, east to west, doors north over the weighing zone.",
     "Street B next, doors south over the cold line.",
     "Morning: all of A out west to east, then B out east to west.",
     "B leaves through A's lane, so A has to be clear first. Order is fixed.",
     "The north strip stays clear for weighing and loading all day."],
   notes=[
     "Eight inside plus the workshop bay. Every one of the nine was driven out of the gate in simulation, past everything still parked.",
     "Two streets is the ceiling, not three. A third row can be parked but it cannot be driven out: it would have to thread the 2196 mm lane between street A and the scales, and the vehicle is 2028 mm wide.",
     "There is no drive aisle. Each street is last in, first out, and B cannot leave until the first two of A have gone.",
     "1098 mm of walkway between the two streets, a real gap rather than a painted line.",
     "Each nose tucks 306 mm under the canopy of the vehicle ahead. That is what puts a 4476 mm vehicle on a 4170 mm pitch."]),
 "two": dict(
   sequence=[
     "Street A fills first, east to west, doors north.",
     "Street B next, doors south over the cold line.",
     "Morning: all of A out, then B out east to west through A's lane.",
     "The west seven metres stay clear as the load and unload apron.",
     "Pull any vehicle onto the apron to open both doors."],
   notes=[
     "Seven inside plus the workshop bay, one fewer than Scheme 1, and much easier to live with.",
     "The whole west end of the hall, seven metres of it, stays clear at the gate: room to turn, to stage a load, and to work on a vehicle with both doors open.",
     "Street A is held back to u = 7000 so its lead vehicle has the run it needs to line up on the gate.",
     "Row to row gap is still 1098 mm.",
     "Same two chains as Scheme 1, one link shorter, and the daily order is easier to hold to."]),
 "rank": dict(
   sequence=[
     "Drive in, turn into the aisle, reverse into any free stand.",
     "Any stand can be taken or vacated at any time.",
     "Doors all open east; the end stand opens into free floor.",
     "Weighing and loading runs on the north strip, undisturbed.",
     "Pull a vehicle onto the aisle to open both doors for service."],
   notes=[
     "Four inside plus the workshop bay. The least dense of the four and the only one with genuinely independent access.",
     "A 2934 mm drive aisle runs the length of the hall, so any vehicle can leave or return at any time without moving another.",
     "Stands are at 3232 mm centres, which is what one open door needs: 2068 mm of door plus 1014 mm of neighbour plus 150 mm.",
     "The turn out of a stand into the aisle is the tightest move in any of these schemes. It is a single left hand sweep at the 3158 mm rear axle radius, and it uses the full width of the aisle.",
     "Choose this if vehicles return at scattered times and the fleet stays at four or five."]),
 "rank8": dict(
   sequence=[
     "Stands K1 to K4 fill first, in any order, reversing in off the aisle.",
     "P1 to P3 then stand in the aisle itself, doors north.",
     "G1 goes in last, across the gate line.",
     "Morning: G1 out, then K1 to K4, then P1 to P3 down the aisle.",
     "By nine the aisle is clear and the scheme is Scheme 3 again."],
   notes=[
     "Eight inside plus the workshop bay, which is the same as Scheme 1 but with four stands that stay independent.",
     "K1 to K4 keep their 2934 mm aisle and their nose-in stands. P1 to P3 borrow the aisle overnight, and G1 borrows the gate.",
     "The compromise is the aisle. While P1 to P3 are in it, the rank empties west to east instead of in any order; once they have gone the aisle is a full drive aisle again.",
     "The aisle row sits 150 mm off the noses of the rank and 221 mm off the scales. Paint it and fit wheel stops.",
     "A full length aisle plus a second nose-in row will not fit: the rank is 4476 mm deep and the aisle 2934 mm, which is 7410 mm of the 9120 mm width."]),
}


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    import sequence as Q, audit_paths as AU
    for f in S.SCHEMES:
        s = f()
        s.update(META[s["key"]])
        ex, paths, bad = Q.solve(s, verbose=False)
        _, tight = AU.audit(s, ex, paths, verbose=False)
        s["tight"] = tight
        fn = f"out/plan_{s['key']}.svg"
        open(fn, "w").write(render(s))
        print("wrote", fn)
