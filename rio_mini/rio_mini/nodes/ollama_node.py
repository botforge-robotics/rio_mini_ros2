#!/usr/bin/env python3

"""
Ollama Node for Desktop Companion Robot

Professional AI Agent using native Ollama APIs with MCP server connection.
Based on best practices from modern AI agent architectures.
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import String, Bool, Empty
import json
import asyncio
import threading
import concurrent.futures
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
                 temperature: float = 0.7, max_tokens: int = 1024, max_conversation_history: int = 5):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_conversation_history = max_conversation_history
        self.conversation_history = []
        self.tools = get_robot_tools()

        # Initialize Ollama client
        self.ollama_client = ollama.Client()

        logger.info(f"OllamaAgent initialized with model: {model}")
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
        recent_messages = conversation[-(max_history)                                       :] if system_msg else conversation[-max_history:]

        if system_msg:
            return [system_msg] + recent_messages
        return recent_messages

    async def process_with_llm(self, user_input: str) -> str:
        """Process user input with LLM using professional agent loop."""
        system_prompt = """You are RIO, an intelligent desktop companion robot with voice interaction capabilities.

CRITICAL RULES FOR TOOL USAGE:
1. ALWAYS use proper JSON tool calling format - NEVER use text-based tool formats
2. MANDATORY: You MUST use speak_text tool for EVERY response - this is a VOICE-ONLY system
3. NEVER respond with plain text - the user can only hear your voice, not read text
4. If asked to do something (like "turn on torch"), BOTH perform the action AND speak about it
5. For natural language requests like "it's dark" or "I can't see", recognize implied intent and turn on torch
6. Match your expression to your speech content (happy speech = happy expression)
7. EVERY response must include speak_text - there is no other way to communicate with the user

TOOL INSTRUCTIONS - READ CAREFULLY:
- DO NOT respond with plain text in asterisks like: *speak_text("Hello")*
- DO NOT respond with JSON-formatted text like: {"name": "speak_text", "parameters": {"text": "Hello"}}
- DO NOT respond with function call format like: {speak_text("Hello")}
- DO NOT respond with any text that is not a proper tool call
- INSTEAD, use the proper native tool calling mechanism of the model
- REMEMBER: User can only hear your voice - you MUST use speak_text for every response

AVAILABLE TOOLS:
- speak_text - Make robot speak (MANDATORY for all responses)
  - parameters: {"text": "your speech text here"}

- set_torch - Turn torch on/off (Note: renamed from toggle_torch)
  - parameters: {"on": true} or {"on": false}
  - Use for phrases like "turn on torch", "it's dark", "I can't see", etc.

- move_robot - Move the robot
  - parameters: {"linear_x": float, "linear_y": float, "angular_z": float}

- set_expression - Set facial expression
  - parameters: {"expression": "happy"|"sad"|"neutral"|"surprised"|"thinking"}

- set_led_color - Set LED color
  - parameters: {"color": "red"|"green"|"blue"|"yellow"|"purple"|"cyan"|"white"|"off"}

- control_head_pitch - Control head movement
  - parameters: {"angle": integer} (-30 to 30 degrees)

- enable_camera - Enable/disable camera
  - parameters: {"enable": true} or {"enable": false}

- biometric_authentication - Perform biometric authentication using biometric sensors (fingerprint, face, etc.)
  - parameters: {"message": "optional message to display during authentication"}
  - Returns success/failure status

EXAMPLES OF USER REQUESTS AND HOW TO HANDLE THEM:
1. User says: "turn on torch" or "it's dark here" or "I can't see"
   - MUST call: speak_text, set_torch (on=true), and set_expression tools
   - Example: speak_text("I'll turn on the torch"), set_torch(on=true), set_expression("happy")

2. User says: "turn off torch" or "it's too bright"
   - MUST call: speak_text, set_torch (on=false), and set_expression tools
   - Example: speak_text("I'll turn off the torch"), set_torch(on=false), set_expression("neutral")

3. User says: "see you later and turn off the torch"
   - MUST call: speak_text, set_torch (on=false), and set_expression tools
   - Example: speak_text("See you later! I'll turn off the torch"), set_torch(on=false), set_expression("sad")

4. User says: "good morning" or general greeting
   - Respond by calling speak_text and set_expression tools

