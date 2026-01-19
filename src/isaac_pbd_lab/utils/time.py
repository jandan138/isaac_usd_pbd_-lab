import time


class FpsTimer:
    def __init__(self, interval_sec=1.0):
        self.interval_sec = interval_sec
        self._last_time = time.time()
        self._frame_count = 0

    def tick(self):
        self._frame_count += 1
        now = time.time()
        elapsed = now - self._last_time
        if elapsed >= self.interval_sec:
            fps = self._frame_count / max(elapsed, 1e-6)
            self._last_time = now
            self._frame_count = 0
            return True, fps, elapsed
        return False, 0.0, 0.0
