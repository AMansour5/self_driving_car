import rclpy
import subprocess
from rclpy.node import Node
from utils.EnvParams import EnvParams

class GUIStreamingNode(Node):
    def __init__(self):
        super().__init__('gui_streaming_node')
        self.timer = self.create_timer(0.1, self.stream)

    def stream(self):
        command = f'mjpg_streamer -o "output_http.so -p 8080 -w {EnvParams().WEB_INDEX_LOCATION}"'
        subprocess.run(command, shell=True)

def main(args=None):
    rclpy.init(args=args)
    gui_streaming_node = GUIStreamingNode()
    try:
        rclpy.spin(gui_streaming_node)
    except KeyboardInterrupt:
        pass
    finally:
        gui_streaming_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == "__main__":
    main()