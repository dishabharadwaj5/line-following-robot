

# 📷 Line Following Module (Member 1)

## 📌 Overview

This module detects a line using camera input and publishes an error signal for robot control in ROS 2 (Humble).

---

## 🧠 Working

* Subscribe to `/camera/image_raw`
* Process image using OpenCV
* Detect line (threshold + contour)
* Compute error:

  ```
  error = center_x - line_x
  ```
* Publish to `/line_error`

---

## 📡 Topics

| Topic               | Type           |
| ------------------- | -------------- |
| `/camera/image_raw` | Image input    |
| `/line_error`       | Float32 output |

---

## ⚙️ Setup

```bash
sudo apt update
sudo apt install python3-opencv ros-humble-cv-bridge
```

---

## 🚀 Run

### 1. Launch simulation

```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 2. Run node

```bash
source /opt/ros/humble/setup.bash
python3 line_follower.py
```

### 3. (Optional) Teleop

```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 run turtlebot3_teleop teleop_keyboard
```

---

## 🎯 Output

* OpenCV window shows line detection
* Terminal prints changing error values

---

## ⚠️ Note

* Ensure a black line exists in Gazebo
* Tune threshold if needed


# 🛑 Obstacle Detection Module (Member 2)

## 📌 Overview
This module gives the robot a "sense of touch." It uses the TurtleBot3's 360-degree LiDAR sensor to detect obstacles in the robot's forward path and triggers an emergency stop flag if anything gets too close.

---

## 🧠 Working
* Subscribes to the LiDAR `/scan` topic.
* Slices the data array to isolate a 60-degree cone directly in front of the robot.
* Checks if any object within that cone is closer than the `safe_distance` (0.5 meters).
* Publishes a `True` or `False` boolean flag to the rest of the system.

---

## 📡 Topics
| Topic                | Type                 | Direction |
| -------------------- | -------------------- | --------- |
| `/scan`              | sensor_msgs/LaserScan| Input     |
| `/obstacle_detected` | std_msgs/Bool        | Output    |

---

## 🚀 Run

### 1. Launch simulation
```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py


2. Run node
Bash

source /opt/ros/humble/setup.bash
python3 obstacle_detector.py

🎯 Output

    Terminal prints Path clear. when safe.

    Terminal prints a yellow OBSTACLE DETECTED within 0.5m! warning when an object blocks the front path.


### **Step 2: Push to GitHub**
Now that your `obstacle_detector.py` is saved in the folder and your `README.md` is updated, go to your terminal. 

Make sure you are inside your project folder:
```bash
cd ~/line-following-robot
