#!/usr/bin/env python3
"""
Line Follower Node
- Subscribes to /camera/image_raw
- Detects black line on white/grey ground using HSV masking
- Publishes line error to /line_error
- Publishes lost-line flag to /line_lost
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, Bool
from cv_bridge import CvBridge
import cv2
import numpy as np


class LineFollower(Node):
    def __init__(self):
        super().__init__('line_follower')

        self.bridge = CvBridge()
        self.last_error = 0.0   # remember last error when line is lost

        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        self.error_pub  = self.create_publisher(Float32, '/line_error', 10)
        self.lost_pub   = self.create_publisher(Bool,    '/line_lost',  10)

        self.get_logger().info("✅ Line Follower Node started")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            h, w, _ = frame.shape

            # --- Use bottom 40% of frame as ROI (closer to ground) ---
            roi = frame[int(h * 0.6):h, :]

            # --- Convert to HSV and mask for BLACK line ---
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            # Black = low value regardless of hue/saturation
            lower_black = np.array([0,   0,   0])
            upper_black = np.array([180, 255, 80])
            mask = cv2.inRange(hsv, lower_black, upper_black)

            # Morphological cleanup
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)

            line_lost = Bool()
            error_msg = Float32()

            if contours:
                c = max(contours, key=cv2.contourArea)
                if cv2.contourArea(c) > 300:   # ignore tiny noise
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        error = float((w // 2) - cx)
                        self.last_error = error

                        error_msg.data = error
                        line_lost.data = False
                        self.error_pub.publish(error_msg)
                        self.lost_pub.publish(line_lost)

                        self.get_logger().info(
                            f"📍 Line found | cx={cx} | error={error:.1f}")

                        # Debug visualisation
                        roi_vis = roi.copy()
                        cv2.circle(roi_vis, (cx, roi.shape[0]//2), 8,
                                   (0, 0, 255), -1)
                        cv2.line(roi_vis, (w//2, 0), (w//2, roi.shape[0]),
                                 (0, 255, 0), 2)
                        cv2.imshow("ROI", roi_vis)
                        cv2.imshow("Mask", mask)
                        cv2.waitKey(1)
                        return

            # Line not found — publish last known error + lost flag
            error_msg.data = self.last_error
            line_lost.data = True
            self.error_pub.publish(error_msg)
            self.lost_pub.publish(line_lost)
            self.get_logger().warn("⚠️  Line NOT detected")

        except Exception as e:
            self.get_logger().error(f"Image callback error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = LineFollower()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
