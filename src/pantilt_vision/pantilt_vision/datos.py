import csv

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.node import Node


class Datos(Node):
    def __init__(self):
        super().__init__('csv_logger')
        self.declare_parameter('csv_path', 'Pan-tilt.csv')
        self.declare_parameter('image_width', 640)
        path = self.get_parameter('csv_path').value
        self.centro = self.get_parameter('image_width').value / 2.0

        self.file = open(path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['t', 'x', 'error'])
        self.get_logger().info(f'Guardando en {path}')

        self.create_subscription(PointStamped, '/aruco/center', self.cb, 10)

    def cb(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        c = msg.point.x
        self.writer.writerow([t, c, self.centro - c])
        self.file.flush()

    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = Datos()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()