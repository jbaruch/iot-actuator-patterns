# Face Recognition Confidence Display System

## Problem Description

A security team has a face-recognition pipeline that runs at 25 fps and produces a per-frame confidence score (0.0–1.0) indicating how likely the current face matches an authorized person. They want this score to drive a 6-segment LED bar indicator mounted at the door entry point. The LED bar has 6 hardware segments (segment 0 is at the top physically), and its state should reflect the current match confidence: more segments lit = higher confidence.

The initial implementation passed the raw confidence float directly to the existing debounce controller, which should have filtered out jitter — but the LED bar never changes state at all after startup. The team suspects the debounce controller is failing silently.

Your job is to fix the integration so the LED bar actually responds to confidence changes. You should also add a brief diagnostic log showing why the naive approach fails, and a validation step that confirms the fixed approach produces a stable, manageable number of distinct target values from a realistic stream of confidence readings.

## Output Specification

Produce `confidence_led_controller.py` that:
- Contains a corrected integration between the confidence producer and the debounce controller
- Demonstrates both the broken approach and the fixed approach (simulating ~5 seconds of producer output each)
- Logs the set_target() call values during the simulation and includes diagnostic evidence showing why the broken approach fails and the fixed approach works
- Includes inline comments explaining why the fix works

Also produce `validation_report.txt` that:
- Shows the distinct-value count from the broken approach (raw float or over-fine rounding)
- Shows the distinct-value count from the fixed approach
- States what the correct target cardinality should be for a 6-segment device
- Explains the rule for choosing target resolution

## Input Files

The following confidence stream is provided as a simulated 5-second recording (25 fps = 125 frames). Extract this before beginning.

=============== FILE: inputs/confidence_stream.txt ===============
0.76
0.83
0.77
0.84
0.79
0.81
0.75
0.82
0.80
0.78
0.85
0.77
0.83
0.80
0.76
0.84
0.81
0.79
0.82
0.77
0.85
0.80
0.76
0.83
0.78
0.81
0.84
0.79
0.77
0.82
0.76
0.85
0.80
0.78
0.83
0.81
0.77
0.84
0.79
0.82
0.76
0.85
0.80
0.78
0.83
0.77
0.81
0.84
0.79
0.82
0.32
0.28
0.35
0.30
0.27
0.33
0.29
0.31
0.34
0.28
0.30
0.27
0.33
0.29
0.31
0.35
0.28
0.32
0.29
0.30
0.91
0.88
0.93
0.90
0.87
0.92
0.89
0.91
0.88
0.93
0.90
0.87
0.92
0.89
0.91
0.88
0.93
0.90
0.87
0.92
0.89
0.91
0.88
0.93
0.90
0.55
0.52
0.58
0.54
0.51
0.57
0.53
0.55
0.52
0.58
0.54
0.51
0.57
0.53
0.55
0.52
0.58
0.54
0.51
0.57
0.63
0.60
0.67
0.64
0.61
