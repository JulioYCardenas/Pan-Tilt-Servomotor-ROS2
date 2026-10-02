# Pan-Tilt con ROS2 

# Instalación

Copia y pega el siguinete comando en tu workspace de ROS:

```bash
git clone https://github.com/JulioYCardenas/Pan-Tilt-Servomotor-ROS2.git
```

Compilalo con:

```bash
colcon build
source install/setup.bash
```

# Lanzar simulación

Para iniciar la simulacion con Gazebo y RVIZ solo pega el siguiente comando:

```bash
ros2 launch pantilt_bringup sim.launch.py
```

Se abrira el simulador Gazebo,el visualizador RVIZ2 y se activaran los nodos del controlador PID para seguimiento de ArUcos y un GUI para el movimiento del cubo.

<img width="484" height="480" alt="Pan-Tilt_move" src="https://github.com/user-attachments/assets/db518def-8e07-4354-bc00-597d20cc34ac" />
