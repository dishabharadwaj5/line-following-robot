#!/usr/bin/env python3
"""
Control Node — the robot's brain
- Uses FULL PID for smooth line following
- Uses a 4-Stage Geometric State Machine for Obstacle Evasion
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import Twist
import time

# ── Tuning parameters ──────────────────────────────────────────────────────────
BASE_SPEED     = 0.20    
MIN_SPEED      = 0.05    
KP             = 0.008   
KI             = 0.001   
KD             = 0.004   
SEARCH_SPEED   = 0.6     
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
        self.sum_error = 0.0
        self.obstacle = False
        self.line_lost = False

        # --- THE NEW STATE MACHINE VARIABLES ---
        self.evasion_state = 0
        self.state_end_time = 0.0

        self.timer = self.create_timer(0.1, self.control_loop)   # 10 Hz
        self.get_logger().info("✅ Control Node with State Machine started")

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
        now = time.time()

        # TRIGGER THE BYPASS SEQUENCE IF AN OBSTACLE IS SEEN
        if self.obstacle and self.evasion_state == 0:
            self.evasion_state = 1
            self.state_end_time = now + 0.8  # Turn right for 0.8 seconds
            self.get_logger().warn("🚨 OBSTACLE! Starting Geometric Bypass...")

        # ── THE OBSTACLE BYPASS STATE MACHINE ──
        if self.evasion_state == 1:
            # STAGE 1: Pivot Right 
            if now < self.state_end_time:
                cmd.linear.x = 0.0
                cmd.angular.z = -0.8
                self.get_logger().info("↪️ Evasion Phase 1: Pivoting Right")
            else:
                self.evasion_state = 2
                self.state_end_time = now + 1.5  # Drive straight for 1.5 seconds

        elif self.evasion_state == 2:
            # STAGE 2: Drive forward past the box
            if now < self.state_end_time:
                cmd.linear.x = 0.15
                cmd.angular.z = 0.0
                self.get_logger().info("⬆️ Evasion Phase 2: Driving Forward")
            else:
                self.evasion_state = 3
                self.state_end_time = now + 0.8  # Turn left for 0.8 seconds

        elif self.evasion_state == 3:
            # STAGE 3: Pivot Left to face the track again
            if now < self.state_end_time:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.8
                self.get_logger().info("↩️ Evasion Phase 3: Pivoting Left")
            else:
                self.evasion_state = 4
                self.get_logger().info("🔎 Evasion Phase 4: Sweeping for Line...")

        elif self.evasion_state == 4:
            # STAGE 4: Sweep until line is found
            if self.line_lost:
                cmd.linear.x = 0.12
                # Drive forward with a slight left curl to guarantee hitting the line
                cmd.angular.z = 0.25 
            else:
                # LINE FOUND! Exit the state machine and return to normal driving
                self.evasion_state = 0
                self.sum_error = 0.0
                self.get_logger().info("✅ Line Acquired! Resuming PID.")

        # ── NORMAL DRIVING BEHAVIOR ──
        elif self.line_lost:
            # Normal Search Mode if it accidentally loses the line with no obstacle
            self.sum_error = 0.0
            cmd.linear.x  = 0.0
            cmd.angular.z = SEARCH_SPEED if self.error >= 0 else -SEARCH_SPEED
            self.get_logger().warn("🔍 Line lost → searching…")

        else:
            # Normal Line Following with FULL PID
            self.sum_error += self.error
            self.sum_error = max(min(self.sum_error, 250.0), -250.0)
            derivative     = self.error - self.prev_err
            
            angular        = -(KP * self.error + KI * self.sum_error + KD * derivative)
            
            speed_penalty = 0.001 * abs(self.error)
            current_speed = max(MIN_SPEED, BASE_SPEED - speed_penalty)

            cmd.linear.x   = float(current_speed)
            cmd.angular.z  = float(angular)
            self.get_logger().info(
                f"📍 PID | err={self.error:.1f} | vel={current_speed:.2f} | ω={angular:.3f}")

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
