"""
Honeyguide WH2 - dimensional basis and layout/clearance engine.

All dimensions in millimetres, extracted from
  Hardware Designs/Warehouse Design.3dm  (Rhino, mm)
via rhino3dm on 2026-08-31.

Site coordinate system:
  origin  = inside face of the SOUTH wall at the inside face of the WEST wall
  +x      = east   (0 .. 9045 across the shed)
  +y      = north  (0 .. 25460 at the west wall, 0 .. 23785 at the east wall)
  +z      = up     (0 = top of slab)

Vehicle local frame (Flagship):
  origin  = centre of the REAR AXLE on the ground
  +y      = forward (towards the nose)
  +x      = to the vehicle's right
"""
import math
import json
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity

# --------------------------------------------------------------------------
# 1. BUILDING
# --------------------------------------------------------------------------
WALL_T = 250.0

# inside face corners, anticlockwise from the SW
SW = (0.0, 0.0)
SE = (9045.0, 0.0)
NE = (9045.0, 23785.0)
NW = (0.0, 25460.0)
INTERIOR = Polygon([SW, SE, NE, NW])

EAVES_Z = 2250.0     # underside of the roof structure at the wall (model 2360)
RIDGE_Z = 4500.0     # underside of the roof at the apex   (model 4610)

# enclosed block already built in the SE corner (3.0 m tall room)
BLOCK = box(5025.0, 0.0, 9045.0, 7705.0)
BLOCK_H = 3000.0

# roller shutter in the south wall
GATE_EXISTING = (1275.0, 3775.0, 2300.0)     # x0, x1, clear height
GATE_DESIGN = (1025.0, 4025.0, 3000.0)       # enlarged, per Michael 2026-08-31

FREE_FLOOR = INTERIOR.difference(BLOCK)

# --------------------------------------------------------------------------
# 2. FLAGSHIP  (Motorking MK-200ZH-23 + Honeyguide market module v1.0.3)
# --------------------------------------------------------------------------
class Flagship:
    # longitudinal, measured from the rear-axle centre (+ = forward)
    Y_NOSE = 2930.0        # front of the front tyre
    Y_FRONT_AXLE = 2650.0  # wheelbase
    Y_ROOF_F = 2472.5      # front edge of the canopy
    Y_BOX_F = 985.0        # front wall of the market module
    Y_DOOR_F = 941.9       # front edge of the door leaf
    Y_DOOR_R = -1016.9     # rear edge of the door leaf
    Y_BOX_R = -1059.5      # rear wall of the market module
    Y_ROOF_R = -1547.5     # rear edge of the canopy = rear-most point

    # lateral, from the centreline
    X_ROOF = 1014.0        # canopy / roof edging half width  -> 2027 overall
    X_BOX = 698.0          # module body half width           -> 1397 overall
    X_FORK = 774.0         # handlebar half width             -> 1549 overall
    X_DOOR_OPEN = 2063.0   # door tip when fully open         -> 4127 overall
    X_TRACK = 480.0        # rear wheel centres               -> 960 track

    # heights above slab
    Z_WHEEL = 555.0
    Z_BAR = 1506.0         # top of the handlebars
    Z_DECK = 764.0         # module floor
    Z_BOX_TOP = 2366.0
    Z_DOOR_LO = 1982.0     # underside of the open door ARMS (leaf sits at 2161)
    Z_DOOR_HI = 2237.0     # top of the open door leaf
    Z_DOOR_LEAF = 2161.0   # underside of the leaf itself
    Z_ROOF_LO = 2232.0
    Z_ROOF_HI = 2524.5     # overall height

    WHEEL_D = 560.0
    WHEELBASE = 2650.0
    STEER_MAX = math.radians(40.0)   # design value

    # derived
    LENGTH = Y_NOSE - Y_ROOF_R                       # 4477.5
    WIDTH_CLOSED = 2 * X_ROOF                        # 2028
    WIDTH_OPEN = 2 * X_DOOR_OPEN                     # 4126
    DOOR_LEN = Y_DOOR_F - Y_DOOR_R                   # 1958.8

    # ---- footprint polygons in the vehicle frame -------------------------
    @classmethod
    def poly_body(cls):
        """Everything below 2.16 m: what the vehicle occupies with doors shut."""
        return Polygon([
            (-cls.X_ROOF, cls.Y_ROOF_R), (cls.X_ROOF, cls.Y_ROOF_R),
            (cls.X_ROOF, cls.Y_ROOF_F), (cls.X_FORK, cls.Y_ROOF_F),
            (cls.X_FORK, cls.Y_FRONT_AXLE), (200.0, cls.Y_NOSE),
            (-200.0, cls.Y_NOSE), (-cls.X_FORK, cls.Y_FRONT_AXLE),
            (-cls.X_FORK, cls.Y_ROOF_F),
        ])

    @classmethod
    def poly_canopy(cls):
        """2.23 - 2.52 m band. Nothing may pass through this, including doors."""
        return box(-cls.X_ROOF, cls.Y_ROOF_R, cls.X_ROOF, cls.Y_ROOF_F)

    @classmethod
    def poly_doors(cls):
        """1.98 - 2.24 m band, both leaves fully open, arms included."""
        left = box(-cls.X_DOOR_OPEN, cls.Y_DOOR_R, -cls.X_BOX, cls.Y_DOOR_F)
        right = box(cls.X_BOX, cls.Y_DOOR_R, cls.X_DOOR_OPEN, cls.Y_DOOR_F)
        return unary_union([left, right])

    @classmethod
    def poly_envelope_open(cls):
        return unary_union([cls.poly_body(), cls.poly_doors()])


