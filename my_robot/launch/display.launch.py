import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # find the installed URDF file and read it as text
    xacro_file = os.path.join(
        get_package_share_directory('my_robot'), 'urdf', 'my_robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()
    
    return LaunchDescription([    
        # reads the URDF, publishes position of all parts (TF)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),
        # small window with sliders to turn the wheels by hand
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
        ),
        # 3D viewer
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-f', 'base_footprint'],
        ),
    ])
    