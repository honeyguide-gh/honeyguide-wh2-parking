# WH2 Tricycle Parking: Opening and Closing

Hardware, 9 September 2026. Michael Kissi Danquah.
Built against `Hardware Designs/Warehouse Design V2.3dm` (Opening) and
`Warehouse Design V3.3dm` (Closing), both saved 9 Sep 2026.
All geometry read from those files at 1:1. Millimetres throughout.

---

## The answer first

Eleven vehicles, one building, two scenarios, and they work as one day:
**everything inside at night, four pulled out to the runway in the morning,
five Flagships loading inside with both doors open.**

| | Scenario 1, Opening | Scenario 2, Closing |
|---|---|---|
| Flagships inside | **5** | **8** |
| Also inside | two HGF bikes | HG3 and two HGF bikes |
| Waiting in the runway | HG3 and three Flagships | none |
| Both doors open | the five Flagships | all eight |
| Any vehicle, any order | **yes, all seven** | no, a fixed order |
| Tightest point driving out | 60 mm | 30 mm |

Every vehicle in both scenarios was planned out of the gate with the others
still standing, then replayed pose by pose in exact polygon geometry. Nothing
here is a sketch.

---

## What changed in this issue

**The workshop is gone.** The outdoor bay west of the shed and everything in
it has been removed. The shop is now the bench run attached to the office's
east face, inside the hall, exactly where the models put it: u 7299 to 7970,
v 0 to 2438, with the shop equipment beside it.

**Check-in / check-out is where the models draw it.** It is a floor zone,
4400 by 1800, marked on the slab at u 3960 to 8360, v 7318 to 9118. Both V2
and V3 carry that rectangle. It is a marking, not a fitting, so vehicles can
stand on it, and two of them do (see below).

**HG3 and the two HGF bikes are real geometry now.** All three are drawn from
the models' own meshes rather than from boxes, and all three drive in and out
in the arrival and exit runs alongside the Flagships.

**HG3 turns out to be smaller than the block bbox suggested.** Measured from
the 237 chassis parts actually placed in V2: **4207 long, 1549 wide, 1513
tall**, not the 4373 by 1813 by 1953 quoted in v0.6.0. That earlier figure
came from a bounding box that caught two stray door leaves; this one comes
from the parts themselves.

**And a useful discovery.** Every Flagship in the model is built on the very
same Zusha chassis as HG3: the market module, the canopy and the two doors
sit on top of it. HG3 is that chassis on its own, which is why it turns
identically and stops 1015 mm below a Flagship's roof.

---

## The four things that are tight

**1. The diagonal's doors overlap, by 21 mm of height.** At a 3494 mm pitch
on a 45.2 degree row, each open door sweeps about 0.63 m2 over the next
vehicle's canopy. Where in the air that happens is the whole story:

| | Height above the slab |
|---|---|
| Open door, underside of the arms | 1988 |
| Door leaf, top | 2167 |
| **Neighbouring canopy, underside** | **2222** |
| **Open door assembly, top** | **2243** |

The leaf clears the canopy by 55 mm. It is the door's upper arm, standing
76 mm proud of the leaf, that fouls, by 21 mm. Nothing at body height touches
anything: the module to door overlap is exactly zero on every pair. So there
are two ways out, and neither is a re-layout:

- lower the door's upper arm by 25 mm, or lift the canopy by 25 mm, and all
  four diagonal stands hold both doors open at once; or
- run it as an operating rule: **to let D1 out, D2 shuts its north door; D2
  needs D3's; D3 needs D4's.** D4 and N1 need nothing from anybody. That is
  one door for a few seconds, not the morning shuffle you are trying to end.

**2. The two HGF bikes clash at the handlebars.** They stand 572 mm apart and
measure 651 mm across the bars, so as drawn the bars overlap by **78 mm** at
1051 mm above the slab. Below bar height the bikes are 97 mm apart and fine.
Give the stands 700 mm, or stagger one bike 300 mm along the wall.

**3. HG3 and N4 park over the check-in zone.** HG3 covers 0.6 m2 of it and
stops 101 mm short of its south edge; N4 covers 0.9 m2. Overnight that costs
nothing. If anyone works late at check-in, HG3 wants to be about 500 mm
further east.

**4. The north rank leaves 593 mm in front of the crates.** Seven millimetres
under the 600 you want. Call it 600. The fridges are comfortable at 723 to
807 mm.

One clarification on that last figure, because it changes the picture: the
canopy edge sits 297 to 427 mm from those fittings, but it is 2222 mm up, so
a person stands under it. The figures above are measured against the cargo
module, which is what actually takes the space at working height.

---

## What each scenario asks of the operators

### Scenario 1, Opening

Five Flagships inside, both doors open, loading together, and the two HGF
bikes in the north-west corner. **Any of the seven leaves at any time and
none of the others moves.** Each departure was planned with the other six
standing and their doors open; the tightest point on any of those runs is
60 mm.

HG3 and three Flagships wait in the runway with their doors shut. They come
in as the first five clear, load, and follow them out. That is the two-wave
day, and it runs without anybody juggling.

### Scenario 2, Closing

All eleven in. The order is fixed and it has to be, for three independent
reasons:

- the north rank stands nose to tail with **509 mm between canopies** at the
  tightest, so it fills deepest first and empties shallowest first;