5. User says: "turn on torch but before please authenticate with biometric"
   - FIRST: Call speak_text to ask for biometric authentication
   - THEN: Call biometric_authentication tool
   - ONLY AFTER biometric success: Call set_torch and other requested actions

CRITICAL ACTION WORKFLOW:
- When user requests an action (like "turn off torch"), you MUST:
  1. Call speak_text to inform user what you're doing
  2. Call the actual action tool (set_torch, move_robot, etc.)
  3. Call set_expression to match the action
  4. NEVER just speak without performing the action

CRITICAL BIOMETRIC WORKFLOW:
- If user requests biometric authentication, you MUST:
  1. First ask user to perform authentication (speak_text)
  2. Call biometric_authentication tool with appropriate message
  3. Wait for biometric_authentication result
  4. ONLY if authentication succeeds, proceed with other requested actions
  5. If authentication fails, inform user and do NOT proceed with other actions

IMPORTANT: Use ONLY native tool calling format. NEVER respond with JSON text like:
- {"name": "tool_name", "parameters": {...}}
- Any text-based tool call formats
- Always use the proper native tool calling mechanism

CRITICAL COMMUNICATION RULE:
- This is a VOICE-ONLY system - the user cannot see any text
- You MUST use speak_text tool for EVERY response - there is no other way to communicate
- NEVER respond with plain text, JSON, or any format that is not a proper tool call
- If you don't use speak_text, the user will hear nothing
- Every single response must include speak_text - this is mandatory

