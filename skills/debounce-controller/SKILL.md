---
name: debounce-controller
description: One-thread-per-device async controller for rate-limited IoT APIs with min-interval throttle, stability filter, and send-latest semantics. Use when a real-time producer (camera loop, sensor feed, event stream) drives a cloud or LAN IoT device that can't keep up with per-frame updates, or when you see flicker / HTTP 429 errors from hammering an actuator.
---

# Debounce Controller

Cloud-controlled IoT devices (Govee, LIFX, Zigbee-over-HTTP, many more) get
hammered into the ground by real-time pipelines that emit 30 updates a second.
This skill encodes the controller pattern that moves the I/O off the hot path
and filters transient noise.

## The pattern

- **One controller thread per physical device.** Don't multiplex from the camera loop.
- **Lock-protected target state.** Producers write `target`. The controller thread reads.
- **Stability filter.** Only commit a target once it has held for at least `N` ticks
  (default `N=2`). Suppresses flicker from borderline classifier output.
- **Min-interval throttle.** Never send twice within `min_interval_sec` (default `1.2s`).
- **Send-latest semantics.** If the target changed during a throttle window, send only
  the freshest value when the window opens. Stale targets are dropped.
- **Tick interval `0.4s`.** Fast enough to feel responsive, slow enough for the
  stability filter to do meaningful work.

## How to act

1. Use [`scripts/debounce_controller.py`](../../scripts/debounce_controller.py). It gives you a ready-to-subclass controller.
2. Implement the device-specific `_apply(target)` method — everything else is generic.
3. Producers call `set_target(...)` from any thread; it's cheap.
4. On shutdown, set a sentinel target (e.g. `"off"`), `time.sleep(1.5)`, then `stop(timeout=2.0)`.
5. **Read the `target-quantization` skill in this plugin BEFORE picking your target type.** The stability filter requires targets to be discrete; float targets will never commit.

## Minimal example

```python
from scripts.debounce_controller import DebouncedDeviceController

class MyController(DebouncedDeviceController):
    def _apply(self, target):
        my_device_api.set_color(target)

ctrl = MyController(min_interval_sec=1.2, stability_ticks=2, tick_sec=0.4, name="lamp")
ctrl.set_target("red")
ctrl.set_target("blue")   # supersedes red if throttle window still open
ctrl.set_target("off")
ctrl.stop(timeout=2.0)
```

## Knobs

```
MIN_INTERVAL_SEC  cloud API  → 1.2s   (default)
                   LAN device → 0.2s   (can drop stability_ticks=1 if producer already filters)

STABILITY_TICKS    2 (default)   → target must hold 2 consecutive ticks to commit
                   1              → responsive, no stability filtering

TICK_SEC           0.4s (default) → 2.5 Hz controller
```

## Validation and troubleshooting

- **Still seeing 429s?** Bump `min_interval_sec` in 0.2s increments.
- **Feels sluggish?** Check quantization of the target (→ quantization skill).
- **Target never applied?** The stability filter never stabilized. Either the producer is emitting too-fine-grained values (quantize more coarsely) or `stability_ticks` is higher than the producer's natural hold time.

## Related skills

- `target-quantization` — discrete targets are a prerequisite for the stability filter
- `render-progress-bar` — UI pattern often paired with a debounced actuator
- In other plugins: `face-recognition-persistence` (producer-side persistence, composes with this actuator-side debounce)
