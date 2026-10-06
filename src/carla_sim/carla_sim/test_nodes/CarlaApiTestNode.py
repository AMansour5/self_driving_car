import rclpy
from rclpy.node import Node
from utils.Configurator import Configurator
from carla_sim.services.CarlaApi import CarlaApi

class CarlaApiTestNode(Node):
    def __init__(self):
        super().__init__('carla_api_test_node')
        self._logger = self.get_logger()
        self.configurator = Configurator("carla_sim")
        self.world_cfg = self.configurator.fetchData(Configurator.CARLA_WORLD)
        self.carla_api = CarlaApi(self.world_cfg)
        self.carla_api.connect()
        self.carla_api.loadWorld()
        self.timer = self.create_timer(0.05, self.tick_carla_world)

    def tick_carla_world(self):
        self.carla_api.tick()

    def disconnect(self):
        self.carla_api.disconnect()

def main(args=None):
    rclpy.init(args=args)
    node = CarlaApiTestNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.disconnect()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()