import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, SetEnvironmentVariable,
                            RegisterEventHandler)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_share = get_package_share_directory('pantilt_description')
    gz_share = get_package_share_directory('pantilt_gazebo')

    xacro_path = os.path.join(desc_share, 'urdf', 'pantilt.xacro')
    rviz_config_path = os.path.join(desc_share, 'rviz', 'pantilt.rviz')

    controllers_yaml = os.path.join(gz_share, 'config', 'pantilt_controllers.yaml')
    camera_bridge_config = os.path.join(gz_share, 'config', 'camera_bridge.yaml')
    world_path = os.path.join(gz_share, 'worlds', 'pantilt_world.sdf')

    set_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=(os.path.dirname(desc_share) + os.pathsep +
               os.path.join(gz_share, 'models'))
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_path,
                 ' controllers_yaml:=', controllers_yaml]),
        value_type=str
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r ' + world_path}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description},
                    {'use_sim_time': True}],
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
        arguments=['pantilt_controller', '--param-file', controllers_yaml],
        output='screen'
    )

    cubo_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='cubo_bridge',
        arguments=['/cubo_aruco/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
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
    ])