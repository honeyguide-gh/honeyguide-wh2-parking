"""WH2 parking schemes, v0.4.0.

Against the 2 Sep 2026 save of Warehouse Design.3dm, which carries the farm
vehicle (Zusha cargo-trike v1) as well as the Flagships.

Two constraints arrived from the review, and they are expensive:
  * both doors open on every parked vehicle, so they can all load at once
  * any vehicle in or out in any order, without moving another

Everything here is checked twice: statically by wh2.check (fit, 600 mm working
clearance, doors), then dynamically - a manoeuvre planned out of the gate for
every vehicle with everything else still parked. A layout that cannot be
driven out of is not a layout.
"""
import math
from wh2 import (Flagship as F, Farm as Z, Veh, HALL, FREE, FACILITIES,
                 WORKSHOP, east_wall_u, GATE, check, interlock_pitch)
from search import free_runs

PITCH = interlock_pitch(150.0)               # 4170, nose under the canopy ahead
DPITCH = F.X_DOOR_OPEN + F.X_ROOF + 150.0    # 3232, one door open
BOTH = 2 * F.X_DOOR_OPEN + 150.0             # 4285, both doors, side by side
DIAG_PITCH = 4450.0                          # the verified diagonal
DIAG_HDG = 145.0
DIAG_V = 6400.0

NORTH, SOUTH = "R", "L"
GATE_V = (GATE[0] + GATE[1]) / 2


