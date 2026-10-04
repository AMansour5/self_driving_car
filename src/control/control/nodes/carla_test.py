#!/usr/bin/env python3
"""Publish one CARLA RGB camera as sensor_msgs/Image (ROS2 Humble, WSL2).

Topic: /carla/camera/image_raw  (encoding bgra8, frame_id "camera")

Run:
  source /opt/ros/humble/setup.bash
  python3 carla_camera_pub.py --ros-args -p host:=<windows-host-ip>
"""
import queue

import carla
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class CarlaCameraPublisher(Node):
    def __init__(self):
        super().__init__("carla_camera_pub")

        self.declare_parameter("host", "172.24.192.1")
        self.declare_parameter("port", 2000)
        self.declare_parameter("width", 640)
        self.declare_parameter("height", 480)
        self.declare_parameter("fps", 20.0)

        host = self.get_parameter("host").value
        port = self.get_parameter("port").value
        width = self.get_parameter("width").value
        height = self.get_parameter("height").value
        fps = self.get_parameter("fps").value

        self.pub = self.create_publisher(Image, "/carla/camera/image_raw", 10)
        self.frames = queue.Queue(maxsize=5)
        self.actors = []
        self.camera = None

        # Connect and report versions
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.get_logger().info(
            f"client={self.client.get_client_version()} "
            f"server={self.client.get_server_version()}"
        )
        self.world = self.client.get_world()
        self.original_settings = self.world.get_settings()

        # Synchronous mode, fixed step: one render per tick keeps GPU load capped
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 1.0 / fps
        self.world.apply_settings(settings)

        # Vehicle + camera
        bp_lib = self.world.get_blueprint_library()
        vehicle_bp = bp_lib.filter("vehicle.tesla.model3")[0]
        spawn_point = self.world.get_map().get_spawn_points()[0]
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
        self.actors.append(self.vehicle)

        cam_bp = bp_lib.find("sensor.camera.rgb")
        cam_bp.set_attribute("image_size_x", str(width))
        cam_bp.set_attribute("image_size_y", str(height))
        cam_bp.set_attribute("fov", "90")
        cam_tf = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(cam_bp, cam_tf, attach_to=self.vehicle)
        self.actors.append(self.camera)
        self.camera.listen(self._on_image)

        # Gentle throttle so the image visibly changes during the test
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.3))

        # Each timer tick advances the sim one step and publishes the new frame
        self.timer = self.create_timer(1.0 / fps, self._step)
        self.get_logger().info(
            f"Publishing {width}x{height} @ {fps:.0f} Hz on /carla/camera/image_raw"
        )

    def _on_image(self, image):
        # Runs on a CARLA thread: only hand the frame over, publish elsewhere
        try:
            self.frames.put_nowait(image)
        except queue.Full:
            pass

    def _step(self):
        self.world.tick()
        try:
            image = self.frames.get(timeout=2.0)
        except queue.Empty:
            self.get_logger().warn("No camera frame received after tick")
            return

        arr = np.frombuffer(image.raw_data, dtype=np.uint8)

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera"
        msg.height = image.height
        msg.width = image.width
        msg.encoding = "bgra8"
        msg.is_bigendian = 0
        msg.step = image.width * 4
        msg.data = arr.tobytes()
        self.pub.publish(msg)

    def cleanup(self):
        # Restore settings, or the server can stay stuck in sync mode
        try:
            if self.camera is not None:
                self.camera.stop()
            for actor in reversed(self.actors):
                actor.destroy()
            self.world.apply_settings(self.original_settings)
            self.get_logger().info("Cleaned up CARLA actors and settings")
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"Cleanup failed: {exc}")


def main():
    rclpy.init()
    node = None
    try:
        node = CarlaCameraPublisher()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()