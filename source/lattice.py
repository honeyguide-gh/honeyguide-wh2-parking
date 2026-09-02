"""A lookup table of legal neighbour offsets for two parallel Flagships
with both doors open, so packing searches are table lookups."""
import os, math, pickle
import numpy as np
from pack import legal

STEP = 50.0
XMAX, YMAX = 6200.0, 6200.0
NX = int(XMAX / STEP) + 1
NY = int(2 * YMAX / STEP) + 1
CACHE = "lattice.pkl"


def build():
    T = np.zeros((NX, NY), dtype=bool)
    for i in range(NX):
        dx = i * STEP
        for j in range(NY):
            dy = -YMAX + j * STEP
            T[i, j] = legal(dx, dy)
    return T


if os.path.exists(CACHE):
    T = pickle.load(open(CACHE, "rb"))
else:
    T = build()
    pickle.dump(T, open(CACHE, "wb"))


def pair_ok(dx, dy):
    """dx, dy = neighbour offset in the vehicle frame (mm)."""
    i = int(round(abs(dx) / STEP))
    j = int(round((dy + YMAX) / STEP))
    if i >= NX or j < 0 or j >= NY:
        return True                      # far away
    return bool(T[i, j])


if __name__ == "__main__":
    print("table", T.shape, "legal fraction %.3f" % T.mean())
    for dy in (0, 2000, 3000, 3650, 4200):
        i = next((i for i in range(NX) if T[i, int((dy + YMAX) / STEP)]), None)
        print(f"  dy {dy:5.0f}  min dx {i * STEP if i is not None else None}")
