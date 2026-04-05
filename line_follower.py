import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from cv_bridge import CvBridge
import cv2


class LineFollower(Node):

    def __init__(self):
        super().__init__('line_follower')

        self.bridge = CvBridge()

        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publish error
        self.publisher = self.create_publisher(
            Float32,
            '/line_error',
            10
        )

        self.get_logger().info("Line Follower Node Started 🚀")

    def image_callback(self, msg):
        try:
            # Convert ROS image to OpenCV
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            height, width, _ = frame.shape

            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Threshold (adjust if needed)
            _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)

            # Region of Interest (bottom half)
            roi = thresh[int(height/2):height, :]

            # Find contours
            contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Largest contour = line
                c = max(contours, key=cv2.contourArea)
                M = cv2.moments(c)

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])

                    # Compute error
                    error = (width // 2) - cx

                    # Publish error
                    error_msg = Float32()
                    error_msg.data = float(error)
                    self.publisher.publish(error_msg)

                    self.get_logger().info(f"Error: {error}")

                    # Draw centroid and center line
                    cv2.circle(roi, (cx, 50), 5, (255, 0, 0), -1)
                    cv2.line(roi, (width//2, 0), (width//2, 100), (0, 255, 0), 2)

            # Show debug windows
            cv2.imshow("Threshold", thresh)
            cv2.imshow("ROI", roi)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Error: {e}")


def main():
    rclpy.init()
    node = LineFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
