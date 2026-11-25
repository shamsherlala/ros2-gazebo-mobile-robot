import math

from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


def yaw_from_quaternion(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))

class GoalByService(Node):
    def __init__(self):
        super().__init__('goal_by_service_action')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)

        self.srv = self.create_service(SetBool, 'enable', self.enable_callback)

        self.odom = None
        self.enabled = True
        self.state = 'TURN'
        
        # declare parameters: name + default value
        self.declare_parameter('max_speed', 0.5)
        self.declare_parameter('goals_x', [2.0, 2.0, 0.0, 0.0])
        self.declare_parameter('goals_y', [0.0, 2.0, 2.0, 0.0])

        # read the goal lists once and pair them
        goals_x = self.get_parameter('goals_x').value
        goals_y = self.get_parameter('goals_y').value
        self.goals = list(zip(goals_x, goals_y))
        
        self.goal_index = 0

    def enable_callback(self, request, response):
        self.enabled = request.data                     # store the switch position
        if self.enabled:
            self.state = 'TURN'                         # re-aim after a pause
            self.get_logger().info('Robot enabled')
            response.message = 'enabled'
        else:
            self.get_logger().info('Robot disabled')
            response.message = 'disabled'
        response.success = True
        return response

    def odom_callback(self, msg):
        self.odom = msg

    def control_loop(self):
        
        if not self.enabled:
            self.publisher.publish(Twist())  # all zeros = stop
            return
        
        if self.odom is None:
            return

        max_speed = self.get_parameter('max_speed').value
        
        x = self.odom.pose.pose.position.x
        y = self.odom.pose.pose.position.y
        yaw = yaw_from_quaternion(self.odom.pose.pose.orientation)

        goal_x, goal_y = self.goals[self.goal_index]
        distance = math.hypot(goal_x - x, goal_y - y)
        angle_to_goal = math.atan2(goal_y - y, goal_x - x)
        angle_error = math.atan2(math.sin(angle_to_goal - yaw),
                                 math.cos(angle_to_goal - yaw))

        cmd = Twist()

        if self.state == 'TURN':
            if abs(angle_error) < 0.05:
                self.state = 'DRIVE'
            else:
                cmd.angular.z = max(-1.0, min(1.0, 2.0 * angle_error))
        elif self.state == 'DRIVE':
            if distance < 0.1:
                self.get_logger().info(f'Reached goal {self.goal_index}')
                self.goal_index = (self.goal_index + 1) % len(self.goals)
                self.state = 'TURN'
            elif abs(angle_error) > 0.5:          # NEW: goal not in front anymore
                self.get_logger().warn('Off course, turning again')
                self.state = 'TURN'
            else:
                cmd.linear.x = min(max_speed, 1.5 * distance)
                cmd.angular.z = cmd.angular.z = 0.5 * angle_error  # limit angular speed

        self.publisher.publish(cmd)


def main():
    rclpy.init()
    node = GoalByService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
