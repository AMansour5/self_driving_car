import rclpy
from rclpy.node import Node
from carla_msgs.msg import CarlaEgoVehicleInfo, CarlaEgoVehicleInfoWheel
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy, DurabilityPolicy

class MockVehicleInfo(Node):
    def __init__(self):
        super().__init__('mock_vehicle_info_node')
        info_qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10,
                                      reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.publisher = self.create_publisher(CarlaEgoVehicleInfo, '/carla/hero/vehicle_info', info_qos)
        self.timer = self.create_timer(1.0, self.publish_mock_info)

    def publish_mock_info(self):
        msg = CarlaEgoVehicleInfo()
        msg.wheels = [CarlaEgoVehicleInfoWheel(max_steer_angle=1.2) for _ in range(4)]
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MockVehicleInfo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()