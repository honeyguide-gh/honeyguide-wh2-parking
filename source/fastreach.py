"""Coarse but fast access test, used inside the layout search.

200 mm grid, the vehicle approximated by a disc of its half width, one
connected-component pass from the gate. A stand counts as reachable when the
point 2.2 m beyond its nose is in the same component as the gate mouth.
"""
import math
import numpy as np
from scipy import ndimage
from shapely.geometry import box
from shapely.ops import unary_union
from PIL import Image, ImageDraw
from wh2 import Flagship as F, Veh, GATE
import planner as PL

C = 100.0
U0, V0 = -13000.0, -2500.0
NU, NV = 400, 125
RAD = (F.X_ROOF + 60.0) / C          # disc radius in cells


def raster(poly):
    img = Image.new("1", (NU, NV), 0)
    d = ImageDraw.Draw(img)
    if poly.is_empty:
        return np.array(img, dtype=bool).T
    gs = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    for g in gs:
        d.polygon([((x - U0) / C, (y - V0) / C) for x, y in g.exterior.coords],
                  fill=1)
    return np.array(img, dtype=bool).T


STATIC = raster(unary_union([PL._solid(100.0)]))
GI = int((-1500.0 - U0) / C)
GJ = int(((GATE[0] + GATE[1]) / 2 - V0) / C)

_cache = {}


def veh_mask(v):
    k = (round(v.u), round(v.v), round(v.hdg, 1))
    m = _cache.get(k)
    if m is None:
        m = raster(unary_union([v.body(), v.doors_poly()]))
        _cache[k] = m
    return m


def reachable_set(masks):
    blocked = STATIC.copy()
    for m in masks:
        blocked |= m
    free = ndimage.distance_transform_edt(~blocked) >= RAD
    lab, _ = ndimage.label(free)
    g = lab[GI, GJ]
    return lab, g


def free_stands(vehicles):
    """Which stands have their own way out to the gate."""
    if not vehicles:
        return []
    lab, g = reachable_set([veh_mask(v) for v in vehicles])
    if g == 0:
        return []
    out = []
    for v in vehicles:
        a = math.radians(v.hdg)
        pu = v.u - math.sin(a) * (F.Y_NOSE + 2200.0)
        pv = v.v + math.cos(a) * (F.Y_NOSE + 2200.0)
        i, j = int((pu - U0) / C), int((pv - V0) / C)
        if 0 <= i < NU and 0 <= j < NV and lab[i, j] == g:
            out.append(v)
    return out