class Flash:
    """Haojue EG125 - from HG_Bike+Box.3dm: 651 x 2059 x 1408 (with top box)."""
    LENGTH = 2059.0
    WIDTH = 651.0        # 900 over the mirrors in practice
    HEIGHT = 1408.0

    @classmethod
    def poly_body(cls):
        return box(-450.0, -1030.0, 450.0, 1030.0)   # 900 wide over bars


# --------------------------------------------------------------------------
# 3. PLACEMENT
# --------------------------------------------------------------------------
class Vehicle:
    """A placed vehicle. (x, y) is the rear-axle centre; hdg in degrees,
    0 = nose pointing north (+y), positive = anticlockwise."""

    def __init__(self, name, x, y, hdg, kind="flagship", doors=True, label=None):
        self.name = name
        self.x, self.y, self.hdg = float(x), float(y), float(hdg)
        self.kind = kind
        self.doors = doors           # may this stand open both doors?
        self.label = label or name

    def _place(self, poly):
        p = affinity.rotate(poly, self.hdg, origin=(0, 0), use_radians=False)
        return affinity.translate(p, self.x, self.y)

    @property
    def cls(self):
        return Flagship if self.kind == "flagship" else Flash

    def body(self):
        return self._place(self.cls.poly_body())

    def canopy(self):
        if self.kind != "flagship":
            return self.body()
        return self._place(Flagship.poly_canopy())

    def doors_poly(self):
        if self.kind != "flagship":
            return Polygon()
        return self._place(Flagship.poly_doors())

    def envelope(self):
        if self.kind != "flagship" or not self.doors:
            return self.body()
        return self._place(Flagship.poly_envelope_open())

    def nose(self):
        c = self.cls
        yn = getattr(c, "Y_NOSE", c.LENGTH / 2)
        a = math.radians(self.hdg)
        return (self.x - yn * math.sin(a), self.y + yn * math.cos(a))

    def as_dict(self):
        return dict(name=self.name, x=self.x, y=self.y, hdg=self.hdg,
                    kind=self.kind, doors=self.doors, label=self.label)


# --------------------------------------------------------------------------
# 4. CLEARANCE CHECKS
# --------------------------------------------------------------------------
MIN_BODY_GAP = 300.0     # vehicle to vehicle, doors shut
MIN_WALL_GAP = 150.0     # nose to wall, set by the wheel stop
MIN_DOOR_GAP = 150.0     # open door leaf to anything else


def check(vehicles, obstacles=(BLOCK,), interior=INTERIOR, verbose=True):
    """Returns (ok, list of findings)."""
    issues = []

    for v in vehicles:
        b = v.body()
        if not interior.buffer(-MIN_WALL_GAP + 1).contains(b):
            d = b.distance(interior.exterior)
            if not interior.contains(b):
                issues.append(f"FAIL {v.name}: body outside the shed")
            else:
                issues.append(f"WARN {v.name}: body {d:.0f} mm from a wall "
                              f"(min {MIN_WALL_GAP:.0f})")
        for ob in obstacles:
            if b.intersects(ob):
                issues.append(f"FAIL {v.name}: body fouls a fixed obstacle")

    for i, a in enumerate(vehicles):
        for bb in vehicles[i + 1:]:
            ga = a.body().distance(bb.body())
            if a.body().intersects(bb.body()):
                issues.append(f"FAIL {a.name} / {bb.name}: bodies overlap")
            elif ga < MIN_BODY_GAP:
                issues.append(f"WARN {a.name} / {bb.name}: body gap {ga:.0f} mm "
                              f"(min {MIN_BODY_GAP:.0f})")

    # open doors must clear other vehicles' canopies and other open doors
    for i, a in enumerate(vehicles):
        if not (a.kind == "flagship" and a.doors):
            continue
        da = a.doors_poly()
        for j, bb in enumerate(vehicles):
            if i == j:
                continue
            if da.intersects(bb.canopy()):
                issues.append(f"FAIL {a.name} door fouls {bb.name} canopy")
            elif da.distance(bb.canopy()) < MIN_DOOR_GAP:
                issues.append(f"WARN {a.name} door {da.distance(bb.canopy()):.0f} mm "
                              f"from {bb.name} canopy")
            if j > i and bb.kind == "flagship" and bb.doors:
                if da.intersects(bb.doors_poly()):
                    issues.append(f"FAIL {a.name} / {bb.name}: open doors clash")
        if not interior.contains(da):
            issues.append(f"FAIL {a.name}: open door hits a wall")
        for ob in obstacles:
            if da.intersects(ob):
                issues.append(f"FAIL {a.name}: open door fouls a fixed obstacle")

    ok = not any(s.startswith("FAIL") for s in issues)
    if verbose:
        for s in issues:
            print("   ", s)
    return ok, issues


