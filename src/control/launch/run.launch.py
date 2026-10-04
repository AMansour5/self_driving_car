from launch_ros.actions import Node
from launch import LaunchDescription

def generate_launch_description():

    joystick_node = Node(
        package='control',
        executable='joystick_node',
        output="screen",
        name="joystick_node"
    )

    rosbridge_server_node = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        output='screen',
        name='rosbridge_websocket',
        parameters=[{'port': 9090}]
    )

    camera_streaming_node = Node(
        package='gui',
        executable='camera_streaming_node',
        output='screen',
        name='camera_streaming_node'
    )

    gui_streaming_node = Node(
        package='gui',
        executable='gui_streaming_node',
        output='screen',
        name='gui_streaming_node'
    )

    carla_camera_pub_node = Node(
        package='control',
        executable='carla_camera_pub',
        output='screen',
        name='carla_camera_pub'
    )

    return LaunchDescription([
        joystick_node,
        rosbridge_server_node,
        camera_streaming_node,
        gui_streaming_node,
        carla_camera_pub_node,
    ])