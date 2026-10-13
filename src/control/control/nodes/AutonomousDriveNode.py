import rclpy
from control.services.Joystick import CJoystick
from control.services.Driver import Driver
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn

class AutonomousDriveNode(LifecycleNode):
    def __init__(self):
        super().__init__('autonomous_drive_node')
        self._logger = self.get_logger()

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Configuring AutonomousDriveNode...')
        self._joystick = CJoystick()
        self._driver = Driver()
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Activating AutonomousDriveNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Deactivating AutonomousDriveNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Cleaning up AutonomousDriveNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Shutting down AutonomousDriveNode...')
        return TransitionCallbackReturn.SUCCESS

def main(args=None):
    rclpy.init(args=args)
    try:
        node = AutonomousDriveNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()

    