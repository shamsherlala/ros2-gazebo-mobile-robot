import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_turtle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shamsher Lala',
    maintainer_email='shamsherlala95@gmail.com',
    description='ROS 2 basics with turtlesim: publishers, subscribers, state machines, P control, parameters, launch files',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'circle_driver = my_turtle.circle_driver:main',
            'square_closed_loop = my_turtle.square_closed_loop:main',
            'go_to_goal = my_turtle.go_to_goal:main',
            'goal_by_param = my_turtle.goal_by_param:main',
        ],
    },
)
