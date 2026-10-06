import rclpy
from rclpy.node import Node
from utils.Configurator import Configurator
from carla_sim.services.CarlaApi import CarlaApi
from carla_sim.exceptions.SimError import SimError
from carla_sim.services.CarlaVehicle import CarlaVehicle

class CarlaVehicleTestNode(Node):
    def __init__(self):
        super().__init__('carla_vehicle_test_node')
        self._logger = self.get_logger()
        self.configurator = Configurator("carla_sim")
        self.carla_api = CarlaApi(self.configurator.fetchData(Configurator.CARLA_WORLD))
        self.vehicle = CarlaVehicle(self.configurator.fetchData(Configurator.VEHICLE))
        self.carla_api.connect()
        self.carla_api.loadWorld()
        try:
            self.vehicle.spawn(self.carla_api.world)
        except SimError:
            # loadWorld switched the server to synchronous mode: restore it before giving up
            self.carla_api.disconnect()
            raise
        self.timer = self.create_timer(0.05, self.tick_carla_world)

    def tick_carla_world(self):
        self.carla_api.tick()

    def cleanup(self):
        # The car goes first, then the connection restores the server's settings
        try:
            self.vehicle.destroy()
        except SimError as e:
            self._logger.error(str(e))
        self.carla_api.disconnect()

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = CarlaVehicleTestNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except SimError as e:
        print(f"Simulation error: {e}")
    finally:
        if node is not None:
            node.cleanup()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()