# WH2 Tricycle Parking

Parking layout study for the Honeyguide WH2 warehouse, Accra. One simulation,
two scenarios — Opening and Closing — read straight out of the Rhino models
and checked twice: that they fit, and that a driver can get every vehicle back
out through the gate.

**Live: https://honeyguide-gh.github.io/honeyguide-wh2-parking/**

Drag to orbit, right-drag to pan, scroll to zoom. Switch between **Scenario 1
· Opening** and **Scenario 2 · Closing** in the header. **Play arrival** fills
the building; **Play exit** empties it. Both run the real planned manoeuvres,
not animations drawn by hand.

## The two scenarios

|  | Scenario 1, Opening | Scenario 2, Closing |
|---|---|---|
| Flagships inside | **5** | **8** |
| HG3, the cargo vehicle | in the runway | inside, by the gate |
| Waiting in the runway | 4 | none |
| Both doors open | the five inside | all eight |
| Any vehicle, any order | **yes, all five** | no, a fixed order |
| Tightest point driving out | 60 mm | 60 mm |

Nine vehicles all day: eight Flagships and HG3. At night they are all inside.
In the morning HG3 and three Flagships pull out to the runway so the five that
stay can open both doors and load together, then leave in any order.

## The three tight points

**The diagonal's doors overlap by 21 mm — of height, not of plan.** At the
3494 mm pitch each open door sweeps about 0.63 m² over the next vehicle's
canopy, but the leaf itself clears by 55 mm; it is the door's upper arm,
topping out at 2243 mm against a canopy underside of 2222 mm, that fouls.
Nothing touches at body height. So either drop that arm 25 mm, or run the
rule that D2 shuts its north door to let D1 out, D3 for D2, D4 for D3.

**HG3 stops 101 mm short of the check-in desk overnight.** Fine at night;
move it 500 mm east if anyone works late.

**The north rank leaves 593 mm in front of the crate stacks**, seven short of
the 600 mm working strip. The fridges are comfortable at 723 to 807 mm.

## How the positions were read

Every trike is exploded into hundreds of part layers in the CAD, so neither
layer names nor block instances identify a vehicle. Instead each wheel is
found by its bounding-box signature, and a pair 960 mm apart with a third
2650 mm ahead of their midpoint fixes a vehicle's rear-axle centre and heading
exactly. The method is rotation-invariant, so the 45.24° diagonal is as
precise as the square-on rows. Nothing in this repository is fitted or
rounded.

## What is here

- `index.html` — the simulation. Three.js is vendored, so it works on a phone
  on a bad connection.
- `offline/` — the same page with everything inlined, one file, no network.
- `plans/` — the two marked-up floor plans, A2, as PDF and editable SVG.
- `docs/` — the write-up.
- `source/` — the geometry engine, the manoeuvre planner and the exact
  polygon audit that every figure above comes from.

Built against `Warehouse Design V2.3dm` and `Warehouse Design V3.3dm`,
9 September 2026. All dimensions in millimetres.
