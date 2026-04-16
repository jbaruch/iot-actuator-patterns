# LED Volume Meter for Live Audio Monitoring

## Problem Description

A studio team has an 8-segment LED strip wired above their mixing desk to show real-time audio input level. The strip hardware numbers its segments from top to bottom (segment 0 is physically at the top). The audio monitoring system feeds a normalized volume level (0.0 to 1.0) to the display module at roughly 10 Hz.

The previous implementation was written quickly by lighting each segment in Python list order, which produced an unintuitive result. The display feels wrong to operators — pushing the fader up doesn't produce the intuitive result they expect. The team wants the display to feel natural, like a physical VU meter, with a color-coded level indication so operators can tell at a glance whether the level is low, mid, or high.

The team has specifically asked for:
- The implementation to be clean and reusable, not tightly coupled to one specific hardware variant
- A terminal ASCII preview mode that can be run without any hardware connected, showing the bar for several test levels

## Output Specification

Produce `volume_meter.py` that:
- Renders the LED level display with correct bottom-up fill behavior
- Is reusable for different hardware configurations
- Produces colored RGB values for each lit segment matching the level
- Includes an ASCII terminal preview that demonstrates the bar at values 0.0, 0.1, 0.25, 0.5, 0.75, and 1.0

The terminal preview should be runnable with `python3 volume_meter.py` and print the ASCII bar for each test value in a way that makes the fill direction clear (bottom of the bar shown at the bottom of the terminal output for each value).

Also produce `rendering_notes.md` explaining:
- Why iterating over segments in Python list order produces the wrong visual result
- How the correct segment selection differs for top-indexed vs bottom-indexed hardware
- The color mapping from level 0.0 to 1.0
