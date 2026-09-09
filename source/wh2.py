"""
Honeyguide WH2 v2 - dimensional basis and layout engine.

Extracted from Hardware Designs/Warehouse Design.3dm (saved 31 Aug 2026 18:43)
with rhino3dm. Millimetres throughout.

Site frame: origin at the inside face of the WEST wall on the inside face of
the SOUTH wall of the main hall.  u = east, v = north, z = up from the slab.
Model coordinates map as  u = x + 10548.9,  v = y + 5647.8,  z = Z - 150.
"""
import math
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

WALL_T = 200.0

# ---------------------------------------------------------------- main hall
SW, SE = (0.0, 0.0), (23120.0, 0.0)
NE, NW = (25400.0, 9120.0), (0.0, 9120.0)
HALL = Polygon([SW, SE, NE, NW])
HALL_H = 4550.0                      # 4700 shell minus the 150 slab

def east_wall_u(v):
    return 23120.0 + (25400.0 - 23120.0) * (v / 9120.0)

# vehicle gate, west wall
GATE = (4900.0, 7650.0, 3500.0)      # v0, v1, clear height

# The outdoor workshop is gone. The shop is now the bench run attached to the
# office's east face, inside the hall - facility key "shop" below.

# ------------------------------------------------- fixed fittings, main hall
class Fac:
    def __init__(self, key, name, poly, h, faces, note=""):
        self.key, self.name, self.poly, self.h = key, name, poly, h
        self.faces = faces          # sides a person works from: N S E W
        self.note = note
        self.zone = (h <= 0.0)      # a floor marking, not something solid

    def clearance(self, d=600.0):
        """The working strip a person needs, on the used faces only."""
        x0, y0, x1, y1 = self.poly.bounds
        out = []
        if "N" in self.faces: out.append(box(x0, y1, x1, y1 + d))
        if "S" in self.faces: out.append(box(x0, y0 - d, x1, y0))
        if "E" in self.faces: out.append(box(x1, y0, x1 + d, y1))
        if "W" in self.faces: out.append(box(x0 - d, y0, x0, y1))
        return unary_union(out) if out else Polygon()


# Read from Warehouse Design V2.3dm / V3.3dm (9 Sep 2026). The two models
# carry an identical set of fittings; only the vehicles differ between them.
#   * the shop now stands where the fridges used to, against the office's
#     east face on the south wall
#   * all three fridges have moved to the north wall, east of check-in
#   * the crate stacks have moved to the north-east corner
#   * the wash area has gone from the south wall
#   * check-in / check-out sits in the north-west corner, by the gate
FACILITIES = [
    Fac("office",  "Office",               box(0, 0, 7360, 3560),           2640, "NE"),
    Fac("shop",    "Shop bench",           box(7299.1, 0, 7969.6, 2438.4),   900, "NE",
        "the workshop, attached to the office's east face"),
    Fac("shoprig", "Shop equipment",       box(8006.1, 110.9, 8640.5, 754.8), 1265, "NE"),
    Fac("checkin", "Check-in / check-out", box(3960.0, 7318.3, 8360.0, 9118.3), 0, "S",
        "floor zone, 4400 x 1800, drawn on the slab in both models"),
    Fac("fridge1", "Fridge 1",             box(8878.1, 8260.0, 10658.1, 9070.0), 860, "S"),
    Fac("fridge2", "Fridge 2",             box(10701.7, 8240.0, 12651.7, 9070.0), 860, "S"),
    Fac("fridge3", "Fridge 3",             box(12689.7, 8240.0, 14639.7, 9070.0), 860, "S"),
    Fac("crates",  "Food storage crates",  box(16985.3, 8110.0, 20392.1, 9120.0), 600, "S"),
]
ZONES = [f for f in FACILITIES if f.zone]
SOLIDS = [f for f in FACILITIES if not f.zone]

FAC = {f.key: f for f in FACILITIES}

FIX_SOLID = unary_union([f.poly for f in SOLIDS])
FIX_KEEP = unary_union([f.poly for f in SOLIDS]
                       + [f.clearance() for f in SOLIDS])
