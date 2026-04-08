import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class ObstacleDetector(Node):
    def __init__(self):
        super().__init__('obstacle_detector')
        
        # Subscribe to LiDAR scan data
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # Publish a True/False flag for obstacles
        self.publisher = self.create_publisher(
            Bool,
            '/obstacle_detected',
            10
        )
        
        # Define how close an object needs to be to trigger the flag (in meters)
        self.safe_distance = 0.5 
        
        self.get_logger().info("LiDAR Obstacle Detector Node Started 🛑")

    def scan_callback(self, msg):
        # The Turtlebot3 LiDAR sends 360 distance readings. 
        # Index 0 is straight ahead. We will check a 60-degree arc in the front.
        # Indices 0 to 30 (front-left) and 330 to 359 (front-right).
        front_angles = list(msg.ranges[0:30]) + list(msg.ranges[330:360])
        
        obstacle_detected = False
        
        for distance in front_angles:
            # Check if the reading is valid (not infinite/NaN) and closer than our safe distance
            if 0.0 < distance < self.safe_distance and not math.isinf(distance) and not math.isnan(distance):
                obstacle_detected = True
                break # We found an obstacle, no need to check the rest of the angles

        # Publish the result
        msg_out = Bool()
        msg_out.data = obstacle_detected
        self.publisher.publish(msg_out)

        # Print debug info to the terminal (throttled so it doesn't spam too fast)
        if obstacle_detected:
            self.get_logger().warn(f"OBSTACLE DETECTED within {self.safe_distance}m!", throttle_duration_sec=1.0)
        else:
            self.get_logger().info("Path clear.", throttle_duration_sec=2.0)

def main():
    rclpy.init()
    node = ObstacleDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
