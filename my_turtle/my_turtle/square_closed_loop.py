import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class SquareClosedLoop(Node):
    def __init__(self):
        super().__init__('square_closed_loop')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)   # listen to real position
        self.timer = self.create_timer(0.05, self.control_loop)  # 20 times per second

        self.pose = None          # latest position from turtlesim
        self.state = 'DRIVE'      # current state: DRIVE or TURN
        self.side_length = 2.0
        self.side = 0
        self.start_x = None       # where the current side started
        self.start_y = None
        self.heading = None       # target direction

    def pose_callback(self, msg):
        self.pose = msg           # just store the newest position

    def control_loop(self):
        if self.pose is None:     # no position received yet
            return

        if self.heading is None:  # first run: remember starting direction
            self.heading = self.pose.theta

        cmd = Twist()

        if self.state == 'DRIVE':
            if self.start_x is None:              # start of a new side
                self.start_x = self.pose.x
                self.start_y = self.pose.y
                if self.side % 2 ==0:
                    self.side_length = 3.0
                else:
                    self.side_length = 1.5

            distance = math.hypot(self.pose.x - self.start_x,
                                  self.pose.y - self.start_y)

            remaining = self.side_length - distance
            if remaining > 0.01:
                cmd.linear.x = min(1.0, 2.0 * remaining)   # full speed, then slow down near the end
            else:
                self.state = 'TURN'               # side done
                self.heading += math.pi / 2       # new target: +90 degrees
                self.side += 1
                self.get_logger().info('Side done, turning')

        elif self.state == 'TURN':
            diff = self.heading - self.pose.theta
            error = math.atan2(math.sin(diff), math.cos(diff))  # keep error between -180 and +180 degrees

            if abs(error) > 0.01:
                cmd.angular.z = 2.0 * error       # P control
            else:
                self.state = 'DRIVE'              # turn done
                self.start_x = None               # new side starts next loop
                self.get_logger().info('Turn done, driving')

        self.publisher.publish(cmd)


def main():
    rclpy.init()
    node = SquareClosedLoop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
