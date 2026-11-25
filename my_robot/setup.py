import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.xacro')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shamsher Lala',
    maintainer_email='shamsherlala95@gmail.com',
    description='Differential drive robot in Gazebo Harmonic: URDF/xacro, sensors, obstacle avoidance, SLAM and Nav2',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'go_to_goal_gz = my_robot.go_to_goal_gz:main',
            'goal_by_service_action = my_robot.goal_by_service_action:main',
            'obstacle_avoider = my_robot.obstacle_avoider:main',
        ],
    },
)
