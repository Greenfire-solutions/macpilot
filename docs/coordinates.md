# Coordinates

Two coordinate spaces, and mixing them is the #1 source of misplaced clicks.

| space | example | who uses it |
|---|---|---|
| **backing pixels** | 3584 × 2240 | `screencapture` output, image tools |
| **logical points** | 1792 × 1120 | CGEvent, macpilot, AppleScript window geometry |

```
logical = pixels / scale        # scale is 2.0 on most Retina displays
```

```bash
macpilot screen
# display 0: logical 1792x1120 at (0,0)  backing 3584x2240  scale 2.00
```

```python
from macpilot import screen
screen.to_points(767, 1285)     # -> (383.5, 642.5)
```

## Reading coordinates off a screenshot
If you view a screenshot downscaled (e.g. a 3584px-wide image shown at 2000px), you have a
**third** factor. Chain them:

```
display_px = viewed_px * (image_width / displayed_width)
logical    = display_px / scale
```

## Multi-display
Coordinates are global and origins can be negative (a display left of or above the main
one). `macpilot screen` prints each display's origin; add it before converting.

## Sanity check before committing to a click
```bash
macpilot peek X Y     # confirms what is actually there
```
If that returns the element you expected, your math is right.
