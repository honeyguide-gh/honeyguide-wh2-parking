# WH2 Tricycle Parking, v0.3.0

Hardware, 31 August 2026. Michael Kissi Danquah.
Built against `Hardware Designs/Warehouse Design.3dm` saved 31 Aug 2026 18:43.
All geometry read from that file at 1:1. Millimetres throughout.

---

## The answer first

**Nine Flagships: eight inside the hall and one in the workshop bay.**

That is down from the eleven I quoted in v0.2.0, and the reason is the thing
you asked for this round. You asked to see the vehicles leave. So I stopped
checking whether a layout *fits* and started checking whether it can be
*driven*, and two of the v0.2.0 schemes turned out to be arrangements you
could park into but never get out of.

Everything below has now been driven, not just drawn. Every vehicle in every
scheme was taken from its stand out through the gate by a manoeuvre planner
working on the real 4476 x 2028 footprint at the real 3158 mm turning radius,
with everything else still parked in its way and its doors still open. Any
layout that could not do that has been thrown out.

Take **Scheme 1, Two Streets** if capacity is the point: eight inside on two
lines, doors alternating south over the cold line and north over the weighing
zone, 1098 mm of walkway between them.

Take **Scheme 4, Rank, Aisle and Apron** if you want the same eight but with
four stands that stay independent through the day.

---

## What the drive check changed

**The third street is gone.** Three streets fit on paper. They cannot be
driven. The northern row would have to leave by threading the lane between
the middle row and the weighing scales, and that lane is 2196 mm for a
2028 mm vehicle: **84 mm a side**. Worse, its lead vehicle has 1200 mm of run
to make a 994 mm lane change, and a 994 mm lane change at a 3158 mm turning
radius needs **3400 mm**. There is no version of this that a driver can do.

**Street A had to come off the west wall.** In v0.2.0 the lead vehicle of the
long street parked with its nose 150 mm from the wall, on a line that is not
the gate line. It could never drive out: it had zero run in which to line up
on a 2750 mm opening. Street A now starts at u = 2700 so its lead vehicle has
the run it needs.

**The scales moved to the north wall.** Two 900 x 900 platforms now sit at
v = 8170, against the wall, with the operator working from the south. That
keeps the south half of the weighing zone open, which is what lets street A
open its doors there and what keeps the north strip usable as a lane.

**Capacity, honestly:**

| | v0.2.0 claimed | v0.3.0 verified |
|---|---|---|
| Best scheme, inside the hall | 10 | **8** |
| Plus the workshop bay | 11 | **9** |
| Schemes that could actually be driven out of | 1 of 3 | **4 of 4** |

---

## The four numbers everything follows from

| | Value | Where it comes from |
|---|---|---|
| Street pitch | **4170 mm** | canopy 4020 plus 150, nose tucked under the canopy ahead |
| Side by side pitch, one door open | **3232 mm** | door tip 2068 plus neighbour half width 1014 plus 150 |
| Open door height band | **1988 to 2243 mm** | leaf at 2167 to 2243, arms hang to 1988 |
| Rear axle turning radius | **3158 mm** | wheelbase 2650 at 40 degrees of steer |

The height band is still the second lever. An open door clears anything under
1900 mm, so it may swing over the fridges, the sinks, the crate rack and the
weighing zone. It may not swing over the office at 2640 mm, and it may never
swing over another Flagship, whose canopy starts at 2222 mm. Headroom under an
open door is 1988 mm.

---

## The four schemes

| | Scheme | Inside | Plus workshop | Access | Tightest point driving out | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Two Streets** | **8** | 1 | strict LIFO, two chains | 41 mm | **RECOMMENDED for capacity** |
| 2 | Two Streets and a Staging Apron | 7 | 1 | strict LIFO, 7 m apron at the gate | 41 mm | The easy one to live with |
| 3 | Rank and Aisle | 4 | 1 | fully independent | 58 mm | For a fleet of four or five |
| 4 | **Rank, Aisle and Apron** | **8** | 1 | 4 independent, 4 LIFO | 58 mm | **RECOMMENDED for flexibility** |

"Tightest point driving out" is the smallest gap between any part of a moving
vehicle and anything else, anywhere in the whole departure sequence. These are
paint-line clearances at one instant of one turn, not gaps to walk through.

### Scheme 1, Two Streets

- **Street A**, five stands at v = 5700, doors **north** over the weighing
  zone. Starts at u = 2700 so the lead vehicle has run to line up on the gate.
- **Street B**, three stands at v = 2574, doors **south** over the fridges,
  sinks and crate rack. Held off by the office corner and the third fridge.
- **1098 mm of walkway** between the rows. A real gap, not a painted line.
- Out in the morning: **all of A, west to east, then B, east to west.**
  B leaves through A's lane, so A has to be clear first.
- Back in at night: the reverse.

### Scheme 4, Rank, Aisle and Apron

- **K1 to K4**, nose-in stands at 3232 mm centres, tails on the 1560 line,
  doors all east, served by a **2934 mm drive aisle**.
- **P1 to P3** stand in the aisle itself overnight, doors north, 150 mm off
  the noses of the rank and 221 mm off the scales.
- **G1** stands on the gate line, last in and first out.
- Out in the morning: **G1, then K1 to K4, then P1 to P3.** By nine the aisle
  is clear and the building is Scheme 3 again for the rest of the day.

### Why the echelon still does not work

