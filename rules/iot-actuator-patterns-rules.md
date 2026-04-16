# IoT Actuator Patterns Rules

Three patterns for driving rate-limited IoT actuators from real-time producers:

## Debounce controller (→ `debounce-controller` skill)
- **One controller thread per device.** Never call the API from the producer loop.
- **Min-interval:** `1.2s` for cloud APIs, `0.2s` for LAN devices.
- **Stability filter:** target must hold for 2 consecutive ticks before commit.
- **Send-latest:** overwrite pending target during throttle; never queue stale intents.
- **Tick `0.4s`.**

## Target quantization (→ `target-quantization` skill)
- **Discrete targets only.** Float targets from noisy producers never satisfy the stability filter.
- **Quantise to the device's distinguishable output resolution.** 6 LED segments → int 0..6. 3-level semaphore → int 0..2.
- Log `set_target` calls for 5 s and count distinct values. If >> the visible-state count, quantise harder.

## Progress bar rendering (→ `render-progress-bar` skill)
- **Fill bottom-up.** Thermometer, not falling bar.
- **Red → Yellow → Green** gradient.
- For top-indexed hardware: `range(total - lit, total)`.
- For bottom-indexed hardware: `range(0, lit)`.
- Never `for i, seg in enumerate(segments)` — that's top-down fill.

Reference scripts: `scripts/debounce_controller.py`, `scripts/progress_bar.py`.
Full context in `skills/*/SKILL.md`.
