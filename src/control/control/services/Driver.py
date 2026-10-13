import math
from typing import Optional
from utils.Dispatcher import Dispatcher
from utils.Configurator import Configurator
from control.DTOs.DriveCommandDTO import DriveCommandDTO

class Driver:
    def __init__(self):
        self.smoother = Dispatcher().get_smoothing_strategy()
        drive_cfg = Configurator().fetchData(Configurator.DRIVE)
        if not drive_cfg or "max_speed" not in drive_cfg:
            raise ValueError("The drive config must define 'max_speed'.")
        self.max_speed = float(drive_cfg["max_speed"])
        self.joystick_timeout_s = float(drive_cfg.get("joystick_timeout_s", 0.5))
        self.max_steering_angle = None
        self._speed = 0.0

    def set_max_steering_angle(self, radians: float):
        self.max_steering_angle = float(radians)

    def reset(self):
        self._speed = 0.0

    def drive(self, fwd_speed: float, rev_speed: float, steering_angle: float) -> Optional[DriveCommandDTO]:
        """Triggers are in [0, 1] and the stick in [-1, 1]. Returns None when the input cannot be trusted."""
        if self.max_steering_angle is None:
            return None
        if not all(math.isfinite(v) for v in (fwd_speed, rev_speed, steering_angle)):
            return None
        fwd = min(max(fwd_speed, 0.0), 1.0)
        rev = min(max(rev_speed, 0.0), 1.0)
        stick = min(max(steering_angle, -1.0), 1.0)

        self._speed = self.smoother.smooth(self._speed, (fwd - rev) * self.max_speed)
        # ROS convention: positive angle turns left, while stick-left reads negative
        return DriveCommandDTO(speed=self._speed,
                               acceleration=0.0,
                               jerk=0.0,
                               steering_angle=-stick * self.max_steering_angle,
                               steering_angle_velocity=0.0)
