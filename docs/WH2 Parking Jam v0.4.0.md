# WH2 Tricycle Parking, v0.4.0

Hardware, 2 September 2026. Michael Kissi Danquah.
Built against `Hardware Designs/Warehouse Design.3dm` saved 2 Sep 2026 01:56,
which now carries the farm vehicle as well as the Flagships.
All geometry read from that file at 1:1. Millimetres throughout.

---

## The answer first

The review asked for two things at once: **both doors open on every parked
vehicle**, so they can all load before checkout, and **any vehicle in or out
in any order**, so the morning juggling stops.

Both are achievable. Together they cost five vehicles.

| Flagships inside the hall | Fixed order, as now | Any order, nobody moves |
|---|---|---|
| **One door open** | **8** | 4 |
| **Both doors open** | **6** | **3** |

Every cell was verified the same way: static fit with 600 mm of working
clearance at every fitting, then a manoeuvre planned out of the gate for each
vehicle with everything else still parked and its doors open, then the whole
path replayed pose by pose in exact polygon geometry.

**So: three inside plus the workshop bay, if both constraints hold.** Ten
vehicles is still reachable, but only by moving the loading formation out to
the yard. That is Scheme 4.

---

## What the review changed, and what it cost

**Both doors open is the cheap constraint.** Nose to tail nothing changes at
all: a door leaf is 1976 mm long and the street pitch is 4170, so two leaves
in a line never meet. What it costs is sideways — two rows now need 4300 mm
between them instead of 3232. That is the whole difference between eight and
six.

**Any-order access is the expensive one.** Every vehicle needing its own route
to the gate, past everything else standing there with its doors open, takes
the count from eight to four with one door, and from six to three with both.

**The diagonal is the right instinct.** Measured off the real door geometry,
the legal neighbour offsets for two both-doors-open vehicles are:

| Two vehicles, both doors open | Centre to centre |
|---|---|
| Side by side | **4300 mm** |
| Nose to tail | **4175 mm** |
| Staggered 3650 mm along their axis | **2200 mm across** |

That third line is what the diagonal buys, and it is the tightest packing
available. The verified layout uses it at 145° on a 4450 mm pitch.

**Why four inside is impossible, not merely tight.** The stand band has
14.9 m of usable length once the office, the third fridge and its working
strip are subtracted. Sweeping every angle from 0° to 90°, the closest two
both-doors-open vehicles can ever be is **3950 mm**. Four stands need 15.8 m.
It misses by 900 mm, so no amount of angle-tuning reaches it.

---

## The four schemes

| | Scheme | Inside | Both doors | Any order | Tightest point driving out |
|---|---|---|---|---|---|
| 1 | **Diagonal Three** | 3 | yes | **yes** | 45 mm |
| 2 | Two Streets, Both Doors | 6 | yes | no | 41 mm |
| 3 | Two Streets, One Door | 8 | no | no | 41 mm |
| 4 | **Three In, Seven Out** | 3 + 7 in the yard | yes | **yes** | 45 mm |

### Scheme 1, Diagonal Three

Three stands at **145° on a 4450 mm pitch**, axle line at v = 6400. Both doors
open on all three at once. Any of the three leaves at any time with the other
two untouched — each departure was planned and audited, and the tightest point
on any of them is 45 mm. The south strip, 2440 mm, is the aisle.

This is the review's two constraints met exactly, and it is the most the shed
will take with them.

### Scheme 4, Three In, Seven Out

The ten-vehicle plan. Three Flagships inside on the diagonal, the farm vehicle
in the workshop bay, and **seven in the yard west of the workshop**, all with
both doors open and none blocking another. In the morning the three inside
load and leave in any order, three come in from the yard to replace them, and
the second shift of operators arrives as the first leaves.

**What the yard has to provide.** Seven stands abreast with both doors open
need **4285 mm of frontage each**:

- one rank of seven: about **30 m of frontage by 10.5 m deep**, including the
  6 m needed to turn out of a stand
- two ranks of four facing one aisle: about **17 m by 15 m**

The site model does not carry a yard boundary — the paved slab in the CAD
stops 2540 mm west of the shed wall, and the farm vehicle you parked sits
beyond it — so those are the figures the formation *needs*, not what the yard
*has*. Chalk it out before committing to it.

---

## The farm vehicle

Read from the `Zusha cargo-trike v1` block you placed in the warehouse model:

| | Farm vehicle | Flagship |
|---|---|---|
| Length | **4373 mm** | 4476 |
| Width | **1813 mm** | 2028 |
| Height | **1953 mm** | 2528 |
| Doors | none, open flatbed | two, 4135 mm overall when open |
| Wheelbase | 2650 | 2650 |
| Rear track | 960 | 960 |

Same chassis, so it turns identically — the 3158 mm rear-axle radius applies
to both. With no doors to swing it is much easier to place, which is why it
takes the workshop bay in Scheme 4.

One caution: the standalone `Zusha Cargo Trike.3dm` measures 6352 mm long,
because the assembly there carries a pair of symmetric members reaching 2.4 m
ahead of the front wheel. The figures above come from the block as placed in
the warehouse model, which is what you confirmed.

---

## The four numbers everything follows from

| | Value | Where it comes from |
|---|---|---|
| Street pitch | **4170 mm** | canopy 4020 plus 150, nose under the canopy ahead |
| Both doors, side by side | **4285 mm** | two door tips at 2068 plus 150 |
| Both doors, diagonal | **2200 mm across** | staggered 3650 mm along the axis |
| Rear axle turning radius | **3158 mm** | wheelbase 2650 at 40° of steer |

An open door occupies 1988 to 2243 mm above the slab, so it may swing over the
fridges, the sinks, the crate rack and the weighing zone, but never over the
office at 2640 mm and never over another vehicle's canopy at 2222 mm.

---

## What I would put to your manager

Three points, in order of how much they change the plan.

1. **The two constraints together cost five vehicles.** Eight becomes three.
   That is worth knowing before the layout is painted.
2. **Any-order access is what costs, not both doors.** If one of the two has
   to give, giving up any-order gets you back to six; giving up both-doors
   only gets you back to four.
3. **If only three can load inside, loading probably does not belong inside.**
   The yard has no walls to work around, so it holds the both-doors-open,
   any-order formation easily. Load in the yard, keep the shed as dense
   overnight storage at eight, and the ten-vehicle day works without a
   three-wave shuffle.

---

## Open questions

1. The yard's real extent — depth, width, whether it is walled or gated at
   night, and whether vehicles can stand there unattended. Every figure in
   Scheme 4 is a requirement rather than a fit until that is known.
2. The fleet mix. I have assumed nine Flagships and one farm vehicle to reach
   ten.
3. Whether the both-doors rule is meant to apply to the farm vehicle at all,
   given it has none.
4. The steering lock. Every manoeuvre here follows from 40°. Measure it on a
   real vehicle; if the real lock is better, the tight moves get easier.

---

## Change log

**v0.4.0, 2 Sep 2026.** Both doors open on every parked vehicle, and any-order
access, both made hard constraints after the review. Added the farm vehicle
from the CAD. Capacity inside falls from eight to three; the four-cell table
above shows what each constraint costs. New Scheme 1, the verified diagonal;
new Scheme 4, the ten-vehicle two-wave plan using the yard.

**v0.3.0, 31 Aug 2026.** Drivability became a hard constraint: a manoeuvre
planner and an exact geometric replay, so every departure is a path a driver
could follow. Dropped the third street, which fit but could not be driven out
of.

**v0.2.0, 31 Aug 2026.** Rebuilt against the revised warehouse model.

**v0.1.0, 31 Aug 2026.** First issue.
