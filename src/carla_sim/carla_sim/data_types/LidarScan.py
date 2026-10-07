from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True, eq=False)
class LidarScan():
    """One full lidar scan, already in ROS convention (x forward, y left, z up)."""
    stamp: float        # simulation seconds
    frame: str          # frame id of the sensor, from lidar.yaml
    points: np.ndarray  # N x 4 float32: x, y, z, intensity