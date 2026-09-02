"""Place a single angled row of both-doors-open stands and count them."""
import math
import numpy as np
from shapely.ops import unary_union
from wh2 import (Flagship as F, Veh, HALL, FACILITIES, TALL, GATE)
from rowsearch import min_pitch

WORK = unary_union([f.clearance() for f in FACILITIES])
SOLID = unary_union([f.poly for f in FACILITIES])
INNER = HALL.buffer(-150.0 + 1)


def ok(v):
    """One stand, both doors open, against the building and the fittings."""
    b = v.body()
    if not HALL.contains(b) or not INNER.contains(b):
        return False
    if b.intersects(SOLID) or b.intersects(WORK.buffer(-1.0)):
        return False
    d = v.doors_poly()
    if not HALL.contains(d):          # a door may not pass through a wall
        return False
    if d.intersects(TALL):            # nor over the office
        return False
    return True


def row(h, v_axle, pitch, u0=25000.0, n_max=12):
    """Stands from the east end westward at this heading and v."""
    out = []
    u = u0
    while u > -2000 and len(out) < n_max:
        cand = Veh(f"D{len(out)+1}", u, v_axle, h, doors=("R", "L"))
        if ok(cand):
            out.append(cand)
            u -= pitch
        else:
            u -= 100.0
    return out


if __name__ == "__main__":
    best = []
    for h in np.arange(0, 181, 5.0):
        p = min_pitch(h % 90 if h % 90 else 90.0)
        if p is None:
            continue
        for v_axle in np.arange(1000, 8200, 200.0):
            r = row(h, v_axle, p)
            if r:
                best.append((len(r), h, v_axle, p, r))
    best.sort(key=lambda x: (-x[0], x[3]))
    seen = set()
    print(f"{'n':>2} {'hdg':>6} {'v_axle':>7} {'pitch':>6}   stand u values")
    for n, h, v, p, r in best:
        k = (n, round(h))
        if k in seen:
            continue
        seen.add(k)
        print(f"{n:2d} {h:6.1f} {v:7.0f} {p:6.0f}   "
              + " ".join(f"{x.u:.0f}" for x in r))
        if len(seen) > 14:
            break
