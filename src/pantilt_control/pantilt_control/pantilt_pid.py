#!/usr/bin/env python3
import csv
import rclpy                                   # librería principal de ROS2 en Python
from rclpy.node import Node                    # clase base para crear nodos
from geometry_msgs.msg import PointStamped     # mensaje: un punto (x, y, z) + encabezado con hora
from std_msgs.msg import Float64MultiArray     # mensaje: una lista de números decimales
import math


class ArucoPanPID(Node):
    def __init__(self):
        super().__init__('aruco_pan_pid')
        #!-------------------------------------------------------------------------------------------- PID
        #** "ros2 param set /aruco_pan_pid kp 0.02"

        self.declare_parameter('ancho', 640)
        self.declare_parameter('kp', 0.03)    # ganancia proporcional
        self.declare_parameter('ki', 0.0)   # ganancia integral
        self.declare_parameter('kd', 0.0)     # ganancia derivativa
        self.declare_parameter('hfov', 1.047)
        self.declare_parameter('csv_path', 'Pan-tilt.csv')

        # Variables de inicio
        self.pan = self.integral = self.prev_error = 0.0

        #!-------------------------------------------------------------------------------------------- CSV
        self.contador = 0
        path = self.get_parameter('csv_path').value
        self.file = open(path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['n', 'pan', 'error'])
        self.get_logger().info(f'Guardando en {path}')

        #!-------------------------------------------------------------------------------------------- FOV

        ancho = self.get_parameter('ancho').value
        hfov = self.get_parameter('hfov').value

        self.cx = ancho / 2
        self.fx = self.cx / math.tan(hfov / 2)

        #!-------------------------------------------------------------------------------------------- ROS

        # Publicador: envía la lista [pan, tilt] al controlador. El 10 es el tamaño de cola.
        self.pub = self.create_publisher(
            Float64MultiArray, '/pantilt_controller/commands', 10)

        # Suscripción: cada vez que llegue un mensaje a /aruco/center se ejecuta self.cb
        self.create_subscription(PointStamped, '/aruco/center', self.cb, 10)

    def cb(self, msg):
        #** Calcula el error
        error = math.atan2(self.cx - msg.point.x, self.fx)

        self.integral += error
        deriv = error - self.prev_error

        #** obtiene los parámetros actuales de las ganancias
        kp = self.get_parameter('kp').value
        ki = self.get_parameter('ki').value
        kd = self.get_parameter('kd').value

        self.pan += kp * error + ki * self.integral + kd * deriv #?-------------------------------- PID
        self.prev_error = error

        self.pub.publish(Float64MultiArray(data=[self.pan, 0.0])) #? -------------------------------- Mover Pan

        #?-------------------------------------------------------------------------------------------- CSV
        self.writer.writerow([self.contador, self.pan, self.cx - msg.point.x])
        self.file.flush()
        self.contador += 1

    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = ArucoPanPID()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()