import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CircleDriver(Node):
    def __init__(self):
        super().__init__('circle_driver')                                      # node name
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)  # topic to send on
        self.timer = self.create_timer(0.5, self.send_command)                 # run every 0.5 s
        self.get_logger().info('Circle driver started')
        self.tick = 0

    def send_command(self):
        msg = Twist()
        step = self.tick % 10

        if step <4:
            msg.linear.x = 2.0    # forward speed
            msg.angular.z = 0.0   # turning speed
        elif step <6:
            msg.linear.x = 0.0
            msg.angular.z = 1.5708
        elif step <8:
            msg.linear.x = 1.0
            msg.angular.z = 0.0
        else:
            msg.linear.x = 0.0
            msg.angular.z = 1.5708

        self.publisher.publish(msg)
        self.tick +=1

def main():
    rclpy.init()
    node = CircleDriver()
    rclpy.spin(node)       # keep running until Ctrl+C
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
