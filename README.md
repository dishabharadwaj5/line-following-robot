# 🤖 Line Tracking Robot with Obstacle Detection and Avoidance using ROS 2

## 📋 Project Overview

Mobile robots operating in structured environments must follow predefined paths while safely handling unexpected obstacles. Basic line-following systems fail when obstacles appear, leading to collisions or interruptions. This project develops a ROS 2-based simulated robot that can accurately track a line and dynamically detect and avoid obstacles, ensuring smooth and safe autonomous navigation in a virtual environment.

**Implementation Type:** Simulation (Gazebo)

---

## 🎯 Objectives

- Design a simulated mobile robot capable of following a predefined path (line) autonomously.
- Detect static and dynamic obstacles using virtual sensors.
- Implement real-time obstacle avoidance without losing the line-following behavior.
- Integrate perception, decision-making, and motion control using ROS nodes.
- Validate the robot's navigation behavior in a Gazebo simulation environment.

---

## ✅ Outcomes

- Successful simulation of a line-following robot in a virtual environment.
- Accurate detection of obstacles placed along the robot's path.
- Smooth avoidance of obstacles and re-alignment with the guiding line.
- Demonstration of ROS-based modular architecture using publishers and subscribers.
- Improved understanding of autonomous navigation concepts in mobile robotics.

---

## 🛠️ Tools & Platforms

| Tool | Purpose |
|---|---|
| ROS 2 Humble | Robot Operating System framework |
| Gazebo Simulator | Environment and robot simulation |
| RViz | Visualization of sensor data |
| OpenCV | Line detection using camera images |
| Python 3 | Implementing ROS nodes |
| Ubuntu 22.04 LTS | Operating system |

---

## 🏗️ System Architecture

```
/camera/image_raw → [line_follower] → /line_error ──────────┐
                                                              ▼
                                                      [control_node] → /cmd_vel → Robot
                                                              ▲
/scan → [obstacle_detector] → /obstacle_detected ────────────┘
```

---

## 📦 Modules

---

## 📷 Line Following Module (Member 1)

### 📌 Overview
This module detects a line using camera input and publishes an error signal for robot control in ROS 2.

### 🧠 Working
- Subscribe to `/camera/image_raw`
- Process image using OpenCV
- Detect line (threshold + contour)
- Compute error:
```
error = center_x - line_x
```
- Publish to `/line_error`

### 📡 Topics

| Topic | Type | Direction |
|---|---|---|
| `/camera/image_raw` | sensor_msgs/Image | Input |
| `/line_error` | std_msgs/Float32 | Output |

### ⚙️ Setup
```bash
sudo apt update
sudo apt install python3-opencv ros-jazzy-cv-bridge
```

### 🚀 Run

1. Launch simulation:
```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

2. Run node:
```bash
source /opt/ros/jazzy/setup.bash
python3 line_follower.py
```

3. (Optional) Teleop:
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 run turtlebot3_teleop teleop_keyboard
```

### 🎯 Output
- OpenCV window shows line detection
- Terminal prints changing error values

### ⚠️ Note
- Ensure a black line exists in Gazebo
- Tune threshold if needed

---

## 🛑 Obstacle Detection Module (Member 2)

### 📌 Overview
This module uses the TurtleBot3's 360-degree LiDAR sensor to detect obstacles in the robot's forward path and triggers an emergency stop flag if anything gets too close.

### 🧠 Working
- Subscribes to the LiDAR `/scan` topic.
- Slices the data array to isolate a 60-degree cone directly in front of the robot (angles 0–30° and 330–360°).
- Checks if any object within that cone is closer than `safe_distance` (0.15 meters).
- Saves the obstacle distance safely before publishing.
- Publishes a `True` or `False` boolean flag to the rest of the system.

### 📡 Topics

| Topic | Type | Direction |
|---|---|---|
| `/scan` | sensor_msgs/LaserScan | Input |
| `/obstacle_detected` | std_msgs/Bool | Output |

### 🚀 Run

1. Launch simulation:
```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

2. Run node:
```bash
source /opt/ros/jazzy/setup.bash
python3 obstacle_detector.py
```

### 🎯 Output
- Terminal prints `✅ Path clear` when safe.
- Terminal prints `🚨 OBSTACLE at X.XX m` warning when an object blocks the front path.

---

## 🧠 Control & Decision Node (Member 3)

### 📌 Overview
This is the brain of the robot. It subscribes to both the line error and obstacle detection topics, makes a real-time decision, and publishes velocity commands to drive the robot safely.

### 🧠 Working
- Subscribes to `/line_error` (from Member 1's camera node).
- Subscribes to `/obstacle_detected` (from Member 2's LiDAR node).
- **Decision logic:**
  - If obstacle detected → **STOP** (linear and angular velocity = 0)
  - If path clear → **Follow line** using a P-controller:
    ```
    angular_z = -k * error     (k = 0.005)
    linear_x  = 0.2 m/s
    ```
- Publishes `TwistStamped` to `/cmd_vel` at 10 Hz.
- Sets header stamp and frame_id for ROS 2 Jazzy compatibility.

### 📡 Topics

| Topic | Type | Direction |
|---|---|---|
| `/line_error` | std_msgs/Float32 | Input |
| `/obstacle_detected` | std_msgs/Bool | Input |
| `/cmd_vel` | geometry_msgs/TwistStamped | Output |

### ⚙️ Setup
```bash
sudo apt update
sudo apt install python3-rclpy ros-jazzy-geometry-msgs
```

### 🚀 Run

1. Launch simulation:
```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

