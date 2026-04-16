"""
Progress bar rendering helpers.

Rules encoded:
- Fill bottom-up (thermometer).
- Red -> Yellow -> Green gradient as value grows.
- Explicitly invert indexing when hardware numbers segments top-to-bottom.
"""

from __future__ import annotations


def gradient_rgb(t: float) -> tuple[int, int, int]:
    """t in [0,1]: 0.0 -> red, 0.5 -> yellow, 1.0 -> green."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return (255, int(255 * (t * 2)), 0)
    return (int(255 * (1 - (t - 0.5) * 2)), 255, 0)


def fill_segments(
    value: float,
    total: int,
    top_index_is_zero: bool = True,
) -> tuple[list[int], tuple[int, int, int]]:
    """
    Return `(segments_to_light, rgb)` for a bottom-up progress bar.

    Parameters
    ----------
    value : float in [0.0, 1.0]
    total : number of physical segments
    top_index_is_zero : True if segment 0 is at the TOP of the hardware.
                        Govee H6056 bars behave this way.

    Examples
    --------
    >>> fill_segments(0.5, 6, top_index_is_zero=True)[0]
    [3, 4, 5]
    >>> fill_segments(0.5, 6, top_index_is_zero=False)[0]
    [0, 1, 2]
    """
    v = max(0.0, min(1.0, float(value)))
    lit = int(round(v * total))
    if lit <= 0:
        return [], (0, 0, 0)
    if top_index_is_zero:
        # bottom-up fill: the lit cells are the high indices
        segments = list(range(total - lit, total))
    else:
        segments = list(range(0, lit))
    return segments, gradient_rgb(v)


def ascii_bar(value: float, total: int = 10) -> str:
    """Quick terminal preview, bottom-up (renders bottom row first when printed)."""
    segments, _ = fill_segments(value, total, top_index_is_zero=False)
    rows = []
    for i in range(total - 1, -1, -1):
        rows.append("█" if i in segments else "·")
    return "\n".join(rows)


if __name__ == "__main__":
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        print(f"value={v:.2f}")
        print(ascii_bar(v, 8))
        print()
