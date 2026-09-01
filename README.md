# WH2 Tricycle Parking

Parking layout study for the Honeyguide WH2 warehouse, Accra. Four schemes,
each one checked twice: that it fits, and that a driver can get every vehicle
back out through the gate.

**Live: https://honeyguide-gh.github.io/honeyguide-wh2-parking/**

Drag to orbit, right-drag to pan, scroll to zoom. **Play arrival** fills the
building; **Play exit** empties it. Both run the real planned manoeuvres, not
animations drawn by hand.

## The schemes

| | Scheme | Inside | Plus workshop | Access | Tightest point driving out |
|---|---|---|---|---|---|
| 1 | Two Streets | 8 | 1 | strict LIFO, two chains | 41 mm |
| 2 | Two Streets and a Staging Apron | 7 | 1 | strict LIFO, 7 m apron at the gate | 41 mm |
| 3 | Rank and Aisle | 4 | 1 | fully independent | 58 mm |
| 4 | Rank, Aisle and Apron | 8 | 1 | 4 independent, 4 LIFO | 58 mm |

Capacity is **nine**: eight inside the hall plus one in the workshop bay. Every
parked vehicle has at least one door open, and every fitting keeps a 600 mm
working strip.

## How the drive check works

The hall, the fittings and every parked vehicle are rasterised on a 50 mm grid
in three height bands — low chassis and forks to 1513, cargo module 764 to
2372, canopy 2222 to 2528 — which is what lets a nose tuck under the canopy in
front and slide under an open door. A hybrid A\* search then plans each vehicle
out of the gate at the real 3158 mm rear-axle turning radius, forward and
reverse, against everything still parked. Every path is finally replayed pose
by pose in exact polygon geometry; the tightest clearance found is the number
in the table.

Two arrangements from the previous version did not survive this. A third
street fits but cannot be driven out of: it would have to thread a 2196 mm
lane with a 2028 mm vehicle. And a street whose lead vehicle parks against the
west wall has no run in which to line up on the gate.

## What is here

- `index.html` — the interactive 3D. Self-contained: three.js is vendored
  alongside it, so the page works on a slow or filtered connection, and offline
  if you save it.
- `plans/` — the four marked floor plans, PDF and SVG, 1:56 at A2.
- `docs/` — the write-up, including the numbers everything follows from.
- `source/` — the Python that produced all of it.
- `offline/` — the same simulation as one 1.07 MB file with three.js inlined.
  Download it, double-click it, works with no internet at all. Handy at the
  warehouse.

## Rebuilding

```
pip install shapely numpy pillow
cd source
python plan.py      # the floor plans
python export.py    # the scene, planning every manoeuvre
python build.py     # the viewer
python audit_paths.py   # the exact geometric proof
```

Geometry read at 1:1 from `Hardware Designs/Warehouse Design.3dm`, saved
31 Aug 2026 18:43. Millimetres throughout.

---

Honeyguide Ghana Ltd, Hardware. v0.3.0, 31 August 2026.