- HG3 parks across the gate, so it is last in and first out;
- the bikes park in the corner behind HG3 and N4, so they are first out in
  the morning and last in at night.

Evening: D4, D3, D2, D1, then N1, N2, N3, N4, then HG3, then the two bikes.
Morning: that list backwards.

The three Flagships that spend the day in the runway open their doors only
once they are back in, which is what you asked for and what V3 shows.

---

## The fittings, as the models now have them

| | Position | Height |
|---|---|---|
| Office | u 0 to 7360, v 0 to 3560 | 2640 |
| Shop bench (the workshop) | u 7299 to 7970, v 0 to 2438 | 900 |
| Shop equipment | u 8006 to 8641, v 111 to 755 | 1265 |
| Check-in / check-out | u 3960 to 8360, v 7318 to 9118 | floor zone |
| Fridge 1 | u 8878 to 10658, v 8260 to 9070 | 860 |
| Fridge 2 | u 10702 to 12652, v 8240 to 9070 | 860 |
| Fridge 3 | u 12690 to 14640, v 8240 to 9070 | 860 |
| Crate stacks, five | u 16985 to 20392, v 8110 to 9120 | 600 |

Site frame: u east from the inside face of the west wall, v north from the
inside face of the south wall, z up from the slab.

---

## The fleet, as measured

| | Flagship | HG3 | HGF |
|---|---|---|---|
| Length | 4476 | **4207** | **2054** |
| Width | 2028 | **1549** | 487 body, **651 bars** |
| Height | 2528 | **1513** | **1404** |
| Wheelbase | 2650 | 2650 | **1341** |
| Doors | two, 4135 open | none | none |
| Turning radius, rear axle | 3158 | 3158 | **1341** |

The bikes are planned with a 15 mm driving margin rather than the 75 mm a
trike gets, because a bike is placed far more finely and can be walked the
last stretch. HGF2, the one nearest the north wall, stands 80 mm off it; its
run out clears everything by 65 mm on its own, and by 30 mm with the rest of
the night's formation still standing. Both figures come from the exact replay,
not the grid.

---

## How the vehicle positions were read

Not by eye, and not fitted. Each trike is exploded into hundreds of part
layers in the model, so neither layer names nor block instances identify a
vehicle. Instead, every wheel in the file was found by its bounding-box
signature, a disc 480 to 900 mm across, as tall as it is wide, sitting low.
For every pair of wheels 900 to 1030 mm apart (the 960 mm rear track), a third
wheel 2550 to 2750 mm ahead of their midpoint (the 2650 mm wheelbase) confirms
a vehicle and fixes both its rear-axle centre and its heading exactly. The
method is rotation invariant, so the 45.24 degree diagonal is as precise as
the square-on rows. The bikes were found the same way, from their own rear
wheels.

As a check, the canopy slats were clustered independently and compared with
where each vehicle's canopy should be. All nine trikes in both models agree to
within a tenth of a millimetre of the same constant offset, which is the
signature of a systematic bias in the check rather than any error in the
positions.

**One thing to look at in V2.** Two orphan door leaves are floating in the
yard at about u -9100, v 5800, 1988 to 2243 mm up, with no vehicle under them.
They are almost certainly left over from an earlier arrangement.

---

## Open questions

1. **The door arm.** Everything in finding 1 turns on the open door topping
   out at 2243 mm. Measure it on a real vehicle. If the arm is 25 mm lower
   than the CAD, all four diagonal stands hold both doors open with no change
   to the layout at all.
2. **The bike stands.** 700 mm centres, or a 300 mm stagger, and the bars stop
   fouling. Which suits the corner better is a question for whoever parks
   there.
3. **The steering lock.** Every trike manoeuvre here follows from 40 degrees.
   If the real lock is better, the tight moves get easier.
4. **The runway.** The site model still carries no yard boundary, so the four
   waiting stands are drawn where V2 puts them, on paving that stops 2540 mm
   west of the shed wall in the CAD. Chalk it out before painting it.

---

## Change log

**v0.7.0, 9 Sep 2026.** Workshop removed. Check-in / check-out moved to the
floor zone the models actually carry. HG3 and both HGF bikes modelled from the
models' own meshes and added to the arrival and exit runs. HG3 re-measured
from its placed parts. Handlebar clash, check-in overparking and the orphan
door leaves reported.

**v0.6.0, 9 Sep 2026.** Rebuilt as one simulation with two scenarios, Opening
and Closing, read from Warehouse Design V2 and V3. Working clearance measured
against the cargo module rather than the canopy footprint. The five earlier
schemes retired.

**v0.5.0, 8 Sep 2026.** The 8 September Rhino layout added as drawn.

**v0.4.0, 2 Sep 2026.** Both doors open and any-order access made hard
constraints after the first review; cargo vehicle added.

**v0.3.0, 31 Aug 2026.** Drivability became a hard constraint: a manoeuvre
planner and an exact geometric replay.

**v0.2.0, 31 Aug 2026.** Rebuilt against the revised warehouse model.

**v0.1.0, 31 Aug 2026.** First issue.

---

*Typeface note: the simulation and sheets are set in Source Sans 3, the
documented fallback for Gibson, which is not available as a web font.*
