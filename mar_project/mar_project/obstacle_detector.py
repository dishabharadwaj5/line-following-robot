#!/usr/bin/env python3
"""
Obstacle Detector Node
- Subscribes to /scan (LiDAR)
- Checks 60° cone in front of robot
- Publishes True/False to /obstacle_detected
- Safe distance increased to 0.40 m (was 0.15 m — too close!)
- Added hysteresis: requires 3 consecutive clear readings before declaring safe
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math


SAFE_DISTANCE   = 0.40   # metres — stop if anything closer than this
CONE_HALF_ANGLE = 30     # degrees — check ±30° in front = 60° total cone
CLEAR_HYSTERESIS = 3     # consecutive clear scans needed before "safe" again


class ObstacleDetector(Node):
    def __init__(self):
        super().__init__('obstacle_detector')

        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        self.pub = self.create_publisher(Bool, '/obstacle_detected', 10)

        self.obstacle_active = False
        self.clear_count = 0

        self.get_logger().info("✅ Obstacle Detector Node started")

    def scan_callback(self, msg: LaserScan):
        ranges = msg.ranges
        n = len(ranges)
        if n == 0:
            return

        angle_inc_deg = math.degrees(msg.angle_increment)

        # Index slices for ±CONE_HALF_ANGLE around front (index 0)
        slice_size = int(CONE_HALF_ANGLE / angle_inc_deg)

        front_indices = list(range(0, slice_size + 1)) + \
                        list(range(n - slice_size, n))

        obstacle_found = False
        min_dist = float('inf')

        for i in front_indices:
            r = ranges[i]
            if math.isfinite(r) and r > 0.01:   # ignore 0 / inf / nan
                if r < SAFE_DISTANCE:
                    obstacle_found = True
                    min_dist = min(min_dist, r)

        # Hysteresis logic: instant trigger, slow reset
        if obstacle_found:
            self.obstacle_active = True
            self.clear_count = 0
            self.get_logger().warn(
                f"🚨 OBSTACLE at {min_dist:.2f} m — STOPPING")
        else:
            self.clear_count += 1
            if self.clear_count >= CLEAR_HYSTERESIS:
                self.obstacle_active = False
                self.get_logger().info("✅ Path clear")

        out = Bool()
        out.data = self.obstacle_active
        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
