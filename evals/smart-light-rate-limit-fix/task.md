# Smart Office Lighting Controller

## Problem Description

A smart office has installed Govee cloud-connected LED light panels in meeting rooms. The building's occupancy system runs a camera-based classifier at 30 fps to detect meeting activity levels (empty, focused, collaborative, social). The engineering team needs to change the room lighting color based on the detected activity so the lights reflect the current mode: a subtle blue for focused work, warm yellow for collaborative sessions, and soft green when the room is empty.

The current prototype calls the Govee cloud API directly from the camera processing loop. The API is rate-limited and the system is getting flooded with HTTP 429 errors whenever the occupancy classifier output fluctuates between two categories near a boundary (which happens frequently in mixed-activity situations). The team also reports visible light flickering as the API alternately succeeds and fails.

The solution needs to decouple the API calls from the camera loop, absorb transient classifier noise, and ensure the device never gets hammered during the throttle window — only the latest intent should be acted on, not a queue of stale ones.

## Output Specification

Produce a working Python implementation in `meeting_room_controller.py` that:
- Implements a controller for the Govee meeting room light that can be driven from a fast producer
- Includes a simulated producer (a simple function or thread that emits activity-level strings at high frequency)
- Demonstrates graceful shutdown
- Includes inline comments explaining the key design decisions

Also produce a short `design_notes.md` explaining:
- Why the design prevents 429 errors even if the producer emits at 30 fps
- What happens when the classifier rapidly alternates between two activity levels
- What the shutdown sequence does and why the order matters