# --------------------------------------------------------------------------
# 5. KINEMATIC SWEPT PATH  (bicycle model, delta trike)
# --------------------------------------------------------------------------
def drive(path, step=100.0):
    """path: list of ('s', dist) straight or ('a', radius, sweep_deg) arc
    segments, plus ('start', x, y, hdg). Returns a list of (x, y, hdg) poses
    of the REAR AXLE CENTRE. Radius is to the rear-axle centre; positive
    radius = turn to the vehicle's left. Negative dist = reverse."""
    poses = []
    x = y = h = 0.0
    for seg in path:
        if seg[0] == "start":
            x, y, h = seg[1], seg[2], math.radians(seg[3])
            poses.append((x, y, math.degrees(h)))
        elif seg[0] == "s":
            d = seg[1]
            n = max(1, int(abs(d) / step))
            for _ in range(n):
                x -= (d / n) * math.sin(h)
                y += (d / n) * math.cos(h)
                poses.append((x, y, math.degrees(h)))
        elif seg[0] == "a":
            r, sweep = seg[1], math.radians(seg[2])
            n = max(1, int(abs(r * sweep) / step))
            # centre of rotation, 90 deg to the left of the heading
            for _ in range(n):
                cx = x - r * math.cos(h)
                cy = y - r * math.sin(h)
                dh = sweep / n
                nx = cx + (x - cx) * math.cos(dh) - (y - cy) * math.sin(dh)
                ny = cy + (x - cx) * math.sin(dh) + (y - cy) * math.cos(dh)
                x, y, h = nx, ny, h + dh
                poses.append((x, y, math.degrees(h)))
    return poses


def swept(poses, kind="flagship", every=1):
    polys = []
    for i, (x, y, h) in enumerate(poses):
        if i % every:
            continue
        polys.append(Vehicle("t", x, y, h, kind).body())
    return unary_union(polys)


def path_ok(poses, obstacles, interior=INTERIOR, clearance=150.0, kind="flagship"):
    sw = swept(poses, kind, every=2)
    bad = []
    if not interior.buffer(-clearance).contains(sw):
        bad.append("clips a wall")
    for nm, ob in obstacles:
        if sw.buffer(clearance).intersects(ob):
            bad.append(f"clips {nm}")
    return (not bad), bad, sw


def min_turn_radius(steer_deg=40.0):
    return Flagship.WHEELBASE / math.tan(math.radians(steer_deg))


def swept_band(steer_deg=40.0):
    """Inner and outer swept radii of the canopy corners, about the rear-axle
    turn centre."""
    R = min_turn_radius(steer_deg)
    out = math.hypot(R + Flagship.X_ROOF, Flagship.Y_ROOF_F)
    inn = R - Flagship.X_ROOF
    return inn, out, out - inn


if __name__ == "__main__":
    print(f"interior free floor      {FREE_FLOOR.area / 1e6:8.1f} m2")
    print(f"interior gross           {INTERIOR.area / 1e6:8.1f} m2")
    print(f"flagship L x W x H       {Flagship.LENGTH:.0f} x "
          f"{Flagship.WIDTH_CLOSED:.0f} x {Flagship.Z_ROOF_HI:.0f}")
    print(f"flagship doors open      {Flagship.WIDTH_OPEN:.0f} wide, "
          f"leaf {Flagship.DOOR_LEN:.0f} long, "
          f"{Flagship.Z_DOOR_LO:.0f}-{Flagship.Z_DOOR_HI:.0f} above slab")
    print(f"closed plan footprint    {Flagship.poly_body().area / 1e6:.2f} m2")
    print(f"open plan envelope       {Flagship.poly_envelope_open().area / 1e6:.2f} m2")
    for s in (35, 40, 45):
        i, o, b = swept_band(s)
        print(f"steer {s} deg: turn R {min_turn_radius(s):6.0f}  "
              f"swept {i:5.0f} - {o:5.0f}  band {b:5.0f}")