# things an open door may pass over: anything under 1900 mm
LOW = unary_union([f.poly for f in SOLIDS if f.h < 1900])
TALL = unary_union([f.poly for f in SOLIDS if f.h >= 1900])

FREE = HALL.difference(FIX_KEEP)

# ------------------------------------------------- equipment on the stations
# (key, label, u0, v0, u1, v1, height, colour role)
EQUIP = [
    # Nothing free-standing is left: the shop bench, the shop equipment, the
    # fridges and the crate stacks are all in FACILITIES above, and the two
    # HGF bikes and HG3 are vehicles, not fittings.
]


# ------------------------------------------------------------- the Flagship
class Flagship:
    """2025.08.25 Trike v1.0.3, doors open. Re-measured from the 31 Aug model:
    overall 4477.6 x 2028 x 2529, doors open 4134.9 wide."""
    Y_NOSE = 2928.4
    Y_FRONT_AXLE = 2650.0
    Y_ROOF_F = 2472.5
    Y_BOX_F = 985.0
    Y_DOOR_F = 957.0
    Y_DOOR_R = -1019.4
    Y_BOX_R = -1059.5
    Y_ROOF_R = -1547.3

    X_ROOF = 1014.0
    X_BOX = 698.0
    X_FORK = 774.0
    X_DOOR_OPEN = 2067.6
    X_TRACK = 480.0

    Z_WHEEL = 555.0
    Z_BAR = 1512.5
    Z_DECK = 764.0
    Z_BOX_TOP = 2372.0
    Z_DOOR_LO = 1987.9          # underside of the open door arms
    Z_DOOR_LEAF = 2167.3
    Z_DOOR_HI = 2243.4
    Z_ROOF_LO = 2222.0
    Z_ROOF_HI = 2528.4

    WHEEL_D = 560.0
    WHEELBASE = 2650.0
    STEER_MAX = math.radians(40.0)

    LENGTH = Y_NOSE - Y_ROOF_R                 # 4475.7
    WIDTH_CLOSED = 2 * X_ROOF                  # 2028
    WIDTH_OPEN = 2 * X_DOOR_OPEN               # 4135.2
    DOOR_LEN = Y_DOOR_F - Y_DOOR_R             # 1976.4

    @classmethod
    def poly_body(cls):
        return Polygon([
            (-cls.X_ROOF, cls.Y_ROOF_R), (cls.X_ROOF, cls.Y_ROOF_R),
            (cls.X_ROOF, cls.Y_ROOF_F), (cls.X_FORK, cls.Y_ROOF_F),
            (cls.X_FORK, cls.Y_FRONT_AXLE), (200.0, cls.Y_NOSE),
            (-200.0, cls.Y_NOSE), (-cls.X_FORK, cls.Y_FRONT_AXLE),
            (-cls.X_FORK, cls.Y_ROOF_F)])

    @classmethod
    def poly_hull(cls):
        """Everything below the canopy: the module (764 to 2372) and the
        chassis, forks and bars ahead of it (nothing above 1513)."""
        return unary_union([
            box(-cls.X_BOX, cls.Y_BOX_R, cls.X_BOX, cls.Y_BOX_F),
            box(-cls.X_FORK, cls.Y_BOX_F, cls.X_FORK, cls.Y_NOSE)])

    @classmethod
    def poly_module(cls):
        """The part of the hull tall enough to foul an open door (to 2372)."""
        return box(-cls.X_BOX, cls.Y_BOX_R, cls.X_BOX, cls.Y_BOX_F)

    @classmethod
    def poly_canopy(cls):
        return box(-cls.X_ROOF, cls.Y_ROOF_R, cls.X_ROOF, cls.Y_ROOF_F)

    @classmethod
    def poly_door(cls, side):
        s = 1 if side == "R" else -1
        a, b = sorted((s * cls.X_BOX, s * cls.X_DOOR_OPEN))
        return box(a, cls.Y_DOOR_R, b, cls.Y_DOOR_F)



