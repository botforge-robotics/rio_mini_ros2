#!/usr/bin/env python3

"""
Ollama Node for Desktop Companion Robot

Professional AI Agent using native Ollama APIs with MCP server connection.
Based on best practices from modern AI agent architectures.
"""

import rclpy
from rclpy.node import Node
# No callback groups needed - single threaded
from std_msgs.msg import String, Bool, Empty
import json
import time
import logging

# Ollama imports
import ollama

# Import robot tools
from rio_mini.tools.robot_tools import get_robot_tools, execute_tool

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s Ollama_Agent %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class OllamaAgent:
    """Professional AI Agent for robot control with native Ollama tool support."""

    def __init__(self, model: str = "llama3-groq-tool-use:8b",
                 temperature: float = 0.7, max_tokens: int = 1024, max_conversation_history: int = 5,
                 max_linear_speed: float = 0.15, max_angular_speed: float = 2.0, inplace_rotation_speed: float = 7.0):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_conversation_history = max_conversation_history
        self.conversation_history = []
        self.tools = get_robot_tools()

        # Movement parameters
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed
        self.inplace_rotation_speed = inplace_rotation_speed

        # Initialize Ollama client
        self.ollama_client = ollama.Client()

        logger.info(f"OllamaAgent initialized with model: {model}")
        logger.info(
            f"Movement params: linear={max_linear_speed}, angular={max_angular_speed}, inplace={inplace_rotation_speed}")
        logger.info(
            f"Available tools: {', '.join(tool['function']['name'] for tool in self.tools)}")

    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a robot tool and return formatted result."""
        try:
            result = execute_tool(tool_name, arguments)

            # Format the result for the LLM
            if result.get("status") == "success":
                return f"Tool {tool_name} executed successfully: {result.get('message', '')}"
            else:
                return f"Tool {tool_name} failed: {result.get('message', 'Unknown error')}"

        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error: {str(e)}"

    def _filter_conversation_history(self, conversation: list) -> list:
        """Filter conversation history to prevent token accumulation."""
        # Use the configured max_conversation_history
        max_history = self.max_conversation_history

        # Keep system message + recent conversation
        if len(conversation) <= max_history + 1:  # +1 for system message
            return conversation

        # Keep system message + last max_history messages
        system_msg = conversation[0] if conversation and conversation[0].get(
            'role') == 'system' else None
        recent_messages = conversation[-(max_history):] if system_msg else conversation[-max_history:]

        if system_msg:
            return [system_msg] + recent_messages
        return recent_messages

    def process_with_llm(self, user_input: str) -> str:
        """Process user input with LLM using professional agent loop."""
        # Mistral raw mode format for proper tool calling
        system_prompt = f"""[AVAILABLE_TOOLS] {json.dumps(self.tools)}[/AVAILABLE_TOOLS]

You are RIO, a desktop companion robot. You MUST use speak_text for every response - this is voice-only.

RESPONSE FORMAT: Return ONLY a JSON array of tool calls. Do not include any other text.

MOVEMENT RULES:
- For forward/backward movement: use linear_x (-{self.max_linear_speed} to {self.max_linear_speed} m/s)
- For rotation while moving: use angular_z (-{self.max_angular_speed} to {self.max_angular_speed} rad/s)
- For in-place rotation (linear_x=0): use angular_z={self.inplace_rotation_speed} rad/s for faster turning

HEAD MOVEMENT RULES:
- Head pitch angle: 150-180 degrees ONLY
- 150° = head up (looking up)
- 165° = head front (neutral position)
- 180° = head down (looking down)
- NEVER use angles outside 150-180 range

CORRECT FORMAT:
[{{"name": "tool_name", "arguments": {{"param": "value"}}}}]

