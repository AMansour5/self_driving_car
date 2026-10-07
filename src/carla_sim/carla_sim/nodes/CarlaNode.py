import rclpy
from utils.Configurator import Configurator
from carla_sim.services.CarlaApi import CarlaApi
from carla_sim.exceptions.SimError import SimError
from carla_sim.services.CarlaLidar import CarlaLidar
from carla_sim.services.CarlaVehicle import CarlaVehicle
from carla_sim.publishers.LidarPublisher import LidarPublisher
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
        self._lidar_cfg = None
        self._lidar = None
        self._lidar_pub = None
        self.timer = None

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Configuring CarlaNode")
        try:
            self.configurator = Configurator("carla_sim")
            self._world_cfg = self.configurator.fetchData(Configurator.CARLA_WORLD)
            self._vehicle_cfg = self.configurator.fetchData(Configurator.VEHICLE)
            self._carla_api = CarlaApi(self._world_cfg)
            self._vehicle = CarlaVehicle(self._vehicle_cfg)
            self._lidar_cfg = self.configurator.fetchData(Configurator.LIDAR)
            self._lidar = CarlaLidar(self._lidar_cfg, self._carla_api.fixed_delta_seconds)
            self._lidar_pub = LidarPublisher(self, self._lidar.topic)
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
            self._lidar.attach(self._world, self._vehicle.actor)
            self.timer = self.create_timer(0.05, self.timer_callback)
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to activate CarlaNode: {e}")
            try:
                self.teardown()  # loadWorld left the server in synchronous mode: undo it
            except SimError as cleanup_error:
                self._logger.error(f"Teardown after failed activation also failed: {cleanup_error}")
            return TransitionCallbackReturn.FAILURE

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Deactivating CarlaNode")
        try:
            self.teardown()
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to deactivate CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Cleaning up CarlaNode")
        try:
            if self._lidar_pub is not None:
                self._lidar_pub.destroy()
                self._lidar_pub = None
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to cleanup CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE 

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info("Shutting down CarlaNode")
        try:
            self.teardown()
            return TransitionCallbackReturn.SUCCESS
        except SimError as e:
            self._logger.error(f"Failed to shutdown CarlaNode: {e}")
            return TransitionCallbackReturn.FAILURE

    def timer_callback(self):
        try:
            self._carla_api.tick()
            for scan in self._lidar.poll():
                self._lidar_pub.publish(scan)
        except SimError as e:
            self._logger.error(f"Failed during timer callback: {e}")

    def teardown(self):
        """Stop ticking, detach the lidar, destroy the car and restore the server.
        Safe to call more than once: deactivate, a failed activate, shutdown and main() all use it."""
        if self.timer is not None:
            self.destroy_timer(self.timer)
            self.timer = None
        try:
            if self._lidar is not None:
                self._lidar.detach()
            if self._vehicle is not None:
                self._vehicle.destroy()
        finally:
            if self._carla_api is not None:
                self._carla_api.disconnect()

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
            try:
                node.teardown()
            except SimError as e:
                print(f"Failed to tear down CarlaNode: {e}")
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()