#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class ObstacleDetector(Node):

    def __init__(self):
        super().__init__('obstacle_detector')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        self.publisher = self.create_publisher(
            Bool,
            '/obstacle_detected',
            10
        )
        self.safe_distance = 0.15
        self.get_logger().info("🚀 LiDAR Obstacle Detector Node Started")

    def scan_callback(self, msg):
        front_angles = list(msg.ranges[0:30]) + list(msg.ranges[330:360])
        obstacle_detected = False
        obstacle_distance = None

        for distance in front_angles:
            if math.isinf(distance) or math.isnan(distance):
                continue
            if distance == 0.0:
                continue
            if 0.05 < distance < self.safe_distance:
                obstacle_detected = True
                obstacle_distance = distance
                break

        msg_out = Bool()
        msg_out.data = obstacle_detected
        self.publisher.publish(msg_out)

        if obstacle_detected:
            self.get_logger().warn(f"🚨 OBSTACLE at {obstacle_distance:.2f} m")
        else:
            self.get_logger().info("✅ Path clear")

def main():
    rclpy.init()
    node = ObstacleDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
