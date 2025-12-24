#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import tensorflow as tf
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import random
from ament_index_python.packages import get_package_share_directory

class FingerDetector(Node):

    def __init__(self):
        super().__init__('finger_detector')

        # ROS publisher
        self.publisher = self.create_publisher(Int32, '/finger_count', 10)

        # Config
        self.IMG_SIZE = (128, 128)
        self.DATA_DIR = "/home/bhanu/Downloads/archive/training_images"

        # File list
        self.files = [
            os.path.join(self.DATA_DIR, f)
            for f in os.listdir(self.DATA_DIR)
            if f.endswith(".png")
        ]
        if not self.files:
            raise RuntimeError("No images found in dataset directory")
        random.shuffle(self.files)

        # Load model
        pkg_path = get_package_share_directory('robot_arm')
        model_path = os.path.join(pkg_path, 'finger_count_detector')
        self.get_logger().info(f"Loading model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)

        # Matplotlib setup
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(tf.zeros((*self.IMG_SIZE, 3)))
        self.ax.axis('off')

        # Timer every 2 seconds (runs in main thread)
        self.timer = self.create_timer(4.0, self.run_inference)

        self.get_logger().info("Finger detector node started.")

    def load_image(self, path):
        img = tf.io.read_file(path)
        img = tf.image.decode_png(img, channels=3)
        img = tf.image.resize(img, self.IMG_SIZE)
        return img / 255.0

    def run_inference(self):
        # Pick a random image
        img_path = random.choice(self.files)
        img = self.load_image(img_path)

        # Run inference
        pred = self.model.predict(tf.expand_dims(img, axis=0), verbose=0)
        pred_label = int(tf.argmax(pred, axis=1)[0])

        # Publish prediction
        msg = Int32()
        msg.data = pred_label
        self.publisher.publish(msg)

        # --- Force synchronous GUI update ---
        self.im.set_data(img.numpy())
        self.ax.set_title(f"Predicted Fingers: {pred_label}")
        self.fig.canvas.flush_events()   # Flush pending GUI events
        self.fig.canvas.draw()           # Draw immediately
        plt.pause(0.01)                  # Tiny pause to process events

        self.get_logger().info(f"Predicted: {pred_label}")



def main():
    rclpy.init()
    node = FingerDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
