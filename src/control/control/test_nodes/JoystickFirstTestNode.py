import rclpy
from rclpy.node import Node
from control.services.Joystick import CJoystick

class JoystickFirstTestNode(Node):
    def __init__(self):
        super().__init__('joystick_first_test_node')
        self.joystick = CJoystick()
        self._logger = self.get_logger()
        self._button_timer = self.create_timer(0.1, self.testButtonPress)
        self._axis_timer = self.create_timer(0.1, self.testAxis)

    def testButtonPress(self):
        if self.joystick.isPressed("L1"):
            self._logger.info("L1 button is pressed")

    def testAxis(self):
        axis = self.joystick.getAxis()
        left_x = axis.get("left_x_axis", 0)
        left_y = axis.get("left_y_axis", 0)
        self._logger.info(f"Left X axis value: {left_x}")
        self._logger.info(f"Left Y axis value: {left_y}")

def main(args=None):
    rclpy.init(args=args)
    node = JoystickFirstTestNode()
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
