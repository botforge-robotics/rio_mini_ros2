# Desktop Companion Robot - LLM Integration

## Overview

This implementation provides intelligent LLM integration for the Desktop Companion Robot using Ollama and ROS2. The system enables natural language interaction with the robot through speech recognition and tool calling.

## Architecture

### Core Components

1. **Ollama Node** (`ollama_node.py`)

   - Main LLM integration hub using Ollama
   - Processes speech recognition results
   - Executes tool calls based on LLM decisions
   - Simplified without environmental context awareness

2. **Robot Tools** (`robot_tools.py`)
   - Comprehensive tool calling framework
   - Interfaces with all RIO robot capabilities
   - Provides methods for LLM to control robot hardware

## Features Implemented

### ✅ Core LLM Integration

- Ollama integration with granite3-dense:2b model
- Tool calling framework for robot control
- Speech-to-action pipeline
- Simplified architecture without environmental context

### ✅ Robot Control Tools

- **Expression Control**: Set facial expressions (happy, sad, thinking, etc.)
- **Voice Interaction**: Text-to-speech with emotional expressions
- **Movement Control**: Robot navigation and gestures
- **LED Control**: Visual feedback with color changes
- **Head Control**: Servo control for head movements
- **Torch Control**: Flashlight on/off
- **Camera Control**: Front/back camera management
- **Authentication**: Biometric authentication support

### ✅ Environmental Intelligence

- **Note**: Environmental awareness will be implemented in a separate node later
- **Current Focus**: Pure LLM integration and tool calling
- **Future**: Battery monitoring, tilt detection, edge detection, light adaptation

### ✅ Speech Processing

- Direct speech recognition result processing
- Hotword detection handling
- Conversation history management

## Configuration Files

### `config/llm_config.yaml`

- Ollama model configuration
- Tool calling parameters
- Speech processing settings
- Context management options
- Safety thresholds
- Expression mappings

### `config/sensor_thresholds.yaml`

- Battery monitoring thresholds
- IMU motion detection limits
- TOF distance sensor ranges
- Illuminance levels
- Speech recognition parameters

## Usage

### Launch the System

```bash
# Build the package
cd /home/chaitu/rio_mini_ws
colcon build --packages-select rio_mini

# Source the workspace
source install/setup.bash

# Launch the complete system
ros2 launch rio_mini bringup.launch.py
```

### Customize Agent Port

```bash
ros2 launch rio_mini bringup.launch.py agent_port:=9999
```

## Speech Commands Examples

The robot can understand and respond to various voice commands:

### Basic Interaction

- "Hello" → Robot greets with happy expression
- "How are you?" → Contextual response with current status
- "Thank you" → Polite acknowledgment

### Robot Control

- "Turn on torch" → Activates flashlight
- "Turn off torch" → Deactivates flashlight
- "Move forward" → Robot moves forward
- "Turn left" → Robot turns left
- "Set LED to red" → Changes LED color

### Expression Control

- "Look happy" → Sets happy expression
- "Look sad" → Sets sad expression
- "Look thinking" → Sets thinking expression

### Camera Control

- "Turn on front camera" → Activates front camera
- "Turn on back camera" → Activates back camera
- "Turn off camera" → Deactivates camera

## Safety Features

### Automatic Safety Responses

- **Low Battery**: Robot expresses sleepiness and requests charging
- **Tilt Detection**: Robot shows fear and asks for help
- **Edge Detection**: Robot shows curiosity and warns about edge

### Environmental Awareness

- Monitors battery level continuously
- Tracks robot orientation and movement
- Monitors proximity to table edges
- Adapts to lighting conditions

## Dependencies

### Python Packages

- `ollama`: LLM integration
- `rclpy`: ROS2 Python client
- `sensor_msgs`: Sensor data types
- `geometry_msgs`: Geometric data types
- `std_msgs`: Standard message types
- `rio_interfaces`: RIO-specific interfaces

### ROS2 Packages

- `rosbridge_server`: WebSocket communication
- `rosapi`: ROS API services
- `micro_ros_agent`: Micro-ROS communication

## Testing

Run the test script to verify the implementation:

```bash
cd /home/chaitu/rio_mini_ws/src/rio_mini
python3 test_llm_integration.py
```

## Future Enhancements

### Phase 2 Features (To Be Added)

- Object recognition with camera
- Gesture recognition with IMU
- Person detection
- Learning system for user preferences

### Phase 3 Features (To Be Added)

- Multi-modal interaction
- Predictive behavior
- Social intelligence
- Complex task automation

## Troubleshooting

### Common Issues

1. **Ollama Not Found**

   ```bash
   pip install ollama
   ollama pull llama3.2:3b
   ```

2. **RIO Interfaces Missing**

   - Ensure `rio_interfaces` package is built and sourced

3. **Speech Recognition Not Working**

   - Check if speech recognition topics are publishing
   - Verify microphone permissions

4. **Robot Not Responding**
   - Check ROS2 topic connections
   - Verify robot hardware is connected
   - Check battery level

## Architecture Diagram

```
Speech Recognition → Speech Processor → LLM Intelligence → Robot Tools → Robot Hardware
        ↓                    ↓                ↓              ↓
   Hotword Detection    Text Cleaning    Context Building   Hardware Control
        ↓                    ↓                ↓              ↓
   Wake Word Trigger    Normalized Text   Environmental     Expression Changes
                        Processing        Awareness        Movement Commands
```

This implementation provides a solid foundation for an intelligent desktop companion robot with natural language interaction capabilities.
