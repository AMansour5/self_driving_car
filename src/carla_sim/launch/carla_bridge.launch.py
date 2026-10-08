import os
from launch import LaunchDescription
from utils.EnvParams import EnvParams
from utils.Configurator import Configurator
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    host = EnvParams().CARLA_HOST
    port = EnvParams().CARLA_PORT
    world_cfg = Configurator("carla_sim").fetchData(Configurator.CARLA_WORLD)["world"]
    objects_file = os.path.join(get_package_share_directory("carla_sim"), "config", "objects.json")

    carla_bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory("carla_ros_bridge"), "carla_ros_bridge.launch.py")),
        launch_arguments={
            'host': host,
            'port': port,
            'town': str(world_cfg["town"]),
            'fixed_delta_seconds': str(world_cfg["fixed_delta_seconds"]),
            'timeout': '60',  # map loads can exceed the bridge's 30 s default
        }.items()
    )
    spawn_objects_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory("carla_spawn_objects"), "carla_spawn_objects.launch.py")),
        launch_arguments={'objects_definition_file': objects_file}.items()
    )
    return LaunchDescription([
        carla_bridge_launch,
        spawn_objects_launch,
    ])