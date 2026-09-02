"""Pairwise packing geometry for two parallel Flagships, BOTH doors open.

Answers one question: for a neighbour offset (dx, dy) in the vehicle frame,
is the pair legal?  Legal means 150 mm everywhere, with the real height bands:
a nose (<=1513) may sit under a canopy (2222+) or under an open door (1988+),
but nothing else may overlap.
"""
import math
import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import affinity
from wh2 import Flagship as F

GAP = 150.0

def parts(dx=0.0, dy=0.0):
    """The four layers of a vehicle at offset (dx, dy), doors both sides."""
    t = lambda g: affinity.translate(g, dx, dy)
    canopy = t(box(-F.X_ROOF, F.Y_ROOF_R, F.X_ROOF, F.Y_ROOF_F))
    module = t(box(-F.X_BOX, F.Y_BOX_R, F.X_BOX, F.Y_BOX_F))
    low    = t(box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE))
    doors  = unary_union([t(F.poly_door("R")), t(F.poly_door("L"))])
    return canopy, module, low, doors

A = parts()

def legal(dx, dy, gap=GAP):
    B = parts(dx, dy)
    ac, am, al, ad = A
    bc, bm, bl, bd = B
    # (moving/parked layer pairs that share height)
    pairs = [(ac, bc), (ac, bm), (ac, bd),          # canopy 2222-2528
             (am, bc), (am, bm), (am, bd), (am, bl),# module  764-2372
             (al, bm), (al, bl),                    # low       0-1513
             (ad, bc), (ad, bm), (ad, bd)]          # door   1988-2243
    return min(p.distance(q) for p, q in pairs) >= gap


def sweep():
    print("legal neighbour offsets, both doors open (x across, y along)")
    print("  the smallest legal |offset| for each family:\n")
    best = []
    for dy in np.arange(0, 6000, 25.0):
        lo = None
        for dx in np.arange(0, 6000, 25.0):
            if legal(dx, dy):
                lo = dx
                break
        if lo is not None:
            best.append((dy, lo, math.hypot(lo, dy)))
    # print a readable ladder
    shown = set()
    for dy, dx, r in best:
        k = round(dx / 100)
        if k in shown:
            continue
        shown.add(k)
        ang = math.degrees(math.atan2(dx, dy)) if dy else 90.0
        print(f"   dy {dy:6.0f}   min dx {dx:6.0f}   pitch {r:6.0f}   "
              f"{ang:5.1f} deg off the vehicle axis")
    return best


if __name__ == "__main__":
    print(f"one door open, side by side: {F.X_DOOR_OPEN + F.X_ROOF + GAP:.0f}")
    print(f"both doors, side by side:    {2*F.X_DOOR_OPEN + GAP:.0f}")
    print(f"nose to tail (canopy):       {F.Y_ROOF_F - F.Y_ROOF_R + GAP:.0f}")
    print()
    sweep()
