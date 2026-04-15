#!/usr/bin/env python3
"""
Control Node — the robot's brain
- Subscribes to /line_error, /line_lost, /obstacle_detected
- Uses a PD controller (not just P) for smoother steering
- If line is lost: spins slowly to search for it
- If obstacle: full stop
- Publishes geometry_msgs/Twist to /cmd_vel  (plain Twist, correct for TurtleBot3)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import Twist


# ── Tuning parameters ──────────────────────────────────────────────────────────
LINEAR_SPEED   = 0.18    # m/s forward speed
KP             = 0.004   # proportional gain  (was 0.005 — same ballpark)
KD             = 0.002   # derivative gain    (new — reduces oscillation)
SEARCH_SPEED   = 0.3     # rad/s spin when line is lost
# ───────────────────────────────────────────────────────────────────────────────


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        self.create_subscription(Float32, '/line_error',        self.line_cb,     10)
        self.create_subscription(Bool,    '/obstacle_detected', self.obstacle_cb, 10)
        self.create_subscription(Bool,    '/line_lost',         self.lost_cb,     10)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.error    = 0.0
        self.prev_err = 0.0
        self.obstacle = False
        self.line_lost = False

        self.timer = self.create_timer(0.1, self.control_loop)   # 10 Hz

        self.get_logger().info("✅ Control Node started")

    # ── Callbacks ──────────────────────────────────────────────────────────────
    def line_cb(self, msg):
        self.error = msg.data

    def obstacle_cb(self, msg):
        self.obstacle = msg.data

    def lost_cb(self, msg):
        self.line_lost = msg.data

    # ── Main control loop ──────────────────────────────────────────────────────
    def control_loop(self):
        cmd = Twist()

        if self.obstacle:
            # PRIORITY 1: obstacle — full stop
            cmd.linear.x  = 0.0
            cmd.angular.z = 0.0
            self.get_logger().warn("🚨 OBSTACLE → STOP")

        elif self.line_lost:
            # PRIORITY 2: lost line — spin slowly in last-error direction
            cmd.linear.x  = 0.0
            cmd.angular.z = SEARCH_SPEED if self.error >= 0 else -SEARCH_SPEED
            self.get_logger().warn("🔍 Line lost → searching…")

        else:
            # PRIORITY 3: normal line following with PD controller
            derivative     = self.error - self.prev_err
            angular        = -(KP * self.error + KD * derivative)
            cmd.linear.x   = LINEAR_SPEED
            cmd.angular.z  = angular
            self.get_logger().info(
                f"📍 Following | err={self.error:.1f} | ω={angular:.3f}")

        self.prev_err = self.error
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
