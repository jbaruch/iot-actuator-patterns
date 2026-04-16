---
name: render-progress-bar
description: Renders a segmented progress bar that fills bottom-up with a red/yellow/green gradient — the thermometer pattern users expect, not top-down list order. Use when the user asks for a thermometer chart, vertical progress bar, gauge, meter, status indicator, temperature indicator, RAG status bar, or any color-coded level display where fill direction matters.
---

# Progress Bar UX

Three things a progress bar must do to feel right:

1. **Fill bottom-up.** It's a thermometer. Liquid rises, it does not fall. If your
   hardware is indexed top-to-bottom (Govee segments, LED strips, etc.) you must
   invert the index when lighting cells.
2. **Red → Yellow → Green gradient** as the value increases from 0 to 1.
3. **Do not use Python list iteration order** to decide which cell to light first.
   That gives you a top-down fill and every user will tell you it feels wrong.

## Mapping a value in [0, 1] to a segmented bar

Given `total_segments`:

```python
lit = int(round(value * total_segments))
```

If hardware has segment 0 at the **top** (e.g. Govee H6056):

```python
# bottom-up fill: the lit cells are the high indices
segments_to_light = range(total_segments - lit, total_segments)
```

If hardware has segment 0 at the **bottom**:

```python
segments_to_light = range(0, lit)
```

## Gradient

Two-stop gradient through yellow:

```python
def gradient_rgb(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return (255, int(255 * (t * 2)), 0)          # red -> yellow
    return (int(255 * (1 - (t - 0.5) * 2)), 255, 0)  # yellow -> green
```

See [`scripts/progress_bar.py`](../../scripts/progress_bar.py) for the reference
implementation. Import `fill_segments(value, total, top_index_is_zero)` and you
cannot get the direction wrong.

## How to act

1. Any time you render a bar — terminal, GUI, physical LEDs — use `fill_segments`.
2. Remove any code that iterates `for i, seg in enumerate(segments)` to light cells in order. That's a top-down fill in disguise.
3. If a designer asks for top-down fill, explain the thermometer convention — liquid-style bottom-up fill is what users expect.
4. **Verify direction:** After wiring up the bar, test with `value=0.1` and confirm only the bottom segment lights up. Flip the `top_index_is_zero` argument if not.

## When paired with `debounce-controller`

The target you pass to `ctrl.set_target(...)` should already be quantised to
`int(round(value * total_segments))` — not the raw float. See the
`target-quantization` skill in this plugin.

## Related

- `debounce-controller` — the actuator pattern usually paired with this UI pattern
- `target-quantization` — discrete targets are a prerequisite for debounce stability
