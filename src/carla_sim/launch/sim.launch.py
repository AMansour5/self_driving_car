"""Start carla_sim and walk it through configure -> activate.

  export CARLA_HOST=$(ip route show default | awk '{print $3}')
  ros2 launch carla_sim sim.launch.py town:=Town03
  ros2 launch carla_sim sim.launch.py auto_start:=false   # then drive it by hand:
      ros2 lifecycle set /carla_sim configure
      ros2 lifecycle set /carla_sim activate
"""
import lifecycle_msgs.msg
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState


def generate_launch_description():
    auto = LaunchConfiguration("auto_start")

    node = LifecycleNode(
        package="carla_sim",
        executable="carla_sim_node",
        name="carla_sim",
        namespace="",
        output="screen",
        parameters=[{"town": LaunchConfiguration("town")}],
    )

    def change(transition_id):
        return EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(node), transition_id=transition_id))

    configure = EmitEvent(
        event=ChangeState(lifecycle_node_matcher=matches_action(node),
                          transition_id=lifecycle_msgs.msg.Transition.TRANSITION_CONFIGURE),
        condition=IfCondition(auto))

    # Only fire right after configuring, so a manual deactivate is not undone
    activate_after_configure = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=node,
            start_state="configuring",
            goal_state="inactive",
            entities=[change(lifecycle_msgs.msg.Transition.TRANSITION_ACTIVATE)]),
        condition=IfCondition(auto))

    return LaunchDescription([
        DeclareLaunchArgument("town", default_value="", description="Overrides world.town in rig.yaml"),
        DeclareLaunchArgument("auto_start", default_value="true"),
        node,
        activate_after_configure,
        configure,
    ])