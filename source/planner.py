"""Manoeuvre planner for WH2.

Hybrid A* over the real Flagship footprint, with the height layers the
warehouse actually has, so the nose may tuck under the canopy in front and
slide under an open door, exactly as it does when parked.

Kinematics: rear axle reference, wheelbase 2650, steer 40 deg, so the
tightest rear axle radius is 3158 mm. Forward and reverse are both allowed,
so the planner shuffles when a bay is tight, which is what a driver does.
"""
import math, heapq
import numpy as np
import shapely
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
from wh2 import (Flagship as F, Veh, HALL, FACILITIES, EQUIP, GATE, WALL_T,
                 WORKSHOP)

CELL = 50.0
U0, V0 = -13000.0, -2500.0
NU, NV = 800, 260

R_MIN = F.WHEELBASE / math.tan(F.STEER_MAX)          # 3158 mm
HBINS = 180                                          # 2 degrees
STEP = 600.0

# ------------------------------------------------------------- drivable area
APRON = box(-12000.0, -2500.0, -WALL_T, 9500.0)      # open yard, west
DOORWAY = box(-WALL_T, GATE[0], 0.0, GATE[1])
DRIVE = unary_union([HALL, APRON, DOORWAY])
OUTSIDE = box(U0, V0, U0 + NU * CELL, V0 + NV * CELL).difference(DRIVE)


def _solid(hmin):
    """Everything standing at least hmin tall that a vehicle must go round."""
    ps = [OUTSIDE, WORKSHOP]
    for f in FACILITIES:
        if f.h >= hmin and f.key != "weigh":
            ps.append(f.poly)
    for k, n, a, b, c, d, h, r in EQUIP:
        if h >= hmin and r != "hole":
            ps.append(box(a, b, c, d))
    return unary_union(ps)


# height bands of the vehicle itself
#   low     chassis, forks and bars      0 to 1513
#   module  the cargo box               764 to 2372
#   canopy  the roof                   2222 to 2528
#   door    an open leaf and its arms  1988 to 2243
LAYERS = ("canopy", "module", "low")


def veh_layers(v):
    return dict(canopy=v.canopy(), module=v.module(),
                low=box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE)
                and affinity.translate(
                    affinity.rotate(box(-F.X_FORK, F.Y_BOX_F, F.X_FORK,
                                        F.Y_NOSE), v.hdg, origin=(0, 0)),
                    v.u, v.v),
                door=v.doors_poly())


def _cells(poly):
    img = Image.new("1", (NU, NV), 0)
    d = ImageDraw.Draw(img)
    if poly.is_empty:
        return np.array(img, dtype=bool).T
    gs = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    for g in gs:
        d.polygon([((x - U0) / CELL, (y - V0) / CELL)
                   for x, y in g.exterior.coords], fill=1)
        for r in g.interiors:
            d.polygon([((x - U0) / CELL, (y - V0) / CELL)
                       for x, y in r.coords], fill=0)
    return np.array(img, dtype=bool).T


STATIC = {"canopy": _cells(_solid(2222.0)),
          "module": _cells(_solid(764.0)),
          "low":    _cells(_solid(100.0))}

# ------------------------------------------------------------ the footprints
INFLATE = 75.0          # driving margin, on top of the 50 mm grid
_LOCAL = {k: g.buffer(INFLATE, join_style=2) for k, g in
          {"canopy": F.poly_canopy(), "module": F.poly_module(),
           "low": box(-F.X_FORK, F.Y_BOX_F, F.X_FORK, F.Y_NOSE)}.items()}
_FOOT = {}
for name, poly in _LOCAL.items():
    fs = []
    for b in range(HBINS):
        p = affinity.rotate(poly, b * 360.0 / HBINS, origin=(0, 0))
        x0, y0, x1, y1 = p.bounds
        ii, jj = np.meshgrid(
            np.arange(int(math.floor(x0 / CELL)), int(math.ceil(x1 / CELL)) + 1),
            np.arange(int(math.floor(y0 / CELL)), int(math.ceil(y1 / CELL)) + 1),
            indexing="ij")
        m = shapely.contains_xy(p, ii * CELL, jj * CELL)
        di, dj = ii[m].astype(np.int64), jj[m].astype(np.int64)
        fs.append((di * NV + dj, int(di.min()), int(di.max()),
                   int(dj.min()), int(dj.max())))
    _FOOT[name] = fs


def hbin(h):
    return int(round((h % 360.0) / (360.0 / HBINS))) % HBINS


