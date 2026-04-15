#!/usr/bin/env python3
"""
line_follower_launch.py

Launches:
  1. Gazebo with custom line-track world
  2. robot_state_publisher with URDF
  3. Spawns robot
  4. Starts line follower, obstacle detector, and control nodes
"""

from ament_index_python.packages import get_package_share_directory
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


# ✅ Correct package path
pkg_path = get_package_share_directory('mar_project')

# ✅ Correct file paths
urdf_file = os.path.join(pkg_path, 'urdf', 'line_follower_robot.urdf')
world_file = os.path.join(pkg_path, 'worlds', 'line_track_world.world')


def generate_launch_description():

    # Read URDF
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # ── 1. Launch Gazebo ───────────────────────────────
    gazebo = ExecuteProcess(
        cmd=[
            'gazebo', '--verbose', world_file,
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen'
    )

    # ── 2. Robot State Publisher ───────────────────────
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }],
        output='screen'
    )

    # ── 3. Spawn Robot ─────────────────────────────────
    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'line_follower_robot',
            '-topic', '/robot_description',
            '-x', '0.0',
            '-y', '-0.8',
            '-z', '0.05',
            '-Y', '0.0',
        ],
        output='screen'
    )

    # ── 4. Nodes (delayed start) ───────────────────────

    line_follower_node = TimerAction(
        period=5.0,
        actions=[Node(
            package='mar_project',   # ✅ FIXED
            executable='line_follower',
            name='line_follower',
            output='screen',
        )]
    )

    obstacle_node = TimerAction(
        period=5.0,
        actions=[Node(
            package='mar_project',   # ✅ FIXED
            executable='obstacle_detector',
            name='obstacle_detector',
            output='screen',
        )]
    )

    control_node = TimerAction(
        period=6.0,
        actions=[Node(
            package='mar_project',   # ✅ FIXED
            executable='control_node',
            name='control_node',
            output='screen',
        )]
    )

    return LaunchDescription([
        gazebo,
        rsp,
        spawn,
        line_follower_node,
        obstacle_node,
        control_node,
    ])
