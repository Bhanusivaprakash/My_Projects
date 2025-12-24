import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # Find the package path
    pkg_path = FindPackageShare('robot_arm').find('robot_arm')

    # URDF file path
    urdf_path = os.path.join(pkg_path, 'urdf', 'robot_assembly.urdf')

    # RViz config path
    rviz_config_path = os.path.join(pkg_path, 'config', 'config.rviz')

    # Read URDF content into a string
    with open(urdf_path, 'r') as urdf_file:
        robot_description = urdf_file.read()

    params = {'robot_description': robot_description}

    # Launch argument to toggle GUI for joint_state_publisher
    declare_gui_arg = DeclareLaunchArgument(
        name='gui',
        default_value='True',
        description='Launch joint_state_publisher_gui if True, else joint_state_publisher'
    )

    # Non-GUI joint_state_publisher
    """joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[params],
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    # GUI joint_state_publisher
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[params],
        condition=IfCondition(LaunchConfiguration('gui'))
    )"""


    # robot_state_publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    joint_state_controller_node = Node(
        package='robot_arm',  # your package name
        executable='joint_state_controller.py',  # the python file made executable
        name='joint_state_controller',
        output='screen'
    )

    finger_detection_node = Node(
        package='robot_arm',  # your package name
        executable='finger_detector_node.py',  # the python file made executable
        name='finger_detector_node',
        output='screen'
    )


    # Return LaunchDescription
    return LaunchDescription([
        declare_gui_arg,
        robot_state_publisher,
        rviz_node,
        joint_state_controller_node,
        finger_detection_node
    ])
