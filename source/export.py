"""Export the revised WH2 scene for the 3D viewer.

The manoeuvres come from planner.py, so every path in the viewer is one the
vehicle can actually drive with everything else still parked in its way."""
import json, math, os
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import affinity
from wh2 import (Flagship as F, Farm as Z, Bike as Bk, HALL, FACILITIES,
                 FAC, EQUIP, GATE, east_wall_u, WALL_T, HALL_H)
import schemes as S
import plan as P


# ------------------------------------------------------------------- marks
def marks(s):
    m = []
    C = P.C

    def L(a, b, c, d, col, w):
        m.append(dict(t="l", a=[a, b, c, d], c=col, w=w))

    def R(a, b, c, d, col, w):
        m.append(dict(t="r", a=[a, b, c, d], c=col, w=w))

    def H(poly, kind="hz"):
        gs = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
        for g in gs:
            m.append(dict(t="h", k=kind,
                          a=[[round(x, 1), round(y, 1)] for x, y in g.exterior.coords]))

    def T(u, v, s_, size, rot=0, col="#FFFFFF"):
        m.append(dict(t="t", a=[u, v], s=s_, z=size, r=rot, c=col))

    H(box(GATE[0], 0, GATE[1], 900))
    H(box(15100, 8200, 16300, 9070), "fire")
    T(15700, 7960, "FIRE", 360, 0, "#C8102E")
    H(box(17500, 150, 18700, 1010), "fire")
    for f in FACILITIES:
        if f.zone:
            continue
        w = f.clearance()
        if not w.is_empty:
            gs = [w] if w.geom_type == "Polygon" else list(w.geoms)
            for g in gs:
                x0, y0, x1, y1 = g.bounds
                R(x0, y0, x1, y1, C["green"], 75)
    R(*FAC["checkin"].poly.bounds, C["blue"], 110)
    T(6160, 8600, "CHECK-IN / CHECK-OUT", 430, 0, C["blue"])
    for v in s["vehicles"]:
        if v.u < 0:
            continue
        c = list(v.stand_poly(110.0).exterior.coords)
        for i in range(4):
            L(c[i][0], c[i][1], c[i + 1][0], c[i + 1][1], C["white"], 75)
        H(v.doors_poly())
        a = math.radians(v.hdg)
        ux, uy = -math.sin(a), math.cos(a)
        px, py = -uy, ux
        nu, nv = v.nose()
        hw = (F.X_ROOF if v.kind == "flagship" else v.cls.X_HALF) * 0.68
        L(nu + px * hw - ux * 25, nv + py * hw - uy * 25,
          nu - px * hw - ux * 25, nv - py * hw - uy * 25, C["yellow"], 210)
        if v.kind == "flagship":
            L(nu - ux * (F.LENGTH + 1500), nv - uy * (F.LENGTH + 1500),
              nu - ux * 350, nv - uy * 350, C["yellow"], 95)
        cu, cv = v.centre()
        T(cu, cv, v.label, 850 if v.kind == "flagship" else 520, -v.hdg)
    L(8600, 5100, 24000, 5100, C["yellow"], 100)
    return m


def build():
    import scenarios as SC
    R = SC.solve_all()
    d = dict(
        hall=[list(c) for c in HALL.exterior.coords],
        wall=WALL_T, hall_h=HALL_H,
        gate=list(GATE),
        facilities=[dict(key=f.key, name=f.name, b=list(f.poly.bounds), h=f.h)
                    for f in FACILITIES],
        equip=[dict(key=k, name=n, b=[a, b, c, dd], h=h, role=r)
               for k, n, a, b, c, dd, h, r in EQUIP],
        farm={k: getattr(Z, k) for k in
              ("LENGTH", "WIDTH", "HEIGHT", "Y_NOSE", "Y_TAIL", "X_HALF")},
        bike={k: getattr(Bk, k) for k in
              ("LENGTH", "WIDTH", "BARS", "HEIGHT", "Y_NOSE", "Y_TAIL",
               "X_HALF", "BAR_HALF", "WHEELBASE")},
        vehicle={k: getattr(F, k) for k in
                 ("Y_NOSE", "Y_FRONT_AXLE", "Y_ROOF_F", "Y_BOX_F", "Y_DOOR_F",
                  "Y_DOOR_R", "Y_BOX_R", "Y_ROOF_R", "X_ROOF", "X_BOX",
                  "X_FORK", "X_DOOR_OPEN", "X_TRACK", "Z_DOOR_LO", "Z_DOOR_HI",
                  "Z_ROOF_LO", "Z_ROOF_HI", "Z_BOX_TOP", "LENGTH",
                  "WIDTH_CLOSED", "WIDTH_OPEN", "DOOR_LEN")},
        schemes=[])
    for f in S.SCENARIOS:
        s = f()
        s.update(P.META[s["key"]])
        r = R[s["key"]]
        s.update(SC.labels(s, r))
        ins = S.inside_of(s)
        by = {v.name: v for v in ins}
        ex = r["order"]
        needs = {nm: [[o, sd, SC.side_name(by[o], sd)] for o, sd in v]
                 for nm, v in r["needs"].items()}
        d["schemes"].append(dict(
            key=s["key"], name=s["name"], tag=s["tag"],
            notes=s["notes"], sequence=s["sequence"],
            inside=len(ins), outside=len(s["vehicles"]) - len(ins),
            aisle=round(s["aisle"]),
            tight=int(round(r["tight"])),
            anyorder=s["anyorder"],
            inside_label=s["inside_label"],
            other_label=s["other_label"],
            outside_label=s["outside_label"],
            tab_label=s["tab_label"],
            doors_label=s["doors_label"],
            order_label=s["order_label"],
            clear_label=s["clear_label"],
            tight_label=s["tight_label"],
            needs=needs,
            vehicles=[v.as_dict() for v in s["vehicles"]],
            order=list(reversed(ex)),
            exit_order=ex,
            paths={k: [(round(a, 1), round(b, 1), round(c, 2)) for a, b, c in p_]
                   for k, p_ in r["paths"].items()},
            marks=marks(s)))
    return d


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    d = build()
    js = json.dumps(d, separators=(",", ":"))
    open("out/scene.json", "w").write(js)
    print(f"scene.json {len(js)/1024:.0f} kB")
    for s in d["schemes"]:
        print(f"  {s['name']:30s} {s['inside']} inside, {len(s['marks'])} marks")
