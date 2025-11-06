"""ReAct (Reasoning + Acting) Agent implementation."""

import json
import logging
from typing import Literal

from langchain.tools import BaseTool
from langgraph.graph import END, StateGraph

from aimq.agents.base import BaseAgent
from aimq.langgraph.exceptions import ToolValidationError
from aimq.langgraph.states import AgentState
from aimq.langgraph.validation import ToolInputValidator

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """
    ReAct agent that reasons about actions and executes tools iteratively.

    Pattern:
    1. Reason about what to do
    2. Execute tool if needed
    3. Observe results
    4. Repeat until done

    Implements:
    - Fix #11: Logger integration in all nodes
    - Fix #12: Tool input validation with ToolInputValidator

    Args:
        tools: List of LangChain tools the agent can use
        system_prompt: Agent instructions
        llm: LLM model name (default: "mistral-large-latest")
        temperature: LLM temperature (default: 0.1)
        memory: Enable conversation memory (default: False)
        max_iterations: Max reasoning loops (default: 10)

    Example:
        from aimq.agents import ReActAgent
        from aimq.tools.supabase import ReadFile
        from aimq.tools.ocr import ImageOCR

        agent = ReActAgent(
            tools=[ReadFile(), ImageOCR()],
            system_prompt="You are a document assistant",
            memory=True
        )

        worker.assign(agent, queue="doc-agent")
    """

    def __init__(
        self,
        tools: list[BaseTool],
        system_prompt: str = "You are a helpful AI assistant.",
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
        max_iterations: int = 10,
    ):
        """Initialize ReActAgent with tool validation."""
        self.max_iterations = max_iterations
        self.validator = ToolInputValidator()  # Fix #12
        super().__init__(tools, system_prompt, llm, temperature, memory)

    def _build_graph(self) -> StateGraph:
        """Build ReAct agent graph."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("reason", self._reasoning_node)
        graph.add_node("act", self._action_node)

        # Add conditional routing
        graph.add_conditional_edges(
            "reason",
            self._should_continue,
            {
                "act": "act",
                "reason": "reason",
                "end": END,
            },
        )

        # After action, go back to reasoning
        graph.add_edge("act", "reason")

        # Start with reasoning
        graph.set_entry_point("reason")

        return graph

    def _reasoning_node(self, state: AgentState) -> AgentState:
        """Reasoning node: decide what to do next (Fix #11)."""
        from aimq.clients.mistral import get_mistral_client

        logger.info(f"ReAct reasoning step {state['iteration']}")  # Fix #11

        client = get_mistral_client()

        # Build ReAct prompt
        prompt = self._build_react_prompt(state)

        try:
            # Get LLM decision
            response = client.chat.completions.create(
                model=self.llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )

            # Parse action from response
            action = self._parse_action(response.choices[0].message.content)

            logger.debug(f"Reasoning result: {action}")  # Fix #11

            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": response.choices[0].message.content,
                    }
                ],
                "current_tool": action.get("tool"),
                "tool_input": action.get("input"),
                "final_answer": action.get("answer"),
                "iteration": state["iteration"] + 1,
            }

        except Exception as e:
            logger.error(f"Reasoning failed: {e}", exc_info=True)  # Fix #11
            return {
                "errors": [f"Reasoning error: {str(e)}"],
                "iteration": state["iteration"] + 1,
            }

    def _action_node(self, state: AgentState) -> AgentState:
        """Action node: execute the chosen tool with validation (Fix #11, #12)."""
        tool_name = state.get("current_tool")
        tool_input = state.get("tool_input", {})

        logger.info(f"Executing tool: {tool_name}")  # Fix #11

        # Find tool
        tool = next((t for t in self.tools if t.name == tool_name), None)

        if not tool:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)  # Fix #11
            return {
                "messages": [{"role": "system", "content": error_msg}],
                "tool_output": error_msg,
                "errors": [error_msg],
            }

        # Validate tool input (Fix #12)
        try:
            validated_input = self.validator.validate(tool, tool_input)
            logger.debug(f"Tool input validated: {validated_input}")  # Fix #11
        except ToolValidationError as e:
            logger.error(f"Tool validation failed: {e}")  # Fix #11
            return {
                "messages": [{"role": "system", "content": str(e)}],
                "tool_output": str(e),
                "errors": [str(e)],
            }

        # Execute tool
        try:
            result = tool.invoke(validated_input)
            logger.info(f"Tool execution successful: {tool_name}")  # Fix #11
            return {
                "messages": [{"role": "system", "content": f"Tool result: {result}"}],
                "tool_output": str(result),
            }
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)  # Fix #11
            return {
                "messages": [{"role": "system", "content": error_msg}],
                "tool_output": error_msg,
                "errors": [str(e)],
            }

    def _should_continue(self, state: AgentState) -> Literal["act", "reason", "end"]:
        """Decide next step based on state."""
        # Stop if we have an answer or hit max iterations
        if state.get("final_answer") or state["iteration"] >= self.max_iterations:
            if state["iteration"] >= self.max_iterations:
                logger.warning(f"Max iterations reached: {self.max_iterations}")  # Fix #11
            return "end"

        # Execute tool if one was chosen
        if state.get("current_tool"):
            return "act"

        # Continue reasoning
        return "reason"

    def _build_react_prompt(self, state: AgentState) -> str:
        """Build ReAct prompt with history."""
        system = f"""{self.system_prompt}

You have access to these tools:
{self._format_tools()}

Respond in this format:
THOUGHT: <your reasoning>
ACTION: <tool_name>
INPUT: <tool input as JSON>

OR if you have the final answer:
THOUGHT: <your reasoning>
ANSWER: <final answer>
"""

        history = "\n\n".join(
            [
                f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}"
                for msg in state.get("messages", [])
            ]
        )

        return f"{system}\n\n{history}"

    def _format_tools(self) -> str:
        """Format tool descriptions."""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])

    def _parse_action(self, content: str) -> dict:
        """Parse LLM response into action dict."""
        lines = content.strip().split("\n")
        action = {}

        for line in lines:
            if line.startswith("ACTION:"):
                action["tool"] = line.replace("ACTION:", "").strip()
            elif line.startswith("INPUT:"):
                try:
                    action["input"] = json.loads(line.replace("INPUT:", "").strip())
                except json.JSONDecodeError:
                    action["input"] = {}
            elif line.startswith("ANSWER:"):
                action["answer"] = line.replace("ANSWER:", "").strip()

        return action
