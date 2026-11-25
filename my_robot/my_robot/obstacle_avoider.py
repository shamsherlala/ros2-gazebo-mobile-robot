import math

from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


def closest(ranges, start, end):
    values = [r for r in ranges[start:end] if math.isfinite(r)]
    return min(values, default=float('inf'))

def farthest(ranges, max_range):
    # largest distance seen in any direction (.inf counts as max range)
    return max(r if math.isfinite(r) else max_range for r in ranges)

class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__('obstacle_avoider')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.laser_callback, 10)
        self.timer = self.create_timer(0.05, self.control_loop)

        self.srv = self.create_service(SetBool, 'enable', self.enable_callback)

        self.laser = None
        self.enabled = True
        self.state = 'TURN'
        self.turn_dir = 1.0
        
        # declare parameters: name + default value
        self.declare_parameter('max_speed', 0.5)

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

    def laser_callback(self, msg):
        self.laser = msg

    def control_loop(self):
        
        if not self.enabled:
            self.publisher.publish(Twist())  # all zeros = stop
            return
        
        if self.laser is None:
            return

        max_speed = self.get_parameter('max_speed').value

        front = closest(self.laser.ranges, 160, 201)  # front is 160-200 degrees
        left = closest(self.laser.ranges, 240, 301)  # left is 240-300 degrees
        right = closest(self.laser.ranges, 60, 121)  # right is 60-120 degrees

        open_space = farthest(self.laser.ranges, self.laser.range_max)
        
        ahead = self.laser.ranges[180]
        if not math.isfinite(ahead):
            ahead = self.laser.range_max
        
        cmd = Twist()

        if self.state == 'TURN':
            if ahead > 0.8 * open_space and front > 0.6:
                self.state = 'DRIVE'
                self.get_logger().info('Switching to DRIVE state')
            else:
                cmd.angular.z = 0.8 * self.turn_dir
        elif self.state == 'DRIVE':
            if front < 0.6:
                self.turn_dir = 1.0 if left > right else -1.0  # turn towards the side with more space
                self.get_logger().info(f'Obstacle at {front:.2f} m, turning {"left" if self.turn_dir > 0 else "right"}')
                self.state = 'TURN'
            else:
                cmd.linear.x = min(max_speed, 0.5 * (front - 0.4))  # slow down near obstacles

        self.publisher.publish(cmd)


def main():
    rclpy.init()
    node = ObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
