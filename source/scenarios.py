"""The two scenarios, solved: departure order, manoeuvres, and what each
departure needs from the vehicles it leaves behind.

Everything is planned with the moving vehicle's own doors shut - a driver
closes up before pulling away - and with every other vehicle exactly where
the CAD puts it. Where a parked door would be in the way, that is reported
rather than quietly ignored: the answer is "N3 goes once N4 shuts its south
door", not "N3 cannot go".
"""
import os, pickle, math
from shapely.ops import unary_union
from shapely.geometry import box
from wh2 import Flagship as F, Veh, check, FACILITIES
import schemes as S
import planner as PL
import sequence as Q
import audit_paths as AU
from independent import free_to_leave

CACHE = "out/scenarios.pkl"

# the morning: HG3 clears the gate, the north rank comes out deepest last,
# then the diagonal from the west
CLOSING_ORDER = ["HGF1", "HGF2", "HG3", "N4", "N3", "N2", "N1",
                 "D1", "D2", "D3", "D4"]
OPENING_ORDER = ["HGF1", "HGF2", "D1", "D2", "D3", "D4", "N1"]


def shut(vs):
    return [Veh(v.name, v.u, v.v, v.hdg, doors=(), label=v.label, kind=v.kind,
                doors_required=False, note=v.note) for v in vs]


FLEET = {"flagship": "Flagship", "farm": "HG3", "bike": "HGF"}


def doors_in_the_way(v, path, others):
    """Which parked doors this manoeuvre would sweep through. Returns a list
    of (name, side)."""
    swept = []
    for u, w, h in path[::3]:
        x = Veh("_", u, w, h)
        swept.append(x.canopy())
        swept.append(x.module())
    sw = unary_union(swept)
    out = []
    for o in others:
        for side in ("R", "L"):
            if o.door(side).intersects(sw):
                out.append((o.name, side))
    return out


def side_name(v, side):
    """Which way a door faces on the floor, in plain words."""
    a = math.radians(v.hdg + (90.0 if side == "R" else -90.0))
    dx, dy = -math.sin(a), math.cos(a)
    if abs(dy) >= abs(dx):
        return "north" if dy > 0 else "south"
    return "east" if dx > 0 else "west"


def solve_one(s, order):
    ins = S.inside_of(s)
    open_by = {v.name: v for v in ins}
    st = shut(ins)
    o, paths, bad = Q.solve(dict(vehicles=st), prefer=order, verbose=False)
    if o is None:
        raise SystemExit(f"{s['name']}: no way out for {bad}")
    bad, tight = AU.audit(dict(key=s["key"], vehicles=st), o, paths, verbose=False)
    if bad:
        raise SystemExit("\n".join(bad))
    # which parked doors each run passes through, of the vehicles still there
    needs = {}
    goneset = set()
    for nm in o:
        still = [open_by[x] for x in o if x not in goneset and x != nm]
        d = doors_in_the_way(open_by[nm], paths[nm], still)
        if d:
            needs[nm] = d
        goneset.add(nm)
    # and independently: with every door shut, can each one go on its own?
    nfree, stuck, _ = free_to_leave(st)
    return dict(order=o, paths=paths, tight=tight, needs=needs,
                anyorder=(nfree == len(st)), stuck=stuck)


def solve_all(force=False):
    if not force and os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    out = {}
    for f, order in ((S.scheme_closing, CLOSING_ORDER),
                     (S.scheme_opening, OPENING_ORDER)):
        s = f()
        out[s["key"]] = solve_one(s, order)
    os.makedirs("out", exist_ok=True)
    pickle.dump(out, open(CACHE, "wb"))
    return out


if __name__ == "__main__":
    r = solve_all(force=True)
    for f in S.SCENARIOS:
        s = f()
        d = r[s["key"]]
        ins = S.inside_of(s)
        by = {v.name: v for v in ins}
        print("=" * 72)
        print(f"{s['name']}   {len(ins)} inside, "
              f"{len(s['vehicles']) - len(ins)} outside")
        print(f"   order out: {' '.join(d['order'])}")
        print(f"   tightest point on any run: {d['tight']:.0f} mm")
        print(f"   any order with doors shut: "
              f"{'yes' if d['anyorder'] else 'no, ' + ', '.join(d['stuck'])}")
        for nm, ds in d["needs"].items():
            w = ", ".join(f"{o}'s {side_name(by[o], sd)} door" for o, sd in ds)
            print(f"   {nm} needs shut: {w}")
        ok, iss = check(ins, verbose=False)
        for x in iss:
            print("   ", x)


def labels(s, r):
    """The short strings the sheet and the viewer both show."""
    ins = S.inside_of(s)
    n_flag = len([v for v in ins if v.kind == "flagship"])
    n_bike = len([v for v in ins if v.kind == "bike"])
    n_farm = len([v for v in ins if v.kind == "farm"])
    n_out = len(s["vehicles"]) - len(ins)
    other = ("HG3 and two HGF bikes" if n_farm else "two HGF bikes")
    if s["key"] == "open":
        clear = "600 mm, all of it"
        doors = "both, the five Flagships"
        order = "yes, all seven"
        outside = "HG3 and three Flagships"
    else:
        clear = "593 mm at the crates"
        doors = "both, all eight Flagships"
        order = "no, a fixed order"
        outside = "none"
    return dict(doors_label=doors, clear_label=clear, order_label=order,
                inside_label=str(n_flag), other_label=other,
                outside_label=outside,
                tab_label=(f"{n_flag} Flagships, {n_bike} HGF"
                           + (", HG3" if n_farm else "")
                           + (f", {n_out} out" if n_out else "")),
                tight_label=f"{r['tight']:.0f} mm",
                anyorder=(s["key"] == "open"))
