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
from aimq.tools.supabase import ReadFile, WriteRecord
from aimq.worker import Worker


# Define custom agent using decorator
@agent(
    tools=[ReadFile(), WriteRecord()],
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
        from aimq.clients.mistral import get_mistral_client

        # Extract file path from user message
        messages = state.get("messages", [])
        if not messages:
            return {
                "errors": ["No messages provided"],
                "iteration": state.get("iteration", 0) + 1,
            }

        # Get the latest user message content
        user_message = next(
            (msg for msg in reversed(messages) if isinstance(msg, HumanMessage)), None
        )
        if not user_message:
            return {
                "errors": ["No user message found"],
                "iteration": state.get("iteration", 0) + 1,
            }

        file_path = user_message.content

        # Get read tool from config
        read_tool = next((t for t in config["tools"] if t.name == "read_file"), None)
        if not read_tool:
            return {
                "errors": ["ReadFile tool not available"],
                "iteration": state.get("iteration", 0) + 1,
            }

        # Read file
        try:
            content = read_tool.invoke({"path": file_path})
        except Exception as e:
            return {
                "errors": [f"Failed to read file: {str(e)}"],
                "iteration": state.get("iteration", 0) + 1,
            }

        # Analyze with LLM
        try:
            client = get_mistral_client()
            response = client.chat.completions.create(
                model=config["llm"],
                messages=[
                    {"role": "system", "content": config["system_prompt"]},
                    {
                        "role": "user",
                        "content": f"Analyze this data file:\n\nPath: {file_path}\n\nContent:\n{content}",
                    },
                ],
                temperature=config.get("temperature", 0.2),
            )

            analysis = response.choices[0].message.content

            return {
                "messages": [AIMessage(content=analysis)],
                "tool_output": analysis,
                "iteration": state.get("iteration", 0) + 1,
            }
        except Exception as e:
            return {
                "errors": [f"LLM analysis failed: {str(e)}"],
                "iteration": state.get("iteration", 0) + 1,
            }

    def store_results(state):
        """Store analysis results in database."""
        analysis = state.get("tool_output")
        if not analysis:
            return {
                "errors": ["No analysis to store"],
                "final_answer": "Analysis failed - no results to store",
                "iteration": state.get("iteration", 0) + 1,
            }

        # Get write tool from config
        write_tool = next((t for t in config["tools"] if t.name == "write_record"), None)
        if not write_tool:
            return {
                "errors": ["WriteRecord tool not available"],
                "final_answer": "Cannot store results - WriteRecord tool missing",
                "iteration": state.get("iteration", 0) + 1,
            }

        # Store results
        try:
            write_tool.invoke(
                {
                    "table": "analysis_results",
                    "data": {
                        "analysis": analysis,
                        "source_file": state["messages"][0].content
                        if state.get("messages")
                        else "unknown",
                        "processed_at": "NOW()",
                    },
                }
            )

            return {
                "final_answer": f"Analysis complete and stored successfully.\n\n{analysis}",
                "iteration": state.get("iteration", 0) + 1,
            }
        except Exception as e:
            return {
                "errors": [f"Failed to store results: {str(e)}"],
                "final_answer": f"Analysis completed but storage failed: {str(e)}",
                "iteration": state.get("iteration", 0) + 1,
            }

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
    print("=" * 60)
    print("Custom Agent - Data Processor")
    print("=" * 60)
    print("\nConfiguration:")
    print("  Queue: data-processor")
    print("  Timeout: 600s (10 minutes)")
    print("  Tools: ReadFile, WriteRecord")
    print("  LLM: mistral-large-latest")
    print("  Memory: Enabled")

    print("\n" + "-" * 60)
    print("Agent Workflow")
    print("-" * 60)
    print("  1. analyze - Read file and analyze with LLM")
    print("  2. store   - Save results to analysis_results table")

    print("\n" + "-" * 60)
    print("Example Jobs")
    print("-" * 60)

    print("\n1. Analyze CSV file:")
    print("   aimq send data-processor '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "data/sales_2024.csv"}')
    print("     ],")
    print('     "tools": [],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n2. Analyze JSON data:")
    print("   aimq send data-processor '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "exports/user_data.json"}')
    print("     ],")
    print('     "tools": [],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n3. Resumable analysis:")
    print("   aimq send data-processor '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "large_files/yearly_report.csv"}')
    print("     ],")
    print('     "thread_id": "analysis-session-789",')
    print('     "tools": [],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n" + "-" * 60)
    print("Decorator Benefits")
    print("-" * 60)
    print("  - Automatic AgentState setup")
    print("  - Tools available in config['tools']")
    print("  - LLM settings in config['llm'], config['temperature']")
    print("  - Memory/checkpointing handled automatically")
    print("  - Focus on business logic, not infrastructure")

    print("\n" + "=" * 60)
    print("Starting worker... Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    worker.start()
