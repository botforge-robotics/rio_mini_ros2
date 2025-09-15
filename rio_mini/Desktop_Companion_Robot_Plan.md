# Desktop Companion Robot - Implementation Plan

## 🤖 **Project Scope Analysis: Intelligent Desktop Companion Robot**

### **Core System Architecture**

#### **1. LLM Integration Layer**

- **Ollama Integration**: Local LLM for privacy and offline operation
- **Tool Calling Framework**: Function calling to ROS2 interfaces
- **Context Management**: Maintain conversation history and robot state
- **Intent Recognition**: Parse user commands and environmental triggers

#### **2. ROS2 Communication Layer**

- **Topic Subscribers**: Monitor sensor data and robot state
- **Topic Publishers**: Control robot hardware
- **Service Clients**: Call expression and camera services
- **Action Clients**: Handle TTS and authentication actions

#### **3. Intelligence Layer**

- **Environmental Awareness**: Process sensor data for context
- **Emotional Intelligence**: Match expressions to situations
- **Proactive Behavior**: React to environmental changes
- **Safety Monitoring**: Edge detection, tilt warnings, battery alerts

### **Required Libraries & Frameworks**

#### **Core Libraries**

- **ROS2 Humble**: Robot operating system
- **Ollama Python SDK**: LLM integration
- **rclpy**: ROS2 Python client library
- **asyncio**: Asynchronous programming for concurrent operations
- **json**: Tool calling parameter handling
- **threading**: Multi-threaded sensor monitoring

#### **Additional Libraries**

- **numpy**: Sensor data processing
- **scipy**: Signal processing for IMU data
- **opencv-python**: Camera feed processing (future)
- **pyaudio**: Audio processing (if needed)
- **websockets**: Real-time communication (if web interface needed)

### **Communication Architecture**

#### **Data Flow Design**

```
Sensor Topics → Context Processor → LLM Tool Caller → Action Executor → Robot Hardware
     ↓              ↓                    ↓                ↓
Environmental    State Machine      Intent Parser    Hardware Control
   Triggers       Management        Tool Selection   Response Generation
```

#### **Component Communication**

1. **Sensor Monitor**: Continuous subscription to all sensor topics
2. **Context Aggregator**: Combines sensor data into environmental context
3. **LLM Interface**: Processes speech and generates tool calls
4. **Tool Executor**: Executes ROS2 commands based on LLM decisions
5. **Response Generator**: Creates TTS responses with appropriate expressions

### **Intelligent Features Implementation**

#### **1. Speech Recognition Integration**

- **Continuous Listening**: Process any speech recognition result as user input
- **Command Parsing**: Convert speech to actionable intents
- **Context Awareness**: Include environmental data in LLM prompts
- **Response Generation**: Dynamic TTS with emotional expressions

#### **2. Environmental Intelligence**

- **Tilt Detection**: Monitor IMU data for robot orientation
- **Edge Detection**: Use TOF sensor for table edge safety
- **Light Adaptation**: Adjust behavior based on illuminance
- **Proximity Awareness**: React to nearby objects
- **Battery Monitoring**: Low power warnings and behavior changes

#### **3. Emotional Intelligence**

- **Expression Matching**: Map situations to appropriate expressions
- **Voice Tone**: Adjust TTS parameters based on context
- **Behavioral Patterns**: Learn user preferences over time
- **Proactive Interactions**: Initiate conversations based on sensor data

### **Advanced Features Scope**

#### **Immediate Implementation**

- Basic tool calling for all interfaces
- Environmental safety monitoring
- Dynamic expression changes
- Speech-to-action mapping

#### **Phase 2 Features**

- **Object Recognition**: Camera-based visual understanding
- **Gesture Recognition**: IMU-based gesture detection
- **Person Detection**: Identify when user is present
- **Learning System**: Adapt to user preferences

#### **Phase 3 Features**

- **Multi-modal Interaction**: Combine voice, gesture, and visual
- **Predictive Behavior**: Anticipate user needs
- **Social Intelligence**: Understand conversation context
- **Task Automation**: Execute complex multi-step tasks

### **System Architecture Components**

#### **1. Main LLM Node**

- **Purpose**: Central intelligence hub
- **Responsibilities**: Tool calling, context management, decision making
- **Inputs**: Speech recognition results (any text = user input), sensor data, user commands
- **Outputs**: Tool calls, TTS commands, expression changes
- **Note**: No hotword detection needed - any speech recognition result triggers LLM processing

#### **2. Sensor Monitor Node**

- **Purpose**: Continuous sensor data collection
- **Responsibilities**: Data aggregation, threshold monitoring, event detection
- **Inputs**: All sensor topics
- **Outputs**: Processed sensor events, environmental context

#### **3. Tool Executor Node**

- **Purpose**: Execute LLM-generated tool calls
- **Responsibilities**: ROS2 command execution, error handling, feedback
- **Inputs**: Tool call requests from LLM
- **Outputs**: Hardware control commands, execution status

#### **4. Context Manager Node**

- **Purpose**: Maintain robot state and conversation history
- **Responsibilities**: State tracking, context building, memory management
- **Inputs**: All system events and user interactions
- **Outputs**: Contextual information for LLM

### **Implementation Strategy**

#### **Phase 1: Core Foundation**

