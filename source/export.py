"""Export the revised WH2 scene for the 3D viewer.

The manoeuvres come from planner.py, so every path in the viewer is one the
vehicle can actually drive with everything else still parked in its way."""
import json, math, os
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import affinity
from wh2 import (Flagship as F, HALL, WORKSHOP, WORKSHOP_H, WORKSHOP_ROOF,
                 FACILITIES, EQUIP, GATE, east_wall_u, WALL_T, HALL_H)
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
    H(box(150, 8100, 1350, 8970), "fire")
    T(750, 7860, "FIRE", 380, 0, "#C8102E")
    H(box(17500, 150, 18700, 1010), "fire")
    for f in FACILITIES:
        w = f.clearance()
        if not w.is_empty:
            gs = [w] if w.geom_type == "Polygon" else list(w.geoms)
            for g in gs:
                x0, y0, x1, y1 = g.bounds
                R(x0, y0, x1, y1, C["green"], 75)
    R(*FACILITIES[-1].poly.bounds, C["blue"], 110)
    T(8100, 8880, "WEIGHING AND LOADING", 420, 0, C["blue"])
    for v in s["vehicles"]:
        if v.name.startswith("W"):
            continue
        pad = 110.0
        bay = box(-F.X_ROOF - pad, F.Y_ROOF_R - pad, F.X_ROOF + pad,
                  F.Y_NOSE + pad)
        bay = affinity.translate(affinity.rotate(bay, v.hdg, origin=(0, 0)),
                                 v.u, v.v)
        c = list(bay.exterior.coords)
        for i in range(4):
            L(c[i][0], c[i][1], c[i + 1][0], c[i + 1][1], C["white"], 75)
        H(v.doors_poly())
        a = math.radians(v.hdg)
        ux, uy = -math.sin(a), math.cos(a)
        px, py = -uy, ux
        nu, nv = v.nose()
        L(nu + px * 690 - ux * 25, nv + py * 690 - uy * 25,
          nu - px * 690 - ux * 25, nv - py * 690 - uy * 25, C["yellow"], 210)
        L(nu - ux * (F.LENGTH + 1500), nv - uy * (F.LENGTH + 1500),
          nu - ux * 350, nv - uy * 350, C["yellow"], 95)
        T(v.u - ux * (F.Y_BOX_R + 250), v.v - uy * (F.Y_BOX_R + 250),
          v.label, 850, -v.hdg)
    if s["key"] in ("diag", "waves"):
        L(9000, 3900, 23500, 3900, C["yellow"], 100)
    if s["key"] in ("streets", "both"):
        L(8000, 3663, 24000, 3663, C["yellow"], 100)
        L(8000, 4611, 24000, 4611, C["yellow"], 100)
    return m


def build():
    d = dict(
        hall=[list(c) for c in HALL.exterior.coords],
        wall=WALL_T, hall_h=HALL_H,
        gate=list(GATE),
        workshop=dict(b=list(WORKSHOP.bounds), h=WORKSHOP_H, roof=WORKSHOP_ROOF),
        facilities=[dict(key=f.key, name=f.name, b=list(f.poly.bounds), h=f.h)
                    for f in FACILITIES],
        equip=[dict(key=k, name=n, b=[a, b, c, dd], h=h, role=r)
               for k, n, a, b, c, dd, h, r in EQUIP],
        farm={k: getattr(__import__("wh2").Farm, k) for k in
              ("LENGTH", "WIDTH", "HEIGHT", "Y_NOSE", "Y_TAIL", "X_HALF")},
        vehicle={k: getattr(F, k) for k in
                 ("Y_NOSE", "Y_FRONT_AXLE", "Y_ROOF_F", "Y_BOX_F", "Y_DOOR_F",
                  "Y_DOOR_R", "Y_BOX_R", "Y_ROOF_R", "X_ROOF", "X_BOX",
                  "X_FORK", "X_DOOR_OPEN", "X_TRACK", "Z_DOOR_LO", "Z_DOOR_HI",
                  "Z_ROOF_LO", "Z_ROOF_HI", "Z_BOX_TOP", "LENGTH",
                  "WIDTH_CLOSED", "WIDTH_OPEN", "DOOR_LEN")},
        schemes=[])
    import sequence as Q
    for f in S.SCHEMES:
        s = f()
        s.update(P.META[s["key"]])
        inside = [v for v in s["vehicles"] if not v.name.startswith("W")]
        if s["key"] in ("diag", "waves"):
            from independent import free_to_leave
            nfree, bad, paths = free_to_leave(inside)
            if bad:
                raise SystemExit(f"{s['name']}: stuck {bad}")
            ex = [v.name for v in inside]
        else:
            ex, paths, bad = Q.solve(s, verbose=False)
            if ex is None:
                raise SystemExit(f"{s['name']}: no exit for {bad}")
        order = list(reversed(ex))          # arrival is the exit run backwards
        import audit_paths as AU
        bad, tight = AU.audit(s, ex, paths, verbose=False)
        if bad:
            raise SystemExit("\n".join(bad))
        d["schemes"].append(dict(
            key=s["key"], name=s["name"], tag=s["tag"],
            notes=s["notes"], sequence=s["sequence"],
            inside=len(inside), aisle=round(s["aisle"]),
            tight=int(round(tight)),
            lane_name=("Walkway between the rows" if s["key"] in ("streets", "both")
                       else "Drive aisle"),
            anyorder=s["key"] in ("diag", "waves"),
            vehicles=[v.as_dict() for v in s["vehicles"]],
            order=order,
            exit_order=ex,
            paths={k: [(round(a, 1), round(b, 1), round(c, 2)) for a, b, c in p]
                   for k, p in paths.items()},
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
