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

    manual_navigation_node = Node(
        package='control',
        executable='manual_drive_node',
        output='screen',
        name='manual_drive_node'
    )

    autonomous_navigation_node = Node(
        package='control',
        executable='autonomous_drive_node',
        output='screen',
        name='autonomous_drive_node'
    )

    mission_manager_node = Node(
        package='control',
        executable='mission_manager_node',
        output='screen',
        name='mission_manager_node'
    )

    return LaunchDescription([
        joystick_node,
        rosbridge_server_node,
        # camera_streaming_node,
        gui_streaming_node,
        # carla_camera_pub_node,
        manual_navigation_node,
        autonomous_navigation_node,
        mission_manager_node,
    ])