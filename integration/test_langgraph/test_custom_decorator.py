"""Tests for custom decorator usage."""

from typing import TypedDict

import pytest  # noqa: F401
from langgraph.graph import END

from aimq.langgraph import agent, workflow
from aimq.langgraph.states import AgentState  # noqa: F401


class CustomState(TypedDict):
    """Custom state for testing."""

    value: int
    result: str


def test_custom_workflow_with_decorator():
    """Test creating and using custom workflow."""

    @workflow(state_class=CustomState)
    def custom_wf(graph, config):
        def process(state):
            return {"result": f"Processed: {state['value']}"}

        graph.add_node("process", process)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        return graph

    wf = custom_wf()
    result = wf.invoke({"value": 42, "result": ""})

    assert "result" in result
    assert "Processed" in result["result"]


def test_custom_agent_with_decorator():
    """Test creating and using custom agent."""

    @agent(system_prompt="Custom agent")
    def custom_agent(graph, config):
        def node(state):
            return {"iteration": state.get("iteration", 0) + 1, "final_answer": "done"}

        graph.add_node("node", node)
        graph.set_entry_point("node")
        graph.add_edge("node", END)
        return graph

    ag = custom_agent()
    result = ag.invoke({"messages": [], "tools": [], "iteration": 0, "errors": []})

    assert result["iteration"] > 0


def test_workflow_with_multiple_nodes():
    """Test workflow with multiple processing nodes."""

    @workflow()
    def multi_step_wf(graph, config):
        def step1(state):
            return {"input": state["input"], "step_results": [{"step": 1}]}

        def step2(state):
            results = state.get("step_results", [])
            return {"step_results": results + [{"step": 2}]}

        def finalize(state):
            return {
                "final_output": {
                    "completed": True,
                    "steps": len(state.get("step_results", [])),
                }
            }

        graph.add_node("step1", step1)
        graph.add_node("step2", step2)
        graph.add_node("finalize", finalize)
        graph.set_entry_point("step1")
        graph.add_edge("step1", "step2")
        graph.add_edge("step2", "finalize")
        graph.add_edge("finalize", END)
        return graph

    wf = multi_step_wf()
    result = wf.invoke({"input": {"data": "test"}, "errors": []})

    assert "final_output" in result
    assert result["final_output"]["completed"] is True


def test_workflow_with_conditional_routing():
    """Test workflow with conditional edges."""

    @workflow()
    def conditional_wf(graph, config):
        def check(state):
            value = state["input"].get("value", 0)
            return {"current_step": "positive" if value > 0 else "negative"}

        def process_positive(state):
            return {"final_output": {"type": "positive"}}

        def process_negative(state):
            return {"final_output": {"type": "negative"}}

        def route(state):
            return state.get("current_step", "positive")

        graph.add_node("check", check)
        graph.add_node("positive", process_positive)
        graph.add_node("negative", process_negative)

        graph.set_entry_point("check")
        graph.add_conditional_edges(
            "check", route, {"positive": "positive", "negative": "negative"}
        )
        graph.add_edge("positive", END)
        graph.add_edge("negative", END)

        return graph

    wf = conditional_wf()

    # Test positive path
    result_pos = wf.invoke({"input": {"value": 5}, "errors": []})
    assert result_pos["final_output"]["type"] == "positive"

    # Test negative path
    result_neg = wf.invoke({"input": {"value": -5}, "errors": []})
    assert result_neg["final_output"]["type"] == "negative"


def test_agent_with_custom_config():
    """Test agent with custom configuration."""

    @agent(system_prompt="Default prompt", temperature=0.5)
    def configurable_agent(graph, config):
        # Access config values
        assert config["system_prompt"] in ["Default prompt", "Override prompt"]
        assert config["temperature"] in [0.5, 0.7]

        def node(state):
            return {"iteration": state.get("iteration", 0) + 1, "final_answer": "done"}

        graph.add_node("node", node)
        graph.set_entry_point("node")
        graph.add_edge("node", END)
        return graph

    # Test with default config
    ag1 = configurable_agent()
    result1 = ag1.invoke({"messages": [], "tools": [], "iteration": 0, "errors": []})
    assert result1["iteration"] > 0

    # Test with override config
    ag2 = configurable_agent(system_prompt="Override prompt", temperature=0.7)
    result2 = ag2.invoke({"messages": [], "tools": [], "iteration": 0, "errors": []})
    assert result2["iteration"] > 0


def test_workflow_streaming():
    """Test workflow supports streaming."""

    @workflow()
    def streamable_wf(graph, config):
        def step1(state):
            return {"input": state["input"], "current_step": "step1"}

        def step2(state):
            return {"current_step": "step2"}

        def step3(state):
            return {"final_output": {"status": "complete"}}

        graph.add_node("step1", step1)
        graph.add_node("step2", step2)
        graph.add_node("step3", step3)
        graph.set_entry_point("step1")
        graph.add_edge("step1", "step2")
        graph.add_edge("step2", "step3")
        graph.add_edge("step3", END)
        return graph

    wf = streamable_wf()

    # Test streaming
    stream = wf.stream({"input": {"data": "test"}, "errors": []})
    states = list(stream)

    assert len(states) > 0


def test_nested_workflow_composition():
    """Test composing workflows from other workflows."""

    @workflow()
    def sub_workflow(graph, config):
        def process(state):
            return {"input": {"processed": True}}

        graph.add_node("process", process)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        return graph

    @workflow()
    def main_workflow(graph, config):
        # Create sub-workflow instance
        sub_wf = sub_workflow()

        def call_sub(state):
            # Invoke sub-workflow
            sub_result = sub_wf.invoke(state)
            return {"final_output": sub_result}

        graph.add_node("call_sub", call_sub)
        graph.set_entry_point("call_sub")
        graph.add_edge("call_sub", END)
        return graph

    main_wf = main_workflow()
    result = main_wf.invoke({"input": {}, "errors": []})

    assert "final_output" in result
