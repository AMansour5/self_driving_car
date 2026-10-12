import rclpy
from rclpy.node import Node
from control.services.Joystick import CJoystick

class JoystickSecondTestNode(Node):
    def __init__(self):
        super().__init__('joystick_second_test_node')
        self.joystick = CJoystick()
        self._logger = self.get_logger()
        self._button_timer = self.create_timer(0.1, self.testButtonPress)
        self._axis_timer = self.create_timer(0.1, self.testAxis)

    def testButtonPress(self):
        if self.joystick.isPressed("BRAKE"):
            self._logger.info("Brake button is pressed")

    def testAxis(self):
        axis = self.joystick.getAxis()
        right_x = axis.get("right_x_axis", 0)
        right_y = axis.get("right_y_axis", 0)
        self._logger.info(f"Right X axis value: {right_x}")
        self._logger.info(f"Right Y axis value: {right_y}")

def main(args=None):
    rclpy.init(args=args)
    node = JoystickSecondTestNode()
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
