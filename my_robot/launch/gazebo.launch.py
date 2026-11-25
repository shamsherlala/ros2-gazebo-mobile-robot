import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro


def generate_launch_description():
    # read the URDF (same as display.launch.py)
    xacro_file = os.path.join(
        get_package_share_directory('my_robot'), 'urdf', 'my_robot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()

    #start Gazebo with an empty world (-r = start physics immediately)
    world_file = os.path.join(
        get_package_share_directory('my_robot'), 'worlds', 'obstacles.sdf')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r ' + world_file}.items(),
    )
    
    return LaunchDescription([
        gazebo,
        
        # publishes the URDF on /robot_description (and TF)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        ),
        
        # spawn: take the URDF from the topic and put th erobot in Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', 'robot_description', '-name', 'my_robot', '-z', '0.1'],
        ),
        
        # rviz: visualize the robot and the laser scan
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-f', 'odom'],
            parameters=[{'use_sim_time': True}],
        ),        
        
        # gateway: Gazebo topics <-> ROS topics
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            ],
            output='screen',
        ),
    ])