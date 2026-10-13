from dataclasses import dataclass

@dataclass
class DriveCommandDTO:
    speed: float
    acceleration: float
    jerk: float
    steering_angle: float
    steering_angle_velocity: float