import rclpy
from control.services.Joystick import CJoystick
from control.services.Navigation import Navigation
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn

class AutonomousNavigationNode(LifecycleNode):
    def __init__(self):
        super().__init__('autonomous_navigation_node')
        self._logger = self.get_logger()

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Configuring AutonomousNavigationNode...')
        self._joystick = CJoystick()
        self._navigation = Navigation()
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Activating AutonomousNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Deactivating AutonomousNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Cleaning up AutonomousNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Shutting down AutonomousNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

def main(args=None):
    rclpy.init(args=args)
    try:
        node = AutonomousNavigationNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()

    