import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command


def generate_launch_description():
    pkg_share = get_package_share_directory('pantilt_description')
    xacro_path = os.path.join(pkg_share, 'urdf', 'pantilt.xacro')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'pantilt.rviz')
    camera_bridge_config = os.path.join(pkg_share, 'config', 'camera_bridge.yaml')

    resource_path = os.path.dirname(pkg_share)
    models_path = os.path.join(pkg_share, 'models')

    set_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=resource_path + os.pathsep + models_path
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_path]), value_type=str
    )

    world_path = os.path.join(pkg_share, 'worlds', 'pantilt_world.sdf')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': '-r ' + world_path}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ],
        output='screen'
    )
    cubo_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='cubo_bridge',
        arguments=['/cubo_aruco/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
        output='screen'
    )
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'pantilt'],
        output='screen'
    )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    pantilt_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'pantilt_controller',
            '--param-file', os.path.join(pkg_share, 'config', 'pantilt_controllers.yaml')
        ],
        output='screen'
    )

    camera_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='camera_bridge',
        parameters=[{'config_file': camera_bridge_config}],
        output='screen'
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        parameters=[{
            'qos_overrides./tf_static.publisher.durability': 'transient_local'
        }],
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_path] if os.path.exists(rviz_config_path) else []
    )



    delayed_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster],
        )
    )

    delayed_pantilt_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster,
            on_exit=[pantilt_controller],
        )
    )

    aruco_detector = Node(
        package='pantilt_description',
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

    return LaunchDescription([
        set_resource_path,
        gz_sim,
        clock_bridge,
        robot_state_publisher,
        spawn_entity,
        delayed_joint_state_broadcaster,
        delayed_pantilt_controller,
        camera_bridge,
        cubo_bridge,
        rviz,
        aruco_detector,
    ])