2. Run node:
```bash
source /opt/ros/jazzy/setup.bash
python3 control_node.py
```

3. Verify output:
```bash
ros2 topic echo /cmd_vel
```

### 🎯 Output
- `Following line | error: X.X` — robot actively steering to follow line
- `🚨 OBSTACLE → STOP` — robot halted due to detected obstacle
- `/cmd_vel` shows `linear.x: 0.2` and `angular.z: -k*error` when following
- `/cmd_vel` shows `linear.x: 0.0, angular.z: 0.0` when stopped

### 🧪 Test Without Simulation (Standalone)
```bash
# Simulate line error
ros2 topic pub /line_error std_msgs/msg/Float32 "data: 50.0"

# Simulate obstacle
ros2 topic pub /obstacle_detected std_msgs/msg/Bool "data: true"

# Simulate clear path
ros2 topic pub /obstacle_detected std_msgs/msg/Bool "data: false"
```

---

## 🖥️ Simulation + Integration + Testing (Member 4)

### 📌 Overview
This module handles the full system integration by launching all ROS 2 nodes together in the Gazebo simulation environment and validating the complete robot behavior through structured testing. The goal is to confirm that line following, obstacle detection, and motion control all work correctly as one unified system.

---

### ⚙️ Setup
```bash
sudo apt update
sudo apt install ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-description
echo "export TURTLEBOT3_MODEL=waffle_pi" >> ~/.bashrc
source ~/.bashrc
```

---

### 🚀 Full System Launch

Open **4 terminals** and run in this exact order:

**Terminal 1 — Gazebo Simulation:**
```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```
> Wait for Gazebo to fully open before running the next terminals.

**Terminal 2 — Obstacle Detector:**
```bash
source /opt/ros/humble/setup.bash
python3 ~/line-following-robot/obstacle_detector.py
```

**Terminal 3 — Line Follower:**
```bash
source /opt/ros/humble/setup.bash
python3 ~/line-following-robot/line_follower.py
```

**Terminal 4 — Control Node:**
```bash
source /opt/ros/humble/setup.bash
python3 ~/line-following-robot/control_node.py
```

---

### 🧪 Integration Tests (Standalone — No Gazebo Needed)

These tests verify each part of the system individually before full integration.

#### Test A — Verify /cmd_vel is publishing
```bash
ros2 topic echo /cmd_vel
```
✅ Expected: `linear.x: 0.2`, `angular.z: ~1.5` (robot steering)

#### Test B — Verify obstacle stop works
```bash
ros2 topic pub --rate 10 /obstacle_detected std_msgs/msg/Bool "data: true"
```
✅ Expected: `linear.x: 0.0`, `angular.z: 0.0` (robot stopped)

#### Test C — Verify line error correction works
```bash
ros2 topic pub --rate 10 /line_error std_msgs/msg/Float32 "data: 100.0"
```
✅ Expected: `angular.z ≈ -0.5` (= -0.005 × 100, P-controller working)

---

### ✅ Test Results

| Test | Description | Result |
|---|---|---|
| Test A | /cmd_vel publishing confirmed | ✅ PASS |
| Test B | Robot stops when obstacle detected | ✅ PASS |
| Test C | Angular correction matches line error | ✅ PASS |
| Full Integration | Robot moves, follows line and stops at obstacle in Gazebo | ✅ PASS |

---

### 🔍 System Verification

After launching all 4 terminals, run:

```bash
source /opt/ros/humble/setup.bash
ros2 node list && ros2 topic list
```

**Expected nodes:**
/control_node
/line_follower
/obstacle_detector
/gazebo
/robot_state_publisher
/turtlebot3_diff_drive

**Expected topics:**
/cmd_vel
/line_error
/obstacle_detected
/scan
/camera/image_raw

---

### 🎯 Observed Behavior in Gazebo

- ✅ Robot moves forward at `linear.x: 0.2 m/s` along the track
- ✅ Line follower computes error values (e.g. `-59`) and steers robot accordingly
- ✅ LiDAR scans 60° front cone continuously for obstacles
- ✅ Robot successfully stops when green obstacle box is within `0.15m`
- ✅ OpenCV **ROI** and **Threshold** windows confirm live camera-based line detection

---

### 🛠️ Environment

| Component | Version |
|---|---|
| ROS 2 | Humble |
| OS | Ubuntu 22.04 LTS |
| Gazebo | Classic 11 |
| TurtleBot3 Model | waffle_pi |
| Python | 3.10 |

---

## 👥 Team Members

| Member | Module |
|---|---|
| Member 1 | Line Following (Computer Vision) |
| Member 2 | LiDAR Obstacle Detection |
| Member 3 | Control & Decision Node |
| Member 4 | Simulation + Integration + Testing |
