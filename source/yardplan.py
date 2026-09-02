"""The outdoor formation, west of the workshop.

The site model does not carry a yard boundary - the paved slab in the CAD
stops 2540 mm west of the shed wall, and the farm vehicle Michael parked sits
beyond it - so this module does not assume one. It lays the formation out in
the yard frame and reports the footprint it needs, for checking on the ground.

Yard frame: same site coordinates. u = 0 is the shed's west wall, so the yard
is u < 0. The workshop canopy occupies u -3400..-200, v -198..4698.
"""
import math
from shapely.geometry import box
from shapely.ops import unary_union
from wh2 import Flagship as F, Farm as Z, Veh, GATE, WORKSHOP

CLEAR = 150.0
GATE_LANE = box(-40000.0, GATE[0] - 300.0, 0.0, GATE[1] + 300.0)   # keep clear


def rank(prefix, u_first, v_axle, n, pitch, hdg=90.0, doors=("R", "L")):
    """A rank of stands abreast, noses pointing the same way."""
    return [Veh(f"{prefix}{i+1}", u_first, v_axle - i * pitch, hdg, doors=doors,
                label=f"{prefix}{i+1}") for i in range(n)]


def formation(n_flag=7, n_farm=1):
    """Nose-in stands off one yard aisle, both doors open on every Flagship.

    Stands face EAST (hdg 270, nose east) in a column west of the workshop,
    so each pulls straight out into the aisle and turns for the gate.
    """
    pitch = 2 * F.X_DOOR_OPEN + CLEAR                 # 4285, both doors clear
    u_stand = -9500.0                                 # nose line of the rank
    v_top = 4400.0
    vs = rank("Y", u_stand, v_top, n_flag, pitch, hdg=270.0)
    if n_farm:
        vf = v_top - n_flag * pitch
        vs += [Veh("Z1", u_stand, vf, 270.0, doors=(), label="Z1",
                   note="farm vehicle, no doors to swing")]
    return vs


def footprint(vs):
    g = unary_union([v.body() for v in vs] +
                    [v.doors_poly() for v in vs if v.doors])
    b = g.bounds
    return b, (b[2] - b[0], b[3] - b[1])


if __name__ == "__main__":
    vs = formation()
    b, (w, h) = footprint(vs)
    print(f"{len(vs)} stands")
    print(f"  stands occupy u {b[0]:.0f}..{b[2]:.0f}  v {b[1]:.0f}..{b[3]:.0f}")
    print(f"  that is {w/1000:.1f} m east-west by {h/1000:.1f} m north-south")
    print(f"  plus an aisle east of the rank, 6.0 m, to turn out of a stand")
    print(f"  total yard needed: about {(w+6000)/1000:.1f} x {h/1000:.1f} m")
    print(f"  pitch between stands {2*F.X_DOOR_OPEN + CLEAR:.0f} mm")
