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
from wh2 import (Flagship as F, Farm as Z, Bike as B, HALL, FACILITIES,
                 EQUIP, GATE, east_wall_u, WALL_T)
import schemes as S

SCALE = 84.0
SHEET_W, SHEET_H = 594.0, 364.0
OX, OY = 256.2, 52.0                 # sheet position of site (0, 9120)

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


RUNWAY = True


def building():
    o = []
    t = WALL_T
    outer = Polygon([(-t, -t), (23120 + t * 0.75, -t),
                     (25400 + t * 0.75, 9120 + t), (-t, 9120 + t)])
    o.append(shp(outer, fill="url(#wall)"))
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
    # the runway, outside and west: no boundary in the site model, so it is
    # drawn as the band the four waiting vehicles actually stand on
    if RUNWAY:
        o.append(rect(-19100, 3900, -8300, 9400, fill="#8F8B80", opacity="0.55",
                      stroke="#6E6A5F", stroke_width=0.25, stroke_dasharray="2 1.6"))
        o.append(txt(-13700, 3300,
                     "RUNWAY - OUTSIDE. NO YARD BOUNDARY IN THE SITE MODEL",
                     2.6, C["faint"]))
    # gate
    o.append(rect(-t - 20, GATE[0], 20, GATE[1], fill="#EDEBE5",
                  stroke=C["wall"], stroke_width=0.2))
    o.append(txt(-900, 8300, f"GATE {int(GATE[1]-GATE[0])} x "
                 f"{int(GATE[2])} CLEAR", 2.5, C["ink"], rot=-90))
    return "\n".join(o)


def facilities():
    o = []
    for f in FACILITIES:
        if f.zone:
            o.append(shp(f.poly, fill=C["blue"], opacity="0.10"))
            o.append(shp(f.poly, fill="none", stroke=C["blue"],
                         stroke_width=100 / SCALE))
            continue
        col = "#6E6A5F" if f.h > 1500 else "#9A958A"
        o.append(shp(f.poly, fill=col, stroke=C["wall"], stroke_width=0.2))
    # 600 working strips, drawn as a light green edge
    for f in FACILITIES:
        if f.zone:
            continue
        w = f.clearance()
        if not w.is_empty:
            o.append(shp(w, fill=C["green"], opacity="0.12"))
    LABTEXT = {"shop": "Shop", "shoprig": "Shop kit",
               "checkin": "Check-in / check-out",
               "crates": "Food storage crates"}
    LABPOS = {"office":  (3680, 1780, 0, "#F2F0EA"),
              "shop":    (7634, 1219, -90, "#F2F0EA"),
              "shoprig": (8323, 1120, 0, C["ink"]),
              "checkin": (6160, 8010, 0, C["blue"]),
              "fridge1": (9768, 8620, 0, "#2C2A24"),
              "fridge2": (11676, 8620, 0, "#2C2A24"),
              "fridge3": (13664, 8620, 0, "#2C2A24"),
              "crates":  (18688, 8560, 0, "#2C2A24")}
    for f in FACILITIES:
        x0, y0, x1, y1 = f.poly.bounds
        lu, lv, rot, col = LABPOS.get(f.key, ((x0+x1)/2, (y0+y1)/2, 0, C["ink"]))
        o.append(txt(lu, lv, LABTEXT.get(f.key, f.name).upper(), 2.5, col, rot=rot))
    for key, label, a, b, c, d, h, role in EQUIP:
        fill = "#EDEAE2" if role == "hole" else C["eq"]
        o.append(rect(a, b, c, d, fill=fill, stroke="#20242A",
                      stroke_width=0.18))
    o.append(txt(6160, 8620, "4400 x 1800 ZONE, MARKED ON THE SLAB", 2.2, C["blue"]))

    return "\n".join(o)


