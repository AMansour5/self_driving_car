from rclpy.qos import QoSProfile
from visualization_msgs.msg import Marker
from carla_sim.data_types.VehicleBody import VehicleBody

class VehicleMarkerPublisher():
    """Draws the car as a translucent box sized from CARLA's own bounding box, attached to base_link.
    Publish it periodically (not once): RViz only shows markers it received after it started."""

    def __init__(self, node, topic: str, frame: str):
        self._node = node
        self._frame = frame
        self._publisher = node.create_publisher(Marker, topic, QoSProfile(depth=1))

    def publish(self, body: VehicleBody):
        marker = Marker()
        marker.header.frame_id = self._frame  # the stamp stays 0: RViz uses the latest transform
        marker.ns = "vehicle"
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        position = marker.pose.position
        position.x, position.y, position.z = body.center
        marker.pose.orientation.w = 1.0
        marker.scale.x, marker.scale.y, marker.scale.z = body.size
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = 0.2, 0.55, 0.9, 0.6
        self._publisher.publish(marker)

    def destroy(self):
        self._node.destroy_publisher(self._publisher)