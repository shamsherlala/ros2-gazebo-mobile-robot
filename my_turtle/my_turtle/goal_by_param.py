import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class GoalByParam(Node):
    def __init__(self):
        super().__init__('goal_by_param')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)

        self.pose = None
        self.state = 'TURN'
        
        # declare parameters: name + default value
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('goals_x', [5.0, 8.0, 8.0, 5.0])
        self.declare_parameter('goals_y', [5.0, 5.0, 8.0, 8.0])

        # read the goal lists once and pair them
        goals_x = self.get_parameter('goals_x').value
        goals_y = self.get_parameter('goals_y').value
        self.goals = list(zip(goals_x, goals_y))
        
        self.goal_index = 0

    def pose_callback(self, msg):
        self.pose = msg

    def control_loop(self):
        if self.pose is None:
            return

        max_speed = self.get_parameter('max_speed').value
        
        goal_x, goal_y = self.goals[self.goal_index]
        distance = math.hypot(goal_x - self.pose.x, goal_y - self.pose.y)
        angle_to_goal = math.atan2(goal_y - self.pose.y, goal_x - self.pose.x)
        angle_error = math.atan2(
            math.sin(angle_to_goal - self.pose.theta),
            math.cos(angle_to_goal - self.pose.theta))

        cmd = Twist()

        if self.state == 'TURN':
            if abs(angle_error) < 0.02:
                self.state = 'DRIVE'
            else:
                cmd.angular.z = 2.0 * angle_error
        elif self.state == 'DRIVE':
            if distance < 0.05:
                self.get_logger().info(f'Reached goal {self.goal_index}')
                self.goal_index = (self.goal_index + 1) % len(self.goals)
                self.state = 'TURN'
            elif abs(angle_error) > 0.5:          # NEW: goal not in front anymore
                self.get_logger().warn('Off course, turning again')
                self.state = 'TURN'
            else:
                cmd.linear.x = min(max_speed, 1.5 * distance)
                cmd.angular.z = 0.5 * angle_error

        self.publisher.publish(cmd)


def main():
    rclpy.init()
    node = GoalByParam()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
