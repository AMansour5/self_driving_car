import math
import time
import rclpy
import signal
from control.services.Driver import Driver
from ackermann_msgs.msg import AckermannDrive
from carla_msgs.msg import CarlaEgoVehicleInfo
from rclpy.signals import SignalHandlerOptions
from control.services.Joystick import CJoystick
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

ROLE_NAME = 'hero'
DEFAULT_MAX_STEERING_ANGLE = math.radians(70)  # same fallback carla_ackermann_control uses

class ManualDriveNode(LifecycleNode):
    def __init__(self):
        super().__init__('manual_drive_node')
        self._logger = self.get_logger()
        self.joystick = None
        self.driver = None
        self.drive_pub = None
        self.vehicle_info_sub = None
        self.control_timer = None

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Configuring ManualDriveNode...')
        try:
            self.joystick = CJoystick()
            self.driver = Driver()
        except Exception as e:
            self._logger.error(f'Failed to configure ManualDriveNode: {e}')
            return TransitionCallbackReturn.FAILURE
        drive_qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10, reliability=ReliabilityPolicy.RELIABLE)
        self.drive_pub = self.create_publisher(AckermannDrive, f'/carla/{ROLE_NAME}/ackermann_cmd', drive_qos)
        # The bridge latches vehicle_info, so a late subscriber only gets it with TRANSIENT_LOCAL
        info_qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10,
                              reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.vehicle_info_sub = self.create_subscription(
            CarlaEgoVehicleInfo, f'/carla/{ROLE_NAME}/vehicle_info', self.vehicle_info_callback, info_qos)
        timer_period = 1.0 / 100.0
        self.control_timer = self.create_timer(timer_period, self.control_loop_callback)
        self.control_timer.cancel()
        return TransitionCallbackReturn.SUCCESS
    
    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Activating ManualDriveNode...')
        self.driver.reset()
        self.control_timer.reset()
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Deactivating ManualDriveNode...')
        self.control_timer.cancel()
        self.publish_safe_stop()
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Cleaning up ManualDriveNode...')
        self._release_resources()
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: LifecycleState) -> TransitionCallbackReturn:
        self._logger.info('Shutting down ManualDriveNode...')
        if self.control_timer is not None:
            self.control_timer.cancel()
        self.publish_safe_stop()
        self._release_resources()
        return TransitionCallbackReturn.SUCCESS

    def vehicle_info_callback(self, msg: CarlaEgoVehicleInfo):
        # Only front wheels steer; the bridge reports the others as 0. Already in radians.
        steering = [w.max_steer_angle for w in msg.wheels if w.max_steer_angle > 0.0]
        self.driver.set_max_steering_angle(min(steering) if steering else DEFAULT_MAX_STEERING_ANGLE)

    def control_loop_callback(self):
        try:
            axes = self.joystick.getAxis()
            if axes is None:
                self._logger.warn('No fresh joystick data, publishing safe stop.', throttle_duration_sec=2.0)
                self.publish_safe_stop()
                return
            command = self.driver.drive(axes.get('r2_axis', 0.0),
                                        axes.get('l2_axis', 0.0),
                                        axes.get('left_x_axis', 0.0))
            if command is None:
                self._logger.warn('Driver rejected the input (or vehicle_info has not arrived), publishing safe stop.',
                                  throttle_duration_sec=2.0)
                self.publish_safe_stop()
                return
            msg = AckermannDrive()
            msg.speed = command.speed
            msg.acceleration = command.acceleration
            msg.jerk = command.jerk
            msg.steering_angle = command.steering_angle
            msg.steering_angle_velocity = command.steering_angle_velocity
            self.drive_pub.publish(msg)
        except Exception as e:
            self._logger.error(f'Control loop failed: {e}', throttle_duration_sec=2.0)
            self.publish_safe_stop()

    def publish_safe_stop(self):
        if self.driver is not None:
            self.driver.reset()
        if self.drive_pub is None:
            return
        try:
            stop_msg = AckermannDrive()
            stop_msg.jerk = 0.0
            stop_msg.speed = 0.0
            stop_msg.acceleration = 0.0
            stop_msg.steering_angle = 0.0
            stop_msg.steering_angle_velocity = 0.0
            self.drive_pub.publish(stop_msg)
        except Exception as e:
            self._logger.error(f'Failed to publish safe stop: {e}')

    def _release_resources(self):
        if self.control_timer is not None:
            self.destroy_timer(self.control_timer)
            self.control_timer = None
        if self.vehicle_info_sub is not None:
            self.destroy_subscription(self.vehicle_info_sub)
            self.vehicle_info_sub = None
        if self.drive_pub is not None:
            self.destroy_publisher(self.drive_pub)
            self.drive_pub = None

def main(args=None):
    # With rclpy's default handler, Ctrl+C invalidates the context before we can publish the stop
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    signal.signal(signal.SIGINT, signal.default_int_handler)  # a parent may start us with SIGINT ignored
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    node = None
    try:
        node = ManualDriveNode()
        # A blocking spin() never returns to Python while no timer fires, so signals would be ignored
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            if rclpy.ok():
                node.publish_safe_stop()
                time.sleep(0.1)  # let the message leave before the publisher is destroyed
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()

