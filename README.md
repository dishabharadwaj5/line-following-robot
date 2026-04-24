
# 🤖 Line-Following Robot with Obstacle Avoidance

A ROS 2 autonomous robot that follows a black line using computer vision and avoids obstacles using LiDAR — built with a full PID controller and a geometric 4-stage evasion state machine.

---

## 📁 Project Structure

```

mar_project/
├── launch/                  # ROS 2 launch files
├── mar_project/             # Main Python package
│   ├── **init**.py
│   ├── control_node.py      # PID controller + obstacle evasion state machine
│   ├── line_follower.py     # Camera-based line detection (HSV masking)
│   └── obstacle_detector.py # LiDAR-based obstacle detection with hysteresis
├── resource/
├── test/
├── urdf/                    # Robot description files
├── worlds/                  # Gazebo simulation worlds
├── package.xml
├── setup.cfg
└── setup.py

```

---

## ⚙️ How It Works

The robot runs three independent ROS 2 nodes that communicate via topics:

### 1. `line_follower.py` — Vision Node

- Subscribes to `/camera/image_raw`
- Converts the camera frame to HSV and applies a black-line mask
- Uses the bottom 60% of the frame as the Region of Interest (ROI)
- Computes the centroid of the largest contour and calculates lateral error

**Publishes:**
- `/line_error` (`Float32`) — signed pixel offset from center  
- `/line_lost` (`Bool`) — flag when no line is detected  

---

### 2. `obstacle_detector.py` — LiDAR Node

- Subscribes to `/scan` (`LaserScan`)
- Checks a 60° cone directly in front of the robot
- Triggers if any reading is closer than **0.40 m**
- Uses hysteresis (3 consecutive clear readings)

**Publishes:**
- `/obstacle_detected` (`Bool`)

---

### 3. `control_node.py` — Brain Node

- Subscribes to:
  - `/line_error`
  - `/line_lost`
  - `/obstacle_detected`
- Publishes velocity commands to `/cmd_vel` at **10 Hz**

---

## 🔁 Normal Line Following — PID Controller

```

angular_z = -(Kp × error + Ki × Σerror + Kd × Δerror)

````

Speed is dynamically reduced based on line error magnitude.

| Parameter   | Value   |
|------------|--------|
| Base Speed | 0.20 m/s |
| Min Speed  | 0.05 m/s |
| Kp         | 0.008 |
| Ki         | 0.001 |
| Kd         | 0.004 |

---

## 🚧 Obstacle Evasion — 4-Stage State Machine

| Stage | Action                                   | Duration |
|------|------------------------------------------|---------|
| 1    | Pivot Right (`ω = -0.8`)                 | 0.8 s   |
| 2    | Drive Forward                            | 1.5 s   |
| 3    | Pivot Left (`ω = +0.8`)                  | 0.8 s   |
| 4    | Sweep forward with left curl             | Until line is found |

Once the line is reacquired, PID control resumes automatically.

---

## 🚀 Getting Started

### Prerequisites

- ROS 2 (Humble or later)
- Python 3
- OpenCV (`cv2`)
- `cv_bridge`
- Robot with camera + LiDAR (or Gazebo simulation)

---

### 🔨 Build

```bash
cd ~/your_ros2_ws
colcon build --packages-select mar_project
source install/setup.bash
````

---

### ▶️ Run Nodes

```bash
ros2 run mar_project control_node
ros2 run mar_project line_follower
ros2 run mar_project obstacle_detector
```

---

### 🚀 Launch (Recommended)

```bash
ros2 launch mar_project <your_launch_file>.launch.py
```

---

## 📡 ROS 2 Topic Summary

| Topic                | Type                    | Publisher         | Subscribers       |
| -------------------- | ----------------------- | ----------------- | ----------------- |
| `/camera/image_raw`  | `sensor_msgs/Image`     | Camera Driver     | line_follower     |
| `/scan`              | `sensor_msgs/LaserScan` | LiDAR Driver      | obstacle_detector |
| `/line_error`        | `std_msgs/Float32`      | line_follower     | control_node      |
| `/line_lost`         | `std_msgs/Bool`         | line_follower     | control_node      |
| `/obstacle_detected` | `std_msgs/Bool`         | obstacle_detector | control_node      |
| `/cmd_vel`           | `geometry_msgs/Twist`   | control_node      | Robot base / sim  |

---

## 🛠️ Tuning Guide

### 🎥 Line Detection (`line_follower.py`)

* Adjust HSV thresholds (`lower_black`, `upper_black`)
* Change ROI crop ratio (`0.4`)
* Increase contour area threshold (`300`) to reduce noise

---

### 📡 Obstacle Detection (`obstacle_detector.py`)

* `SAFE_DISTANCE` → Increase if robot reacts too late
* `CONE_HALF_ANGLE` → Widen detection range
* `CLEAR_HYSTERESIS` → Prevent flickering detection

---

### ⚙️ Control (`control_node.py`)

* Tune `Kp`, `Ki`, `Kd` for your robot
* Adjust evasion stage durations
* Modify `SEARCH_SPEED` for line recovery behavior

---

## 📷 Debug Visualisation

`line_follower.py` opens two OpenCV windows:

* **ROI Window**

  * Shows cropped image
  * Red dot = detected centroid
  * Green line = image center

* **Mask Window**

  * Binary image after thresholding + cleanup

---

## 📝 License

This project was developed as part of a **Mobile and Autonomous Robots (MAR)** course.

---


