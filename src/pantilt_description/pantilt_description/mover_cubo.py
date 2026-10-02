import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MoverCubo(Node):
    def __init__(self):
        super().__init__('mover_cubo_aruco')
        self.pub = self.create_publisher(Twist, '/cubo_aruco/cmd_vel', 10)

        self.dt = 0.05  # 20 Hz
        self.timer = self.create_timer(self.dt, self.mover)

        self.velocidad = 0.3          # m/s
        self.tiempo_por_tramo = 2.0   # s para ir de un punto al siguiente (0.6 m)
        self.tiempo_pausa = 3.0       # s de pausa en cada punto

        # Secuencia: (direccion, duracion). direccion 0 = pausa
        # Posiciones: centro -> derecha -> centro -> izquierda -> centro
        self.secuencia = [
            (0,  self.tiempo_pausa),       # pausa en centro
            (1,  self.tiempo_por_tramo),   # centro -> derecha
            (0,  self.tiempo_pausa),       # pausa en derecha
            (-1, self.tiempo_por_tramo),   # derecha -> centro
            (0,  self.tiempo_pausa),       # pausa en centro
            (-1, self.tiempo_por_tramo),   # centro -> izquierda
            (0,  self.tiempo_pausa),       # pausa en izquierda
            (1,  self.tiempo_por_tramo),   # izquierda -> centro
        ]
        self.indice = 0
        self.contador = 0.0

    def mover(self):
        direccion, duracion = self.secuencia[self.indice]

        msg = Twist()
        msg.linear.y = self.velocidad * direccion  # 0 durante las pausas
        self.pub.publish(msg)

        self.contador += self.dt
        if self.contador >= duracion:
            self.contador = 0.0
            self.indice = (self.indice + 1) % len(self.secuencia)

    def detener(self):
        self.pub.publish(Twist())  # velocidad cero al cerrar

def main():
    rclpy.init()
    node = MoverCubo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.detener()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()