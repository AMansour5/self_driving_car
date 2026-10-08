from dataclasses import dataclass

@dataclass(frozen=True)
class VehicleBody():
    """The car's bounding box, expressed in the base_link frame (ROS convention)."""
    center: tuple  # (x, y, z) of the box center, meters
    size: tuple    # (length, width, height), meters