# ------------------------------------------------------- the farm vehicle
class Farm:
    """HG3, the cargo vehicle. Measured from the 237 chassis parts placed in
    Warehouse Design V2.3dm, 9 Sep 2026: 4207 long, 1549 wide, 1513 tall.

    The Flagship is this same chassis with a market module, a canopy and two
    doors on top of it - every Flagship in the model carries these very parts.
    HG3 is the chassis on its own, so it turns identically and stops 1015 mm
    below a Flagship's roof."""
    LENGTH = 4207.2
    WIDTH = 1548.8
    HEIGHT = 1512.5
    WHEELBASE = 2650.0
    X_TRACK = 480.0
    STEER_MAX = math.radians(40.0)

    Y_NOSE = 2930.0                    # front of the front tyre
    Y_TAIL = Y_NOSE - LENGTH           # -1277.2
    X_HALF = WIDTH / 2.0               # 774.4
    Z_TOP = HEIGHT

    @classmethod
    def poly_body(cls):
        return box(-cls.X_HALF, cls.Y_TAIL, cls.X_HALF, cls.Y_NOSE)

    @classmethod
    def poly_hull(cls):
        return cls.poly_body()

    @classmethod
    def poly_canopy(cls):
        """HG3 tops out at 1513, well under the 2222 mm canopy band, so it
        occupies nothing up there and a Flagship roof may overhang it."""
        return Polygon()

    @classmethod
    def poly_module(cls):
        return cls.poly_body()

    @classmethod
    def poly_door(cls, side):
        return Polygon()


# ------------------------------------------------------------------- HGF
class Bike:
    """HGF, the Honda CG125 with its rear box. Two of them stand in the
    north-west corner in both models. Measured from the placed geometry:
    2055 long, 650 wide, 1404 tall, 1341 mm wheelbase.

    A bike steers far harder than a trike, so it gets its own lock."""
    LENGTH = 2054.1
    WIDTH = 487.2               # frame, box and panniers, below the bars
    BARS = 650.9                # across the handlebars, at 1051 mm up
    BARS_Y = 857.9              # where the bars sit, ahead of the rear axle
    HEIGHT = 1403.6
    WHEELBASE = 1341.2
    X_TRACK = 0.0
    STEER_MAX = math.radians(45.0)

    Y_NOSE = 1651.1
    Y_TAIL = -403.1
    X_HALF = WIDTH / 2.0        # 243.6
    BAR_HALF = BARS / 2.0       # 325.5
    Z_TOP = HEIGHT

    @classmethod
    def poly_bars(cls):
        """The handlebars, the widest thing on the bike. Kept apart from the
        body because a rider turns them to get out of a tight stand."""
        return box(-cls.BAR_HALF, cls.BARS_Y - 120.0,
                   cls.BAR_HALF, cls.BARS_Y + 120.0)

    @classmethod
    def poly_body(cls):
        return box(-cls.X_HALF, cls.Y_TAIL, cls.X_HALF, cls.Y_NOSE)

    @classmethod
    def poly_hull(cls):
        return cls.poly_body()

    @classmethod
    def poly_canopy(cls):
        return Polygon()

    @classmethod
    def poly_module(cls):
        return cls.poly_body()

    @classmethod
    def poly_door(cls, side):
        return Polygon()


