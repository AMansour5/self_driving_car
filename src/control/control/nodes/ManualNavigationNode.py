import rclpy
from control.services.Joystick import CJoystick
from control.services.Navigation import Navigation
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn

class ManualNavigationNode(LifecycleNode):
    def __init__(self):
        super().__init__('manual_navigation_node')
        self._logger = self.get_logger()

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Configuring ManualNavigationNode...')
        self._joystick = CJoystick()
        self._navigation = Navigation()
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Activating ManualNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Deactivating ManualNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Cleaning up ManualNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Shutting down ManualNavigationNode...')
        return TransitionCallbackReturn.SUCCESS

def main(args=None):
    rclpy.init(args=args)
    try:
        node = ManualNavigationNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
