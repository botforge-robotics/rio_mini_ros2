# RIO ROS2 Interfaces Documentation for LLM Tool Calling

## Overview

This document provides a comprehensive overview of all RIO ROS2 interfaces for building an interactive desktop companion robot with Ollama LLM tool calling capabilities.

## 📢 Topics

### Publishers (Robot → LLM)

These topics provide sensor data and robot state information that the LLM can monitor:

#### Sensor Data Topics

- **`/battery`** (`sensor_msgs/BatteryState`)

  - Battery status information
  - Use case: Monitor power levels, trigger low battery warnings

- **`/gps`** (`sensor_msgs/NavSatFix`)

  - GPS location data
  - Use case: Location-based interactions, navigation context

- **`/illuminance`** (`sensor_msgs/Illuminance`)

  - Ambient light sensor readings
  - Use case: Adjust behavior based on lighting conditions

- **`/imu/data`** (`sensor_msgs/Imu`)

  - Combined IMU data with acceleration, velocity and orientation
  - Use case: Motion detection, gesture recognition

- **`/imu/absolute_orientation`** (`geometry_msgs/Vector3Stamped`)

  - Absolute orientation using magnetic reference
  - Use case: Compass-based interactions

- **`/imu/heading`** (`std_msgs/Float32`)

  - Compass heading in degrees (0-360°)
  - Use case: Direction-based conversations

- **`/imu/linear_acceleration`** (`geometry_msgs/Vector3Stamped`)

  - User acceleration without gravity (m/s²)
  - Use case: Movement detection, activity recognition

- **`/imu/mag`** (`sensor_msgs/MagneticField`)

  - Magnetometer readings in μT (micro-Tesla)
  - Use case: Environmental sensing

- **`/imu/orientation`** (`geometry_msgs/Vector3Stamped`)

  - Device orientation (pitch, roll, yaw)
  - Use case: Gesture recognition, pose-based interactions

- **`/tof`** (`sensor_msgs/Range`)

  - Time-of-flight range sensor data
  - Use case: Proximity detection, safety interactions

#### Robot State Topics

- **`/expression`** (`std_msgs/String`)
  - Current facial expression
  - Use case: Monitor robot's emotional state

#### Speech Recognition Topics

- **`/speech_recognition/hotword_detected`** (`std_msgs/Empty`)

  - Wake word detection
  - Use case: Trigger LLM interactions when user says wake word

- **`/speech_recognition/result`** (`std_msgs/String`)

  - Recognized speech text
  - Use case: Process user voice commands

- **`/speech_recognition/status`** (`std_msgs/String`)
  - Speech Recognition system status ("listening", "done")
  - Use case: Monitor speech system state

### Subscribers (LLM → Robot)

These topics allow the LLM to control robot hardware:

#### Movement Control

- **`/cmd_vel`** (`geometry_msgs/Twist`)
  - Control robot's linear and angular velocity
  - Use case: Move robot, navigate, dance

#### LED Control

- **`/led`** (`std_msgs/ColorRGBA`)

  - Control LED color with RGBA values (RGB: 0-255, Alpha: 0-255)
  - Use case: Visual feedback, mood indication

#### Servo Control

- **`/head_pitch`** (`std_msgs/Int32`)

  - Control head pitch servo position in degrees (0-180)
  - Use case: Head movement, nodding gestures

#### Flashlight Control

- **`/torch`** (`std_msgs/Bool`)
  - Control phone's flashlight (true = on, false = off)
  - Use case: Visual effects, attention grabbing

## ⚡ Actions

### Authentication Action

- **`/auth`** (`rio_interfaces/action/Auth`)
  - **Purpose**: Authenticate using phone's biometric sensors
  - **LLM Use Case**: Secure interactions, user verification
  - **Usage Example**:
    ```bash
    ros2 action send_goal /auth rio_interfaces/action/Auth \
    "{message: 'Please authenticate to continue'}"
    ```

### Text-to-Speech Action

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

## 🔧 Services

### Camera Control Service

- **`/enable_camera`** (`rio_interfaces/srv/Camera`)

  - **Purpose**: Control phone's front/back cameras
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

    # Disable camera
    ros2 service call /enable_camera rio_interfaces/srv/Camera \
    "{direction: 0, status: false}"
    ```

### Expression Management Services

#### Get Expression Status

- **`/expression_status`** (`rio_interfaces/srv/GetExpression`)
  - **Purpose**: Get current facial expression
  - **LLM Use Case**: Check robot's current emotional state
  - **Usage**:
    ```bash
    ros2 service call /expression_status rio_interfaces/srv/GetExpression "{}"
    ```

#### Set Expression

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

## 😊 Available Facial Expressions

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

## 🤖 LLM Tool Calling Integration Strategy

### 1. Sensor Monitoring Tools

Create tools that subscribe to sensor topics to provide context:

- **Environment Monitor**: `/illuminance`, `/imu/data`, `/gps`
- **User Presence**: `/speech_recognition/hotword_detected`, `/speech_recognition/result`
- **Robot State**: `/battery`, `/expression`
- **Proximity Sensing**: `/tos` for range detection

### 2. Control Tools

Create tools that publish to control topics:

- **Movement Control**: `/cmd_vel` for navigation and gestures
- **Visual Feedback**: `/led`, `/torch` for mood indication
- **Physical Interaction**: `/head_pitch` for head movements

### 3. Expression Tools

Create tools for emotional interaction:

- **Expression Control**: `/set_expression` service for emotional responses
- **Voice Interaction**: `/tts` action for speech with expressions
- **Expression Monitoring**: `/expression_status` service for state awareness

### 4. Camera Tools

Create tools for visual interaction:

- **Camera Control**: `/enable_camera` service for visual tasks
- **Object Recognition**: Process camera feed for visual understanding

### 5. Authentication Tools

Create tools for secure interactions:

- **Biometric Auth**: `/auth` action for secure operations

## 🔧 Implementation Notes

### Message Types Reference

- `sensor_msgs/BatteryState`: Battery information
- `sensor_msgs/NavSatFix`: GPS coordinates
- `sensor_msgs/Illuminance`: Light levels
- `sensor_msgs/Imu`: Motion data
- `geometry_msgs/Vector3Stamped`: 3D vectors
- `geometry_msgs/Twist`: Velocity commands
- `std_msgs/String`: Text data
- `std_msgs/Float32`: Single float values
- `std_msgs/Bool`: Boolean values
- `std_msgs/ColorRGBA`: Color with alpha
- `std_msgs/Int16`: Integer values
- `std_msgs/Int32`: 32-bit integer values
- `std_msgs/Empty`: Empty messages
- `sensor_msgs/Range`: Distance data (TOS sensor)
- `sensor_msgs/MagneticField`: Magnetic readings

### Tool Calling Best Practices

1. **Context Awareness**: Use sensor data to provide environmental context
2. **Emotional Intelligence**: Match expressions to conversation context
3. **Proactive Interaction**: Use wake word detection for spontaneous interactions
4. **Safety First**: Monitor battery levels and proximity sensors
5. **User Experience**: Combine voice, visual, and movement for rich interactions

This documentation provides the foundation for building a comprehensive LLM tool calling system that can interact with all aspects of the RIO robot platform.
