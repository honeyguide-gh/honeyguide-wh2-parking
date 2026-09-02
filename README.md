# WH2 Tricycle Parking

Parking layout study for the Honeyguide WH2 warehouse, Accra. Four schemes,
each checked twice: that it fits, and that a driver can get every vehicle back
out through the gate.

**Live: https://honeyguide-gh.github.io/honeyguide-wh2-parking/**

Drag to orbit, right-drag to pan, scroll to zoom. **Play arrival** fills the
building; **Play exit** empties it. Both run the real planned manoeuvres, not
animations drawn by hand.

## What the two operating constraints cost

The review asked for both doors open on every parked vehicle, so they can all
load at once, and any vehicle in or out in any order, so the morning juggling
stops. Both are achievable. Together they cost five vehicles.

| Flagships inside the hall | Fixed order, as now | Any order, nobody moves |
|---|---|---|
| **One door open** | **8** | 4 |
| **Both doors open** | **6** | **3** |

Any-order access is the expensive constraint, not both doors. Nose to tail,
both doors open changes nothing at all: a door leaf is 1976 mm and the street
pitch is 4170, so two leaves in a line never meet.

## The schemes

| | Scheme | Inside | Both doors | Any order | Tightest point driving out |
|---|---|---|---|---|---|
| 1 | Diagonal Three | 3 | yes | **yes** | 45 mm |
| 2 | Two Streets, Both Doors | 6 | yes | no | 41 mm |
| 3 | Two Streets, One Door | 8 | no | no | 41 mm |
| 4 | Three In, Seven Out | 3 + 7 in the yard | yes | **yes** | 45 mm |

Scheme 1 is the review's constraints met exactly: three stands at 145° on a
4450 mm pitch, both doors open on all three, any of them out at any time.

**Why four inside is impossible rather than merely tight.** The stand band has
14.9 m of usable length once the office, the third fridge and its working strip
are subtracted, and the closest two both-doors-open vehicles can ever be, at
any angle from 0° to 90°, is 3950 mm. Four stands need 15.8 m.

**The diagonal is the right instinct.** Two both-doors-open vehicles staggered
3650 mm along their own axis sit only 2200 mm apart across, against 4300 mm
side by side. That is the tightest packing available.

## How the checks work

The hall, the fittings and every parked vehicle are rasterised on a 50 mm grid
in three height bands — low chassis and forks to 1513, cargo module 764 to
2372, canopy 2222 to 2528 — which is what lets a nose tuck under the canopy in
front and slide under an open door. A hybrid A\* search then plans each vehicle
out of the gate at the real 3158 mm rear-axle turning radius, forward and
reverse, against everything still parked with its doors open. Every path is
finally replayed pose by pose in exact polygon geometry; the tightest clearance
found is the number in the table.

## The vehicles

| | Flagship | Farm vehicle (Zusha cargo-trike) |
|---|---|---|
| Length | 4476 mm | 4373 mm |
| Width | 2028 mm | 1813 mm |
| Height | 2528 mm | 1953 mm |
| Doors | two, 4135 mm overall when open | none, open flatbed |
| Wheelbase | 2650 mm | 2650 mm |

Same chassis, so both turn identically.

## What is here

- `index.html` — the interactive 3D. Self-contained: three.js is vendored
  alongside it, so the page works on a slow or filtered connection.
- `plans/` — the four marked floor plans, PDF and SVG, 1:56 at A2.
- `docs/` — the write-up, including what each constraint costs and the open
  questions.
- `source/` — the Python that produced all of it.
- `offline/` — the same simulation as one file with three.js inlined.
  Download it, double-click it, works with no internet at all.

## Rebuilding

```
pip install shapely numpy pillow scipy
cd source
python plan.py            # the floor plans
python export.py          # the scene, planning every manoeuvre
python build.py           # the viewer
python audit_paths.py     # the exact geometric proof
```

Geometry read at 1:1 from `Hardware Designs/Warehouse Design.3dm`, saved
2 Sep 2026 01:56. Millimetres throughout.

---

Honeyguide Ghana Ltd, Hardware. v0.4.0, 2 September 2026.
