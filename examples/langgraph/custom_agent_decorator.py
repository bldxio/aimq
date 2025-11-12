"""
Example: Creating custom agent with @agent decorator

Demonstrates how to define a custom agent using the decorator pattern.

The @agent decorator provides:
- Automatic tool integration
- LLM configuration
- Memory/checkpointing setup
- Access to agent configuration in nodes

This example shows a data processing agent that:
1. Reads data files from storage
2. Analyzes content using LLM
3. Stores structured results in database

Usage:
    # Terminal 1: Start worker
    uv run python examples/langgraph/custom_agent_decorator.py

    # Terminal 2: Send test job
    aimq send data-processor '{
      "messages": [
        {"role": "user", "content": "data/sales_report.csv"}
      ],
      "tools": [],
      "iteration": 0,
      "errors": []
    }'
"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph

from aimq.langgraph import agent
from aimq.tools.supabase import WriteRecord
from aimq.worker import Worker


# Define custom agent using decorator
@agent(
    tools=[WriteRecord()],  # Only need WriteRecord for storing results
    system_prompt="""You are a data processing specialist.
    Your job is to analyze data files and extract key insights.

    For CSV files:
    - Identify column structure
    - Summarize data trends
    - Flag any anomalies

    For JSON files:
    - Parse structure
    - Validate schema
    - Extract important fields

    Provide clear, actionable analysis.""",
    llm="mistral-large-latest",
    temperature=0.2,  # Slight creativity for analysis
    memory=True,  # Enable resumable workflows
)
def data_processor_agent(graph: StateGraph, config: dict) -> StateGraph:  # noqa: C901
    """
    Custom agent that processes data files and stores results.

    The config dict contains:
    - tools: List[BaseTool] - Available tools
    - system_prompt: str - Agent instructions
    - llm: str - LLM model name
    - temperature: float - LLM temperature
    - memory: bool - Whether checkpointing is enabled
    - max_iterations: int - Maximum iterations

    The graph parameter is a pre-initialized StateGraph with AgentState.
    """

    def read_and_analyze(state):
        """Read file and analyze data with LLM."""
        # Extract file path from user message
        messages = state.get("messages", [])
        if not messages:
            return {
                "errors": ["No messages provided"],
                "iteration": state.get("iteration", 0) + 1,
            }

        # Get the latest user message content (handle both dict and HumanMessage)
        user_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_message = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "user":
                user_message = msg.get("content")
                break

        if not user_message:
            return {
                "errors": ["No user message found"],
                "iteration": state.get("iteration", 0) + 1,
            }

        file_path = user_message

        # Read file from local filesystem
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except FileNotFoundError as e:
            raise RuntimeError(f"File not found: {file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {str(e)}") from e

        # Analyze with LLM (use the configured LangChain ChatMistralAI from config)
        try:
            from langchain_core.messages import HumanMessage as LCHumanMessage
            from langchain_core.messages import SystemMessage

            llm = config["llm"]  # This is a LangChain ChatMistralAI object
            messages = [
                SystemMessage(content=config["system_prompt"]),
                LCHumanMessage(
                    content=f"Analyze this data file:\n\nPath: {file_path}\n\nContent:\n{content}"
                ),
            ]

            response = llm.invoke(messages)
            analysis = response.content

            return {
                "messages": [AIMessage(content=analysis)],
                "tool_output": analysis,
                "iteration": state.get("iteration", 0) + 1,
            }
        except Exception as e:
            raise RuntimeError(f"LLM analysis failed: {str(e)}") from e

    def store_results(state):
        """Store analysis results in database."""
        analysis = state.get("tool_output")
        if not analysis:
            raise RuntimeError("No analysis to store - previous step failed")

        # Get write tool from config
        write_tool = next((t for t in config["tools"] if t.name == "write_record"), None)
        if not write_tool:
            raise RuntimeError("WriteRecord tool not available in config")

        # Store results
        try:
            # Extract source file from first message (handle both dict and HumanMessage)
            source_file = "unknown"
            if state.get("messages"):
                first_msg = state["messages"][0]
                if isinstance(first_msg, dict):
                    source_file = first_msg.get("content", "unknown")
                elif hasattr(first_msg, "content"):
                    source_file = first_msg.content

            write_tool.invoke(
                {
                    "table": "analysis_results",
                    "data": {
                        "analysis": analysis,
                        "source_file": source_file,
                        "processed_at": "NOW()",
                    },
                }
            )

            return {
                "final_answer": f"Analysis complete and stored successfully.\n\n{analysis}",
                "iteration": state.get("iteration", 0) + 1,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to store results: {str(e)}") from e

    # Build graph
    # The decorator provides a StateGraph pre-configured with AgentState
    graph.add_node("analyze", read_and_analyze)
    graph.add_node("store", store_results)

    # Define edges
    graph.add_edge("analyze", "store")
    graph.add_edge("store", END)

    # Set entry point
    graph.set_entry_point("analyze")

    return graph


# Use the custom agent
worker = Worker()
agent_instance = data_processor_agent()
worker.assign(agent_instance, queue="data-processor", timeout=600, delete_on_finish=False)

if __name__ == "__main__":
    from pathlib import Path

    motd_path = Path(__file__).parent / "custom_agent_decorator_MOTD.md"
    worker.start(motd=str(motd_path), show_info=True)
