#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import Twist


class ControlNode(Node):

    def __init__(self):
        super().__init__('control_node')

        # Subscribers
        self.create_subscription(Float32, '/line_error', self.line_callback, 10)
        self.create_subscription(Bool, '/obstacle_detected', self.obstacle_callback, 10)

        # Publisher (TwistStamped ONLY)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.error = 0.0
        self.obstacle = False

        self.timer = self.create_timer(0.1, self.control_loop)

    def line_callback(self, msg):
        self.error = msg.data

    def obstacle_callback(self, msg):
        self.obstacle = msg.data

    def control_loop(self):
        cmd = Twist()

        if self.obstacle:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.get_logger().warn("🚨 OBSTACLE → STOP")
        else:
            k = 0.005
            cmd.linear.x = 0.2
            cmd.angular.z = -k * self.error

            self.get_logger().info(f"Following line | error: {self.error}")

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
