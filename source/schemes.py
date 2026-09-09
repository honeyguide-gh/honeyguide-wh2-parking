"""WH2 parking, v0.6.0 - the two scenarios, read straight out of the CAD.

Source models, both saved 9 September 2026 in Hardware Designs:
    Warehouse Design V2.3dm   Scenario 1, Opening
    Warehouse Design V3.3dm   Scenario 2, Closing

Nothing here is fitted, rounded or re-derived. Every position was found by
locating each vehicle's three wheels in the model - the rear pair 960 mm
apart gives the axle centre, the single front wheel 2650 mm ahead gives the
heading - so the numbers are the model's own, to a tenth of a millimetre.

The fleet is nine: eight Flagships and HG3, the cargo vehicle. The same nine
appear in both scenarios, under the same names, standing in different places.

  Scenario 1, Opening.  Five Flagships inside with both doors open, loading:
  four on the diagonal and one on the north row. The other three Flagships
  and HG3 stand in the runway outside, pulled out before loading, doors shut.

  Scenario 2, Closing.  All nine inside for the night: four on the diagonal,
  four on the north row, HG3 by the gate. Doors open - the three that spent
  the day in the runway open theirs only once they are back in.
"""
from wh2 import (Flagship as F, Farm as Z, Bike as B, Veh, HALL, FREE,
                 FACILITIES, GATE)

# ---------------------------------------------------------- the CAD figures
# the diagonal row, identical in both models
DIAGONAL = [
    ("D1", 11085.0, 2318.0, 45.24),
    ("D2", 14579.1, 2318.0, 45.24),
    ("D3", 18082.6, 2318.0, 45.24),
    ("D4", 21573.8, 2318.0, 45.24),
]
# the north row, nose west; N1 is occupied in both scenarios, N2-N4 only at night
NORTH = [
    ("N1", 22960.7, 6817.5, 90.08),
    ("N2", 18432.3, 6817.5, 90.08),
    ("N3", 13885.9, 6817.5, 90.08),
    ("N4",  9285.3, 6817.5, 90.08),
]
# HG3, the cargo vehicle, inside at night: nearest the gate, last in and first out
HG3_IN = ("HG3", 4940.7, 6810.7, 90.08)

# the runway outside, nose north, doors shut. The three Flagships here are
# N2, N3 and N4 - the same vehicles, standing outside for the day.
RUNWAY = [
    ("N2", -12083.9, 6132.9, 0.08),
    ("N3", -14390.1, 6132.9, 0.08),
    ("N4", -16705.8, 6132.9, 0.08),
]
HG3_OUT = ("HG3", -10056.5, 6133.2, 0.08)

# HGF, the two CG125 bikes with rear boxes. They stand in the north-west
# corner, nose east, in exactly the same place in both models - rear-wheel
# centres read straight off the model.
HGF = [
    ("HGF1", 1593.9, 8141.8, 270.0),
    ("HGF2", 1593.9, 8714.2, 270.0),
]

BOTH = ("R", "L")


def _flag(spec, doors, parked=True, note=""):
    n, u, v, h = spec
    return Veh(n, u, v, h, doors=doors, label=n, note=note,
               doors_required=bool(doors))


def _hg3(spec, note=""):
    n, u, v, h = spec
    return Veh(n, u, v, h, doors=(), label=n, kind="farm", note=note)


def _bikes(note="parked in the north-west corner"):
    return [Veh(n, u, v, h, doors=(), label=n, kind="bike", note=note)
            for n, u, v, h in HGF]


# ------------------------------------------------------------- Scenario 1
def opening():
    """Warehouse Design V2. Five loading inside, four waiting in the runway."""
    vs = [_flag(s, BOTH, note="loading, both doors open") for s in DIAGONAL]
    vs.append(_flag(NORTH[0], BOTH, note="loading, both doors open"))
    vs += _bikes()
    for s in RUNWAY:
        vs.append(_flag(s, (), note="in the runway, doors shut"))
    vs.append(_hg3(HG3_OUT, note="in the runway, cargo vehicle"))
    return vs


def scheme_opening():
    return dict(key="open", name="Scenario 1 - Opening",
                vehicles=opening(),
                inside=[v.name for v in opening() if v.u > 0],
                aisle=2800.0, rows=1, scale=84.0, ox=256.2,
                tag="Five Flagships loading with both doors open, four waiting in the runway")


# ------------------------------------------------------------- Scenario 2
def closing():
    """Warehouse Design V3. All nine in for the night."""
    vs = [_flag(s, BOTH, note="parked for the night, both doors open")
          for s in DIAGONAL]
    vs += [_flag(s, BOTH, note="parked for the night, both doors open")
           for s in NORTH]
    vs.append(_hg3(HG3_IN, note="parked by the gate, cargo vehicle"))
    vs += _bikes()
    return vs


def scheme_closing():
    return dict(key="close", name="Scenario 2 - Closing",
                vehicles=closing(),
                inside=[v.name for v in closing()],
                aisle=2800.0, rows=1, scale=60.0, ox=85.5,
                tag="Every vehicle inside for the night, HG3 last in by the gate")


SCENARIOS = [scheme_opening, scheme_closing]
SCHEMES = SCENARIOS          # kept so the older tools still import cleanly


def inside_of(s):
    """The vehicles this scenario has standing inside the hall."""
    keep = set(s["inside"])
    return [v for v in s["vehicles"] if v.name in keep]


def outside_of(s):
    keep = set(s["inside"])
    return [v for v in s["vehicles"] if v.name not in keep]


if __name__ == "__main__":
    from wh2 import check
    from independent import free_to_leave
    import sequence as Q
    for f in SCENARIOS:
        s = f()
        ins = inside_of(s)
        print("=" * 72)
        print(f"{s['name']}   {len(ins)} inside, {len(s['vehicles'])-len(ins)} outside")
        ok, iss = check(ins, verbose=False)
        for x in iss:
            print("   ", x)
        n, bad, _ = free_to_leave(ins)
        print(f"   static {'ok' if ok else 'FAIL'}   any-order {n}/{len(ins)}")