class Field:
    """Static obstacles plus whatever vehicles are still parked, by layer."""

    def __init__(self, parked=()):
        p = {k: [] for k in ("canopy", "module", "low", "door")}
        for v in parked:
            L = veh_layers(v)
            for k in p:
                if not L[k].is_empty:
                    p[k].append(L[k])
        P = {k: unary_union(v) if v else Polygon() for k, v in p.items()}
        # what each moving layer may not touch
        block = {
            "canopy": unary_union([P["canopy"], P["module"], P["door"]]),
            "module": unary_union([P["canopy"], P["module"], P["door"],
                                   P["low"]]),
            "low":    unary_union([P["module"], P["low"]])}
        self.m = {k: (STATIC[k] | _cells(block[k])).ravel() for k in LAYERS}

    def hits(self, u, v, h):
        b = hbin(h)
        i = int(round((u - U0) / CELL))
        j = int(round((v - V0) / CELL))
        for k in LAYERS:
            off, i0, i1, j0, j1 = _FOOT[k][b]
            if i + i0 < 0 or j + j0 < 0 or i + i1 >= NU or j + j1 >= NV:
                return True
            if self.m[k][i * NV + j + off].any():
                return True
        return False


# ------------------------------------------------------------------ kinematics
def step(p, k, d, s):
    u, v, h = p
    a = math.radians(h)
    if abs(k) < 1e-9:
        return (u - math.sin(a) * s * d, v + math.cos(a) * s * d, h)
    R = 1.0 / k
    cx, cy = u - math.cos(a) * R, v - math.sin(a) * R
    dp = s * d * k
    c, sn = math.cos(dp), math.sin(dp)
    du, dv = u - cx, v - cy
    return (cx + du * c - dv * sn, cy + du * sn + dv * c, h + math.degrees(dp))


KS = [0.0, 1.0 / R_MIN, -1.0 / R_MIN, 0.5 / R_MIN, -0.5 / R_MIN]


def plan(start, field, goal_u=-1400.0, goal_v=None, goal_h=90.0,
         gu=350.0, gh=10.0, cap=200000):
    goal_v = goal_v if goal_v is not None else (GATE[0] + GATE[1]) / 2

    def key(p):
        return (int(round(p[0] / gu)), int(round(p[1] / gu)),
                int(round((p[2] % 360) / gh)) % int(360 / gh))

    def hcost(p):
        return math.hypot(p[0] - goal_u, p[1] - goal_v)

    def done(p):
        dh = (p[2] - goal_h + 180) % 360 - 180
        return (p[0] <= goal_u and abs(dh) < 12.0
                and abs(p[1] - goal_v) < 500.0)

    st = (start[0], start[1], start[2] % 360.0)
    open_ = [(hcost(st), 0.0, 0, st, 1)]
    best = {(key(st), 1): 0.0}
    came, n = {}, 0
    while open_ and n < cap:
        f, g, idx, p, d0 = heapq.heappop(open_)
        n += 1
        if done(p):
            out, cur = [], (idx, p, d0)
            while cur is not None:
                out.append(cur[1])
                cur = came.get(cur[0])
            return list(reversed(out)), n
        for k in KS:
            for d in (1, -1):
                q, ok = p, True
                for t in range(3):
                    q = step(q, k, d, STEP / 3.0)
                    if field.hits(*q):
                        ok = False
                        break
                if not ok:
                    continue
                c = (g + STEP * (1.0 if d > 0 else 1.7)
                     + (450.0 if d != d0 else 0.0) + 220.0 * abs(k) * R_MIN)
                kk = (key(q), d)
                if c < best.get(kk, 1e18) - 1.0:
                    best[kk] = c
                    nid = len(came) + 1
                    came[nid] = (idx, p, d0)
                    heapq.heappush(open_, (c + hcost(q), c, nid, q, d))
    return None, n


# ---------------------------------------------------------------- densifying
def densify(nodes, spacing=150.0):
    out = [nodes[0]]
    for a, b in zip(nodes, nodes[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        dh = (b[2] - a[2] + 180) % 360 - 180
        n = max(1, int(round(max(d, abs(dh) * 12.0) / spacing)))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                        a[2] + dh * t))
    return out


def run_out(p, to_u=-7500.0, spacing=150.0):
    u, v, h = p
    a = math.radians(h)
    n = int((u - to_u) / spacing)
    return [(u - math.sin(a) * spacing * i, v + math.cos(a) * spacing * i, h)
            for i in range(1, n + 1)]
