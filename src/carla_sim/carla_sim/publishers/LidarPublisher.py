import numpy as np
from rclpy.qos import QoSProfile
from builtin_interfaces.msg import Time
from sensor_msgs.msg import PointCloud2, PointField
from carla_sim.data_types.LidarScan import LidarScan

class LidarPublisher():
    FIELDS = ("x", "y", "z", "intensity")

    def __init__(self, node, topic: str):
        self._node = node
        self._publisher = node.create_publisher(PointCloud2, topic, QoSProfile(depth=5))

    def publish(self, scan: LidarScan):
        self._publisher.publish(self.toMsg(scan))

    def toMsg(self, scan: LidarScan) -> PointCloud2:
        points = np.ascontiguousarray(scan.points, dtype=np.float32).reshape(-1, len(self.FIELDS))
        sec = int(scan.stamp)
        msg = PointCloud2()
        msg.header.stamp = Time(sec=sec, nanosec=int((scan.stamp - sec) * 1e9))
        msg.header.frame_id = scan.frame
        msg.height = 1
        msg.width = points.shape[0]
        msg.fields = [PointField(name=name, offset=4 * i, datatype=PointField.FLOAT32, count=1)
                      for i, name in enumerate(self.FIELDS)]
        msg.is_bigendian = False
        msg.point_step = 4 * len(self.FIELDS)
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = True
        msg.data = points.tobytes()
        return msg

    def destroy(self):
        self._node.destroy_publisher(self._publisher)