EXAMPLES:
- "turn on torch" → [{{"name": "speak_text", "arguments": {{"text": "Turning on torch"}}}}, {{"name": "set_torch", "arguments": {{"on": true}}}}, {{"name": "set_expression", "arguments": {{"expression": "happy"}}}}]
- "turn right" → [{{"name": "speak_text", "arguments": {{"text": "Turning right"}}}}, {{"name": "move_with_duration", "arguments": {{"linear_x": 0, "angular_z": {self.inplace_rotation_speed}, "duration": 0.5}}}}, {{"name": "set_expression", "arguments": {{"expression": "happy"}}}}]
- "move forward" → [{{"name": "speak_text", "arguments": {{"text": "Moving forward"}}}}, {{"name": "move_with_duration", "arguments": {{"linear_x": {self.max_linear_speed}, "angular_z": 0, "duration": 0.5}}}}, {{"name": "set_expression", "arguments": {{"expression": "happy"}}}}]
- "look up" → [{{"name": "speak_text", "arguments": {{"text": "Looking up"}}}}, {{"name": "control_head_pitch", "arguments": {{"angle": 150}}}}, {{"name": "set_expression", "arguments": {{"expression": "happy"}}}}]
- "look down" → [{{"name": "speak_text", "arguments": {{"text": "Looking down"}}}}, {{"name": "control_head_pitch", "arguments": {{"angle": 180}}}}, {{"name": "set_expression", "arguments": {{"expression": "happy"}}}}]

