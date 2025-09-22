# RIO Mini Desktop Companion Robot

🤖 **RIO Mini** - A desktop companion robot powered by ROS2, Ollama LLM, and ESP32 micro-ROS integration! Experience intelligent voice interactions, environment awareness, and autonomous behaviors through advanced sensor fusion and AI-driven decision making.

## 📑 Table of Contents

- [RIO Mini Desktop Companion Robot](#rio-mini-desktop-companion-robot)
  - [📑 Table of Contents](#-table-of-contents)
  - [🎯 Core Features](#-core-features)
    - [🧠 AI-Powered Intelligence](#-ai-powered-intelligence)
    - [🔧 Hardware Integration](#-hardware-integration)
      - [ESP32 Robot Platform](#esp32-robot-platform)
      - [Mobile App Sensor Suite](#mobile-app-sensor-suite)
  - [🏗️ System Architecture](#️-system-architecture)
  - [⚙️ Requirements](#️-requirements)
    - [Hardware Requirements](#hardware-requirements)
      - [ESP32 Robot Platform](#esp32-robot-platform-1)
    - [Software Requirements](#software-requirements)
      - [PC/Laptop (ROS2)](#pclaptop-ros2)
      - [ESP32 Robot base](#esp32-robot-base)
      - [Mobile App](#mobile-app)
  - [🔧 Circuit Assembly Instructions](#-circuit-assembly-instructions)
    - [Wiring Diagram](#wiring-diagram)
    - [Power Distribution](#power-distribution)
    - [Component Connections](#component-connections)
      - [I2C Communication (ToF Sensor)](#i2c-communication-tof-sensor)
      - [Motor Control (MX1508 Driver)](#motor-control-mx1508-driver)
      - [Servo Control](#servo-control)
      - [LED Control](#led-control)
  - [⚠️ Assembly Suggestions](#️-assembly-suggestions)
    - [1. Motor and Wheel Mounting](#1-motor-and-wheel-mounting)
    - [2. Servo Arm Assembly](#2-servo-arm-assembly)
    - [3. Top Case Bonding](#3-top-case-bonding)
  - [🚀 Getting Started](#-getting-started)
    - [1. Environment Setup](#1-environment-setup)
      - [1.1 ROS2 Setup](#11-ros2-setup)
      - [1.2 Micro-ROS Setup](#12-micro-ros-setup)
      - [1.3 RIO Mini Workspace Setup](#13-rio-mini-workspace-setup)
    - [2. Ollama Setup](#2-ollama-setup)
    - [3. Communication Setup](#3-communication-setup)
      - [3.1 WiFi Network Configuration](#31-wifi-network-configuration)
    - [3.2 Launch the System](#32-launch-the-system)
  - [📡 ROS2 Interfaces](#-ros2-interfaces)
    - [📢 Topics](#-topics)
      - [Publishers](#publishers)
      - [Subscribers](#subscribers)
    - [⚡ Actions](#-actions)
      - [Authentication Action](#authentication-action)
      - [Text-to-Speech Action](#text-to-speech-action)
    - [🔧 Services](#-services)
      - [Camera Control Service](#camera-control-service)
      - [Expression Management Services](#expression-management-services)
    - [😊 Available Facial Expressions](#-available-facial-expressions)
  - [🤖 Ollama Agent Tool Calling](#-ollama-agent-tool-calling)
    - [Advanced AI Integration](#advanced-ai-integration)
      - [Tool Calling Architecture](#tool-calling-architecture)
      - [Available Tools](#available-tools)
      - [Tool Calling Examples](#tool-calling-examples)
  - [🔧 Configuration](#-configuration)
    - [Robot Parameters (`robot_params.yaml`)](#robot-parameters-robot_paramsyaml)
    - [Sensor Thresholds (`sensor_thresholds.yaml`)](#sensor-thresholds-sensor_thresholdsyaml)
  - [🔗 Reference Links](#-reference-links)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)

## 🎯 Core Features

### 🧠 AI-Powered Intelligence

- **Ollama LLM Integration**: Local language model for natural voice interactions and tool calling for robot actions.

### 🔧 Hardware Integration

#### ESP32 Robot Platform

- **ESP32 Micro-ROS**: Real-time sensor data and motor control
- **2x DC Motors**: Differential drive with precise movement control
- **1x Servo Motor**: Head pitch control with safety limits (150-180°)
- **LED**: WS2812B NeoPixel for visual feedback
- **TOF Sensor**: VL53L0X proximity detection for safety
- **Rechargeable Battery**: Type-C USB charging for convenience

#### Mobile App Sensor Suite

- **Comprehensive Sensors**: Accelerometer, Gyroscope, Magnetometer, GPS, Ambient Light
- **Audio/Visual**: Dual cameras, microphone, speaker, display for rich interactions
- **Security**: Fingerprint scanner for biometric authentication
- **Utilities**: Torch, NFC (coming soon), IR (coming soon)
- **Hotword Detection**: Always-listening voice activation
- **Facial Expressions**: Dynamic visual feedback on mobile display

## 🏗️ System Architecture

```
                    ┌─────────────────────────────────────────┐
                    │            WiFi Router                  │
                    │         (Central Hub)                   │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┼───────────────────────┐
                    │                 │                       │
         ┌──────────▼──────────┐      │      ┌──────────────▼──────────────┐
         │    ESP32 Robot      │      │      │      Mobile App             │
         │   (Micro-ROS)       │      │      │   (ROS Bridge WebSocket)    │
         │                     │      │      │                             │
         │ • 2x DC Motors      │      │      │ • Accelerometer             │
         │ • 1x Servo          │      │      │ • Gyroscope                 │
         │ • Ws2812b Led       │      │      │ • Magnetometer              │
         │ • TOF Sensor        │      │      │ • 2x Cameras                │
         │ • Battery           │      │      │ • GPS                       │
         │ • Type-C USB        │      │      │ • Ambient Light             │
         │ • Esp-32            │      │      │ • Microphone                │
         │                     │      │      │ • Speaker                   │
         │                     │      │      │ • Display                   │
         │                     │      │      │ • Fingerprint               │
         │                     │      │      │ • Torch                     │
         │                     │      │      │ • NFC (Soon)                │
         │                     │      │      │ • IR (Soon)                 │
         └─────────────────────┘      │      └─────────────────────────────┘
                                      │
                    ┌─────────────────▼───────────────────────┐
                    │           PC/Laptop                     │
                    │         (ROS2 Hub)                      │
                    │                                         │
                    │ • Environment Node                      │
                    │ • Ollama Node                           │
                    │ • WebRTC Node                           │
                    │ • Micro-ROS Agent                       │
                    │ • ROS Bridge Server                     │
                    │                                         │
                    │ ┌─────────────────────────────────────┐ │
                    │ │           AI Agent                  │ │
                    │ │                                     │ │
                    │ │ • Ollama LLM                        │ │
                    │ │ • Tool Calling                      │ │
                    │ └─────────────────────────────────────┘ │
                    │                                         │
                    │                                         │
                    └─────────────────────────────────────────┘

```

## ⚙️ Requirements

### Hardware Requirements

#### ESP32 Robot Platform

| **Component**                                        | **Qty** | **Unit Price (₹)** | **Total Price (₹)** | **Product Link**                                                                                                                                              |
| ---------------------------------------------------- | ------- | ------------------ | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **N20 6V 60 RPM Micro Metal Gear Motor**             | 2       | ₹274               | ₹548                | [Robu.in](https://robu.in/product/n20-6v-60-rpm-micro-metal-gear-motor/)                                                                                      |
| **Mini 3Pi Car N20 Caster Robot Ball Wheel**         | 1       | ₹38                | ₹38                 | [Robu.in](https://robu.in/product/mini-3pi-car-n20-caster-robot-ball-wheel/)                                                                                  |
| **34mm Mini Car N20 Motor Wheel Rubber Small Wheel** | 2       | ₹45                | ₹90                 | [Robu.in](https://robu.in/product/34mm-mini-car-n20-motor-wheel-rubber-small-wheel/)                                                                          |
| **ESP32 Base PCB**                                   | 1       | ₹122               | ₹122                | [ZBotic.in](https://zbotic.in/product/esp32-base-pcb-with-motor-driver-ic-for-receiver-custom-pcb/)                                                           |
| **ESP-32 Development Board(30-Pin)**                 | 1       | ₹400               | ₹400                | [Robu.in](https://robu.in/product/30pin-ch9102x-esp-32-wifibluetooth-development-board-with-type-c-usb-interface/)                                            |
| **Type-C USB 5V 2A Step-Up Boost Converter**         | 1       | ₹55                | ₹55                 | [Robu.in](https://robu.in/product/type-c-usb-5v-2a-step-up-boost-converter-with-usb-charger/)                                                                 |
| **1000mAh 3.7V Single Cell LiPo Battery**            | 1       | ₹350               | ₹350                | [Robu.in](https://robu.in/product/wly102050-1000mah-3-7v-single-cell-rechargeable-lipo-battery/)                                                              |
| **VL53L0X ToF Laser Ranging Sensor**                 | 1       | ₹179               | ₹179                | [Robu.in](https://robu.in/product/unsoldered-purple-gy-530-vl53l0x-time-of-flight-tof-laser-ranging-sensor-module/)                                           |
| **1pc WS2812B 5V RGB LED**                           | 1       | ₹5                 | ₹5                  | [Robu.in](https://robu.in/product/1m-ws2812b-5v-addressable-rgb-non-waterproof-led-strip-light-60leds-m/)                                                     |
| **MX1508 Motor Driver**                              | 1       | ₹45                | ₹45                 | [Robu.in](https://robu.in/product/mx1508-dual-h-bridge-dc-pwm-stepper-motor-driver/)                                                                          |
| **MG995 Servo Metal Gear**                           | 1       | ₹340               | ₹340                | [Robu.in](https://robu.in/product/towerpro-mg995-servo-high-speed-digital-metal-gear-ball-bearing-torque-12kg-robot-arduino-good-quality180-degree-rotation/) |
| **Aluminum Servo Horn 25T**                          | 1       | ₹34                | ₹34                 | [Robu.in](https://robu.in/product/aluminum-servo-hornarm-25t-round-type-disc-mg995-mg996/)                                                                    |
| **Mobile Holder**                                    | 1       | ₹130               | ₹130                | [Amazon.in](https://amazon.in/dp/B095C56NYD?ref=ppx_yo2ov_dt_b_fed_asin_title)                                                                                |
| **Screws & Fasteners**                               | 1 set   | ₹25                | ₹25                 | _Available at local hardware stores_                                                                                                                          |
| **Slide Switch**                                     | 1       | ₹3                 | ₹3                  | [Robu.in](https://robu.in/product/1-month-warranty-254/)                                                                                                      |
| **3D Printed Body Parts**                            | 1 set   | ₹50                | ₹50                 | _Custom 3D printing service_                                                                                                                                  |
| **RIO Ros2Sense Mobile App**                         | 1       | ₹990               | ₹990                | [Google Play Store](https://play.google.com/store/apps/details?id=com.botforge.rio&hl=en_IN)                                                                  |
|                                                      |         |                    |                     |                                                                                                                                                               |
| **📊 TOTAL PROJECT COST**                            |         |                    | **₹3,404**          |                                                                                                                                                               |

**Additional Notes:**

- Prices are approximate and may vary based on supplier and availability
- Shipping costs not included in the above calculation
- Some components may be available at local electronics stores at different prices
- 3D printed parts require access to 3D printing services or personal 3D printer

**Reference Links:**

- **3D Model & Assembly**: [RIO Mini 3D Model Repository](https://github.com/botforge-robotics/rio_mini_3d_model)

### Software Requirements

#### PC/Laptop (ROS2)

- **ROS2 Jazzy** (Recommended)
- **Ollama Installation** with Mistral model

#### ESP32 Robot base

- **Micro-ROS Firmware**: [RIO Mini Firmware Repository](https://github.com/botforge-robotics/rio_mini_firmware)

#### Mobile App

- **[RIO Ros2Sense App](https://play.google.com/store/apps/details?id=com.botforge.rio&hl=en_IN)** (Google Play Store) - ₹990

## 🔧 Circuit Assembly Instructions

### Wiring Diagram

![RIO Mini Circuit Schematic](https://raw.githubusercontent.com/botforge-robotics/rio_mini_3d_model/refs/heads/master/images/rio_mini_schematic.jpg)

### Power Distribution

```
[LiPo 3.7V]
   |
 [IP5306]----5V----+---- ESP32 VIN/5V
   |               +---- MX1508 VM
   |               +---- Servo V+
   |               +---- WS2812B V+
   |               +---- TOF V+
   |
 [Slide Switch]
   |
  GND--------------+---- (COMMON GND)
```

### Component Connections

#### I2C Communication (ToF Sensor)

```
ESP32 GPIO21 (SDA) ---- ToF SDA
ESP32 GPIO22 (SCL) ---- ToF SCL
```

#### Motor Control (MX1508 Driver)

```
ESP32 GPIO25 ---- MX1508 IN1   -> Motor Left
ESP32 GPIO26 ---- MX1508 IN2   -> Motor Left
ESP32 GPIO27 ---- MX1508 IN3   -> Motor Right
ESP32 GPIO13 ---- MX1508 IN4   -> Motor Right
MX1508 OUTA+/- -> Motor Left terminals
MX1508 OUTB+/- -> Motor Right terminals
```

#### Servo Control

```
ESP32 GPIO17 ---- Servo Signal (MG996R)
```

#### LED Control

```
ESP32 GPIO16 ---> WS2812 DIN
```

## ⚠️ Assembly Suggestions

### 1. Motor and Wheel Mounting

![Wheel Gap Measurement](https://raw.githubusercontent.com/botforge-robotics/rio_mini_3d_model/refs/heads/master/images/wheelgap.jpg)

**Important**: While mounting motors and wheels, ensure there is **no more than 1.5mm gap** between the wheel and bottom base edge. If the gap exceeds this limit, it may obstruct the other wheel edge when the top case is installed.

### 2. Servo Arm Assembly

![Arm Assembly](https://raw.githubusercontent.com/botforge-robotics/rio_mini_3d_model/refs/heads/master/images/armAssembling.jpg)

**Critical Steps**:

- The arm should be positioned **between the servo horn and servo body**
- **Set servo to 180° position** before mounting the arm to the servo
- Upload the firmware first - it automatically sets the servo to 180° position
- Only mount the arm after confirming the servo is at 180°

### 3. Top Case Bonding

![Glueing Process](https://raw.githubusercontent.com/botforge-robotics/rio_mini_3d_model/refs/heads/master/images/glueing.jpg)

**Final Assembly**:

- Use **Cynabond** adhesive to securely bond the top 2 parts after arm assembly
- Ensure proper alignment before applying adhesive
- Allow sufficient curing time as per adhesive instructions

## 🚀 Getting Started

### 1. Environment Setup

#### 1.1 ROS2 Setup

```bash
# Source ROS installation
source /opt/ros/jazzy/setup.bash
```

#### 1.2 Micro-ROS Setup

```bash
# Set up Micro-ROS workspace
mkdir -p ~/uros_ws/src
cd ~/uros_ws/src
git clone -b humble https://github.com/micro-ROS/micro_ros_setup.git

# Build Micro-ROS
cd ~/uros_ws
rosdep update && rosdep install --from-paths src --ignore-src -y
colcon build
source install/setup.bash

# Build Micro-ROS Agent
ros2 run micro_ros_setup create_agent_ws.sh
ros2 run micro_ros_setup build_agent.sh
source install/setup.bash
```

#### 1.3 RIO Mini Workspace Setup

```bash
# Set up RIO Mini workspace
mkdir -p ~/rio_mini_ws/src
cd ~/rio_mini_ws/src
git clone https://github.com/botforge-robotics/rio_mini_ros2.git

# Build RIO Mini packages
cd ~/rio_mini_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

### 2. Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Mistral model
ollama pull mistral

# Verify installation
ollama list
```

### 3. Communication Setup

#### 3.1 WiFi Network Configuration

```bash
# Ensure all devices are on the same WiFi network
# PC/Laptop: Connect to WiFi
# ESP32: Configure WiFi credentials in firmware
# Mobile: Connect to same WiFi network
```

### 3.2 Launch the System

```bash
# Launch all nodes
ros2 launch rio_mini bringup.launch.py

# Or launch individual components
ros2 run rio_mini ollama_node
ros2 run rio_mini environment_node
ros2 run rio_mini webrtc_node
```

## 📡 ROS2 Interfaces

### 📢 Topics

#### Publishers

**Sensor Data Topics:**

- `/battery` (`sensor_msgs/BatteryState`) - Battery status information
- `/gps` (`sensor_msgs/NavSatFix`) - GPS location data
- `/illuminance` (`sensor_msgs/Illuminance`) - Ambient light sensor readings
- `/imu/data` (`sensor_msgs/Imu`) - Combined IMU data with acceleration, velocity and orientation
- `/imu/absolute_orientation` (`geometry_msgs/Vector3Stamped`) - Absolute orientation using magnetic reference
- `/imu/heading` (`std_msgs/Float32`) - Compass heading in degrees (0-360°)
- `/imu/linear_acceleration` (`geometry_msgs/Vector3Stamped`) - User acceleration without gravity (m/s²)
- `/imu/mag` (`sensor_msgs/MagneticField`) - Magnetometer readings in μT (micro-Tesla)
- `/imu/orientation` (`geometry_msgs/Vector3Stamped`) - Device orientation (pitch, roll, yaw)
- `/tof` (`sensor_msgs/Range`) - Time-of-flight range sensor data

- `/expression` (`std_msgs/String`) - Current facial expression

- `/speech_recognition/hotword_detected` (`std_msgs/Empty`) - Wake word detection
- `/speech_recognition/result` (`std_msgs/String`) - Recognized speech text
- `/speech_recognition/status` (`std_msgs/String`) - Speech Recognition system status ("listening", "done")

#### Subscribers

- `/cmd_vel` (`geometry_msgs/TwistStamped`) - Control robot's linear and angular velocity

- `/led` (`std_msgs/ColorRGBA`) - Control LED color with RGBA values (RGB: 0-255, Alpha: 0-255)

- `/head_pitch` (`std_msgs/Float32`) - Control head pitch servo position in degrees (150-180°)

- `/torch` (`std_msgs/Bool`) - Control flashlight (true = on, false = off)

### ⚡ Actions

#### Authentication Action

- **`/auth`** (`rio_interfaces/action/Auth`)
  - **Purpose**: Authenticate using biometric sensors
  - **LLM Use Case**: Secure interactions, user verification
  - **Usage Example**:
    ```bash
    ros2 action send_goal /auth rio_interfaces/action/Auth \
    "{message: 'Please authenticate to continue'}"
    ```

#### Text-to-Speech Action

- **`/tts`** (`rio_interfaces/action/TTS`)
  - **Purpose**: Converts text to speech with facial expressions
  - **LLM Use Case**: Voice responses with emotional expressions
  - **Parameters**:
    - `text`: Text to speak
    - `voice_output`: Enable voice output
    - `start_expression`: Expression at start of speech
    - `end_expression`: Expression at end of speech
    - `expression_sound`: Play expression sound
  - **Usage Example**:
    ```bash
    ros2 action send_goal /tts rio_interfaces/action/TTS \
    "{text: 'Hello, how are you?', voice_output: true, start_expression: 'happy', end_expression: 'neutral', expression_sound: false}"
    ```

### 🔧 Services

#### Camera Control Service

- **`/enable_camera`** (`rio_interfaces/srv/Camera`)

  - **Purpose**: Control front/back cameras
  - **LLM Use Case**: Visual interactions, object recognition, video calls
  - **Parameters**:
    - `direction`: 0 (front) or 1 (back)
    - `status`: true (enable) or false (disable)
  - **Usage Examples**:

    ```bash
    # Enable front camera
    ros2 service call /enable_camera rio_interfaces/srv/Camera \
    "{direction: 0, status: true}"

    # Enable back camera
    ros2 service call /enable_camera rio_interfaces/srv/Camera \
    "{direction: 1, status: true}"
    ```

#### Expression Management Services

**Get Expression Status:**

- **`/expression_status`** (`rio_interfaces/srv/GetExpression`)
  - **Purpose**: Get current facial expression
  - **LLM Use Case**: Check robot's current emotional state
  - **Usage**:
    ```bash
    ros2 service call /expression_status rio_interfaces/srv/GetExpression "{}"
    ```

**Set Expression:**

- **`/set_expression`** (`rio_interfaces/srv/Expression`)
  - **Purpose**: Set robot's facial expression
  - **LLM Use Case**: Express emotions, provide visual feedback
  - **Parameters**:
    - `expression`: Expression name (see list below)
    - `expression_sound`: Play expression sound (true/false)
  - **Usage**:
    ```bash
    ros2 service call /set_expression rio_interfaces/srv/Expression \
    "{expression: 'happy', expression_sound: true}"
    ```

### 😊 Available Facial Expressions

| Expression  | Description                 | LLM Use Cases                               |
| ----------- | --------------------------- | ------------------------------------------- |
| `afraid`    | Displays fear or concern    | Danger warnings, scary stories, caution     |
| `angry`     | Shows frustration or anger  | Expressing disagreement, warnings           |
| `blush`     | Embarrassed or shy          | Compliments, shy responses                  |
| `curious`   | Shows interest or curiosity | Asking questions, learning mode             |
| `happy`     | Shows joy or pleasure       | Greetings, positive responses, celebrations |
| `idle`      | Default neutral state       | Waiting, standby mode                       |
| `listening` | Active listening mode       | Processing user input, attention            |
| `sad`       | Displays sadness            | Empathy, condolences, disappointment        |
| `sleep`     | Power saving mode           | Low energy, bedtime mode                    |
| `speaking`  | Talking animation           | During speech, conversations                |
| `surprise`  | Displays astonishment       | Unexpected events, discoveries              |
| `thinking`  | Processing or computing     | Problem solving, calculations               |
| `wakeup`    | Activation animation        | Startup, awakening from sleep               |

## 🤖 Ollama Agent Tool Calling

### Advanced AI Integration

The RIO Mini uses Ollama with Mistral model for sophisticated tool calling capabilities, enabling natural language control of all robot functions.

#### Tool Calling Architecture

```
User Speech → Speech Recognition → Ollama LLM → Tool Execution → Robot Action
```

#### Available Tools

**Movement Control:**

- `move_with_duration`: Safe, time-limited movement with speed limits
- `move_robot`: Direct velocity control (advanced users)

**Voice & Expression:**

- `speak_text`: Text-to-speech with automatic expression
- `set_expression`: Change facial expression
- `control_head_pitch`: Head movement (150-180°)

**Hardware Control:**

- `set_torch`: Flashlight on/off
- `set_led_color`: RGB LED control
- `enable_camera`: Front/back camera control

**Security:**

- `biometric_authentication`: Fingerprint/face verification

#### Tool Calling Examples

**Simple Movement:**

```json
[
  { "name": "speak_text", "arguments": { "text": "Moving forward" } },
  {
    "name": "move_with_duration",
    "arguments": { "linear_x": 0.25, "angular_z": 0, "duration": 0.5 }
  },
  { "name": "set_expression", "arguments": { "expression": "happy" } }
]
```

**Head Movement:**

```json
[
  { "name": "speak_text", "arguments": { "text": "Looking up" } },
  { "name": "control_head_pitch", "arguments": { "angle": 150 } },
  { "name": "set_expression", "arguments": { "expression": "curious" } }
]
```

**Security Workflow:**

```json
[
  {
    "name": "speak_text",
    "arguments": { "text": "Please authenticate to continue" }
  },
  {
    "name": "biometric_authentication",
    "arguments": { "message": "Authentication required" }
  },
  { "name": "speak_text", "arguments": { "text": "Access granted" } },
  { "name": "set_expression", "arguments": { "expression": "happy" } }
]
```

## 🔧 Configuration

### Robot Parameters (`robot_params.yaml`)

```yaml
ollama_node:
  ros__parameters:
    robot_movement:
      movement:
        max_linear_speed: 0.25 # m/s forward/backward
        max_angular_speed: 2.0 # rad/s rotation
        inplace_rotation_speed: 9.5 # rad/s for pure rotation
        default_duration: 0.5 # seconds
      head:
        top_position: 150 # degrees (head up)
        bottom_position: 180 # degrees (head down)
        front_position: 165 # degrees (neutral)
```

### Sensor Thresholds (`sensor_thresholds.yaml`)

```yaml
environment_node:
  ros__parameters:
    imu:
      tilt_threshold: 4.0 # m/s² for tilt detection
      axis: "y" # Use Y-axis acceleration
    tof:
      edge_threshold: 0.05 # meters (5cm) edge detection
    illuminance:
      bright_threshold: 2000.0 # lux bright detection
      dark_threshold: 1.5 # lux dark detection
```

## 🔗 Reference Links

- [RIO Hardware](https://github.com/botforge-robotics/rio_mini_hardware) - Hardware design and assembly
- [RIO Firmware](https://github.com/botforge-robotics/rio_mini_firmware) - Esp32 firmware

## 🤝 Contributing

1. Fork the Repository
2. Create Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit Changes (`git commit -m 'Add amazing feature'`)
4. Push to Branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**RIO Mini** - Bringing intelligence and awareness to desktop robotics! 🤖✨