def street(prefix, v, side, n=None, u_min=None, u_max=None, phase=0.0,
           hdg=90.0, pitch=PITCH):
    runs = [r for r in free_runs(v)
            if (u_min is None or r[1] > u_min) and (u_max is None or r[0] < u_max)]
    if not runs:
        return []
    a, b = max(runs, key=lambda r: r[1] - r[0])
    if u_min is not None: a = max(a, u_min)
    if u_max is not None: b = min(b, u_max)
    a += phase
    k = int((b - a - F.LENGTH) // pitch) + 1
    if n is not None:
        k = min(k, n)
    return [Veh(f"{prefix}{i+1}", a + F.Y_NOSE + i * pitch, v, hdg,
                doors=(side,), label=f"{prefix}{i+1}") for i in range(max(0, k))]


def both_street(prefix, v_axle, u_min, n=3, pitch=PITCH):
    """A street with BOTH doors open. The pitch does not change: a door leaf
    is 1976 mm and the pitch 4170, so the leaves never meet."""
    return [Veh(f"{prefix}{i+1}", u_min + F.Y_NOSE + i * pitch, v_axle, 90.0,
                doors=("R", "L"), label=f"{prefix}{i+1}") for i in range(n)]


def diagonal(prefix="D", n=3, u_east=22300.0, pitch=DIAG_PITCH,
             v_axle=DIAG_V, hdg=DIAG_HDG):
    """The manager's diagonal, at the angle and pitch that survive the check."""
    return [Veh(f"{prefix}{i+1}", u_east - i * pitch, v_axle, hdg,
                doors=("R", "L"), label=f"{prefix}{i+1}") for i in range(n)]


def workshop_bay(farm=False):
    if farm:
        return [Veh("W1", -1799.0, 3600.0, 180.0, doors=(), label="W1",
                    kind="farm", note="workshop bay, the farm vehicle")]
    return [Veh("W1", -1799.0, 3930.0, 180.0, doors=("R", "L"), label="W1",
                note="workshop service bay, both doors open")]


# ==========================================================================
def scheme_diagonal():
    """The review's constraints, met exactly: both doors open on every
    vehicle, and any of them in or out in any order."""
    v = diagonal(n=3)
    return dict(key="diag", name="Scheme 1 - Diagonal Three",
                vehicles=v + workshop_bay(), aisle=2440.0, rows=1,
                tag="Both doors open, any vehicle out at any time")


def scheme_bothstreets():
    """What both doors costs on its own, with order kept as it is today."""
    v = both_street("B", 2574.0, 8850.0, 3) + both_street("A", 6874.0, 10300.0, 3)
    return dict(key="both", name="Scheme 2 - Two Streets, Both Doors",
                vehicles=v + workshop_bay(), aisle=2272.0, rows=2,
                tag="Both doors open, but a fixed order in and out")


def scheme_onedoor():
    """The v0.3.0 answer, kept as the reference point: one door open."""
    v = street("B", 2574.0, SOUTH) + street("A", 5700.0, NORTH, u_min=2700.0)
    return dict(key="streets", name="Scheme 3 - Two Streets, One Door",
                vehicles=v + workshop_bay(), aisle=1098.0, rows=2,
                tag="The densest layout, one door open and a fixed order")


def scheme_waves():
    """Three inside on the diagonal, the rest in the yard, swapped over
    through the morning."""
    v = diagonal(n=3)
    return dict(key="waves", name="Scheme 4 - Three In, Seven Out",
                vehicles=v + workshop_bay(farm=True), aisle=2440.0, rows=1,
                tag="Wave one inside, wave two in the yard, both doors open")



# --------------------------------------------------------------- as drawn
# Read out of Warehouse Design.3dm saved 8 Sep 2026 10:24, by finding every
# vehicle's three wheels: the rear pair 960 apart gives the axle centre, the
# single front wheel 2650 ahead gives the heading. Nothing here is fitted or
# rounded - these are the model's own positions.
AS_DRAWN_INSIDE = [
    ("D1", 10767.1, 3048.7, 45.24),
    ("D2", 14261.2, 3048.7, 45.24),
    ("D3", 17764.8, 3048.7, 45.24),
    ("D4", 21256.0, 3048.7, 45.24),
    ("N1", 22960.7, 6817.5, 90.08),
]
AS_DRAWN_FARM = ("Z1", 4321.1, 4784.6, 90.08)
AS_DRAWN_SHUT = [
    ("W1", -1826.1, 3008.8, 180.00),      # workshop bay
    ("Y1", -10732.2, 5832.4, 0.08),       # the yard, west of the workshop
    ("Y2", -13325.7, 5815.3, 0.08),
    ("Y3", -15864.9, 5838.4, 0.08),
    ("Y4", -18291.7, 5826.1, 0.08),
]


def as_drawn():
    """Michael's 8 Sep layout, exactly as the model has it."""
    v = [Veh(n, u, w, h, doors=("R", "L"), label=n)
         for n, u, w, h in AS_DRAWN_INSIDE]
    n, u, w, h = AS_DRAWN_FARM
    v.append(Veh(n, u, w, h, doors=(), kind="farm", label=n,
                 note="farm vehicle, no doors"))
    v += [Veh(nm, u, w, h, doors=(), label=nm, doors_required=False,
              note="doors shut" + (", workshop bay" if nm == "W1" else ", yard"))
          for nm, u, w, h in AS_DRAWN_SHUT]
    return v


def scheme_asdrawn():
    return dict(key="drawn", name="Scheme 5 - As Drawn, 8 September",
                vehicles=as_drawn(), aisle=2800.0, rows=1, scale=88.0, ox=256.6,
                tag="Michael's Rhino layout: five inside plus the farm vehicle")


SCHEMES = [scheme_diagonal, scheme_bothstreets, scheme_onedoor,
           scheme_waves, scheme_asdrawn]


if __name__ == "__main__":
    import sequence as Q
    from independent import free_to_leave
    print(f"street pitch {PITCH:.0f}   one door {DPITCH:.0f}   both doors {BOTH:.0f}")
    for f in SCHEMES:
        s = f()
        inside = [x for x in s["vehicles"] if not x.name.startswith("W")]
        ok, iss = check(inside, verbose=False)
        n, bad, _ = free_to_leave(inside)
        o, p, _ = Q.solve(dict(vehicles=inside), verbose=False)
        print("=" * 72)
        print(f"{s['name']}   {len(inside)} inside + 1 = {len(inside)+1}")
        print(f"   static {'ok' if ok else 'FAIL'}   any-order {n}/{len(inside)}"
              f"   LIFO order {o}")
        for x in iss:
            if x.startswith("FAIL"):
                print("   ", x)