1. Set up Ollama integration with ROS2
2. Implement basic tool calling framework
3. Create sensor monitoring system
4. Build speech-to-action pipeline

#### **Phase 2: Intelligence Layer**

1. Add environmental awareness
2. Implement safety monitoring
3. Create dynamic expression system
4. Add proactive behavior triggers

#### **Phase 3: Advanced Features**

1. Multi-modal interaction
2. Learning and adaptation
3. Complex task execution
4. Social intelligence features

### **Key Technical Considerations**

#### **Performance Optimization**

- **Asynchronous Processing**: Non-blocking sensor monitoring
- **Context Caching**: Efficient state management
- **Tool Call Optimization**: Minimize latency in responses
- **Memory Management**: Efficient data handling

#### **Safety & Reliability**

- **Error Handling**: Graceful failure recovery
- **Safety Limits**: Hardware protection mechanisms
- **Battery Management**: Power-aware operation
- **Edge Detection**: Prevent falls from table

#### **User Experience**

- **Response Time**: Minimize latency for natural interaction
- **Contextual Responses**: Relevant and timely reactions
- **Emotional Engagement**: Expressive and empathetic behavior
- **Proactive Interaction**: Anticipate user needs

## 🎯 **Specific Use Cases & Examples**

### **Environmental Safety Examples**

#### **Tilt Detection Scenario**

- **Trigger**: IMU detects robot tilted > 30 degrees
- **Action**: Set expression to "afraid", TTS: "Oh no! I'm falling! Please help me!"
- **Safety**: Alert user to potential danger

#### **Edge Detection Scenario**

- **Trigger**: TOF sensor reads > 55cm (edge of table)
- **Action**: Set expression to "curious", TTS: "I can see the edge! I should be careful."
- **Safety**: Prevent robot from falling off table

#### **Low Battery Scenario**

- **Trigger**: Battery level < 20%
- **Action**: Set expression to "sleepy", TTS: "I'm getting tired. Please charge me soon."
- **Behavior**: Reduce activity, prepare for sleep mode

### **Interactive Examples**

#### **Voice Command: "Turn on torch"**

- **Speech Recognition**: Captures command
- **LLM Processing**: Identifies intent and tool needed
- **Tool Call**: Publish to `/torch` topic (true)
- **Response**: TTS with "happy" expression: "Torch is now on! I can see better now."

#### **Voice Command: "How are you feeling?"**

- **Context Check**: Current expression, battery, sensor data
- **LLM Response**: Generate contextual response
- **Expression**: Match emotion to response
- **TTS**: "I'm feeling great! My battery is at 85% and I can see everything clearly."

#### **Proactive Interaction: User Approaches**

- **Trigger**: TOF sensor detects object < 30cm
- **Context**: Check if it's a person (future: camera recognition)
- **Action**: Set expression to "happy", TTS: "Hello! I see you there!"
- **Behavior**: Turn head towards user, light up LED

### **Advanced Interaction Scenarios**

#### **Multi-step Task: "Help me find my phone"**

1. **Parse Intent**: User wants to find phone
2. **Tool Sequence**:
   - Enable camera
   - Set expression to "thinking"
   - TTS: "Let me help you find your phone!"
3. **Visual Processing**: Scan for phone-like objects
4. **Response**: "I found something that looks like a phone on your desk!"

#### **Emotional Support: User seems sad**

- **Context**: User's voice tone, time of day, recent interactions
- **Expression**: Set to "concerned"
- **TTS**: "You seem down today. Would you like to talk about it?"
- **Behavior**: Gentle head movement, warm LED color

## 🔧 **Technical Implementation Details**

### **Node Structure**

```
rio_mini/
├── nodes/
│   ├── llm_intelligence_node.py      # Main LLM integration
│   ├── sensor_monitor_node.py         # Sensor data processing
│   ├── tool_executor_node.py         # ROS2 command execution
│   ├── context_manager_node.py       # State and memory management
│   └── speech_processor_node.py      # Speech recognition integration
├── tools/
│   ├── robot_tools.py               # Tool definitions for LLM
│   ├── sensor_analyzers.py          # Sensor data analysis
│   └── expression_manager.py       # Expression logic
└── config/
    ├── llm_config.yaml             # LLM parameters
    ├── sensor_thresholds.yaml     # Safety thresholds
    └── behavior_patterns.yaml     # Behavioral rules
```

### **Tool Calling Framework**

- **Tool Registration**: Register all ROS2 interfaces as LLM tools
- **Parameter Validation**: Ensure tool calls have correct parameters
- **Error Handling**: Graceful failure and recovery
- **Response Generation**: Create appropriate TTS responses

### **Sensor Processing Pipeline**

1. **Raw Data Collection**: Subscribe to all sensor topics
2. **Data Filtering**: Remove noise and outliers
3. **Threshold Monitoring**: Check for safety conditions
4. **Context Building**: Combine sensor data into environmental context
5. **Event Generation**: Create triggers for LLM processing

### **Safety Systems**

- **Emergency Stop**: Immediate halt on critical sensor readings
- **Battery Protection**: Automatic sleep mode on low battery
- **Edge Protection**: Prevent movement near table edges
- **Tilt Recovery**: Alert and request help when tilted

This comprehensive plan provides a roadmap for building an intelligent desktop companion robot that can understand context, respond emotionally, and interact naturally with users while maintaining safety and reliability.
