#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Int32
import math
import time

# ------------------------
# JOINT LOGIC
# ------------------------
class JointModel:
    def __init__(self):
        self.joint_names = [
            'joint_robot_base',
            'joint_robot_link_1',
            'joint_robot_base_2',
            'joint_robot_link_2',
            'gripper_joint'
        ]

        self.home_positions = [
            0.0,
           -0.186,
            0.93,
            0.0,
            3.14
        ]

        self.joint_positions = self.home_positions.copy()

        self.start_time = time.time()
        self.frequency = 0.2
        self.current_digit = 0   # updated by subscriber

    def set_digit(self, digit: int):
        self.current_digit = digit

    def update(self):
        t = time.time() - self.start_time
        motion = 0.4 * math.sin(2 * math.pi * self.frequency * t)

        # reset first (IMPORTANT)
        self.joint_positions = self.home_positions.copy()

        if self.current_digit == 1:
            self.joint_positions[1] += motion
        elif self.current_digit == 2:
            self.joint_positions[0] += motion
        elif self.current_digit == 3:
            self.joint_positions[2] += motion
        elif self.current_digit == 4:
            self.joint_positions[3] += motion
        elif self.current_digit == 5:
            self.joint_positions[4] += motion
        # digit 0 → home pose

    def get_positions(self):
        self.update()
        return self.joint_positions

    def get_names(self):
        return self.joint_names


# ------------------------
# ROS NODE
# ------------------------
class JointStateController(Node):

    def __init__(self):
        super().__init__('joint_state_controller')

        self.model = JointModel()

        self.publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        self.subscription = self.create_subscription(
            Int32,
            '/finger_count',
            self.finger_callback,
            10
        )

        self.timer = self.create_timer(0.05, self.publish_joint_state)

        self.get_logger().info('JointStateController running (finger-driven).')

    def finger_callback(self, msg: Int32):
        digit = msg.data
        self.model.set_digit(digit)

    def publish_joint_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.model.get_names()
        msg.position = self.model.get_positions()
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = JointStateController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
