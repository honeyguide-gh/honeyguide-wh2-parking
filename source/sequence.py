"""Work out a drivable exit order and the manoeuvre for every vehicle."""
import math, time
from shapely.ops import unary_union
import planner as P
from wh2 import Flagship as F


def solve(scheme, prefer=None, verbose=True):
    """Greedy: at each step take the first vehicle in the preferred order that
    can actually drive out past everything still parked."""
    inside = [v for v in scheme["vehicles"] if not v.name.startswith("W")]
    by = {v.name: v for v in inside}
    if prefer is None:
        # the order a yard would actually use: the gate stand, then the row
        # nearest the gate, then the back row, each west to east
        rankfirst = {"G": 0, "A": 1, "B": 2, "K": 3, "P": 4}
        prefer = [v.name for v in sorted(
            inside, key=lambda v: (rankfirst.get(v.label[0], 9), v.u))]
    left = list(prefer)
    order, paths = [], {}
    while left:
        got = None
        for nm in left:
            v = by[nm]
            still = [by[o] for o in left if o != nm]
            f = P.Field(still)
            nodes, n = P.plan((v.u, v.v, v.hdg), f)
            if nodes:
                got = (nm, nodes, n)
                break
        if not got:
            if verbose:
                print("   NO EXIT for", left)
            return None, None, left
        nm, nodes, n = got
        p = P.densify(nodes)
        p += P.run_out(p[-1])
        paths[nm] = p
        order.append(nm)
        left.remove(nm)
        if verbose:
            print(f"   {nm:4s} out in {len(nodes)} moves, {len(p)} poses "
                  f"({n} expansions)")
    return order, paths, []