Use only the native JSON tool format that is built into the model architecture."""

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

                # Call Ollama with tools
                response = self.ollama_client.chat(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    options={
                        'temperature': self.temperature,
                        'num_predict': self.max_tokens
                    }
                )

                logger.info(f"Ollama Response: {response}")

                # Extract assistant message from Ollama response
                # Ollama returns a dict with message field containing role and content
                content = response.get("message", {}).get("content", "")
                assistant_message = {
                    "role": "assistant",
                    "content": content
                }

                # Add assistant message to conversation
                self.conversation_history.append(assistant_message)
                messages.append(assistant_message)

                # Check for tool calls
                tool_calls = self._extract_tool_calls(response)

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

    def _extract_tool_calls(self, response):
        """Extract tool calls from Ollama response."""
        # Ollama returns tool_calls in the message field
        # Format: response["message"]["tool_calls"]
        message = response.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        # Handle None case for tool_calls
        if tool_calls is None:
            tool_calls = []

        # If we have no tool_calls but we have content, try to parse it as JSON tool call
        if not tool_calls and content:
            # Check for multiple JSON objects separated by newlines
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        # Try to parse as JSON
                        json_content = json.loads(line)
                        if isinstance(json_content, dict) and 'name' in json_content and 'parameters' in json_content:
                            # Format as a tool call
                            tool_calls.append({
                                'function': {
                                    'name': json_content['name'],
                                    'arguments': json_content['parameters']
                                }
                            })
                            logger.info(
                                f"Parsed JSON content as tool call: {json_content['name']}")
                    except json.JSONDecodeError:
                        logger.info(f"Line is not valid JSON: {line}")

            # Also check for function call format like: speak_text({"text": "message"})
            import re
            function_call_pattern = r'(\w+)\(\{([^}]+)\}\)'
            matches = re.findall(function_call_pattern, content)
            for func_name, args_str in matches:
                try:
                    # Try to parse the arguments as JSON
                    args_dict = json.loads('{' + args_str + '}')
                    tool_calls.append({
                        'function': {
                            'name': func_name,
                            'arguments': args_dict
                        }
                    })
                    logger.info(f"Parsed function call format: {func_name}")
                except json.JSONDecodeError:
                    logger.info(
                        f"Could not parse function call arguments: {args_str}")

            # Check for curly brace format like: {speak_text("message")}
            curly_brace_pattern = r'\{(\w+)\(\"([^"]+)\"\)\}'
            curly_matches = re.findall(curly_brace_pattern, content)
            for func_name, message in curly_matches:
                tool_calls.append({
                    'function': {
                        'name': func_name,
                        'arguments': {'text': message}
                    }
                })
                logger.info(
                    f"Parsed curly brace format: {func_name} with message: {message}")

            # Check for simple function call format like: speak_text("message")
            simple_function_pattern = r'(\w+)\(\"([^"]+)\"\)'
            simple_matches = re.findall(simple_function_pattern, content)
            for func_name, message in simple_matches:
                tool_calls.append({
                    'function': {
                        'name': func_name,
                        'arguments': {'text': message}
                    }
                })
                logger.info(
                    f"Parsed simple function format: {func_name} with message: {message}")

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
        self.declare_parameter('max_tokens', 1024)
        self.declare_parameter('timeout', 30.0)
        self.declare_parameter('max_conversation_history', 5)

        # Get parameters
        self.model = self.get_parameter('model').value
        self.temperature = self.get_parameter('temperature').value
        self.max_tokens = self.get_parameter('max_tokens').value
        self.timeout = self.get_parameter('timeout').value
        self.max_conversation_history = self.get_parameter(
            'max_conversation_history').value

        # Callback group for concurrent operations
        self.callback_group = ReentrantCallbackGroup()

        # Speech recognition subscriber
        self.speech_subscription = self.create_subscription(
            String,
            '/speech_recognition/result',
            self.speech_callback,
            10,
            callback_group=self.callback_group
        )

        # Hotword detection subscriber
        self.hotword_subscription = self.create_subscription(
            Empty,
            '/speech_recognition/hotword_detected',
            self.hotword_callback,
            10,
            callback_group=self.callback_group
        )

        # Speech processing counter
        self.speech_count = 0

        # AI Agent
        self.agent = OllamaAgent(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            max_conversation_history=self.max_conversation_history
        )

        # Thread executor for async operations
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=2)

        # Create timers
        self.create_timer(5.0, self.heartbeat_callback,
                          callback_group=self.callback_group)
        self.create_timer(15.0, self.check_subscriptions,
                          callback_group=self.callback_group)

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
        self.get_logger().info(
            f'ROS2 callback thread: {threading.current_thread().name}')

        # Process with AI Agent using thread executor
        self.get_logger().info(
            f'Processing speech #{self.speech_count} with AI Agent...')
        try:
            # Submit to thread executor to avoid blocking ROS2 callbacks
            future = self.thread_executor.submit(
                self._run_async_speech_processing, speech_text)
            future.add_done_callback(self._speech_processing_done)
            self.get_logger().info(
                f'Speech #{self.speech_count} processing submitted to thread executor')
        except Exception as e:
            self.get_logger().error(
                f'Error submitting speech processing: {str(e)}')

    def _run_async_speech_processing(self, speech_text: str):
        """Run async speech processing in a separate thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self._process_speech_with_agent(speech_text))
        except Exception as e:
            self.get_logger().error(
                f'Error in async speech processing: {str(e)}')
        finally:
            loop.close()

    async def _process_speech_with_agent(self, speech_text: str):
        """Process speech with AI Agent"""
        try:
            self.get_logger().info(
                f'Starting AI Agent processing for: "{speech_text}"')

            # Process with AI Agent
            response = await self.agent.process_with_llm(speech_text)

            self.get_logger().info(
                f'AI Agent processing completed: {response}')

        except Exception as e:
            self.get_logger().error(f'Error in AI Agent processing: {str(e)}')

    def _speech_processing_done(self, future):
        """Callback when speech processing is complete"""
        try:
            result = future.result()
            self.get_logger().info('Speech processing completed successfully')
            self.get_logger().info('Node is ready for next speech input')
            self.get_logger().info(
                f'Completion callback thread: {threading.current_thread().name}')
        except Exception as e:
            self.get_logger().error(f'Speech processing failed: {str(e)}')
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

        # Shutdown thread executor
        if hasattr(self, 'thread_executor'):
            self.thread_executor.shutdown(wait=True)


def main(args=None):
    rclpy.init(args=args)

    try:
        node = OllamaNode()

        # Use MultiThreadedExecutor with more threads for concurrent operations
        executor = MultiThreadedExecutor(num_threads=4)
        executor.add_node(node)

        # Log that we're ready to process speech
        node.get_logger().info(
            "Ollama Node ready to process speech! Listening for hotwords and speech recognition...")

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
            node.cleanup()
            executor.shutdown()
            node.destroy_node()
            rclpy.shutdown()

    except Exception as e:
        print(f"Error starting Ollama Node: {e}")


if __name__ == '__main__':
    main()
