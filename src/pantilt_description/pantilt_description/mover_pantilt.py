import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class PanTiltOnce(Node):
    def __init__(self):
        super().__init__('pantilt_once')
        self.pub = self.create_publisher(
            Float64MultiArray, '/pantilt_controller/commands', 10)
        self.timer = self.create_timer(1.0, self.send)

    def send(self):
        msg = Float64MultiArray()
        msg.data = [0.0, 0.0]
        self.pub.publish(msg)
        self.get_logger().info('Comando enviado')
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