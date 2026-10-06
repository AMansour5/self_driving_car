import rclpy
from rclpy.qos import QoSProfile
from utils.Configurator import Configurator
from carla_sim.services.CarlaApi import CarlaApi
from carla_sim.exceptions.SimError import SimError
from carla_sim.services.CarlaVehicle import CarlaVehicle
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn

class CarlaNode(LifecycleNode):
    def __init__(self):
        super().__init__('carla_lifecycle_node')
        self._logger = self.get_logger()
        self._world_cfg = None
        self._vehicle_cfg = None
        self._carla_api = None
        self._vehicle = None
        self._world = None

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Configuring CarlaNode")
        try:
            self.configurator = Configurator("carla_sim")
            self._world_cfg = self.configurator.fetchData(Configurator.CARLA_WORLD)
            self._vehicle_cfg = self.configurator.fetchData(Configurator.VEHICLE)
            self._carla_api = CarlaApi(self._world_cfg)
            self._vehicle = CarlaVehicle(self._vehicle_cfg)
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to configure CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Activating CarlaNode")
        try:
            self._carla_api.connect()
            self._carla_api.loadWorld()
            self._world = self._carla_api.getWorld()
            self._vehicle.spawn(self._world)
            self.timer = self.create_timer(0.05, self.timer_callback)
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to activate CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Deactivating CarlaNode")
        try:
            if self._vehicle is not None:
                self._vehicle.destroy()
            if self._carla_api is not None:
                self._carla_api.disconnect()
            self.timer.cancel()
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to deactivate CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Cleaning up CarlaNode")
        try:
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to cleanup CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE 

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Shutting down CarlaNode")
        try:
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to shutdown CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE

    def timer_callback(self):
        try:
            self._carla_api.tick()
        except SimError as e:
            self._logger.error(f"Failed during timer callback: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = CarlaNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()