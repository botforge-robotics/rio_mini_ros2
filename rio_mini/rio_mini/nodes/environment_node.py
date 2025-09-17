#!/usr/bin/env python3

"""
Environment Monitoring Node for Desktop Companion Robot

Continuously monitors sensor data and triggers environment-aware reactions
through LLM tool calling when thresholds are crossed.
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
import threading
import time
import logging
import math

# ROS2 message types
from sensor_msgs.msg import Imu, Range, Illuminance
from geometry_msgs.msg import Twist
from std_msgs.msg import String

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s Environment_Node %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class SensorMonitor:
    """Monitors sensor data and detects threshold crossings."""

    def __init__(self, thresholds):
        self.thresholds = thresholds

        # Current sensor values
        self.current_imu = None
        self.current_tof = None
        self.current_illuminance = None

        # Last trigger times for cooldown
        self.last_trigger_times = {
            'imu': 0.0,
            'tof': 0.0,
            'illuminance': 0.0,
            'danger': 0.0  # Combined danger detection
        }

        # Danger detection state
        self.danger_active = False
        self.danger_sources = set()  # Track which sensors triggered danger

    def update_sensor_data(self, sensor_type: str, data):
        """Update sensor data and check for threshold crossings."""
        triggers = []

        if sensor_type == 'imu':
            self.current_imu = data
            triggers = self._check_imu_thresholds(data)
        elif sensor_type == 'tof':
            self.current_tof = data
            triggers = self._check_tof_thresholds(data)
        elif sensor_type == 'illuminance':
            self.current_illuminance = data
            triggers = self._check_illuminance_thresholds(data)

        # Check for combined danger detection (IMU + TOF)
        danger_triggers = self._check_combined_danger()
        triggers.extend(danger_triggers)

        return triggers

    def _check_imu_thresholds(self, msg: Imu):
        """Check IMU data for tilt detection using specified axis."""
        triggers = []

        # Get the specified axis (y-axis)
        axis = self.thresholds['imu']['axis']
        if axis == 'x':
            accel_value = abs(msg.linear_acceleration.x)
        elif axis == 'y':
            accel_value = abs(msg.linear_acceleration.y)
        elif axis == 'z':
            accel_value = abs(msg.linear_acceleration.z)
        else:
            logger.warning(f"Unknown axis: {axis}, using y-axis")
            accel_value = abs(msg.linear_acceleration.y)

        # Check for tilt (absolute value, no sign needed)
        tilt_threshold = self.thresholds['imu']['tilt_threshold']
        if accel_value > tilt_threshold:
            triggers.append(('imu', 'tilt', accel_value, tilt_threshold))

        return triggers

    def _check_tof_thresholds(self, msg: Range):
        """Check TOF data for edge detection."""
        triggers = []

        # Check for edge detection (distance > threshold)
        edge_threshold = self.thresholds['tof']['edge_threshold']
        if msg.range > edge_threshold:
            triggers.append(('tof', 'edge', msg.range, edge_threshold))

        return triggers

    def _check_illuminance_thresholds(self, msg: Illuminance):
        """Check illuminance data for bright and dark detection."""
        triggers = []

        illuminance = msg.illuminance

        # Check for bright light
        bright_threshold = self.thresholds['illuminance']['bright_threshold']
        if illuminance > bright_threshold:
            triggers.append(
                ('illuminance', 'bright', illuminance, bright_threshold))

        # Check for dark conditions
        dark_threshold = self.thresholds['illuminance']['dark_threshold']
        if illuminance < dark_threshold:
            triggers.append(
                ('illuminance', 'dark', illuminance, dark_threshold))

        return triggers

    def _check_combined_danger(self):
        """Check for combined danger from IMU tilt + TOF edge detection."""
        triggers = []

        # Only check if we have both IMU and TOF data
        if self.current_imu is None or self.current_tof is None:
            return triggers

        # Check if both IMU tilt and TOF edge are detected
        imu_tilt_detected = False
        tof_edge_detected = False

        # Check IMU tilt
        axis = self.thresholds['imu']['axis']
        if axis == 'y':
            accel_value = abs(self.current_imu.linear_acceleration.y)
        elif axis == 'x':
            accel_value = abs(self.current_imu.linear_acceleration.x)
        elif axis == 'z':
            accel_value = abs(self.current_imu.linear_acceleration.z)
        else:
            accel_value = abs(self.current_imu.linear_acceleration.y)

        tilt_threshold = self.thresholds['imu']['tilt_threshold']
        if accel_value > tilt_threshold:
            imu_tilt_detected = True

        # Check TOF edge
        edge_threshold = self.thresholds['tof']['edge_threshold']
        if self.current_tof.range > edge_threshold:
            tof_edge_detected = True

        # If both are detected, trigger combined danger
        if imu_tilt_detected and tof_edge_detected:
            if not self.danger_active:
                # New danger detected
                self.danger_active = True
                self.danger_sources = {'imu', 'tof'}
                triggers.append(('danger', 'combined', 0.0, 0.0))
                logger.info(
                    "Combined danger detected: IMU tilt + TOF edge (robot likely lifted)")
        else:
            # Danger cleared
            if self.danger_active:
                self.danger_active = False
                self.danger_sources.clear()
                logger.info("Danger cleared: sensors back to normal")

        return triggers

    def should_trigger(self, sensor_type: str, trigger_type: str, sensor_value: float, threshold_value: float, cooldown_period: float) -> bool:
        """Check if trigger should be activated based on cooldown."""
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_trigger_times[sensor_type] < cooldown_period:
            return False

        # Update last trigger time
        self.last_trigger_times[sensor_type] = current_time
        return True


class EnvironmentNode(Node):
    """
    Environment Monitoring Node for Desktop Companion Robot
    """

    def __init__(self):
        super().__init__('environment_node')

        # Declare parameters from sensor_thresholds.yaml
        # IMU Thresholds - Y-axis acceleration only
        self.declare_parameter('imu.tilt_threshold', 8.0)
        self.declare_parameter('imu.axis', 'y')

        # TOF Thresholds - Edge detection only
        self.declare_parameter('tof.edge_threshold', 0.55)

        # Illuminance Thresholds - Bright and Dark only
        self.declare_parameter('illuminance.bright_threshold', 100.0)
        self.declare_parameter('illuminance.dark_threshold', 10.0)

        # Sensor Topics
        self.declare_parameter('sensor_topics.imu_topic', '/imu/data')
        self.declare_parameter('sensor_topics.tof_topic', '/tof')
        self.declare_parameter(
            'sensor_topics.illuminance_topic', '/illuminance')

        # Reaction Settings
        self.declare_parameter('reaction.cooldown_period', 3.0)
        self.declare_parameter('reaction.enable_imu_reactions', True)
        self.declare_parameter('reaction.enable_tof_reactions', True)
        self.declare_parameter('reaction.enable_illuminance_reactions', True)

        # Monitoring Frequency
        self.declare_parameter('monitoring.update_rate', 10.0)
        self.declare_parameter('monitoring.threshold_check_rate', 5.0)

        # Callback group for concurrent operations
        self.callback_group = ReentrantCallbackGroup()

        # Initialize sensor monitor
        self.sensor_monitor = SensorMonitor(self._load_thresholds())

        # Initialize sensor subscribers
        self._init_sensor_subscribers()

        # Speech publisher for environment reactions
        self.speech_pub = self.create_publisher(
            String, '/speech_recognition/result', 10, callback_group=self.callback_group)

        # Create timer for monitoring
        self.create_timer(1.0 / self.get_parameter('monitoring.update_rate').value,
                          self.monitoring_callback, callback_group=self.callback_group)

        self.get_logger().info('Environment Node initialized')

    def _load_thresholds(self):
        """Load sensor thresholds from parameter server."""
        try:
            # Load thresholds from parameters
            thresholds = {
                'imu': {
                    'tilt_threshold': self.get_parameter('imu.tilt_threshold').value,
                    'axis': self.get_parameter('imu.axis').value
                },
                'tof': {
                    'edge_threshold': self.get_parameter('tof.edge_threshold').value
                },
                'illuminance': {
                    'bright_threshold': self.get_parameter('illuminance.bright_threshold').value,
                    'dark_threshold': self.get_parameter('illuminance.dark_threshold').value
                }
            }

            logger.info("Loaded sensor thresholds from configuration")
            logger.info(
                f"IMU thresholds: tilt={thresholds['imu']['tilt_threshold']} m/s² on {thresholds['imu']['axis']}-axis")
            logger.info(
                f"TOF thresholds: edge={thresholds['tof']['edge_threshold']} m")
            logger.info(
                f"Illuminance thresholds: bright={thresholds['illuminance']['bright_threshold']} lux, dark={thresholds['illuminance']['dark_threshold']} lux")

            return thresholds

        except Exception as e:
            logger.error(f"Error loading sensor thresholds: {str(e)}")
            logger.warning("Using default thresholds")

            # Fallback to default values
            return {
                'imu': {
                    'tilt_threshold': 8.0,
                    'axis': 'y'
                },
                'tof': {
                    'edge_threshold': 0.55
                },
                'illuminance': {
                    'bright_threshold': 100.0,
                    'dark_threshold': 10.0
                }
            }

    def _init_sensor_subscribers(self):
        """Initialize sensor data subscribers."""
        # Get sensor topic names from configuration
        imu_topic = self.get_parameter('sensor_topics.imu_topic').value
        tof_topic = self.get_parameter('sensor_topics.tof_topic').value
        illuminance_topic = self.get_parameter(
            'sensor_topics.illuminance_topic').value

        logger.info(
            f"Subscribing to sensor topics: IMU={imu_topic}, TOF={tof_topic}, Illuminance={illuminance_topic}")

        # Create QoS profile for sensor data (best effort, volatile)
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # IMU subscriber
        self.imu_sub = self.create_subscription(
            Imu, imu_topic, self.imu_callback, sensor_qos, callback_group=self.callback_group)

        # TOF subscriber
        self.tof_sub = self.create_subscription(
            Range, tof_topic, self.tof_callback, sensor_qos, callback_group=self.callback_group)

        # Illuminance subscriber
        self.illuminance_sub = self.create_subscription(
            Illuminance, illuminance_topic, self.illuminance_callback, sensor_qos, callback_group=self.callback_group)

    def imu_callback(self, msg: Imu):
        """Process IMU data for tilt and shake detection."""
        triggers = self.sensor_monitor.update_sensor_data('imu', msg)
        self._process_triggers(triggers)

    def tof_callback(self, msg: Range):
        """Process TOF data for edge detection."""
        triggers = self.sensor_monitor.update_sensor_data('tof', msg)
        self._process_triggers(triggers)

    def illuminance_callback(self, msg: Illuminance):
        """Process illuminance data for light level detection."""
        triggers = self.sensor_monitor.update_sensor_data('illuminance', msg)
        self._process_triggers(triggers)

    def _process_triggers(self, triggers):
        """Process sensor triggers and send environment reactions."""
        cooldown_period = self.get_parameter('reaction.cooldown_period').value

        # Prioritize combined danger over individual sensor triggers
        combined_danger_triggered = False

        for sensor_type, trigger_type, sensor_value, threshold_value in triggers:
            # Check if reactions are enabled for this sensor type
            if sensor_type == 'imu' and not self.get_parameter('reaction.enable_imu_reactions').value:
                continue
            elif sensor_type == 'tof' and not self.get_parameter('reaction.enable_tof_reactions').value:
                continue
            elif sensor_type == 'illuminance' and not self.get_parameter('reaction.enable_illuminance_reactions').value:
                continue

            # Check cooldown
            if self.sensor_monitor.should_trigger(sensor_type, trigger_type, sensor_value, threshold_value, cooldown_period):
                # If combined danger is triggered, skip individual sensor triggers
                if sensor_type == 'danger' and trigger_type == 'combined':
                    combined_danger_triggered = True
                    self.trigger_environment_reaction(
                        sensor_type, trigger_type, sensor_value, threshold_value)
                elif not combined_danger_triggered:
                    # Only trigger individual sensors if no combined danger
                    self.trigger_environment_reaction(
                        sensor_type, trigger_type, sensor_value, threshold_value)

    def monitoring_callback(self):
        """Periodic monitoring callback."""
        # This can be used for additional monitoring logic
        pass

    def trigger_environment_reaction(self, sensor_type: str, trigger_type: str,
                                     sensor_value: float, threshold_value: float):
        """Trigger environment reaction by publishing to speech topic."""
        try:
            # Check if reactions are enabled for this sensor type
            if sensor_type == 'imu' and not self.get_parameter('reaction.enable_imu_reactions').value:
                return
            elif sensor_type == 'tof' and not self.get_parameter('reaction.enable_tof_reactions').value:
                return
            elif sensor_type == 'illuminance' and not self.get_parameter('reaction.enable_illuminance_reactions').value:
                return

            logger.info(
                f"Triggering environment reaction: {sensor_type} {trigger_type}")

            # Create environment-aware speech message
            speech_message = self._create_environment_speech(
                sensor_type, trigger_type)

            # Publish to speech recognition topic
            speech_msg = String()
            speech_msg.data = speech_message
            self.speech_pub.publish(speech_msg)

            logger.info(f"Published environment speech: {speech_message}")

        except Exception as e:
            logger.error(f"Error triggering environment reaction: {str(e)}")

    def _create_environment_speech(self, sensor_type: str, trigger_type: str) -> str:

        if sensor_type == 'danger' and trigger_type == 'combined':
            return (
                "React or act for the below described scene, "
                "You are in danger! You are being lifted up or moved unsafely. "
                "Please put me down immediately and safely."
            )

        elif sensor_type == 'imu' and trigger_type == 'tilt':
            return (
                "React or act for the below described scene, "
                "You are being tilted and feel unstable. "
                "Please stabilize me."
            )

        elif sensor_type == 'tof' and trigger_type == 'edge':
            return (
                "React or act for the below described scene, "
                "You detected an edge and might fall. "
                "Please move me away from the edge."
            )

        elif sensor_type == 'illuminance' and trigger_type == 'bright':
            return (
                "React or act for the below descibed scene, "
                "It is extremely bright use directs focused light on your face and uncomfortable due to strong light. "
                "Please stop shining light on me"
            )

        elif sensor_type == 'illuminance' and trigger_type == 'dark':
            return (
                "React or act for the below descibed scene, "
                "It is very dark and you cannot see or you are scared. "
                "Turning on torch"
            )

        else:
            return (
                "React or act for the below descibed scene, "
                "You detected an environmental change that may require attention. "
                "Please check your surroundings and ensure everything is safe."
            )


def main(args=None):
    rclpy.init(args=args)

    try:
        node = EnvironmentNode()

        # Use MultiThreadedExecutor for concurrent operations
        executor = MultiThreadedExecutor(num_threads=4)
        executor.add_node(node)

        # Log that we're ready to monitor environment
        node.get_logger().info("Environment Node ready to monitor sensors!")

        try:
            # Spin in a separate thread to keep the main thread responsive
            executor_thread = threading.Thread(
                target=executor.spin, daemon=True)
            executor_thread.start()

            # Keep the main thread alive
            while rclpy.ok():
                time.sleep(0.1)

        except KeyboardInterrupt:
            node.get_logger().info("Keyboard interrupt received, shutting down...")
        finally:
            executor.shutdown()
            node.destroy_node()
            rclpy.shutdown()

    except Exception as e:
        print(f"Error starting Environment Node: {e}")


if __name__ == '__main__':
    main()
