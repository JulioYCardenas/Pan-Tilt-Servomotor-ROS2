import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    gz_share = get_package_share_directory('pantilt_gazebo')

    args = [
        DeclareLaunchArgument('kp', default_value='0.03',
                              description='Ganancia proporcional del PID'),
        DeclareLaunchArgument('csv_path', default_value='Pan-tilt.csv',
                              description='Archivo CSV donde el PID guarda sus datos'),
        DeclareLaunchArgument('mover_cubo', default_value='false',
                              description='Lanzar el nodo que mueve el cubo'),
    ]

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_share, 'launch', 'gazebo.launch.py')))

    aruco_detector = Node(
        package='pantilt_vision',
        executable='camara',
        name='aruco_detector',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'image_topic': '/pantilt/camera/image_raw',
            'show_window': False,
            'publish_annotated': True,
            'detect_scale': 0.5,
        }],
    )

    pid = Node(
        package='pantilt_control',
        executable='pantilt_pid',
        name='aruco_pan_pid',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'kp': ParameterValue(LaunchConfiguration('kp'), value_type=float),
            'csv_path': LaunchConfiguration('csv_path'),
        }],
    )

    cubo = Node(
        package='pantilt_gazebo',
        executable='mover_cubo',
        name='mover_cubo',
        output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('mover_cubo')),
    )

    # Esperar a que Gazebo, robot y controladores esten listos
    nodos = TimerAction(period=8.0, actions=[aruco_detector, pid, cubo])

    return LaunchDescription(args + [gazebo, nodos])