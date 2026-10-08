from dataclasses import dataclass

@dataclass(frozen=True)
class VehicleState():
    """Pose of base_link (the rear axle) in the map frame, already in ROS convention."""
    stamp: float     # simulation seconds
    position: tuple  # (x, y, z) in meters
    rpy: tuple       # (roll, pitch, yaw) in radians