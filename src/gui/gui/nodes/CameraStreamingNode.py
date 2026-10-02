#!/usr/bin/env python3
"""Republish raw camera Images as JPEG CompressedImage (<topic>/compressed).

rosbridge sends everything as JSON, so raw 640x480 frames are far too heavy
for a browser. Run alongside carla_camera_pub.py.
"""
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image

TOPICS = [
    "/carla/camera/image_raw",
    "/carla/camera_rear/image_raw",
    "/carla/camera_left/image_raw",
    "/carla/camera_right/image_raw",
]
JPEG_QUALITY = 70


class CameraStreamingNode(Node):
    def __init__(self):
        super().__init__("camera_streaming_node")
        for topic in TOPICS:
            # Default (reliable) QoS on the output so rosbridge can subscribe
            pub = self.create_publisher(CompressedImage, topic + "/compressed", 1)
            self.create_subscription(
                Image, topic, lambda msg, p=pub: self.on_image(msg, p), qos_profile_sensor_data
            )

    def on_image(self, msg, pub):
        channels = 4 if msg.encoding == "bgra8" else 3
        if msg.encoding not in ("bgra8", "bgr8", "rgb8"):
            return
        img = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, channels)
        if msg.encoding == "bgra8":
            img = np.ascontiguousarray(img[:, :, :3])
        elif msg.encoding == "rgb8":
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ok:
            return
        out = CompressedImage()
        out.header = msg.header
        out.format = "jpeg"
        out.data = buf.tobytes()
        pub.publish(out)


def main():
    rclpy.init()
    node = CameraStreamingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()