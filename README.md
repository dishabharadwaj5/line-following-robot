

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

