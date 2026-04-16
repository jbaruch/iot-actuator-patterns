"""
Reusable async device controller for rate-limited IoT APIs.

Features:
- One thread per device.
- Lock-protected target state; producers call `set_target` from any thread.
- Stability filter: target must hold for `stability_ticks` before commit.
- Min-interval throttle between actual applications.
- Send-latest semantics: stale targets are overwritten, never queued.

The target MUST be a discrete value (int, str, enum, tuple of ints) — not a
raw float. See the `target-quantization` skill in this plugin for why.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from typing import Any


class DebouncedDeviceController(ABC):
    """
    Subclass and implement `_apply(target)` for your device.

    target is any comparable Python value (tuple, str, frozen dataclass).
    """

    def __init__(
        self,
        min_interval_sec: float = 1.2,
        stability_ticks: int = 2,
        tick_sec: float = 0.4,
        name: str = "device",
    ) -> None:
        self.min_interval_sec = float(min_interval_sec)
        self.stability_ticks = int(stability_ticks)
        self.tick_sec = float(tick_sec)
        self.name = name

        self._lock = threading.Lock()
        self._target: Any = None
        self._pending: Any = None
        self._pending_hold = 0
        self._last_sent: Any = None
        self._last_sent_at = 0.0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"debounce-{name}")
        self._thread.start()

    # ---- Producer API --------------------------------------------------

    def set_target(self, target: Any) -> None:
        """Called from any thread. Cheap: just records the latest target."""
        with self._lock:
            self._target = target

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        self._thread.join(timeout=timeout)

    # ---- Device adapter ------------------------------------------------

    @abstractmethod
    def _apply(self, target: Any) -> None:
        """Perform the actual network call. Raise on failure."""

    # ---- Controller loop -----------------------------------------------

    def _run(self) -> None:
        while not self._stop.is_set():
            with self._lock:
                target = self._target

            # Stability filter
            if target == self._pending:
                self._pending_hold += 1
            else:
                self._pending = target
                self._pending_hold = 1

            committed = self._pending if self._pending_hold >= self.stability_ticks else None

            # Min-interval throttle + send-latest
            now = time.monotonic()
            if (
                committed is not None
                and committed != self._last_sent
                and (now - self._last_sent_at) >= self.min_interval_sec
            ):
                try:
                    self._apply(committed)
                    self._last_sent = committed
                    self._last_sent_at = now
                except Exception as exc:  # pragma: no cover - caller logs
                    print(f"[{self.name}] apply failed: {exc!r}")

            self._stop.wait(self.tick_sec)


# ---- Example usage ------------------------------------------------------

class _PrintController(DebouncedDeviceController):
    def _apply(self, target: Any) -> None:
        print(f"[{self.name}] APPLY {target!r} @ {time.monotonic():.2f}")


if __name__ == "__main__":
    c = _PrintController(min_interval_sec=0.5, stability_ticks=2, tick_sec=0.1, name="demo")
    print("Rapidly bouncing targets — only stable ones should be applied.")
    for v in ("red", "red", "green", "red", "red", "green", "green", "green"):
        c.set_target(v)
        time.sleep(0.1)
    time.sleep(1.5)
    c.stop()
