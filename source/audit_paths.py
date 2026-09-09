"""Exact check of every planned manoeuvre, in shapely, at 1:1.

The planner works on a 50 mm grid, so this is the authority: it replays each
path pose by pose against the real polygons and reports the tightest point.
"""
import math
from shapely.geometry import box
from shapely.ops import unary_union
from wh2 import Flagship as F, Veh, HALL, FACILITIES, EQUIP, GATE
import planner as PL
DRIVE = PL.DRIVE
FIX = unary_union([PL._solid(100.0)])


def layers(u, v, h, kind="flagship"):
    x = Veh("_", u, v, h, kind=kind, doors_required=False)
    if kind == "flagship":
        return (x.canopy(), x.module(),
                x._p(box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE)))
    b = x.body()
    from shapely.geometry import Polygon as _P
    return (_P(), b, b)


def audit(s, order, paths, verbose=True):
    by = {v.name: v for v in s["vehicles"]}
    gone, bad = set(), []
    worst = 1e9
    for nm in order:
        p = paths[nm]
        still = [by[o] for o in order if o not in gone and o != nm]
        # what each moving band may not touch
        def low_of(x):
            if x.kind == "flagship":
                return x._p(box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE))
            return x.body()
        pc = unary_union([x.canopy() for x in still] +
                         [x.module() for x in still] +
                         [x.doors_poly() for x in still])
        pl = unary_union([x.module() for x in still] + [low_of(x) for x in still])
        blk = {"canopy": unary_union([PL._solid(2222.0), pc]),
               "module": unary_union([PL._solid(764.0), pc, pl]),
               "low": unary_union([PL._solid(100.0), pl])}
        m = 1e9
        kind = by[nm].kind
        for i, (u, v, h) in enumerate(p):
            L = dict(zip(("canopy", "module", "low"), layers(u, v, h, kind)))
            if L["canopy"].is_empty:
                L = {k: g for k, g in L.items() if not g.is_empty}
            for k, g in L.items():
                if g.intersects(blk[k]):
                    bad.append(f"{s['key']} {nm}: {k} fouls at pose {i} "
                               f"u={u:.0f} v={v:.0f}")
                    break
                m = min(m, g.distance(blk[k]))
            else:
                continue
            break
        worst = min(worst, m)
        if verbose:
            print(f"   {nm:4s} {len(p):4d} poses   tightest {m:6.0f} mm")
        gone.add(nm)
    return bad, worst


