"""Four parking schemes for WH2, against the 31 Aug 2026 model.

Every scheme is checked twice: statically by wh2.check (fit, 600 mm working
clearance, one door open on every vehicle) and dynamically by sequence.solve,
which plans a real manoeuvre out of the gate for each vehicle in turn with
everything still parked in its way.  A layout that cannot be driven out of is
not a layout, so nothing here is quoted until it passes both.
"""
import math
from wh2 import (Flagship as F, Veh, HALL, FREE, FACILITIES, WORKSHOP,
                 east_wall_u, GATE, check, interlock_pitch)
from search import free_runs

PITCH = interlock_pitch(150.0)               # 4170, nose under the canopy ahead
DPITCH = F.X_DOOR_OPEN + F.X_ROOF + 150.0    # 3232, side by side, one door open

# hdg 90 puts the nose to the west, so the vehicle's right hand side is NORTH
NORTH, SOUTH = "R", "L"
GATE_V = (GATE[0] + GATE[1]) / 2             # 6275, the gate centre line


def street(prefix, v, side, n=None, u_min=None, u_max=None, phase=0.0,
           hdg=90.0, pitch=PITCH):
    """A street: vehicles nose to tail at v, each nose tucked under the canopy
    of the one ahead. Placed inside the free run for that v."""
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


def rank(prefix, v_axle, u_first, n, side, hdg=0.0, pitch=DPITCH):
    """Nose-in stands side by side, all opening the same way."""
    return [Veh(f"{prefix}{i+1}", u_first + i * pitch, v_axle, hdg,
                doors=(side,), label=f"{prefix}{i+1}") for i in range(n)]


def gate_stand():
    """One vehicle on the gate line: last in at night, first out in the
    morning, and it does not block anything else while it stands there."""
    return [Veh("G1", 3078.0, GATE_V, 90.0, doors=(NORTH,), label="G1",
                note="gate stand, last in and first out")]


def workshop_bay():
    return [Veh("W1", -1799.0, 3930.0, 180.0, doors=("R", "L"), label="W1",
                note="workshop service bay, both doors open")]


# the two rows the building actually allows:
#   B at 2574, doors south over the cold line   (body 1560 to 3588)
#   A at 5700, doors north over the weighing zone (body 4686 to 6714)
# 1098 mm of walkway between them, and the north strip left as the lane.
V_B, V_A = 2574.0, 5700.0
V_AXLE = 1560.0 - F.Y_ROOF_R                 # rank tail on the 1560 line
V_AISLE = 6960.0                             # a vehicle standing in the aisle


# ==========================================================================
def scheme_streets():
    """Maximum capacity: two full streets, strict LIFO, north strip free."""
    v = street("B", V_B, SOUTH) + street("A", V_A, NORTH, u_min=2700.0)
    return dict(key="streets", name="Scheme 1 - Two Streets",
                vehicles=v + workshop_bay(), aisle=1098.0, rows=2,
                tag="Every metre of floor used, strict order in and out")


def scheme_two():
    """Balanced: the same two streets held back east, so the whole west end
    of the hall stays clear as the load and unload apron."""
    v = street("B", V_B, SOUTH) + street("A", V_A, NORTH, u_min=7000.0)
    return dict(key="two", name="Scheme 2 - Two Streets and a Staging Apron",
                vehicles=v + workshop_bay(), aisle=1098.0, rows=2,
                tag="One fewer vehicle, seven metres of clear apron at the gate")


def scheme_rank():
    """Independent access: nose-in stands off a full 2934 mm drive aisle."""
    v = rank("K", V_AXLE, 9834.0, 4, "R", hdg=0.0)
    return dict(key="rank", name="Scheme 3 - Rank and Aisle",
                vehicles=v + workshop_bay(), aisle=2934.0, rows=1,
                tag="Every stand reached without moving another vehicle")


def scheme_rank8():
    """The rank at full capacity: the four stands keep their aisle, and the
    aisle itself is used as a LIFO street overnight, plus the gate stand."""
    v = rank("K", V_AXLE, 9834.0, 4, "R", hdg=0.0)
    v += [Veh(f"P{i+1}", 13228.0 + i * PITCH, V_AISLE, 90.0, doors=(NORTH,),
              label=f"P{i+1}", note="stands in the aisle overnight")
          for i in range(3)]
    v += gate_stand()
    return dict(key="rank8", name="Scheme 4 - Rank, Aisle and Apron",
                vehicles=v + workshop_bay(), aisle=2934.0, rows=1,
                tag="Four independent stands, and the aisle itself parked overnight")


SCHEMES = [scheme_streets, scheme_two, scheme_rank, scheme_rank8]


def report(s):
    inside = [x for x in s["vehicles"] if not x.name.startswith("W")]
    print("=" * 72)
    print(f"{s['name']}   {len(inside)} inside + 1 workshop = {len(inside)+1}")
    ok, iss = check(inside)
    print("   " + ("VALID" if ok else "INVALID"))
    return ok


if __name__ == "__main__":
    import sequence as Q
    print(f"street pitch {PITCH:.0f}   rank pitch {DPITCH:.0f}")
    for f in SCHEMES:
        s = f()
        report(s)
        o, p, bad = Q.solve(s, verbose=False)
        print(f"   drivable: {'yes' if o else 'NO ' + str(bad)}   {o}")
