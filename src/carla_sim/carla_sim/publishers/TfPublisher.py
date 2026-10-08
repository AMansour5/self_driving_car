import math
from builtin_interfaces.msg import Time
from geometry_msgs.msg import TransformStamped
from carla_sim.exceptions.SimError import SimError
from carla_sim.data_types.VehicleState import VehicleState
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster

class TfPublisher():
    """Publishes the transforms of the car:
    - static: base_link -> every sensor frame, from the poses in the sensor YAMLs
    - dynamic: map -> <ground truth frame>, the car's true pose from CARLA (switchable)"""

    def __init__(self, node, tf_cfg: dict):
        try:
            self.map_frame = tf_cfg["map_frame"]
            self.base_frame = tf_cfg["base_frame"]
            ground_truth = tf_cfg["ground_truth"]
            self.publish_ground_truth = bool(ground_truth["publish"])
            self.ground_truth_frame = ground_truth["child_frame"]
        except (KeyError, TypeError) as e:
            raise SimError("The vehicle config needs a 'tf' section with map_frame, base_frame and "
                           "ground_truth: {publish, child_frame}.") from e
        self._node = node
        self._static = StaticTransformBroadcaster(node)
        self._dynamic = TransformBroadcaster(node)

    def publishStatic(self, mounts):
        """mounts is a list of (frame, pose). Send them all in one call: a late subscriber only
        receives the last /tf_static message, so a second call would replace the first."""
        stamp = self._node.get_clock().now().to_msg()
        transforms = []
        for frame, pose in mounts:
            rpy = tuple(math.radians(pose[key]) for key in ("roll", "pitch", "yaw"))
            transforms.append(self.__transform(stamp, self.base_frame, frame,
                                               (pose["x"], pose["y"], pose["z"]), rpy))
        if transforms:
            self._static.sendTransform(transforms)

    def publishGroundTruth(self, state: VehicleState):
        if not self.publish_ground_truth:
            return
        sec = int(state.stamp)
        stamp = Time(sec=sec, nanosec=int((state.stamp - sec) * 1e9))
        self._dynamic.sendTransform(self.__transform(stamp, self.map_frame, self.ground_truth_frame,
                                                     state.position, state.rpy))

    @staticmethod
    def quaternionFromRpy(roll: float, pitch: float, yaw: float):
        """Radians -> (x, y, z, w)."""
        cr, sr = math.cos(roll / 2), math.sin(roll / 2)
        cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
        cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
        return (sr * cp * cy - cr * sp * sy,
                cr * sp * cy + sr * cp * sy,
                cr * cp * sy - sr * sp * cy,
                cr * cp * cy + sr * sp * sy)

    @staticmethod
    def __transform(stamp, parent: str, child: str, position, rpy):
        msg = TransformStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = parent
        msg.child_frame_id = child
        t, q = msg.transform.translation, msg.transform.rotation
        t.x, t.y, t.z = position
        q.x, q.y, q.z, q.w = TfPublisher.quaternionFromRpy(*rpy)
        return msg