"""Search for the densest legal arrangement of parallel rows.

A row is a line of Flagships nose to tail along the hall, all facing the same
way, so the front wheel and bars of each tuck under the canopy of the one in
front (the canopy is 4020 long against a 4476 long vehicle). One door of every
vehicle opens, all on the same side of the row.
"""
import math, itertools, json
from shapely.geometry import box
from shapely.ops import unary_union
from wh2 import (HALL, FIX_KEEP, TALL, LOW, Flagship, Veh, east_wall_u,
                 GATE, FACILITIES, check, interlock_pitch)

F = Flagship
PITCH = interlock_pitch(150.0)          # 4170
HALF = F.X_ROOF                          # 1014
DOOR_IN, DOOR_OUT = F.X_BOX, F.X_DOOR_OPEN
WALL = 150.0


def free_runs(v, half=HALF, step=50.0):
    """u intervals over which the whole body band [v-half, v+half] is clear of
    the fittings, their 600 mm working strips and the walls."""
    lo, hi = v - half, v + half
    if lo < WALL or hi > 9120 - WALL:
        return []
    free = HALL.buffer(-WALL).difference(FIX_KEEP)
    runs, start, u = [], None, -200.0
    while u <= 25600.0:
        cell = box(u, lo, u + step, hi)
        ok = free.contains(cell)
        if ok and start is None:
            start = u
        elif not ok and start is not None:
            if u - start >= F.LENGTH:
                runs.append((start, u))
            start = None
        u += step
    if start is not None and 25600.0 - start >= F.LENGTH:
        runs.append((start, 25600.0))
    return runs


def row_count(v, runs, pitch=PITCH):
    n, spans = 0, []
    for a, b in runs:
        L = b - a
        if L < F.LENGTH:
            continue
        k = int((L - F.LENGTH) // pitch) + 1
        n += k
        spans.append((a, b, k))
    return n, spans


def door_band(v, side):
    return (v + DOOR_IN, v + DOOR_OUT) if side == "N" else (v - DOOR_OUT, v - DOOR_IN)


def door_ok(v, side, runs):
    """The open doors must clear the office and stay inside the hall."""
    a, b = door_band(v, side)
    if a < WALL or b > 9120 - WALL:
        return False
    for u0, u1 in runs:
        if box(u0, a, u1, b).intersects(TALL):
            return False
    return True


def stack_ok(rows):
    """rows: list of (v, side). Bodies must not overlap; a door must not enter
    another row's body band; two door bands may share space only if the rows
    are staggered, which we allow when the pitch exceeds the door length."""
    rows = sorted(rows)
    for i, (v, s) in enumerate(rows):
        a, b = door_band(v, s)
        for j, (w, t) in enumerate(rows):
            if i == j:
                continue
            if not (b < w - HALF - 150 or a > w + HALF + 150):
                return False
        for j in range(i + 1, len(rows)):
            w = rows[j][0]
            if abs(v - w) < 2 * HALF + 150:
                return False
    return True


def evaluate(rows):
    total, detail = 0, []
    for v, s in rows:
        runs = free_runs(v)
        if not door_ok(v, s, runs):
            return None
        n, spans = row_count(v, runs)
        total += n
        detail.append(dict(v=v, side=s, n=n, spans=spans))
    return total, detail


def search(nrows=3, grid=50.0):
    vs = [v for v in range_f(WALL + HALF, 9120 - WALL - HALF, grid)]
    best = []
    for k in range(1, nrows + 1):
        for combo in itertools.combinations(vs, k):
            for sides in itertools.product("NS", repeat=k):
                rows = list(zip(combo, sides))
                if not stack_ok(rows):
                    continue
                r = evaluate(rows)
                if r is None:
                    continue
                best.append((r[0], rows, r[1]))
    best.sort(key=lambda x: -x[0])
    return best


def range_f(a, b, s):
    x = a
    while x <= b:
        yield x
        x += s


if __name__ == "__main__":
    print(f"pitch {PITCH:.0f}  vehicle {F.LENGTH:.0f} long, {F.WIDTH_CLOSED:.0f} wide")
    print("scanning single rows:")
    for v in range_f(1200, 8000, 200):
        runs = free_runs(v)
        n, _ = row_count(v, runs)
        sN, sS = door_ok(v, "N", runs), door_ok(v, "S", runs)
        if n:
            print(f"  v={v:6.0f}  n={n}  runs={[(round(a),round(b)) for a,b in runs]}"
                  f"  doorN={sN} doorS={sS}")
    print()
    res = search(3, 100.0)
    print("top stacks:")
    seen = set()
    for tot, rows, det in res[:14]:
        key = tuple(round(v / 500) for v, _ in rows)
        if key in seen:
            continue
        seen.add(key)
        print(f"  {tot:2d} vehicles  " + "  ".join(
            f"v={v:.0f}{s}({d['n']})" for (v, s), d in zip(rows, det)))
