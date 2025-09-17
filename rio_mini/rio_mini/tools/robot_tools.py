#!/usr/bin/env python3

"""
Robot Tools for Desktop Companion Robot

Direct implementation of robot control tools for Ollama's native tool calling.
"""

import logging
import time
from typing import Dict, Any

# ROS2 imports
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
# No callback groups needed - single threaded

# ROS2 message types
from std_msgs.msg import String, Bool, ColorRGBA, Int32, Float32, Header
from geometry_msgs.msg import Twist, TwistStamped

# RIO interfaces
from rio_interfaces.action import TTS, Auth
from rio_interfaces.srv import Expression, GetExpression, Camera

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s Robot_Tools %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class RobotController:
    """Robot controller with ROS2 integration"""

    def __init__(self):
        self.logger = logger

        # Initialize ROS2
        if not rclpy.ok():
            rclpy.init()

        self.node = Node('robot_controller')

        # Declare robot movement parameters
        self._declare_parameters()

        # Initialize ROS2 interfaces
        self._init_ros2_interfaces()

        self.logger.info("RobotController initialized successfully")

    def _declare_parameters(self):
        """Declare robot movement parameters"""
        # Head movement parameters
        self.node.declare_parameter('robot_movement.head.top_position', 150)
        self.node.declare_parameter('robot_movement.head.bottom_position', 180)
        self.node.declare_parameter('robot_movement.head.front_position', 165)
        self.node.declare_parameter(
            'robot_movement.head.gesture_duration', 0.8)
        self.node.declare_parameter('robot_movement.head.gesture_speed', 0.5)

        # Movement parameters
        self.node.declare_parameter(
            'robot_movement.movement.max_linear_speed', 0.3)
        self.node.declare_parameter(
            'robot_movement.movement.max_angular_speed', 2.0)
        self.node.declare_parameter(
            'robot_movement.movement.default_duration', 0.5)

    def _init_ros2_interfaces(self):
        """Initialize ROS2 publishers, subscribers, and clients"""
        # Publishers
        self.twist_pub = self.node.create_publisher(
            TwistStamped, '/cmd_vel', 10)

        self.led_pub = self.node.create_publisher(
            ColorRGBA, '/led_color', 10)

        self.torch_pub = self.node.create_publisher(
            Bool, '/torch', 10)

        self.head_pitch_pub = self.node.create_publisher(
            Float32, '/head_pitch', 10)

        # Service clients
        self.expression_client = self.node.create_client(
            Expression, '/set_expression')

        self.get_expression_client = self.node.create_client(
            GetExpression, '/get_expression')

        self.camera_client = self.node.create_client(
            Camera, '/enable_camera')

        # Action clients
        self.tts_client = ActionClient(
            self.node, TTS, '/tts')

        self.auth_client = ActionClient(
            self.node, Auth, '/auth')

        self.logger.info("ROS2 interfaces initialized")

    def get_current_state(self) -> Dict[str, Any]:
        """Get current robot state"""
        return {
            "status": "success",
            "message": "Robot is ready",
            "robot_state": {
                "movement": "ready",
                "expression": "neutral",
                "torch": "off",
                "camera": "enabled"
            }
        }

    def set_expression(self, expression: str) -> Dict[str, Any]:
        """Set robot facial expression to display emotions."""
        try:
            logger.info(f"Setting expression to: {expression}")

            if not self.expression_client.wait_for_service(timeout_sec=5.0):
                raise Exception("Expression service not available")

            request = Expression.Request()
            request.expression = expression

            future = self.expression_client.call_async(request)
            rclpy.spin_until_future_complete(
                self.node, future, timeout_sec=5.0)

            if not future.done():
                raise Exception("Expression service call timeout")

            response = future.result()
            if not response.success:
                raise Exception("Expression service failed")

            return {
                "status": "success",
                "message": f"Expression set to: {expression}",
                "expression": expression
            }

        except Exception as e:
            error_msg = f"Error in set_expression: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def speak_text(self, text: str) -> Dict[str, Any]:
        """Make the robot speak text."""
        try:
            logger.info(f"Speaking: {text[:50]}...")

            if not self.tts_client.wait_for_server(timeout_sec=5.0):
                raise Exception("TTS action server not available")

            goal_msg = TTS.Goal()
            goal_msg.text = text

            future = self.tts_client.send_goal_async(goal_msg)
            rclpy.spin_until_future_complete(
                self.node, future, timeout_sec=5.0)

            if not future.done():
                raise Exception("TTS action call timeout")

            goal_handle = future.result()
            if not goal_handle.accepted:
                raise Exception("TTS goal rejected")

            return {
                "status": "success",
                "message": f"Successfully spoke: {text}",
                "spoken": text
            }

        except Exception as e:
            error_msg = f"Error in speak_text: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def move_robot(self, linear_x: float = 0.0, linear_y: float = 0.0, angular_z: float = 0.0) -> Dict[str, Any]:
        """Move the robot with specified linear and angular velocities."""
        try:
            # Convert string arguments to float if needed
            linear_x = float(linear_x) if isinstance(
                linear_x, str) else linear_x
            linear_y = float(linear_y) if isinstance(
                linear_y, str) else linear_y
            angular_z = float(angular_z) if isinstance(
                angular_z, str) else angular_z

            logger.info(
                f"Moving robot: linear_x={linear_x}, linear_y={linear_y}, angular_z={angular_z}")

            # Create TwistStamped message
            from geometry_msgs.msg import TwistStamped
            from std_msgs.msg import Header
            twist_stamped = TwistStamped()
            twist_stamped.header = Header()
            twist_stamped.header.stamp = self.node.get_clock().now().to_msg()
            twist_stamped.header.frame_id = 'base_link'
            twist_stamped.twist.linear.x = float(linear_x)
            twist_stamped.twist.linear.y = float(linear_y)
            twist_stamped.twist.linear.z = 0.0
            twist_stamped.twist.angular.x = 0.0
            twist_stamped.twist.angular.y = 0.0
            twist_stamped.twist.angular.z = float(angular_z)

            self.twist_pub.publish(twist_stamped)
            time.sleep(0.1)  # Brief pause for movement

            return {
                "status": "success",
                "message": f"Robot moved: linear_x={linear_x}, linear_y={linear_y}, angular_z={angular_z}",
                "movement": {"linear_x": linear_x, "linear_y": linear_y, "angular_z": angular_z}
            }

        except Exception as e:
            error_msg = f"Error in move_robot: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def move_with_duration(self, linear_x: float = 0.0, angular_z: float = 0.0, duration: float = 0.5) -> Dict[str, Any]:
        """Move the robot with specified velocities for a specific duration, then stop."""
        try:
            # Convert string arguments to float if needed
            linear_x = float(linear_x) if isinstance(
                linear_x, str) else linear_x
            angular_z = float(angular_z) if isinstance(
                angular_z, str) else angular_z
            duration = float(duration) if isinstance(
                duration, str) else duration

            logger.info(
                f"Moving robot with duration: linear_x={linear_x}, angular_z={angular_z}, duration={duration}s")

            # Apply safety limits
            # Clamp between 0.1 and 2.0 seconds
            duration = max(0.1, min(2.0, duration))
            linear_x = max(-0.45, min(0.45, linear_x))  # Clamp linear speed
            angular_z = max(-2.0, min(2.0, angular_z))  # Clamp angular speed

            # Create TwistStamped message
            from geometry_msgs.msg import TwistStamped
            from std_msgs.msg import Header
            twist_stamped = TwistStamped()
            twist_stamped.header = Header()
            twist_stamped.header.stamp = self.node.get_clock().now().to_msg()
            twist_stamped.header.frame_id = 'base_link'
            twist_stamped.twist.linear.x = float(linear_x)
            twist_stamped.twist.linear.y = 0.0  # Differential drive: ignore linear_y
            twist_stamped.twist.linear.z = 0.0  # No vertical movement
            twist_stamped.twist.angular.x = 0.0  # No roll
            twist_stamped.twist.angular.y = 0.0  # No pitch
            twist_stamped.twist.angular.z = float(angular_z)

            # Publish movement command
            self.twist_pub.publish(twist_stamped)

            # Wait for specified duration
            time.sleep(duration)

            # Stop the robot
            stop_twist_stamped = TwistStamped()
            stop_twist_stamped.header = Header()
            stop_twist_stamped.header.stamp = self.node.get_clock().now().to_msg()
            stop_twist_stamped.header.frame_id = 'base_link'
            stop_twist_stamped.twist.linear.x = 0.0
            stop_twist_stamped.twist.linear.y = 0.0
            stop_twist_stamped.twist.linear.z = 0.0
            stop_twist_stamped.twist.angular.x = 0.0
            stop_twist_stamped.twist.angular.y = 0.0
            stop_twist_stamped.twist.angular.z = 0.0
            self.twist_pub.publish(stop_twist_stamped)

            # Brief pause to ensure stop command is processed
            time.sleep(0.1)

            return {
                "status": "success",
                "message": f"Robot moved for {duration}s: linear_x={linear_x}, angular_z={angular_z}",
                "movement": {"linear_x": linear_x, "angular_z": angular_z, "duration": duration}
            }

        except Exception as e:
            error_msg = f"Error in move_with_duration: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def set_led_color(self, color: str) -> Dict[str, Any]:
        """Set the color of the robot's LED lights."""
        try:
            logger.info(f"Setting LED color to: {color}")

            color_map = {
                'red': (1.0, 0.0, 0.0, 1.0),
                'green': (0.0, 1.0, 0.0, 1.0),
                'blue': (0.0, 0.0, 1.0, 1.0),
                'yellow': (1.0, 1.0, 0.0, 1.0),
                'purple': (1.0, 0.0, 1.0, 1.0),
                'cyan': (0.0, 1.0, 1.0, 1.0),
                'white': (1.0, 1.0, 1.0, 1.0),
                'off': (0.0, 0.0, 0.0, 1.0)
            }

            if color.lower() not in color_map:
                raise Exception(f"Unknown color: {color}")

            rgba = color_map[color.lower()]
            led_msg = ColorRGBA()
            led_msg.r = rgba[0]
            led_msg.g = rgba[1]
            led_msg.b = rgba[2]
            led_msg.a = rgba[3]

            self.led_pub.publish(led_msg)

            return {
                "status": "success",
                "message": f"LED color set to: {color}",
                "color": color
            }

        except Exception as e:
            error_msg = f"Error in set_led_color: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def control_head_pitch(self, angle: int) -> Dict[str, Any]:
        """Control the pitch angle of the robot's head with safety limits."""
        try:
            # Convert string input to int if needed
            if isinstance(angle, str):
                angle = int(float(angle))
            else:
                angle = int(angle)

            # Get head movement limits from parameters
            top_position = self.node.get_parameter(
                'robot_movement.head.top_position').value
            bottom_position = self.node.get_parameter(
                'robot_movement.head.bottom_position').value

            # Enforce head movement limits
            if angle < top_position:
                angle = top_position
                logger.warning(
                    f"Head angle {angle} below minimum {top_position}, clamping to {top_position}")
            elif angle > bottom_position:
                angle = bottom_position
                logger.warning(
                    f"Head angle {angle} above maximum {bottom_position}, clamping to {bottom_position}")

            logger.info(
                f"Setting head pitch to: {angle} degrees (limits: {top_position}-{bottom_position})")

            pitch_msg = Float32()
            pitch_msg.data = float(angle)
            self.head_pitch_pub.publish(pitch_msg)

            return {
                "status": "success",
                "message": f"Head pitch set to: {angle} degrees (limits: {top_position}-{bottom_position})",
                "angle": angle,
                "limits": f"{top_position}-{bottom_position}"
            }

        except Exception as e:
            error_msg = f"Error in control_head_pitch: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def set_torch(self, on: bool) -> Dict[str, Any]:
        """Set the robot's torch (flashlight) on or off."""
        try:
            # Ensure boolean conversion
            torch_state = bool(on)
            logger.info(
                f"Setting torch: {torch_state} (input was: {on}, type: {type(on)})")

            torch_msg = Bool()
            torch_msg.data = torch_state
            self.torch_pub.publish(torch_msg)

            # Brief pause to ensure message is sent
            time.sleep(0.1)

            return {
                "status": "success",
                "message": f"Torch {'enabled' if torch_state else 'disabled'}",
                "torch_on": torch_state
            }

        except Exception as e:
            error_msg = f"Error in set_torch: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def enable_camera(self, enable: bool) -> Dict[str, Any]:
        """Enable or disable the robot's camera."""
        try:
            logger.info(f"Setting camera: {enable}")

            if not self.camera_client.wait_for_service(timeout_sec=5.0):
                raise Exception("Camera service not available")

            request = Camera.Request()
            request.enable = bool(enable)

            future = self.camera_client.call_async(request)
            rclpy.spin_until_future_complete(
                self.node, future, timeout_sec=5.0)

            if not future.done():
                raise Exception("Camera service call timeout")

            response = future.result()
            if not response.success:
                raise Exception(f"Camera service failed: {response.message}")

            return {
                "status": "success",
                "message": f"Camera {'enabled' if enable else 'disabled'}",
                "camera_enabled": enable
            }

        except Exception as e:
            error_msg = f"Error in enable_camera: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def biometric_authentication(self, message: str = "Please authenticate to continue") -> Dict[str, Any]:
        """Perform biometric authentication using the robot's sensors."""
        try:
            logger.info(
                f"Starting biometric authentication with message: {message}")

            if not self.auth_client.wait_for_server(timeout_sec=5.0):
                raise Exception("Auth action server not available")

            # Create goal with message parameter as per Auth.action definition
            goal_msg = Auth.Goal()
            goal_msg.message = message

            future = self.auth_client.send_goal_async(goal_msg)
            rclpy.spin_until_future_complete(
                self.node, future, timeout_sec=10.0)

            if not future.done():
                raise Exception("Auth action call timeout")

            goal_handle = future.result()
            if not goal_handle.accepted:
                raise Exception("Auth goal rejected")

            # Get the result
            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(
                self.node, result_future, timeout_sec=10.0)

            if not result_future.done():
                raise Exception("Auth result timeout")

            result = result_future.result().result

            # Handle result based on Auth.action definition: bool success, string error_message
            if result.success:
                return {
                    "status": "success",
                    "message": "Biometric authentication successful",
                    "authenticated": True,
                    "auth_message": result.error_message if hasattr(result, 'error_message') else "Authentication completed"
                }
            else:
                error_msg = result.error_message if hasattr(
                    result, 'error_message') and result.error_message else "Authentication failed"
                return {
                    "status": "error",
                    "message": f"Biometric authentication failed: {error_msg}",
                    "authenticated": False,
                    "auth_message": error_msg
                }

        except Exception as e:
            error_msg = f"Error in biometric_authentication: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg, "authenticated": False}

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'node'):
            self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