# ------------------------------------------------------------------ placing
class Veh:
    """(u, v) is the rear-axle centre. hdg deg, 0 = nose north, ccw positive.
    doors is a subset of {'L','R'} that are open in the parked state."""

    def __init__(self, name, u, v, hdg, doors=("R",), label=None, note="",
                 kind="flagship", doors_required=True):
        self.name, self.u, self.v, self.hdg = name, float(u), float(v), float(hdg)
        self.doors = tuple(doors)
        self.label = label or name
        self.note = note
        self.kind = kind
        self.cls = {"farm": Farm, "bike": Bike}.get(kind, Flagship)
        self.doors_required = doors_required and kind == "flagship"

    @classmethod
    def from_module_centre(cls, name, mu, mv, hdg, **kw):
        a = math.radians(hdg)
        fx, fy = -math.sin(a), math.cos(a)
        off = -(Flagship.Y_BOX_R + Flagship.Y_BOX_F) / 2.0     # +37.25
        return cls(name, mu + fx * off, mv + fy * off, hdg, **kw)

    def _p(self, poly):
        return affinity.translate(
            affinity.rotate(poly, self.hdg, origin=(0, 0)), self.u, self.v)

    def body(self):   return self._p(self.cls.poly_body())
    def hull(self):   return self._p(self.cls.poly_hull())
    def module(self): return self._p(self.cls.poly_module())
    def canopy(self): return self._p(self.cls.poly_canopy())
    def upper(self):
        return unary_union([self.canopy(), self.module()])

    def door(self, s): return self._p(self.cls.poly_door(s))

    def doors_poly(self):
        ds = [self.door(s) for s in self.doors]
        return unary_union(ds) if ds else Polygon()

    def envelope(self):
        return unary_union([self.body(), self.doors_poly()])

    def stand_poly(self, pad=110.0):
        c = self.cls
        if self.kind == "flagship":
            b = box(-c.X_ROOF - pad, c.Y_ROOF_R - pad,
                    c.X_ROOF + pad, c.Y_NOSE + pad)
        else:
            b = box(-c.X_HALF - pad, c.Y_TAIL - pad,
                    c.X_HALF + pad, c.Y_NOSE + pad)
        return self._p(b)

    def centre(self):
        """Middle of the body, for a label."""
        return self.body().centroid.coords[0]

    def nose(self):
        a = math.radians(self.hdg)
        return (self.u - self.cls.Y_NOSE * math.sin(a),
                self.v + self.cls.Y_NOSE * math.cos(a))

    def fwd(self):
        a = math.radians(self.hdg)
        return (-math.sin(a), math.cos(a))

    def as_dict(self):
        return dict(name=self.name, u=self.u, v=self.v, hdg=self.hdg,
                    doors=list(self.doors), label=self.label, note=self.note,
                    kind=self.kind)


# ------------------------------------------------------------------- checks
GAP_VEH = 150.0        # body to body, and door tip to anything
GAP_WALL = 150.0
CLEAR_HUMAN = 600.0


