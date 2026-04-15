# 🤖 Line Tracking Robot with Obstacle Detection — ROS 2 Jazzy

## 📋 Project Overview

A ROS 2-based simulated differential-drive robot that:
- Follows a black oval line track using a downward-facing camera + OpenCV
- Detects obstacles using a 360° LiDAR and stops safely
- Re-finds the line after obstacle clearance using a search spin
- Runs in a custom Gazebo world (white floor + black line + red obstacle boxes)

**Implementation Type:** Simulation (Gazebo Classic + ROS 2 Jazzy)

---

## 📁 File Structure

```
line-following-robot/
├── line_follower.py          # Camera → line error (HSV-based, robust)
├── obstacle_detector.py      # LiDAR → obstacle flag (with hysteresis)
├── control_node.py           # PD controller + lost-line recovery
├── line_follower_robot.urdf  # Custom robot model (orange chassis, camera, LiDAR)
├── line_track_world.world    # Custom Gazebo world with oval black line track
├── line_follower_launch.py   # Launch everything in one command
└── README.md
```

---

## 🏗️ System Architecture

```
/camera/image_raw  →  [line_follower]      →  /line_error        ──┐
                                            →  /line_lost         ──┤
                                                                     ▼
                                                             [control_node]  →  /cmd_vel → Robot
                                                                     ▲
/scan              →  [obstacle_detector]  →  /obstacle_detected ──┘
```

---

## 🤖 Robot Model (`line_follower_robot.urdf`)

The robot looks like a real line follower:

| Part | Description |
|---|---|
| Chassis | Orange rectangular box (26×18×5 cm) |
| Drive wheels | Two black rubber wheels with silver hub caps |
| Caster | Front ball caster (frictionless) |
| Camera | Dark grey box with blue lens, mounted on front bracket, angled 30° down |
| LiDAR | Red cylinder on top of electronics deck |
| Electronics deck | Dark grey raised box on chassis |

Gazebo plugins included: `diff_drive`, `camera`, `ray_sensor` (LiDAR)

---

## 🌍 World (`line_track_world.world`)

- White ground plane for maximum camera contrast
- Black oval loop (~3 m × 2 m) made of flat 6 cm-wide boxes
- 3 red obstacle boxes placed on the track
- Bright ambient lighting for reliable line detection
- Physics tuned for real-time factor ≈ 1.0

---

## 📦 Modules

### 📷 Line Follower (`line_follower.py`)

**Fixed from original:**
- Uses HSV colour space instead of greyscale threshold — more robust to lighting
- ROI is bottom 40% of frame (was 50%) — closer to ground, cleaner line view
- Ignores contours < 300px² to filter noise
- Publishes `/line_lost` (Bool) in addition to `/line_error`
- Remembers last error when line is momentarily lost

**Topics:**

| Topic | Type | Direction |
|---|---|---|
| `/camera/image_raw` | `sensor_msgs/Image` | Input |
| `/line_error` | `std_msgs/Float32` | Output |
| `/line_lost` | `std_msgs/Bool` | Output |

---

### 🛑 Obstacle Detector (`obstacle_detector.py`)

**Fixed from original:**
- `safe_distance` increased from **0.15 m → 0.40 m** (was dangerously close)
- Hysteresis: requires 3 consecutive clear readings before publishing "safe" (prevents flickering)
- Properly handles `inf` and `nan` LiDAR values

**Topics:**

| Topic | Type | Direction |
|---|---|---|
| `/scan` | `sensor_msgs/LaserScan` | Input |
| `/obstacle_detected` | `std_msgs/Bool` | Output |

---

### 🧠 Control Node (`control_node.py`)

**Fixed from original:**
- Uses **PD controller** (added derivative term) — smoother steering, less oscillation
- Added `/line_lost` subscriber — robot spins to search for lost line instead of driving blind
- **Corrected message type:** uses `geometry_msgs/Twist` (not `TwistStamped`)
- Priority order: obstacle stop → line-lost search → normal PD following

**Tuning parameters:**

| Parameter | Value | Notes |
|---|---|---|
| `LINEAR_SPEED` | 0.18 m/s | Slightly slower = more stable |
| `KP` | 0.004 | Proportional gain |
| `KD` | 0.002 | Derivative gain (new) |
| `SEARCH_SPEED` | 0.3 rad/s | Spin speed when line is lost |

**Topics:**

| Topic | Type | Direction |
|---|---|---|
| `/line_error` | `std_msgs/Float32` | Input |
| `/line_lost` | `std_msgs/Bool` | Input |
| `/obstacle_detected` | `std_msgs/Bool` | Input |
| `/cmd_vel` | `geometry_msgs/Twist` | Output |

---

## 🚀 Running the Full System

### Option A — Launch file (recommended)
```bash
source /opt/ros/jazzy/setup.bash
cd ~/line-following-robot
ros2 launch line_follower_launch.py
```

### Option B — 4 terminals manually

**Terminal 1 — Gazebo:**
```bash
source /opt/ros/jazzy/setup.bash
gazebo --verbose line_track_world.world \
  -s libgazebo_ros_init.so \
  -s libgazebo_ros_factory.so
```

**Terminal 2 — Spawn robot:**
```bash
source /opt/ros/jazzy/setup.bash
ros2 run gazebo_ros spawn_entity.py \
  -entity line_follower_robot \
  -file ~/line-following-robot/line_follower_robot.urdf \
  -x 0.0 -y -0.8 -z 0.05 -Y 0.0
```

**Terminal 3 — Sensor nodes:**
```bash
source /opt/ros/jazzy/setup.bash
cd ~/line-following-robot
python3 obstacle_detector.py &
python3 line_follower.py
```

**Terminal 4 — Control:**
```bash
source /opt/ros/jazzy/setup.bash
cd ~/line-following-robot
python3 control_node.py
```

---

## 🧪 Testing Without Simulation

```bash
# Simulate line found with error
ros2 topic pub /line_error std_msgs/msg/Float32 "data: 50.0"
ros2 topic pub /line_lost  std_msgs/msg/Bool    "data: false"

# Simulate line lost
ros2 topic pub /line_lost  std_msgs/msg/Bool    "data: true"

# Simulate obstacle
ros2 topic pub /obstacle_detected std_msgs/msg/Bool "data: true"

# Clear obstacle
ros2 topic pub /obstacle_detected std_msgs/msg/Bool "data: false"

# Verify cmd_vel output
ros2 topic echo /cmd_vel
```

---

## ⚙️ Dependencies

```bash
sudo apt update
sudo apt install \
  python3-opencv \
  ros-jazzy-cv-bridge \
  ros-jazzy-gazebo-ros \
  ros-jazzy-gazebo-ros-pkgs \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-geometry-msgs
```

---

## 👥 Team Members

| Member | Module |
|---|---|
| Member 1 | Line Following (Computer Vision) |
| Member 2 | LiDAR Obstacle Detection |
| Member 3 | Control & Decision Node |
| Member 4 | URDF Robot Model + Custom World + Integration |

---

## 🐛 Known Issues & Tips

- **Camera sees no line?** Check that the ground is white (`Gazebo/White` material) and lighting is bright. Adjust HSV threshold in `line_follower.py` if needed.
- **Robot doesn't move?** Check `/cmd_vel` with `ros2 topic echo /cmd_vel`. If empty, check that line_follower and obstacle_detector are running first.
- **Low FPS in Gazebo?** Reduce camera resolution to 160×120 in the URDF, or close other applications.
- **Robot overshoots corners?** Reduce `LINEAR_SPEED` to 0.12 or increase `KD` to 0.004.