# Global robot controller instance
_robot_controller = None


def get_robot() -> RobotController:
    """Lazy-initialize the global RobotController instance"""
    global _robot_controller
    if _robot_controller is None:
        try:
            _robot_controller = RobotController()
            logger.info("RobotController initialized successfully")
        except Exception as e:
            logger.error(
                f"FATAL - Error initializing robot: {e}", exc_info=True)
            raise SystemExit(f"Robot controller failed to initialize ({e})")
    return _robot_controller


# Tool definitions for Ollama
def get_robot_tools():
    """Get list of robot tools formatted for Ollama's native tool calling."""
    return [
        {
            'type': 'function',
            'function': {
                'name': 'set_expression',
                'description': 'Set robot facial expression',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'expression': {
                            'type': 'string',
                            'description': 'Expression: happy, sad, neutral, surprised, thinking',
                        },
                    },
                    'required': ['expression'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'speak_text',
                'description': 'Make the robot speak text',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'text': {
                            'type': 'string',
                            'description': 'The text for the robot to speak',
                        },
                    },
                    'required': ['text'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'move_with_duration',
                'description': 'Move robot safely with auto-stop',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'linear_x': {'type': 'number', 'description': 'Forward speed (-0.45 to 0.45)'},
                        'angular_z': {'type': 'number', 'description': 'Turn speed (-2.0 to 2.0)'},
                        'duration': {'type': 'number', 'description': 'Move time (0.1 to 2.0)'},
                    },
                    'required': [],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'set_led_color',
                'description': 'Set LED color',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'color': {'type': 'string', 'description': 'Color: red, green, blue, yellow, purple, cyan, white, off'},
                    },
                    'required': ['color'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'control_head_pitch',
                'description': 'Control head pitch angle (150-180 degrees: 150=up, 165=front, 180=down)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'angle': {'type': 'integer', 'description': 'Head pitch angle in degrees (150-180: 150=up, 165=front, 180=down)'},
                    },
                    'required': ['angle'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'set_torch',
                'description': 'Set torch on/off',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'on': {'type': 'boolean', 'description': 'Turn torch on (true) or off (false)'},
                    },
                    'required': ['on'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'enable_camera',
                'description': 'Enable/disable camera',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'enable': {'type': 'boolean', 'description': 'Enable (true) or disable (false) camera'},
                    },
                    'required': ['enable'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'biometric_authentication',
                'description': 'Perform biometric authentication',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'description': 'Auth message'},
                    },
                    'required': [],
                },
            },
        },
    ]


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a robot tool and return the result."""
    robot = get_robot()

    try:
        if tool_name == 'set_expression':
            return robot.set_expression(arguments['expression'])
        elif tool_name == 'speak_text':
            return robot.speak_text(arguments['text'])
        elif tool_name == 'move_robot':
            return robot.move_robot(
                arguments.get('linear_x', 0.0),
                arguments.get('linear_y', 0.0),
                arguments.get('angular_z', 0.0)
            )
        elif tool_name == 'move_with_duration':
            return robot.move_with_duration(
                arguments.get('linear_x', 0.0),
                arguments.get('angular_z', 0.0),
                arguments.get('duration', 0.5)
            )
        elif tool_name == 'set_led_color':
            return robot.set_led_color(arguments['color'])
        elif tool_name == 'control_head_pitch':
            return robot.control_head_pitch(arguments['angle'])
        # Support both names for backward compatibility
        elif tool_name == 'set_torch' or tool_name == 'toggle_torch':
            # Convert string 'True'/'False' to boolean
            on_value = arguments['on']
            if isinstance(on_value, str):
                on_value = on_value.lower() in ['true', '1', 'yes', 'on']
            return robot.set_torch(on_value)
        elif tool_name == 'enable_camera':
            # Convert string 'True'/'False' to boolean
            enable_value = arguments['enable']
            if isinstance(enable_value, str):
                enable_value = enable_value.lower() in [
                    'true', '1', 'yes', 'on']
            return robot.enable_camera(enable_value)
        elif tool_name == 'biometric_authentication':
            return robot.biometric_authentication(arguments.get('message', 'Please authenticate to continue'))
        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {"status": "error", "message": f"Error executing {tool_name}: {str(e)}"}
