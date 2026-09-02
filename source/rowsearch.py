"""How many stands fit in a single angled row, both doors open."""
import math
import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import affinity
from wh2 import Flagship as F, Veh, HALL, FACILITIES, east_wall_u
from pack import legal

def frame_offset(p, h):
    """Neighbour p mm to the EAST, expressed in the vehicle frame."""
    a = math.radians(h)
    # world (p,0) -> vehicle frame: rotate by -h.  vehicle +y = world dir(h)
    dx =  p * math.cos(a)
    dy = -p * math.sin(a)
    return dx, dy

def min_pitch(h, lo=1500.0, hi=9000.0, step=25.0):
    for p in np.arange(lo, hi, step):
        dx, dy = frame_offset(p, h)
        if legal(abs(dx), abs(dy)) and legal(abs(dx), -abs(dy)):
            return float(p)
    return None

def envelope(h):
    """v-extent of one vehicle with both doors open, at heading h."""
    v = Veh("_", 0.0, 0.0, h, doors=("R", "L"))
    g = unary_union([v.body(), v.doors_poly()])
    b = g.bounds
    return b[1], b[3], b[0], b[2]      # vmin, vmax, umin, umax

print(f"{'hdg':>5} {'pitch':>7} {'depth incl doors':>17} {'left for aisle':>15}")
rows = []
for h in np.arange(0, 91, 2.5):
    p = min_pitch(h)
    if p is None:
        continue
    v0, v1, u0, u1 = envelope(h)
    depth = v1 - v0
    rows.append((h, p, depth))
    print(f"{h:5.1f} {p:7.0f} {depth:17.0f} {9120-depth:15.0f}")
