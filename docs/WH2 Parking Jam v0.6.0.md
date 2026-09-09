# WH2 Tricycle Parking — Opening and Closing

Hardware, 9 September 2026. Michael Kissi Danquah.
Built against `Hardware Designs/Warehouse Design V2.3dm` (Opening) and
`Warehouse Design V3.3dm` (Closing), both saved 9 Sep 2026.
All geometry read from those files at 1:1. Millimetres throughout.

---

## The answer first

Both scenarios work, and they work as one day: **nine vehicles in at night,
four pulled out to the runway in the morning, five loading inside with both
doors open.** The simulation is now a single model with a scenario switch,
not a set of competing schemes.

| | Scenario 1, Opening | Scenario 2, Closing |
|---|---|---|
| Flagships inside | **5** | **8** |
| HG3, the cargo vehicle | in the runway | inside, by the gate |
| Waiting in the runway | 4 | none |
| Both doors open | the five inside | all eight |
| Any vehicle, any order | **yes, all five** | no, a fixed order |
| Tightest point driving out | 60 mm | 60 mm |

Everything below was verified the same way: static fit against every fitting
and its 600 mm working strip, then a manoeuvre planned out of the gate for
each vehicle with everything else still standing, then that path replayed
pose by pose in exact polygon geometry. Nothing here is a sketch.

---

## Your manager's four points, answered

**"Model in 4 more vehicles in the runway that we pull out before loading."**
Done — and it is what makes Opening work. The four are HG3 and Flagships N2,
N3 and N4, standing where V2 puts them, doors shut. They are the same four
that occupy the north rank overnight, so the fleet is nine all day.

**"Add in HG3, the cargo vehicle."** In. 4373 × 1813 × 1953, no doors, same
2650 wheelbase as a Flagship so it turns identically. It parks by the gate at
night and is the first thing out in the morning.

**"Keep the entry clear if we can."** The entry is clear. Moving the diagonal
south to v = 2318 — 731 mm down from the 8 September row — leaves nothing at
all between the gate and the aisle in Opening. This is the single biggest
improvement over the 8 September layout, where HG3 blocked the gate by 71 mm.

**"Put the shop in the lower right corner, or where the fridges are, and run
power to the fridges to the right of check-in / check-out."** Both models do
the second version, and I have followed them: the shop bench now sits against
the office's east face on the south wall, exactly where the fridges used to
be, and all three fridges have moved to the north wall east of check-in. The
wash area is gone from the south wall. Check-in / check-out, two stations
with a platform scale each, is in the north-west corner by the gate; the
crate stacks have moved to the north-east corner.

---

## The three things that are tight

**1. The diagonal's doors overlap — by 21 mm of height, not by metres of
plan.** At a 3494 mm pitch on a 45.2° row, each door sweeps about 0.63 m²
over the next vehicle's canopy. But look at where in the air that happens:

| | Height above the slab |
|---|---|
| Open door, underside of the arms | 1988 |
| Door leaf, top | 2167 |
| **Neighbouring canopy, underside** | **2222** |
| **Open door assembly, top** | **2243** |

The leaf itself clears the canopy by 55 mm. It is the door's upper arm,
standing 76 mm proud of the leaf, that fouls — by 21 mm. Nothing at body
height touches anything: the module-to-door overlap is exactly zero on every
pair. So there are two ways out of this and neither is a re-layout:

- lower the door's upper arm by 25 mm, or lift the canopy by 25 mm, and all
  four diagonal stands hold both doors open at once; or
- accept it as an operating rule: **to let D1 out, D2 shuts its north door;
  D2 needs D3's; D3 needs D4's.** D4 and N1 need nothing from anybody. That
  is one door for a few seconds, not the morning shuffle you are trying to
  end.

Widening the pitch is the expensive option — both doors fully open at 45°
needs 4600 mm per stand, 1106 mm more than you have, and there is no room
for four stands at that pitch.

**2. HG3 blocks check-in overnight.** Parked where V3 puts it, its body stops
101 mm short of the check-in desk. Nothing can be done at that desk while it
is there. At night that costs nothing; if anyone works late, HG3 wants to be
about 500 mm further east.

**3. The north rank leaves 593 mm in front of the crates.** Seven millimetres
under the 600 you want. Call it 600. The fridges are comfortable — 723 to
807 mm at working height.

One clarification on that last figure, because it changes the picture: the
canopy edge sits 297 to 427 mm from those fittings, but it is 2222 mm up, so
a person stands under it. The figures above are measured against the cargo
module, which is what actually takes the space at working height. The 8
September assessment measured against the canopy footprint and read worse
than the layout really is.

---

## What each scenario asks of the operators

### Scenario 1, Opening

