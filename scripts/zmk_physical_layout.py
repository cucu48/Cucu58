#!/usr/bin/env python3
"""Print the ZMK physical layout (key_physical_attrs) for the Cucu58 from Ergogen's points.

Usage:
    ergogen config.yaml -o output --debug
    python3 scripts/zmk_physical_layout.py output/points/points.yaml

Paste the output into the `keys` property in boards/shields/cucu58/cucu58-layout.dtsi.
The key order must match the matrix-transform `map` in cucu58.dtsi (and so the keymap):
for each row (num, top, home, bottom, thumb) the left half outer -> inner, then the
right half inner -> outer. The right half is the left half mirrored.

Units: ZMK uses 1/100 of a key unit. 1 unit = 18 mm (one Choc column, `cx`), so keys are
100 wide and 94 tall (17 mm / 18 mm). Rotation is in 1/100 degree, clockwise on screen.
Requires PyYAML.
"""
import sys

import yaml

U = 18.0  # mm per ZMK key unit (Ergogen's cx)
W, H = 100, round(17 / 18 * 100)
COLS = ["outer", "pinky", "ring", "middle", "index", "inner"]
ROWS = ["num", "top", "home", "bottom"]
THUMBS = ["thumb_super", "thumb_inny", "thumb_middy", "thumb_reachy", "thumb_extra"]

points = yaml.safe_load(open(sys.argv[1]))

order = [[f"matrix_{c}_{r}" for c in COLS] for r in ROWS] + [THUMBS]

xs = [p["x"] for p in points.values()]
ys = [p["y"] for p in points.values()]
xmin = min(xs) - 9      # left edge of the outer column (half a key)
ymax = max(ys) + 8.5    # top edge of the highest key (Ergogen y points up, ZMK y points down)
xmax = max(xs) + 9
mirror = 2 * xmax + 1.5 * U  # 1.5 key units between the two halves on screen


def attrs(name, right):
    p = points[name]
    x, y, r = p["x"], p["y"], p["r"]
    if right:
        x, r = mirror - x, -r
    cx = (x - xmin) / U * 100
    cy = (ymax - y) / U * 100
    rot = round(-r * 100)  # Ergogen: counter-clockwise positive; ZMK: clockwise positive
    rot_s = f"({rot})" if rot < 0 else str(rot)
    rx, ry = (0, 0) if rot == 0 else (round(cx), round(cy))  # rotate around the key centre
    return f"<&key_physical_attrs {W:3} {H:3} {round(cx - W / 2):5} {round(cy - H / 2):4} {rot_s:>8} {rx:5} {ry:4}>"


i = 0
for row in order:
    for name, right in [(k, False) for k in row] + [(k, True) for k in reversed(row)]:
        sep = "=" if i == 0 else ","
        print(f"            {sep} {attrs(name, right)}  // {name}{' (R)' if right else ''}")
        i += 1
