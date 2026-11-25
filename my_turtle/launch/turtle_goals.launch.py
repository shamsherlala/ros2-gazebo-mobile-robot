from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # node1: simulator
        Node(
            package='turtlesim',
            executable='turtlesim_node',
        ),
        
        #node2: controller with parameters
        Node(
            package='my_turtle',
            executable='goal_by_param',
            parameters=[{
                'max_speed': 2.0,
                'goals_x': [3.0, 8.0, 5.5],
                'goals_y': [3.0, 3.0, 8.0]
            }]
        ),
        
        #node3: teleop
        Node(
            package='turtlesim',
            executable='turtle_teleop_key',
        ),
    ])