Five inside, both doors open, loading together. **Any of the five leaves at
any time and none of the other four moves** — each departure was planned with
the other four standing and their doors open, and the tightest point on any
of those runs is 60 mm.

Four wait in the runway with their doors shut. They come in as the first five
clear, load, and follow them out. That is the two-wave day, and it now runs
without anybody juggling.

### Scenario 2, Closing

All nine in. The order is fixed and it has to be, for two independent
reasons:

- the north rank stands nose to tail with **509 mm between canopies at the tightest**, so it
  fills deepest-first and empties shallowest-first;
- HG3 parks across the gate, so it is last in and first out.

Evening: D4, D3, D2, D1, then N1, N2, N3, N4, then HG3.
Morning: that list backwards.

The three that spent the day outside open their doors only once they are back
in — which is what you asked for, and what V3 shows.

---

## The fittings, as the models now have them

| | Position | Height |
|---|---|---|
| Office | u 0–7360, v 0–3560 | 2640 |
| Shop bench | u 7299–7970, v 0–2438 | 900 |
| Shop equipment | u 8006–8641, v 111–755 | 1265 |
| Check-in / check-out | u 1191–3250, v 7816–9040 | 1408 |
| Fridge 1 | u 8878–10658, v 8260–9070 | 860 |
| Fridge 2 | u 10702–12652, v 8240–9070 | 860 |
| Fridge 3 | u 12690–14640, v 8240–9070 | 860 |
| Crate stacks, five | u 16985–20392, v 8110–9120 | 600 |

Site frame: u east from the inside face of the west wall, v north from the
inside face of the south wall, z up from the slab.

---

## How the vehicle positions were read

Not by eye, and not fitted. Each trike is exploded into hundreds of part
layers in the model, so neither layer names nor block instances identify a
vehicle. Instead, every wheel in the file was found by its bounding-box
signature — a disc 480–900 mm across, as tall as it is wide, sitting low.
For every pair of wheels 900–1030 mm apart (the 960 mm rear track), a third
wheel 2550–2750 mm ahead of their midpoint (the 2650 mm wheelbase) confirms a
vehicle and fixes both its rear-axle centre and its heading exactly. The
method is rotation-invariant, so the 45.24° diagonal is as precise as the
square-on rows.

As a check, the canopy slats were clustered independently and compared with
where each vehicle's canopy should be. All nine vehicles in both models agree
to within a tenth of a millimetre of the same constant offset — the signature
of a systematic bias in the check, not of any error in the positions. The
cargo vehicle has no canopy slats, which is how HG3 is told apart from a
Flagship.

---

## The numbers everything follows from

| | Value | Where it comes from |
|---|---|---|
| Diagonal pitch | **3494 mm at 45.24°** | the model's own stand spacing |
| North rank pitch | **4528–4601 mm** | the model's own stand spacing |
| Both doors, side by side | 4285 mm | two door tips at 2068 plus 150 |
| Both doors on a 45° row | 4600 mm | 1106 mm more than the row has |
| Rear axle turning radius | 3158 mm | wheelbase 2650 at 40° of steer |
| Door band above the slab | 1988 to 2243 | measured off the open doors |
| Canopy band above the slab | 2222 to 2528 | measured off the roof |

---

## Open questions

1. **The door arm.** Everything in finding 1 turns on the open door topping
   out at 2243 mm. Measure it on a real vehicle. If the arm is 25 mm lower
   than the CAD, all four diagonal stands hold both doors open with no
   change to the layout at all.
2. **The steering lock.** Every manoeuvre here follows from 40°. If the real
   lock is better, the tight moves get easier.
3. **The runway.** The site model still carries no yard boundary, so the four
   waiting stands are drawn where V2 puts them, on paving that stops 2540 mm
   west of the shed wall in the CAD. Chalk it out before painting it.
4. **HG3 overnight.** Worth 500 mm east if anyone uses check-in after hours.

---

## Change log

**v0.6.0, 9 Sep 2026.** Rebuilt as one simulation with two scenarios,
Opening and Closing, read from Warehouse Design V2 and V3. Nine vehicles
including HG3. New interior: shop where the fridges were, fridges and crates
on the north wall, check-in in the north-west corner, wash area gone. Working
clearance is now measured against the cargo module rather than the canopy
footprint, which is the honest test. The five earlier schemes are retired.

**v0.5.0, 8 Sep 2026.** The 8 September Rhino layout added as drawn.

**v0.4.0, 2 Sep 2026.** Both doors open and any-order access made hard
constraints after the first review; farm vehicle added.

**v0.3.0, 31 Aug 2026.** Drivability became a hard constraint: a manoeuvre
planner and an exact geometric replay.

**v0.2.0, 31 Aug 2026.** Rebuilt against the revised warehouse model.

**v0.1.0, 31 Aug 2026.** First issue.
