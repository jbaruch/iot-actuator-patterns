# iot-actuator-patterns

A [Tessl](https://tessl.io) plugin encoding three patterns for driving
rate-limited IoT actuators from real-time producers — without strobing,
flickering, or tripping rate limits.

## Skills

| Skill | Purpose |
|---|---|
| `debounce-controller` | One-thread-per-device async controller with min-interval, stability filter, send-latest. |
| `target-quantization` | Discretise your target so the stability filter can commit. Float targets from noisy producers never stabilise. |
| `render-progress-bar` | Bottom-up thermometer fill with red → yellow → green gradient. |

## Why one plugin

These three skills compose. A real pipeline that drives a status bar on an
IoT device wants all three: debounce to avoid rate limits, quantization so
the debounce filter can commit, and the rendering convention so the UI lands
right-side-up.

## Supersedes

This plugin replaces the older `jbaruch/rate-limited-iot-debounce` and
`jbaruch/progress-bar-ux` plugins. Install this one instead.

## Install

```bash
tessl install jbaruch/iot-actuator-patterns
```

## Usage (quick)

```python
from scripts.debounce_controller import DebouncedDeviceController
from scripts.progress_bar import fill_segments

class BarController(DebouncedDeviceController):
    def _apply(self, lit_count):
        segs, rgb = fill_segments(lit_count / 6, total=6, top_index_is_zero=True)
        my_bar_api.set_segments(segs, rgb)

ctrl = BarController(min_interval_sec=1.2, stability_ticks=2, tick_sec=0.4, name="yankee")

# Producer (camera loop, sensor, etc.) — cheap, any thread
ctrl.set_target(int(round(confidence * 6)))    # quantised integer target
```

## License

MIT — see `LICENSE`.
