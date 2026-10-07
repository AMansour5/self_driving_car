import numpy as np
from carla_sim.exceptions.SimError import SimError
from carla_sim.data_types.LidarScan import LidarScan
from carla_sim.abc.CarlaSensor import CarlaSensor
from carla_sim.helpers.ScanAssembler import ScanAssembler

class CarlaLidar(CarlaSensor):
    """A spinning lidar. With a world step shorter than one revolution, every tick
    only holds a slice of the sweep, so slices are assembled into full scans."""

    BLUEPRINT = "sensor.lidar.ray_cast"
    USE_SENSOR_TICK = False  # the sensor must see every tick to deliver every slice

    def __init__(self, lidar_cfg: dict, fixed_delta_seconds: float):
        if not lidar_cfg or "lidar" not in lidar_cfg:
            raise SimError("Lidar config must contain a 'lidar' section.")
        super().__init__("lidar", lidar_cfg["lidar"])
        if self.rate_hz is None:
            raise SimError("Lidar config needs 'rate_hz' (full scans per second).")
        self.__assembler = ScanAssembler(self.__slicesPerScan(self.rate_hz, fixed_delta_seconds))

    def detach(self):
        super().detach()
        self.__assembler.reset()  # a half-built scan must not leak into the next attach

    def _blueprintAttributes(self):
        attributes = super()._blueprintAttributes()
        attributes["rotation_frequency"] = self.rate_hz  # one revolution per scan
        return attributes

    def _convert(self, raw):
        # Each point is x, y, z, intensity (float32), in the sensor's left-handed frame
        points = np.frombuffer(raw.raw_data, dtype=np.float32).reshape(-1, 4).copy()
        points[:, 1] *= -1.0  # CARLA y points right, ROS y points left
        scan = self.__assembler.add(raw.timestamp, points)
        if scan is None:
            return []
        stamp, cloud = scan
        return [LidarScan(stamp=stamp, frame=self.frame, points=cloud)]

    @staticmethod
    def __slicesPerScan(rate_hz: float, fixed_delta_seconds: float):
        if fixed_delta_seconds is None:
            raise SimError("The world config needs 'fixed_delta_seconds' to size lidar scans.")
        if rate_hz <= 0 or fixed_delta_seconds <= 0:
            raise SimError("Lidar rate and world step must be positive.")
        slices = 1.0 / (rate_hz * fixed_delta_seconds)
        if slices < 1.0 - 1e-6 or abs(slices - round(slices)) > 1e-3 * max(1.0, slices):
            raise SimError(f"A {rate_hz:g} Hz lidar is not reachable with a "
                           f"{fixed_delta_seconds:g} s world step ({slices:.3f} ticks per scan).")
        return int(round(slices))