def check(vehicles, verbose=True, hall=HALL):
    issues = []
    inner = hall.buffer(-GAP_WALL + 1)

    for v in vehicles:
        b = v.body()
        if not hall.contains(b):
            issues.append(f"FAIL {v.label}: body outside the hall")
        elif not inner.contains(b):
            issues.append(f"WARN {v.label}: body {b.distance(hall.exterior):.0f} mm from a wall")
        # body must respect every facility and its working strip. The strip is
        # tested against the module - the part of the vehicle standing at the
        # height a person works at. A canopy edge at 2222 mm overhangs the
        # strip without taking it away, so it is reported separately.
        m = v.module()
        for f in FACILITIES:
            if f.zone:
                ov = b.intersection(f.poly)
                if not ov.is_empty:
                    issues.append(f"NOTE {v.label}: stands over "
                                  f"{ov.area/1e6:.1f} m2 of {f.name}")
                continue
            if b.intersects(f.poly):
                issues.append(f"FAIL {v.label}: body fouls {f.name}")
                continue
            work = f.clearance()
            if work.is_empty:
                continue
            if m.intersects(work.buffer(-1.0)):
                issues.append(f"FAIL {v.label}: {m.distance(f.poly):.0f} mm to "
                              f"{f.name} at working height, needs {CLEAR_HUMAN:.0f}")
            elif b.intersects(work.buffer(-1.0)):
                issues.append(f"NOTE {v.label}: canopy overhangs the strip at "
                              f"{f.name} ({b.distance(f.poly):.0f} mm at 2222 mm, "
                              f"{m.distance(f.poly):.0f} mm at working height)")
        if not v.doors and getattr(v, "doors_required", True):
            issues.append(f"FAIL {v.label}: no door can be opened")

    for i, a in enumerate(vehicles):
        for b in vehicles[i + 1:]:
            dc = a.canopy().distance(b.canopy())
            dh = a.hull().distance(b.hull())
            if dc <= 0 or dh <= 0:
                issues.append(f"FAIL {a.label}/{b.label}: vehicles collide "
                              f"(canopy {dc:.0f}, hull {dh:.0f})")
            elif min(dc, dh) < GAP_VEH:
                issues.append(f"WARN {a.label}/{b.label}: {min(dc,dh):.0f} mm "
                              f"apart (canopy {dc:.0f}, hull {dh:.0f})")

    bikes = [v for v in vehicles if v.kind == "bike"]
    for i, a in enumerate(bikes):
        for b in bikes[i + 1:]:
            ba, bb = a._p(Bike.poly_bars()), b._p(Bike.poly_bars())
            if ba.intersects(bb):
                w = 2 * Bike.BAR_HALF
                d = math.dist((a.u, a.v), (b.u, b.v))
                issues.append(f"FAIL {a.label}/{b.label}: handlebars overlap by "
                              f"{w - d:.0f} mm - {w:.0f} mm across the bars on "
                              f"{d:.0f} mm centres")

    for i, a in enumerate(vehicles):
        da = a.doors_poly()
        if da.is_empty:
            continue
        if not hall.contains(da):
            issues.append(f"FAIL {a.label}: open door hits a wall")
        if da.intersects(TALL):
            issues.append(f"FAIL {a.label}: open door fouls the office")
        for j, b in enumerate(vehicles):
            if i == j:
                continue
            if da.intersects(b.module()):
                issues.append(f"FAIL {a.label} door fouls the body of {b.label} "
                              f"({da.intersection(b.module()).area/1e6:.2f} m2)")
            elif da.intersects(b.canopy()):
                ov = da.intersection(b.canopy()).area / 1e6
                issues.append(f"FAIL {a.label} door sweeps {ov:.2f} m2 over the "
                              f"canopy of {b.label}; the top "
                              f"{Flagship.Z_DOOR_HI - Flagship.Z_ROOF_LO:.0f} mm "
                              f"of the leaf is at canopy height")
            if j > i and da.intersects(b.doors_poly()):
                issues.append(f"FAIL {a.label}/{b.label}: open doors clash")

    ok = not any(s.startswith("FAIL") for s in issues)
    if verbose:
        for s in issues:
            print("   ", s)
    return ok, issues


# ------------------------------------------------- nose-under-canopy pitch
def interlock_pitch(clear=150.0):
    """Nose-to-tail pitch when the front wheel and bars tuck under the
    canopy of the vehicle in front. Limited by canopy to canopy."""
    return (Flagship.Y_ROOF_F - Flagship.Y_ROOF_R) + clear


def door_pitch(clear=150.0):
    """Side-by-side pitch when every vehicle opens the same side door."""
    return Flagship.X_DOOR_OPEN + Flagship.X_ROOF + clear


if __name__ == "__main__":
    print(f"hall            {HALL.area/1e6:7.1f} m2   9120 wide, "
          f"25400 north, 23120 south")
    print(f"fittings        {FIX_SOLID.area/1e6:7.1f} m2")
    print(f"with 600 strips {FIX_KEEP.area/1e6:7.1f} m2")
    print(f"free floor      {FREE.area/1e6:7.1f} m2")
    print(f"workshop        {WORKSHOP.area/1e6:7.1f} m2 (outside, covered)")
    F = Flagship
    print(f"flagship        {F.LENGTH:.0f} x {F.WIDTH_CLOSED:.0f} x {F.Z_ROOF_HI:.0f}"
          f"   doors open {F.WIDTH_OPEN:.0f}")
    print(f"open door band  {F.Z_DOOR_LO:.0f} to {F.Z_DOOR_HI:.0f} above the slab")
    print(f"interlock pitch {interlock_pitch():.0f}   one-door pitch {door_pitch():.0f}")
    print(f"gate            {GATE[1]-GATE[0]:.0f} wide x {GATE[2]:.0f} high, west wall")
