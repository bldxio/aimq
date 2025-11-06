"""Plan-and-Execute Agent implementation."""

import logging
from operator import add
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, StateGraph

from aimq.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class PlanExecuteState(TypedDict):
    """State for plan-execute agent.

    Required fields must be present at initialization.
    NotRequired fields are optional.
    """

    input: str
    plan: list[str]
    current_step: int
    step_results: Annotated[list[dict], add]
    final_output: dict | None
    needs_replan: bool


class PlanExecuteAgent(BaseAgent):
    """
    Plan-and-Execute agent that creates a plan then executes steps sequentially.

    Pattern:
    1. Create execution plan
    2. Execute each step
    3. Collect results
    4. Replan if needed

    Implements:
    - Fix #11: Logger integration in all nodes

    Args:
        tools: List of LangChain tools
        system_prompt: Agent instructions
        llm: LLM model name
        temperature: LLM temperature
        memory: Enable checkpointing

    Example:
        from aimq.agents import PlanExecuteAgent
        from aimq.tools.supabase import ReadFile, WriteRecord

        agent = PlanExecuteAgent(
            tools=[ReadFile(), WriteRecord()],
            system_prompt="You are a task planner",
            memory=True
        )

        worker.assign(agent, queue="planner")
    """

    def _build_graph(self) -> StateGraph:
        """Build plan-execute graph."""
        graph = StateGraph(PlanExecuteState)

        graph.add_node("plan", self._plan_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("finalize", self._finalize_node)

        graph.add_edge("plan", "execute")
        graph.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "execute": "execute",
                "replan": "plan",
                "finalize": "finalize",
            },
        )
        graph.add_edge("finalize", END)

        graph.set_entry_point("plan")

        return graph

    def _plan_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Generate execution plan (Fix #11)."""
        from aimq.clients.mistral import get_mistral_client

        logger.info("Creating execution plan")  # Fix #11

        client = get_mistral_client()

        prompt = f"""{self.system_prompt}

Task: {state['input']}

Available tools: {self._format_tools()}

Create a step-by-step plan. Respond with a numbered list:
1. <step 1>
2. <step 2>
...
"""

        try:
            response = client.chat.completions.create(
                model=self.llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )

            # Parse plan
            steps = self._parse_plan(response.choices[0].message.content)

            logger.info(f"Plan created with {len(steps)} steps")  # Fix #11

            return {
                "plan": steps,
                "current_step": 0,
            }

        except Exception as e:
            logger.error(f"Planning failed: {e}", exc_info=True)  # Fix #11
            return {
                "plan": ["Error: Failed to create plan"],
                "current_step": 0,
            }

    def _execute_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Execute current step (Fix #11)."""
        current = state["plan"][state["current_step"]]

        logger.info(
            f"Executing step {state['current_step'] + 1}/{len(state['plan'])}: "
            f"{current[:50]}..."
        )  # Fix #11

        # Execute with tools (simplified)
        result = self._execute_step_with_tools(current)

        logger.debug(f"Step result: {result}")  # Fix #11

        return {
            "step_results": [
                {
                    "step": current,
                    "result": result,
                    "step_number": state["current_step"],
                }
            ],
            "current_step": state["current_step"] + 1,
        }

    def _finalize_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Compile final output (Fix #11)."""
        logger.info("Finalizing results")  # Fix #11

        return {
            "final_output": {
                "task": state["input"],
                "plan": state["plan"],
                "results": state["step_results"],
                "status": "completed",
            }
        }

    def _should_continue(self, state: PlanExecuteState) -> Literal["execute", "replan", "finalize"]:
        """Decide next step."""
        if state["current_step"] >= len(state["plan"]):
            return "finalize"
        if state.get("needs_replan"):
            return "replan"
        return "execute"

    def _format_tools(self) -> str:
        """Format tool descriptions."""
        return "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])

    def _parse_plan(self, content: str) -> list[str]:
        """Parse plan from LLM response."""
        lines = content.strip().split("\n")
        steps = []
        for line in lines:
            # Remove numbering (1., 2., etc.)
            if line.strip() and (line[0].isdigit() or line.strip()[0] in ["-", "*"]):
                step = line.split(".", 1)[-1].strip()
                if step:
                    steps.append(step)
        return steps

    def _execute_step_with_tools(self, step: str) -> str:
        """Execute a step using available tools (simplified).

        In production, this would:
        1. Parse step to identify needed tool
        2. Extract tool inputs
        3. Execute tool with validation
        4. Return result

        For now, this is a placeholder that returns a formatted message.
        """
        logger.debug(f"Executing step with tools: {step}")
        return f"Executed: {step}"