def stand(v, show=True):
    o = []
    bay = v.stand_poly(110.0)
    o.append(shp(bay, fill="none", stroke=C["white"], stroke_width=75 / SCALE))
    o.append(shp(v.doors_poly(), fill="url(#hz)", opacity="0.92"))
    a = math.radians(v.hdg)
    ux, uy = -math.sin(a), math.cos(a)
    px, py = -uy, ux
    nu, nv = v.nose()
    hw = (F.X_ROOF if v.kind == "flagship" else v.cls.X_HALF) * 0.68
    o.append(line(nu + px * hw - ux * 25, nv + py * hw - uy * 25,
                  nu - px * hw - ux * 25, nv - py * hw - uy * 25,
                  C["yellow"], 210))
    if v.u > 0 and v.kind == "flagship":
        L = v.cls.LENGTH
        o.append(line(nu - ux * (L + 1400), nv - uy * (L + 1400),
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
    sc = 1.0 if v.kind == "flagship" else 0.5
    bu, bv = nu - ux * 760 * sc, nv - uy * 760 * sc
    o.append(f'<polygon points="{pts([(nu-ux*240*sc, nv-uy*240*sc),(bu+px*320*sc, bv+py*320*sc),(bu-px*320*sc, bv-py*320*sc)])}" fill="#2B2924" opacity="0.85"/>')
    return "\n".join(o)


def label(v):
    a = math.radians(v.hdg)
    ux, uy = -math.sin(a), math.cos(a)
    cu, cv = v.centre()
    w, h, sz = (560, 470, 6.2) if v.kind == "flagship" else (380, 235, 3.4)
    return (shp(box(cu - w, cv - h, cu + w, cv + h), fill="#1B1A16",
                opacity="0.6") +
            txt(cu, cv + h * 0.42, v.label, sz, "#FFFFFF", weight="700"))


def zones(s):
    o = []
    o.append(rect(GATE[0], 0, GATE[1], 900, fill="url(#hz)", opacity="0.95"))
    o.append(rect(15100, 8200, 16300, 9070, fill="url(#fire)", opacity="0.95"))
    o.append(txt(15700, 7980, "FIRE POINT", 2.2, C["red"]))
    o.append(rect(17500, 150, 18700, 1010, fill="url(#fire)", opacity="0.95"))
    o.append(txt(18100, 1250, "PANEL", 2.2, C["red"]))
    o.append(line(8600, 5100, 24000, 5100, C["yellow"], 100))
    o.append(txt(16000, 5400, "DRIVE AISLE - KEEP CLEAR", 2.8, C["yellow"]))
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
    inside = S.inside_of(s)
    o.append(f'<line x1="{x}" y1="{y0-8}" x2="{SHEET_W-30}" y2="{y0-8}" '
             f'stroke="#DCD8CE" stroke-width="0.5"/>')
    n_flag = len([v for v in inside if v.kind == "flagship"])
    n_farm = len([v for v in inside if v.kind == "farm"])
    n_bike = len([v for v in inside if v.kind == "bike"])
    out = len(s["vehicles"]) - len(inside)
    facts = [("Flagships inside", str(n_flag)),
             ("Also inside", s.get("other_label", "")),
             ("Waiting in the runway", s.get("outside_label", "none")),
             ("Doors open in place", s.get("doors_label", "both, every Flagship")),
             ("Diagonal pitch", "3494 mm at 45.2 deg"),
             ("Working clearance", s.get("clear_label", "600 mm")),
             ("Drive aisle", f"{s['aisle']:.0f} mm" if s["aisle"] else "none"),
             ("Any order, nobody moves", s.get("order_label", "no")),
             ("Tightest point driving out", f"{s.get('tight', 0):.0f} mm")]
    cy = y0 + 4
    for k, v in facts:
        o.append(stxt(x, cy, k.upper(), 2.4, C["faint"], ls=0.7))
        o.append(stxt(x + 92, cy, v, 2.9, C["ink"], anchor="end", weight="700"))
        cy += 7.4
    x2 = x + 112
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
    globals()["SHEET_H"] = OY + 9120.0 / SCALE + 26.0 + 186.0
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" '
         f'height="{SHEET_H}mm" viewBox="0 0 {SHEET_W} {SHEET_H}">',
         f'<rect width="{SHEET_W}" height="{SHEET_H}" fill="#FFFFFF"/>', defs()]
    o.append(stxt(30, 16, "HONEYGUIDE GHANA LTD   WH2", 2.8, C["faint"],
                  weight="700", ls=1.6))
    o.append(stxt(30, 30, s["name"].upper().replace(" - ", "  \u00b7  "), 8.0, C["ink"],
                  weight="700"))
    o.append(stxt(30, 38, s["tag"], 3.4, C["faint"]))
    o.append(stxt(SHEET_W - 30, 16, "v0.7.0   9 Sep 2026   1:%d at A2" % int(SCALE),
                  2.5, C["faint"], anchor="end"))
    globals()["RUNWAY"] = any(v.u < 0 for v in s["vehicles"])
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
    a = p(24200, 8600)
    o.append(f'<g transform="translate({a[0]:.2f} {a[1]:.2f})">'
             f'<path d="M0,-5.5 L2.8,3.6 L0,1.8 L-2.8,3.6 Z" fill="{C["ink"]}"/>'
             f'<text y="8" font-size="2.8" font-family="Helvetica, Arial" '
             f'text-anchor="middle" fill="{C["ink"]}">N</text></g>')
    o.append(panel(s, OY + 9120.0 / SCALE + 26.0))
    o.append(stxt(30, SHEET_H - 12,
                  "Geometry read directly from Hardware Designs/Warehouse "
                  "Design V2.3dm and V3.3dm, 9 Sep 2026. Trike positions found from "
                  "each vehicle's own three wheels, HGF from its rear wheel. "
                  "All dimensions in millimetres.", 2.4, C["faint"]))
    o.append("</svg>")
    return "\n".join(o)


META = {
 "close": dict(
   sequence=[
     "Evening. The diagonal fills first, east to west: D4, D3, D2, D1.",
     "Then the north rank, deepest first: N1 against the east wall, then N2, N3, N4.",
     "HG3 comes in last and stands by the gate. It is first out in the morning.",
     "The two HGF bikes ride in and park in the north-west corner, nose east.",
     "Morning is this list read backwards: the bikes, HG3, then N4 to N1, then D1 to D4."],
   notes=[
     "Eleven vehicles inside for the night: eight Flagships, HG3 and the two HGF bikes. This is Warehouse Design V3 exactly as the model has it, not a redesign of it.",
     "The order is fixed, and it has to be. The north rank stands nose to tail with 509 mm between canopies, so it comes out shallowest first; and HG3 parks across the gate, so it moves before anything else can.",
     "The diagonal's doors overlap. At a 3494 mm pitch each door sweeps about 0.63 m2 over the next canopy, and the top 21 mm of the open door sits at canopy height. The leaf itself clears by 55 mm, so it is the upper arm that fouls. Shutting one door lets the neighbour out; dropping that arm 25 mm would let them all stand open.",
     "The two bikes are 572 mm apart and 651 mm across the handlebars, so as drawn the bars overlap by 78 mm. Below bar height they are 97 mm apart and fine. Space them 700 mm, or stagger one 300 mm along the wall.",
     "N4 and HG3 park over 0.9 and 0.6 square metres of the check-in zone, and HG3 stops 101 mm short of the zone's south edge. That costs nothing overnight and everything if anyone works late.",
     "Verified by driving it: all eleven were planned out of the gate against the others still standing, then replayed pose by pose in exact geometry. Tightest point anywhere is 30 mm, on the bike that parks nearest the north wall."]),

 "open": dict(
   sequence=[
     "Morning. HG3 and three Flagships are already out in the runway, doors shut.",
     "Five Flagships stay inside to load: four on the diagonal and N1 against the east wall.",
     "Both doors open on all five, so they load together, then go to check-out.",
     "Any of the seven inside leaves at any time. None of the others has to move.",
     "As they clear, the runway four come in, load, and follow them out."],
   notes=[
     "Five Flagships loading inside, the two HGF bikes in the north-west corner, and four waiting in the runway. This is Warehouse Design V2 exactly as the model has it.",
     "The entry is clear. The diagonal now sits at v = 2318, nearly a metre south of the 8 September row, and nothing stands between the gate and the aisle.",
     "Any order, both doors, seven vehicles inside. Each was planned out of the gate with the other six still standing; tightest point on any of those runs is 60 mm.",
     "One caveat, and it is small: to let D1 out, D2 shuts its north door; D2 needs D3's; D3 needs D4's. D4 and N1 need nothing from anybody. That is one door for a few seconds, not a shuffle.",
     "The runway four keep their doors shut while they are outside. They open them when they come in, which is what Scenario 2 shows."]),
}


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    import scenarios as SC
    R = SC.solve_all()
    base_scale, base_ox = SCALE, OX
    for f in S.SCENARIOS:
        s = f()
        s.update(META[s["key"]])
        s.update(SC.labels(s, R[s["key"]]))
        globals()["SCALE"] = s.get("scale", base_scale)
        globals()["OX"] = s.get("ox", base_ox)
        s["tight"] = R[s["key"]]["tight"]
        fn = f"out/plan_{s['key']}.svg"
        open(fn, "w").write(render(s))
        print("wrote", fn)
