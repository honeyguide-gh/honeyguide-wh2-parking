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
    LABTEXT = {"shop": "Shop", "shoprig": "Shop kit",
               "checkin": "Check-in / check-out",
               "crates": "Food storage crates"}
    LABPOS = {"office":  (3680, 1780, 0, "#F2F0EA"),
              "shop":    (7634, 1219, -90, "#F2F0EA"),
              "shoprig": (8323, 1120, 0, C["ink"]),
              "checkin": (2220, 8600, 0, "#F2F0EA"),
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
    o.append(txt(2220, 7620, "TWO STATIONS, PLATFORM SCALE EACH", 2.3, C["blue"]))

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
    o.append(rect(3900, 8200, 5100, 9070, fill="url(#fire)", opacity="0.95"))
    o.append(txt(4500, 7980, "FIRE POINT", 2.2, C["red"]))
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
    n_flag = len([v for v in inside if v.kind != "farm"])
    n_farm = len([v for v in inside if v.kind == "farm"])
    out = len(s["vehicles"]) - len(inside)
    facts = [("Flagships inside", str(n_flag)),
             ("HG3, the cargo vehicle", "inside" if n_farm else "in the runway"),
             ("Waiting in the runway", str(out) if out else "none"),
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
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" '
         f'height="{SHEET_H}mm" viewBox="0 0 {SHEET_W} {SHEET_H}">',
         f'<rect width="{SHEET_W}" height="{SHEET_H}" fill="#FFFFFF"/>', defs()]
    o.append(stxt(30, 16, "HONEYGUIDE GHANA LTD   WH2", 2.8, C["faint"],
                  weight="700", ls=1.6))
    o.append(stxt(30, 30, s["name"].upper().replace(" - ", "  \u00b7  "), 8.0, C["ink"],
                  weight="700"))
    o.append(stxt(30, 38, s["tag"], 3.4, C["faint"]))
    o.append(stxt(SHEET_W - 30, 16, "v0.6.0   9 Sep 2026   1:88 at A2",
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
    o.append(dim_v(-198, 4698, -3398, "4896", off=-6))
    a = p(24200, 8600)
    o.append(f'<g transform="translate({a[0]:.2f} {a[1]:.2f})">'
             f'<path d="M0,-5.5 L2.8,3.6 L0,1.8 L-2.8,3.6 Z" fill="{C["ink"]}"/>'
             f'<text y="8" font-size="2.8" font-family="Helvetica, Arial" '
             f'text-anchor="middle" fill="{C["ink"]}">N</text></g>')
    o.append(panel(s, 196.0))
    o.append(stxt(30, SHEET_H - 12,
                  "Geometry read directly from Hardware Designs/Warehouse "
                  "Design V2.3dm and V3.3dm, 9 Sep 2026. Vehicle positions found "
                  "from each vehicle's own three wheels. All dimensions in millimetres.", 2.4, C["faint"]))
    o.append("</svg>")
    return "\n".join(o)


META = {
 "close": dict(
   sequence=[
     "Evening. The diagonal fills first, east to west: D4, D3, D2, D1.",
     "Then the north rank, deepest first: N1 against the east wall, then N2, N3, N4.",
     "HG3 comes in last and stands by the gate. It is first out in the morning.",
     "Both doors open on all eight Flagships once they are in. HG3 has none.",
     "Morning is this list read backwards: HG3 out, then N4, N3, N2, N1, then D1 to D4."],
   notes=[
     "Nine vehicles inside for the night: eight Flagships and HG3. This is Warehouse Design V3 exactly as the model has it, not a redesign of it.",
     "The order is fixed, and it has to be. The north rank stands nose to tail with 508 mm between canopies, so it comes out shallowest first; and HG3 parks across the gate, so it moves before anything else can.",
     "The diagonal's doors overlap. At a 3494 mm pitch each door sweeps about 0.63 m2 over the next canopy, and the top 21 mm of the open door sits at canopy height. The leaf itself clears by 55 mm - it is the upper arm that fouls. Shutting one door lets the neighbour out; dropping that arm 25 mm would let them all stand open.",
     "Two clearances are short. HG3 stops 101 mm from the check-in desk, so check-in is unusable while it is parked there, and the north rank leaves 593 mm in front of the crates where 600 is wanted. The fridges are fine at 723 to 807 mm.",
     "Verified by driving it: every one of the nine was planned out of the gate against the others still standing, then replayed pose by pose in exact geometry. Tightest point anywhere is 60 mm."]),

 "open": dict(
   sequence=[
     "Morning. HG3 and three Flagships are already out in the runway, doors shut.",
     "Five stay inside to load: four on the diagonal and N1 against the east wall.",
     "Both doors open on all five, so they load together, then go to check-out.",
     "Any of the five leaves at any time - none of the other four has to move.",
     "As they clear, the runway four come in, load, and follow them out."],
   notes=[
     "Five loading inside, four waiting in the runway. This is Warehouse Design V2 exactly as the model has it.",
     "The entry is clear. The diagonal now sits at v = 2318, nearly a metre south of the 8 September row, and nothing stands between the gate and the aisle.",
     "Any order, both doors, five vehicles. Each of the five was planned out of the gate with the other four still standing; tightest point on any of those runs is 60 mm.",
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
