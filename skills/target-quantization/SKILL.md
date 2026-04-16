---
name: target-quantization
description: Discretise your target values so the debounce controller's stability filter can commit. A floating-point target from a noisy producer will never hold for 2 consecutive ticks — the filter blocks every send and the actuator stays dark. Use when wiring a continuous producer signal (confidence score, sensor reading) into a debounced controller, or debugging "I set_target() but _apply() never fires".
---

# Target Quantization

The stability filter in `debounce-controller` requires the **same target value**
for N consecutive ticks before it commits. That only works if your target is a
small, discrete set of values.

## The trap

```python
# WRONG — producer emits per-frame float target
conf = compute_confidence(...)            # 0.76, 0.83, 0.77, 0.84, 0.79
ctrl.set_target(round(conf, 2))           # each tick sees a new unique value
```

With `stability_ticks=2`, the controller needs two consecutive ticks with the
same target. Rounded to 2 decimals, strong-match confidence still jitters every
tick. The filter never stabilises. `_apply` is never called. The actuator
stays in whatever state it was in at startup (which may be "off").

## The fix

Quantise the target to the **resolution the device actually uses**. If you're
painting 6 LED segments from a 0.0–1.0 confidence, the target should be an
integer 0..6, not a float:

```python
lit = int(round(conf * 6))                # 0, 1, 2, 3, 4, 5, 6
ctrl.set_target(lit)
```

Now conf=0.76–0.91 all map to `lit=5`. The stability filter sees `5, 5, 5` at
consecutive ticks, commits, and `_apply(5)` fires.

## The rule

> **Target cardinality should match the number of distinguishable output states
> your device can actually show. Everything finer than that is noise that the
> stability filter will correctly refuse to act on.**

## Examples

| Producer signal | Device | Good target | Bad target |
|---|---|---|---|
| Face-recognition confidence | 6-segment LED bar | `int(round(conf*6))` ∈ 0..6 | `round(conf, 2)` |
| Face-recognition confidence | 3-level semaphore | 0 / 1 / 2 | raw float |
| Temperature sensor | on/off relay | bool (>= threshold) | raw degrees |
| Emotion classifier | colour enum | emotion label (already discrete) | softmax probabilities |
| Position tracker | stepper motor (stops) | nearest stop index | raw angle |

## Validation

To check if your target is quantised coarsely enough, log `set_target` values
for ~5 s of typical producer output. Count **distinct values**. If that count
is much larger than the number of distinct visual/physical states you want to
express on the device, your quantisation is too fine.

## Related

- `debounce-controller` — the filter that depends on this skill
- Producer-side stability (e.g. `face-recognition-persistence` in the
  `face-recognition-calibration` plugin) — handles a different layer of noise
  (detector dropouts) and composes with actuator-side debounce
