"""Any-order access: every vehicle must reach the gate with all the others
still parked, both doors open. Entry is the same path in reverse."""
import time
import planner as PL


def free_to_leave(vehicles, verbose=False):
    """Returns (n_ok, failures, paths)."""
    ok, bad, paths = 0, [], {}
    for v in vehicles:
        others = [x for x in vehicles if x is not v]
        f = PL.Field(others)
        nodes, n = PL.plan((v.u, v.v, v.hdg), f)
        if nodes:
            p = PL.densify(nodes)
            p += PL.run_out(p[-1])
            paths[v.name] = p
            ok += 1
        else:
            bad.append(v.name)
        if verbose:
            print(f"   {v.name:4s} {'out' if nodes else 'STUCK':>5s}  ({n} expansions)")
    return ok, bad, paths


def largest_independent(vehicles, verbose=False):
    """Drop the ones that cannot get out, until everyone left can."""
    keep = list(vehicles)
    while keep:
        ok, bad, paths = free_to_leave(keep, verbose)
        if not bad:
            return keep, paths
        # drop the single worst offender and try again
        keep = [v for v in keep if v.name != bad[0]]
    return [], {}
