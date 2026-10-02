import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class PanTiltOnce(Node):
    def __init__(self):
        super().__init__('pantilt_once')
        self.declare_parameter('pan', 0.0)
        self.declare_parameter('tilt', 0.0)
        self.pub = self.create_publisher(
            Float64MultiArray, '/pantilt_controller/commands', 10)
        self.timer = self.create_timer(1.0, self.send)

    def send(self):
        pan = float(self.get_parameter('pan').value)
        tilt = float(self.get_parameter('tilt').value)
        self.pub.publish(Float64MultiArray(data=[pan, tilt]))
        self.get_logger().info(f'Comando enviado: pan={pan}, tilt={tilt}')
        self.timer.cancel()
        raise SystemExit


def main():
    rclpy.init()
    node = PanTiltOnce()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()