"""Multi-agent collaboration workflow."""

import logging
from typing import Callable, Dict

from langgraph.graph import END, StateGraph

from aimq.langgraph.states import AgentState
from aimq.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class MultiAgentWorkflow(BaseWorkflow):
    """
    Multi-agent collaboration with supervisor pattern.

    Pattern:
    1. Supervisor assigns work to specialized agents
    2. Each agent completes their portion
    3. Supervisor coordinates and decides next steps
    4. Process continues until task complete

    Args:
        agents: Dict of agent_name -> agent_function
        supervisor_llm: LLM for supervisor decisions
        checkpointer: Enable state persistence

    Example:
        from aimq.workflows import MultiAgentWorkflow

        workflow = MultiAgentWorkflow(
            agents={
                "researcher": researcher_func,
                "analyst": analyst_func,
                "writer": writer_func,
            },
            supervisor_llm="mistral-large-latest",
            checkpointer=True
        )

        worker.assign(workflow, queue="multi-agent")
    """

    def __init__(
        self,
        agents: Dict[str, Callable],
        supervisor_llm: str = "mistral-large-latest",
        checkpointer: bool = False,
    ):
        """Initialize multi-agent workflow.

        Args:
            agents: Dictionary mapping agent names to agent functions
            supervisor_llm: Model name for supervisor LLM
            checkpointer: Enable state persistence
        """
        self.agents = agents
        self.supervisor_llm = supervisor_llm
        super().__init__(checkpointer=checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build multi-agent graph.

        Returns:
            StateGraph with supervisor and agent nodes
        """
        graph = StateGraph(AgentState)

        # Add supervisor
        graph.add_node("supervisor", self._supervisor_node)

        # Add agent nodes
        for agent_name, agent_func in self.agents.items():
            graph.add_node(agent_name, agent_func)
            # Each agent reports back to supervisor
            graph.add_edge(agent_name, "supervisor")

        # Supervisor routes to agents or ends
        graph.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {**{name: name for name in self.agents.keys()}, "end": END},
        )

        graph.set_entry_point("supervisor")

        return graph

    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor decides which agent to invoke (Fix #11 - Logger integration).

        Args:
            state: Current agent state

        Returns:
            Updated state with next agent decision
        """
        from aimq.clients.mistral import get_mistral_client

        logger.info(f"Supervisor coordinating (iteration {state['iteration']})")

        client = get_mistral_client()

        # Build coordination prompt
        prompt = self._build_supervisor_prompt(state)

        try:
            response = client.chat.completions.create(
                model=self.supervisor_llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            next_agent = response.choices[0].message.content.strip().lower()

            logger.info(f"Supervisor routing to: {next_agent}")

            return {
                "messages": [{"role": "supervisor", "content": f"Routing to: {next_agent}"}],
                "current_tool": next_agent,  # Reuse field for next agent
                "iteration": state["iteration"] + 1,
            }

        except Exception as e:
            logger.error(f"Supervisor failed: {e}", exc_info=True)
            return {
                "errors": [f"Supervisor error: {str(e)}"],
                "iteration": state["iteration"] + 1,
            }

    def _route_to_agent(self, state: AgentState) -> str:
        """Route to next agent.

        Args:
            state: Current agent state

        Returns:
            Next agent name or "end"
        """
        next_agent = state.get("current_tool", "end")

        # Safety: prevent infinite loops
        if state["iteration"] >= 20:
            logger.warning("Max iterations reached, ending workflow")
            return "end"

        logger.debug(f"Routing to agent: {next_agent}")
        return next_agent

    def _build_supervisor_prompt(self, state: AgentState) -> str:
        """Build supervisor coordination prompt.

        Args:
            state: Current agent state

        Returns:
            Prompt for supervisor LLM
        """
        agent_list = ", ".join(self.agents.keys())

        return f"""You are coordinating a team of agents.

Available agents: {agent_list}

Task progress:
{self._format_progress(state)}

Which agent should work next? Respond with just the agent name, or "end" if complete.
"""

    def _format_progress(self, state: AgentState) -> str:
        """Format task progress from state.

        Args:
            state: Current agent state

        Returns:
            Formatted progress string
        """
        messages = state.get("messages", [])
        return "\n".join(
            [
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..."
                for msg in messages[-5:]  # Last 5 messages
            ]
        )
