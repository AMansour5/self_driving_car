from rclpy.qos import QoSProfile
from rosgraph_msgs.msg import Clock
from builtin_interfaces.msg import Time

class ClockPublisher():
    """Publishes the simulation time on /clock. Run RViz and any other consumer of the
    simulated data with use_sim_time:=true; this node itself stays on wall time."""

    def __init__(self, node):
        self._node = node
        self._publisher = node.create_publisher(Clock, "/clock", QoSProfile(depth=10))

    def publish(self, stamp: float):
        sec = int(stamp)
        self._publisher.publish(Clock(clock=Time(sec=sec, nanosec=int((stamp - sec) * 1e9))))

    def destroy(self):
        self._node.destroy_publisher(self._publisher)