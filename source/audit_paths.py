"""Exact check of every planned manoeuvre, in shapely, at 1:1.

The planner works on a 50 mm grid, so this is the authority: it replays each
path pose by pose against the real polygons and reports the tightest point.
"""
import math
from shapely.geometry import box
from shapely.ops import unary_union
from wh2 import Flagship as F, Veh, HALL, FACILITIES, EQUIP, GATE
import planner as PL
import schemes as S
import sequence as Q

DRIVE = PL.DRIVE
FIX = unary_union([PL._solid(100.0)])


def layers(u, v, h):
    x = Veh("_", u, v, h)
    return (x.canopy(), x.module(),
            x._p(box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE)))


def audit(s, order, paths, verbose=True):
    inside = [v for v in s["vehicles"] if not v.name.startswith("W")]
    by = {v.name: v for v in inside}
    gone, bad = set(), []
    worst = 1e9
    for nm in order:
        p = paths[nm]
        still = [by[o] for o in order if o not in gone and o != nm]
        # what each moving band may not touch
        pc = unary_union([x.canopy() for x in still] +
                         [x.module() for x in still] +
                         [x.doors_poly() for x in still])
        pl = unary_union([x.module() for x in still] +
                         [x._p(box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE))
                          for x in still])
        blk = {"canopy": unary_union([PL._solid(2222.0), pc]),
               "module": unary_union([PL._solid(764.0), pc, pl]),
               "low": unary_union([PL._solid(100.0), pl])}
        m = 1e9
        for i, (u, v, h) in enumerate(p):
            L = dict(zip(("canopy", "module", "low"), layers(u, v, h)))
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


if __name__ == "__main__":
    allbad = []
    for f in S.SCHEMES:
        s = f()
        print("=" * 70)
        print(s["name"])
        o, p, _ = Q.solve(s, verbose=False)
        b, w = audit(s, o, p)
        print(f"   tightest anywhere in the scheme: {w:.0f} mm")
        allbad += b
    print("=" * 70)
    print("ALL PATHS CLEAN" if not allbad else "\n".join(allbad))