IMPORTANT: Return ONLY the JSON array. No explanations, no additional text."""

        # Add user input to conversation
        self.conversation_history.append(
            {"role": "user", "content": user_input})

        # Filter conversation history to prevent token accumulation
        filtered_conversation = self._filter_conversation_history(
            self.conversation_history)

        # Prepare messages for Ollama
        messages = [{"role": "system", "content": system_prompt}
                    ] + filtered_conversation

        max_iterations = 10
        for iteration in range(max_iterations):
            try:
                logger.info(
                    f"Agent iteration {iteration + 1}/{max_iterations}")

                # Debug: Log tools being sent
                logger.info(f"Sending {len(self.tools)} tools to Ollama")
                for tool in self.tools:
                    logger.info(
                        f"Tool: {tool['function']['name']} - {tool['function']['description']}")

                # Measure Ollama response time
                ollama_start_time = time.time()
                logger.info(f"Calling Ollama at {ollama_start_time:.3f}")

                # Call Ollama with tools (use raw mode for Mistral)
                if 'mistral' in self.model.lower():
                    # Use raw mode for Mistral - convert messages to single prompt
                    prompt = self._convert_messages_to_prompt(messages)
                    response = self.ollama_client.generate(
                        model=self.model,
                        prompt=prompt,
                        options={
                            'temperature': self.temperature,
                            'num_predict': self.max_tokens,
                            'raw': True
                        }
                    )
                else:
                    # Use standard tool calling for other models
                    response = self.ollama_client.chat(
                        model=self.model,
                        messages=messages,
                        tools=self.tools,
                        options={
                            'temperature': self.temperature,
                            'num_predict': self.max_tokens
                        }
                    )

                ollama_end_time = time.time()
                ollama_duration = ollama_end_time - ollama_start_time
                logger.info(
                    f"Ollama response received at {ollama_end_time:.3f}")
                logger.info(
                    f"Ollama response time: {ollama_duration:.3f} seconds")
                logger.info(f"Ollama Response: {response}")

                # Extract assistant message from Ollama response
                if 'mistral' in self.model.lower():
                    # Raw mode response format
                    content = response.get("response", "")
                    assistant_message = {
                        "role": "assistant",
                        "content": content
                    }
                else:
                    # Standard chat response format
                    content = response.get("message", {}).get("content", "")
                    assistant_message = {
                        "role": "assistant",
                        "content": content
                    }

                # Add assistant message to conversation
                self.conversation_history.append(assistant_message)
                messages.append(assistant_message)

                # Check for tool calls
                tool_calls = self._extract_tool_calls(response, content)

                # llama3.1:8b supports proper tool calling, so we should get tool_calls in response

                if not tool_calls:
                    # No tool calls - force tool usage for voice interaction
                    logger.info(
                        "No tool calls found - forcing speak_text tool for voice interaction")

                    # Use the content as-is for speech
                    clean_content = assistant_message['content'] or "I understand your request."

                    # Force a speak_text tool call
                    forced_tool_call = {
                        'function': {
                            'name': 'speak_text',
                            'arguments': {'text': clean_content or "I understand your request."}
                        }
                    }

                    logger.info(
                        f"Executing forced tool: speak_text with args: {forced_tool_call['function']['arguments']}")
                    result = self.execute_tool(
                        'speak_text', forced_tool_call['function']['arguments'])

                    return result

                # Execute tool calls
                tool_results = []
                speech_text = None
                biometric_success = None

                for tool_call in tool_calls:
                    tool_name = tool_call.get('function', {}).get('name', '')
                    tool_args = tool_call.get(
                        'function', {}).get('arguments', '{}')

                    if isinstance(tool_args, str):
                        tool_args = json.loads(tool_args)

                    # Handle empty tool name
                    if not tool_name:
                        logger.error(
                            f"Cannot execute tool with empty name and args: {tool_args}")
                        tool_results.append(f"Error: Tool name is empty")
                        continue

                    logger.info(
                        f"Executing tool: {tool_name} with args: {tool_args}")
                    result = self.execute_tool(tool_name, tool_args)
                    tool_results.append(result)

                    # Capture speech text from speak_text tool
                    if tool_name == 'speak_text' and 'text' in tool_args:
                        speech_text = tool_args['text']

                    # Check biometric authentication result
                    if tool_name == 'biometric_authentication':
                        # The execute_tool method returns a formatted string, so check the string content
                        if isinstance(result, str):
                            if 'successful' in result.lower():
                                biometric_success = True
                                logger.info(
                                    "Biometric authentication successful")
                            else:
                                biometric_success = False
                                logger.info("Biometric authentication failed")
                        else:
                            biometric_success = False
                            logger.info(
                                "Biometric authentication failed - unexpected result type")

                # If biometric authentication failed, inform user and stop
                if biometric_success is False:
                    logger.info(
                        "Biometric authentication failed - stopping execution")
                    return "Biometric authentication failed. Please try again."

                # If we have speech text from tool calls, return it and stop iterating
                if speech_text:
                    logger.info(f"Task completed with speech: {speech_text}")
                    return speech_text

                # Add tool results to conversation
                tool_message = {
                    "role": "tool",
                    "content": f"Tool execution results: {tool_results}"
                }
                self.conversation_history.append(tool_message)
                messages.append(tool_message)

            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}")
                return f"An error occurred: {str(e)}"

        return f"Completed {max_iterations} iterations without a final answer."

    def _extract_tool_calls(self, response, content=None):
        """Extract tool calls from Ollama response."""
        if content is None:
            # Fallback to extracting from response structure
            message = response.get("message", {})
            content = message.get("content", "")

        tool_calls = response.get("tool_calls", [])

        # Handle None case for tool_calls
        if tool_calls is None:
            tool_calls = []

        # If we have no tool_calls but we have content, try to parse Mistral's format
        if not tool_calls and content:
            import re
            logger.info(
                f"Attempting to parse tool calls from content: {content[:200]}...")

            # First try [TOOL_CALLS] format
            tool_calls_pattern = r'\[TOOL_CALLS\]\s*(\[.*?\])'
            match = re.search(tool_calls_pattern, content, re.DOTALL)

            if match:
                try:
                    # Parse the JSON array of tool calls
                    tool_calls_json = json.loads(match.group(1))
                    for tool_call in tool_calls_json:
                        if isinstance(tool_call, dict) and 'name' in tool_call and 'arguments' in tool_call:
                            tool_calls.append({
                                'function': {
                                    'name': tool_call['name'],
                                    'arguments': tool_call['arguments']
                                }
                            })
                            logger.info(
                                f"Parsed Mistral tool call: {tool_call['name']}")
                except json.JSONDecodeError as e:
                    logger.info(f"Could not parse Mistral tool calls: {e}")
                    logger.info(f"Raw content: {match.group(1)}")
            else:
                # Fallback: Try to parse direct JSON array format that Mistral is actually returning
                # Look for JSON array anywhere in the content
                json_array_pattern = r'\[.*?\]'
                matches = re.findall(json_array_pattern, content, re.DOTALL)

                # Try each JSON array found
                for json_str in matches:
                    try:
                        # Parse the JSON array of tool calls
                        tool_calls_json = json.loads(json_str)
                        if isinstance(tool_calls_json, list):
                            for tool_call in tool_calls_json:
                                if isinstance(tool_call, dict) and 'name' in tool_call and 'arguments' in tool_call:
                                    tool_calls.append({
                                        'function': {
                                            'name': tool_call['name'],
                                            'arguments': tool_call['arguments']
                                        }
                                    })
                                    logger.info(
                                        f"Parsed Mistral JSON array tool call: {tool_call['name']}")
                            # If we found valid tool calls, break
                            if tool_calls:
                                break
                    except json.JSONDecodeError as e:
                        logger.info(f"Could not parse JSON array: {e}")
                        continue

                if not tool_calls:
                    logger.info(
                        "No valid JSON array tool calls found in response")

        # Convert to standard format
        formatted_tool_calls = []
        for tool_call in tool_calls:
            if hasattr(tool_call, 'function'):
                formatted_tool_calls.append({
                    'function': {
                        'name': tool_call.function.name,
                        'arguments': tool_call.function.arguments
                    }
                })
            else:
                formatted_tool_calls.append(tool_call)

        return formatted_tool_calls

    def _convert_messages_to_prompt(self, messages):
        """Convert messages to a single prompt for raw mode."""
        prompt_parts = []
        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')

            if role == 'system':
                prompt_parts.append(content)
            elif role == 'user':
                prompt_parts.append(f"[INST] {content} [/INST]")
            elif role == 'assistant':
                prompt_parts.append(content)
            elif role == 'tool':
                prompt_parts.append(f"Tool result: {content}")

        return '\n\n'.join(prompt_parts)

    def cleanup(self):
        """Clean up resources."""
        # No MCP connection to clean up
        pass


class OllamaNode(Node):
    """
    Ollama Node for Desktop Companion Robot
    """

    def __init__(self):
        super().__init__('ollama_node')

        # Declare parameters
        self.declare_parameter('model', 'llama3-groq-tool-use:8b')
        self.declare_parameter('temperature', 0.7)
        self.declare_parameter('max_tokens', 256)
        self.declare_parameter('timeout', 30.0)
        self.declare_parameter('max_conversation_history', 2)

        # Robot movement parameters
        self.declare_parameter(
            'robot_movement.movement.max_linear_speed', 0.15)
        self.declare_parameter(
            'robot_movement.movement.max_angular_speed', 2.0)
        self.declare_parameter(
            'robot_movement.movement.inplace_rotation_speed', 7.0)
        self.declare_parameter('robot_movement.movement.default_duration', 0.5)

        # Get parameters
        self.model = self.get_parameter('model').value
        self.temperature = self.get_parameter('temperature').value
        self.max_tokens = self.get_parameter('max_tokens').value
        self.timeout = self.get_parameter('timeout').value
        self.max_conversation_history = self.get_parameter(
            'max_conversation_history').value

        # Robot movement parameters
        self.max_linear_speed = self.get_parameter(
            'robot_movement.movement.max_linear_speed').value
        self.max_angular_speed = self.get_parameter(
            'robot_movement.movement.max_angular_speed').value
        self.inplace_rotation_speed = self.get_parameter(
            'robot_movement.movement.inplace_rotation_speed').value
        self.default_duration = self.get_parameter(
            'robot_movement.movement.default_duration').value

        # Debug logging
        self.get_logger().info(f"Loaded movement parameters:")
        self.get_logger().info(f"  max_linear_speed: {self.max_linear_speed}")
        self.get_logger().info(
            f"  max_angular_speed: {self.max_angular_speed}")
        self.get_logger().info(
            f"  inplace_rotation_speed: {self.inplace_rotation_speed}")
        self.get_logger().info(f"  default_duration: {self.default_duration}")

        # No callback groups needed - single threaded processing

        # Speech recognition subscriber
        self.speech_subscription = self.create_subscription(
            String,
            '/speech_recognition/result',
            self.speech_callback,
            10
        )

        # Hotword detection subscriber
        self.hotword_subscription = self.create_subscription(
            Empty,
            '/speech_recognition/hotword_detected',
            self.hotword_callback,
            10
        )

        # Speech processing counter
        self.speech_count = 0

        # AI Agent
        self.agent = OllamaAgent(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            max_conversation_history=self.max_conversation_history,
            max_linear_speed=self.max_linear_speed,
            max_angular_speed=self.max_angular_speed,
            inplace_rotation_speed=self.inplace_rotation_speed
        )

        # No thread executor needed - direct processing

        # Create timers
        self.create_timer(5.0, self.heartbeat_callback)
        self.create_timer(15.0, self.check_subscriptions)

        self.get_logger().info(
            f'Ollama Node initialized with model: {self.model}')

    def speech_callback(self, msg: String):
        """Process speech recognition results"""
        self.get_logger().info(
            f'SPEECH CALLBACK TRIGGERED! Raw message: "{msg.data}"')
        self.get_logger().info(f'Callback timestamp: {time.time()}')
        self.get_logger().info(f'Previous speech count: {self.speech_count}')

        speech_text = msg.data.strip()
        if not speech_text:
            self.get_logger().warn('Empty speech text received')
            return

        self.speech_count += 1
        self.get_logger().info(
            f'=== SPEECH #{self.speech_count} RECOGNIZED: "{speech_text}" ===')
        self.get_logger().info(
            f'Speech callback is working! Count: {self.speech_count}')
        self.get_logger().info('Processing speech in main thread')

        # Process with AI Agent directly
        self.get_logger().info(
            f'Processing speech #{self.speech_count} with AI Agent...')
        try:
            # Measure total processing time
            processing_start_time = time.time()
            self.get_logger().info(
                f'Starting AI Agent processing for: "{speech_text}" at {processing_start_time:.3f}')

            # Process with AI Agent directly (no async)
            response = self.agent.process_with_llm(speech_text)

            processing_end_time = time.time()
            processing_duration = processing_end_time - processing_start_time

            self.get_logger().info(
                f'AI Agent processing completed: {response}')
            self.get_logger().info(
                f'Total processing time: {processing_duration:.3f} seconds')
            self.get_logger().info('Speech processing completed successfully')
            self.get_logger().info('Node is ready for next speech input')

        except Exception as e:
            self.get_logger().error(f'Error in AI Agent processing: {str(e)}')
            self.get_logger().error('Node may need restart to continue listening')

    def hotword_callback(self, msg: Empty):
        """Handle hotword detection"""
        self.get_logger().info('Hotword detected!')
        self.get_logger().info('Node is still listening for speech...')

    def check_subscriptions(self):
        """Check if subscriptions are active"""
        self.get_logger().info('Checking subscriptions:')
        self.get_logger().info(
            f'- Speech subscription active: {self.speech_subscription is not None}')
        self.get_logger().info(
            f'- Hotword subscription active: {self.hotword_subscription is not None}')

    def heartbeat_callback(self):
        """Heartbeat to show node is alive"""
        self.get_logger().info('Ollama Node heartbeat - still alive and listening')

    def cleanup(self):
        """Cleanup resources"""
        # Cleanup AI Agent
        if hasattr(self, 'agent'):
            self.agent.cleanup()


def main(args=None):
    rclpy.init(args=args)

    try:
        node = OllamaNode()

        # Log that we're ready to process speech
        node.get_logger().info(
            "Ollama Node ready to process speech! Listening for hotwords and speech recognition...")

        try:
            # Simple node spin - no executor
            rclpy.spin(node)

        except KeyboardInterrupt:
            node.get_logger().info("Keyboard interrupt received, shutting down...")
        finally:
            node.cleanup()
            node.destroy_node()
            rclpy.shutdown()

    except Exception as e:
        print(f"Error starting Ollama Node: {e}")


if __name__ == '__main__':
    main()
