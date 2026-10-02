import csv
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped 

class Datos(Node):
    def __init__(self):
        super().__init__('csv_logger')
        self.file = open('Pan-tilt.csv', 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['t', 'x', 'error'])

        self.create_subscription(PointStamped, '/aruco/center', self.cb, 10)

    def cb(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        c = msg.point.x
        e = 320 - c
        self.writer.writerow([t, c, e])

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