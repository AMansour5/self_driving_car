import numpy as np

class ScanAssembler():
    """Collects `slices` consecutive lidar slices and emits them as one scan,
    stamped at the first slice. Pure: it knows nothing about CARLA."""

    def __init__(self, slices: int):
        self.slices = max(1, int(slices))
        self._buffer = []
        self._first_stamp = 0.0

    def add(self, stamp: float, points: np.ndarray):
        """Returns (stamp, points) when a full scan is ready, otherwise None."""
        if not self._buffer:
            self._first_stamp = stamp
        self._buffer.append(points)
        if len(self._buffer) < self.slices:
            return None
        scan = (self._first_stamp, np.vstack(self._buffer))
        self._buffer = []
        return scan

    def reset(self):
        self._buffer = []