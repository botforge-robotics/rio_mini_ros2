import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Declare launch argument for micro-ROS agent port
    agent_port_arg = DeclareLaunchArgument(
        'agent_port',
        default_value='8888',
        description='Port for micro-ROS agent'
    )

    webrtc_node = Node(
        package='rio_mini',
        executable='webrtc_node',
        name='webrtc_node',
        parameters=[
            {'port': 8080, 'host': '0.0.0.0'}
        ],
        output='screen'
    )

    rosbridge_node = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        name='rosbridge_websocket',
        parameters=[
            {'send_action_goals_in_new_thread': True},
            {'call_services_in_new_thread': True},
        ],
        output='screen'
    )
    rosapi_node = Node(
        package='rosapi',
        executable='rosapi_node',
        name='rosapi',
        output='screen'
    )
    # Micro-ROS Agent
    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        arguments=['udp4', '--port', LaunchConfiguration('agent_port')],
        output='screen'
    )

    # Ollama Node
    ollama_node = Node(
        package='rio_mini',
        executable='ollama_node',
        name='ollama_node',
        parameters=[
            os.path.join(get_package_share_directory(
                'rio_mini'), 'config', 'llm_config.yaml'),
            os.path.join(get_package_share_directory(
                'rio_mini'), 'config', 'robot_params.yaml')
        ],
        output='screen'
    )

    # Environment Node
    environment_node = Node(
        package='rio_mini',
        executable='environment_node',
        name='environment_node',
        parameters=[os.path.join(get_package_share_directory(
            'rio_mini'), 'config', 'sensor_thresholds.yaml')],
        output='screen'
    )

    return LaunchDescription([
        agent_port_arg,
        webrtc_node,
        rosbridge_node,
        rosapi_node,
        micro_ros_agent,
        ollama_node,
        environment_node
    ])
