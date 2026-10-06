from glob import glob
from setuptools import find_packages, setup

package_name = 'carla_sim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
        ("share/" + package_name + "/launch", glob("launch/*.py")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mansour',
    maintainer_email='ahmedmonsour5@icloud.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'carla_api_test_node = carla_sim.test_nodes.CarlaApiTestNode:main',
            'carla_vehicle_test_node = carla_sim.test_nodes.CarlaVehicleTestNode:main',
            'carla_lifecycle_node = carla_sim.nodes.CarlaNode:main'
        ],
    },
)
