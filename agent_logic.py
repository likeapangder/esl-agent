"""
Agent Logic Module
Contains the LLM interaction logic using Anthropic API or Google Gemini API with enforced diagnostic reasoning.
"""
import os
from typing import Dict, Any, Optional, List
import anthropic
from anthropic.types import ToolUseBlock, TextBlock

try:
    import google.generativeai as genai
    from google.generativeai.types import content_types
    from collections.abc import Iterable
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


# System prompt that enforces the diagnostic phase
SYSTEM_PROMPT = """You are an expert ESL (English as a Second Language) teacher and collaborative co-pilot for lesson planning.

**ROLE & OBJECTIVE:**
Your goal is to work collaboratively with the user to design personalized lesson plans. You are NOT just a content generator; you are a pedagogical consultant.

**CRITICAL RULES:**

1. **INITIAL DIAGNOSIS:**
   - Always call `get_student_profile` first to understand the student.
   - Analyze their weaknesses, goals, and CEFR level.

2. **TOOL USE RESTRICTION:**
   - **DO NOT** call the `save_lesson_plan` tool until the user explicitly issues the 'finalize' command or directly asks to save the plan.
   - Until then, just discuss and refine the content.

3. **COLLABORATIVE PLANNING (The Co-Pilot Phase):**
   - **DO NOT generate the full lesson plan immediately.**
   - Instead, propose a strategy or topic based on the profile.
   - **ASK clarifying questions** to the user. Example: "Given Alice's struggle with past tense, should we focus on a storytelling activity or a formal grammar review?" or "Do you have a specific article in mind, or should I suggest one about travel?"
   - Refine the plan based on user feedback.

3. **STRICT STRUCTURE ENFORCEMENT:**
   - Only when the user confirms the direction or says "Go ahead", generate the final plan.
   - The final lesson plan **MUST** strictly follow this 4-part structure:
     1. **Small Talk Practice**: 5-10 mins of casual conversation warm-up.
     2. **Warm-up Questions**: 3-5 specific questions related to the main topic to activate schema.
     3. **Listen and Read Article**: A short, level-appropriate text (150-300 words) with key vocabulary highlighted.
     4. **Post-discussion Questions**: Deep comprehension and critical thinking questions about the article.

4. **FORMATTING:**
   - Use clear Markdown headings for the final plan.
   - Present the "Listen and Read Article" clearly.
   - Ensure questions are open-ended to encourage speaking.

**INTERACTION FLOW:**
- **User:** "Plan a lesson for Bob."
- **You:** (Load profile) "I see Bob is B1 and likes technology. Since he struggled with conditionals last time, maybe we can discuss 'The Future of AI'? We could use the second conditional to talk about hypothetical future scenarios. What do you think?"
- **User:** "Sounds good, but keep it simple."
- **You:** "Understood. I'll focus on simple 'If... would' structures. Shall I include a specific vocabulary list?"
- ... (Iterate until agreed) ...
- **You:** (Generates Final Plan with the 4 sections)

Remember: Be helpful, inquisitive, and structured.
"""


class ESLAgent:
    """Agentic ESL lesson planner with diagnostic reasoning."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "anthropic"):
        """
        Initialize the ESL Agent.

        Args:
            api_key: API key for the chosen provider
            provider: "anthropic" or "google"
        """
        self.provider = provider
        self.conversation_history = []

        if self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        elif self.provider == "google":
            if not HAS_GOOGLE:
                raise ImportError("google-generativeai package is not installed. Please install it to use Google provider.")

            genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
            # For Gemini, we don't store a client object the same way, we create GenerativeModel instances
            self.gemini_chat_session = None
            self.gemini_history = []
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _get_tools(self):
        """Define the tools available to the agent (Anthropic schema)."""
        return [
            {
                "name": "get_student_profile",
                "description": "Loads a student's profile from local storage. This MUST be called before generating any lesson plan. Returns the student's CEFR level, interests, weaknesses, last lesson, and goals.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The student's name (case-insensitive)"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "save_lesson_plan",
                "description": "Saves the generated markdown lesson plan to a local file in the plans/ directory with a timestamp.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "student_name": {
                            "type": "string",
                            "description": "The student's name"
                        },
                        "content": {
                            "type": "string",
                            "description": "The markdown content of the lesson plan"
                        }
                    },
                    "required": ["student_name", "content"]
                }
            }
        ]

    def start_chat(self, student_name: str):
        """
        Initialize a new chat session for a student.

        Args:
            student_name: The name of the student to start a session for.
        """
        self.conversation_history = []
        self.gemini_chat_session = None
        self.gemini_history = []

    def chat(self, user_message: str, data_manager, max_iterations: int = 5) -> str:
        """
        Interact with the agent in a conversational loop.

        Args:
            user_message: The user's input message
            data_manager: DataManager instance for accessing profiles
            max_iterations: Maximum number of agent iterations per turn

        Returns:
            The agent's text response
        """
        if self.provider == "anthropic":
            return self._chat_anthropic(user_message, data_manager, max_iterations)
        elif self.provider == "google":
            return self._chat_gemini(user_message, data_manager)
        return "Error: Unknown provider"

    def _chat_gemini(self, user_message: str, data_manager) -> str:
        """Handle chat interaction using Google Gemini."""
        if not self.gemini_chat_session:
            # Create tools list with bound methods
            tools = [
                data_manager.get_student_profile,
                data_manager.save_lesson_plan
            ]

            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro-latest',
                tools=tools,
                system_instruction=SYSTEM_PROMPT
            )

            # Initialize chat with history if needed, though for now we rely on the session object
            self.gemini_chat_session = model.start_chat(
                enable_automatic_function_calling=True,
                history=self.gemini_history
            )

        try:
            # Send message - Gemini handles tool calling loop automatically with enable_automatic_function_calling=True
            response = self.gemini_chat_session.send_message(user_message)
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

    def _chat_anthropic(self, user_message: str, data_manager, max_iterations: int = 5) -> str:
        """Handle chat interaction using Anthropic Claude."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        iteration = 0
        final_response = ""

        while iteration < max_iterations:
            iteration += 1

            # Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250514",
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                tools=self._get_tools(),
                messages=self.conversation_history
            )

            # Check if we need to process tool calls
            if response.stop_reason == "tool_use":
                # Extract tool calls and text
                assistant_content = []
                tool_uses = []

                for block in response.content:
                    if isinstance(block, ToolUseBlock):
                        tool_uses.append(block)
                        assistant_content.append(block)
                    elif isinstance(block, TextBlock):
                        assistant_content.append(block)

                # Add assistant's response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content
                })

                # Process tool calls
                tool_results = []
                for tool_use in tool_uses:
                    if tool_use.name == "get_student_profile":
                        name = tool_use.input["name"]
                        profile = data_manager.get_student_profile(name)

                        if profile:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": str(profile)
                            })
                        else:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "is_error": True,
                                "content": f"Student profile not found: {name}"
                            })

                    elif tool_use.name == "save_lesson_plan":
                        student_name = tool_use.input["student_name"]
                        content = tool_use.input["content"]
                        result = data_manager.save_lesson_plan(student_name, content)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": result
                        })

                # Add tool results to conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })

            elif response.stop_reason == "end_turn":
                # Agent finished - extract final text
                for block in response.content:
                    if isinstance(block, TextBlock):
                        final_response += block.text

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })

                break
            else:
                # Unexpected stop reason
                break

        return final_response if final_response else "Error: Could not generate response."