Your angled row packs the length well at 3494 mm per vehicle, but in an
echelon the neighbour sits 2460 mm away perpendicular to the axis and one open
door needs 3077 mm. To open even the leading door the pitch has to go to
3750 mm, and at that point a straight street at 4170 mm holds the same number
in less width.

---

## The equipment

- **Weighing and loading:** two 900 x 900 platform scales with indicator
  columns, at u = 6500 and 8800, against the north wall at v = 8170, operator
  working from the south with 600 mm clear.
- **Wash area:** a two bowl food grade stainless sink table on the full
  1477 x 830 footprint, 900 mm working height with a 500 mm splashback. Bowls
  500 x 550 x 300 deep.
- **Workshop:** a single 3000 x 600 bench along the short south wall with a
  vice, and the plant ranged along the long west wall: pillar drill, bench
  grinder on a stand, welder and trolley, compressor, and a tool board and
  parts rack.

**One workshop finding, unchanged.** The bay is 4896 mm deep. A 600 mm bench
plus 600 mm of working clearance leaves 3696 mm against a 4476 mm vehicle, so
the vehicle stands 780 mm proud of the canopy line. The north side is open so
that is acceptable, but the tail is out in the weather. Either accept it,
shorten the bench to 450 mm deep, or move the bench to the west wall.

---

## How the drive check works

1. **Occupancy.** The hall, the yard, the fittings and every parked vehicle
   are rasterised on a 50 mm grid, in three height bands: the low chassis and
   forks to 1513, the cargo module 764 to 2372, the canopy 2222 to 2528. That
   is what lets a nose tuck under the canopy in front and slide under an open
   door, exactly as it does when parked.
2. **Search.** Hybrid A star over that grid at 2 degree heading resolution,
   forward and reverse, at curvatures up to the 3158 mm limit, with a penalty
   on reversing and on changing direction. A 75 mm driving margin is carried
   through the search.
3. **Order.** Vehicles are taken out one at a time, in the order a yard would
   use, and each one is planned against everything still parked. If nobody can
   move, the layout is rejected.
4. **Proof.** Every planned path is then replayed pose by pose in exact
   polygon geometry, not on the grid. The tightest clearance found is the
   number quoted in the table above. All four schemes come back clean.

---

## Floor marking

| Colour | Width | Used for |
|---|---|---|
| Yellow | 100 mm | Lead-in lines, lane edges and the walkway |
| Yellow bar | 210 mm | Wheel stop position at the head of each stand |
| White | 75 mm | Vehicle stand outline and stand number |
| Blue | 100 mm | Weighing and loading zone boundary |
| Green | 75 mm | 600 mm working strip at every fitting |
| Black and yellow 45 degree hatch | band | Door swing zone. Keep clear. 1988 mm headroom |
| Red and white 45 degree hatch | band | Fire point and electrical panel, 900 mm clear |

Marking follows OSHA 1910.22(b) for aisles and ANSI Z535.1 for the safety
colours. Two pack epoxy or chlorinated rubber, not road paint, on a swept,
degreased and primed slab.

---

## Deliverables

| File | What it is |
|---|---|
| `WH2 Parking Scheme 1 - Two Streets.pdf` | Marked floor plan, 1:56 at A2, with the marking schedule, daily sequence and notes |
| `WH2 Parking Scheme 2 - Two Streets and a Staging Apron.pdf` | as above |
| `WH2 Parking Scheme 3 - Rank and Aisle.pdf` | as above |
| `WH2 Parking Scheme 4 - Rank, Aisle and Apron.pdf` | as above |
| `wh2-parking.html` | Interactive 3D of all four schemes, with **Play arrival** and **Play exit**. The vehicles are the real CAD mesh out of the Rhino file, doors animated |
| `trike_mesh.json` | The decimated Flagship mesh, quantised, in the vehicle frame |
| `source/` | The Python that produced all of it: `wh2.py` dimensions, `planner.py` manoeuvres, `sequence.py` order, `audit_paths.py` proof, `plan.py` drawings, `export.py` and `build.py` the 3D |

---

## Next

1. Decide between Scheme 1 and Scheme 4. Both hold nine. Scheme 1 is simpler
   to mark and to teach; Scheme 4 keeps four stands independent all day.
2. Confirm the scales can sit against the north wall with the operator working
   from the south. If they cannot, the north strip loses its lane and Scheme 1
   drops a vehicle.
3. Confirm the wash area is a two bowl sink, not three.
4. Confirm the workshop bench depth and which wall it goes on.
5. Measure a real HG vehicle, and measure the **steering lock**. Every
   manoeuvre here follows from a 2650 mm wheelbase at 40 degrees. If the real
   lock is better than that, the tight moves get easier; if it is worse, the
   rank turns need re-checking.
6. Chalk out street A and drive HG1 in and out of the gate before any paint.

---

## Change log

**v0.3.0, 31 Aug 2026.** Drivability became a hard constraint. Added a
manoeuvre planner and an exact geometric replay; every departure in every
scheme is now a path a driver could follow. Dropped the third street and the
dead end stand, which fit but could not be driven out of. Moved the scales to
the north wall and street A off the west wall. Added Scheme 4 at eight inside
with four independent stands. Fixed the walls, which were floating one storey
above the slab in the 3D. Added a **Play exit** control to the viewer.

**v0.2.0, 31 Aug 2026.** Rebuilt against the revised warehouse model. New
gate, office, fridges, wash area, crate rack, weighing zone and workshop. One
door open on every parked vehicle, 600 mm at every fitting. Vehicles in the 3D
became the real CAD mesh.

**v0.1.0, 31 Aug 2026.** First issue against the previous model.
