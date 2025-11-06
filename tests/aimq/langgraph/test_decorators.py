"""Tests for @workflow and @agent decorators."""

from unittest.mock import MagicMock, patch

import pytest
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END

from aimq.langgraph import agent, workflow
from aimq.langgraph.states import AgentState, WorkflowState  # noqa: F401


class DummyTool(BaseTool):
    """Dummy tool for testing."""

    name: str = "dummy"
    description: str = "Test tool"

    def _run(self, input: str) -> str:
        return f"Result: {input}"


class DummyLLM(BaseChatModel):
    """Dummy LLM for testing."""

    def _generate(self, *args, **kwargs):
        pass

    def _llm_type(self) -> str:
        return "dummy"


def test_workflow_decorator_returns_factory():
    """Test @workflow returns factory function."""

    @workflow()
    def my_workflow(graph, config):
        return graph

    assert callable(my_workflow)


def test_workflow_decorator_creates_instance():
    """Test factory creates workflow instance."""

    @workflow()
    def my_workflow(graph, config):
        graph.add_node("start", lambda s: s)
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_workflow()
    assert instance is not None
    assert hasattr(instance, "invoke")
    assert hasattr(instance, "stream")


def test_workflow_decorator_with_checkpointer():
    """Test @workflow with checkpointer option."""

    @workflow(checkpointer=True)
    def my_workflow(graph, config):
        graph.add_node("start", lambda s: s)
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_workflow()
    assert instance.config.get("checkpointer") is True


def test_workflow_decorator_with_custom_state():
    """Test @workflow with custom state class."""

    class CustomState(WorkflowState):
        custom_field: str

    @workflow(state_class=CustomState)
    def my_workflow(graph, config):
        graph.add_node("start", lambda s: s)
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_workflow()
    assert instance.config.get("state_class") == CustomState


def test_agent_decorator_returns_factory():
    """Test @agent returns factory function."""

    @agent()
    def my_agent(graph, config):
        return graph

    assert callable(my_agent)


def test_agent_decorator_creates_instance():
    """Test factory creates agent instance."""

    @agent(tools=[DummyTool()])
    def my_agent(graph, config):
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_agent()
    assert instance is not None
    assert hasattr(instance, "invoke")
    assert hasattr(instance, "stream")


def test_agent_decorator_with_all_options():
    """Test @agent with all configuration options."""

    @agent(
        tools=[DummyTool()],
        system_prompt="Test prompt",
        temperature=0.5,
        memory=False,
        allow_system_prompt=True,
    )
    def my_agent(graph, config):
        assert config["system_prompt"] == "Test prompt"
        assert config["temperature"] == 0.5
        assert config["allow_system_prompt"] is True
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_agent()
    assert instance is not None


@patch("aimq.langgraph.utils.get_default_llm")
def test_agent_decorator_llm_string_resolution(mock_get_default):
    """Test LLM parameter resolution with string model name."""
    mock_llm_instance = MagicMock(spec=BaseChatModel)
    mock_get_default.return_value = mock_llm_instance

    @agent(llm="mistral-small-latest")
    def agent1(graph, config):
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance1 = agent1()
    assert instance1.config["llm"] is not None


def test_agent_decorator_llm_object_resolution():
    """Test LLM parameter resolution with LLM object."""
    llm_obj = DummyLLM()

    @agent(llm=llm_obj)
    def agent2(graph, config):
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance2 = agent2()
    assert instance2.config["llm"] == llm_obj


def test_agent_decorator_config_override():
    """Test factory-level config overrides."""

    @agent(system_prompt="Default", temperature=0.1)
    def my_agent(graph, config):
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    # Override at factory level
    instance = my_agent(system_prompt="Override", temperature=0.7)
    assert instance.config["system_prompt"] == "Override"
    assert instance.config["temperature"] == 0.7


def test_agent_decorator_invalid_state_class():
    """Test @agent with invalid state_class."""

    class NotADict:
        pass

    with pytest.raises(TypeError, match="state_class must be a dict subclass"):

        @agent(state_class=NotADict)
        def bad_agent(graph, config):
            return graph

        bad_agent()


def test_workflow_factory_config_merging():
    """Test workflow factory merges decorator and factory configs."""

    @workflow(checkpointer=False)
    def my_workflow(graph, config):
        graph.add_node("start", lambda s: s)
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    # Override checkpointer at factory level
    instance = my_workflow(checkpointer=True)
    assert instance.config.get("checkpointer") is True


def test_agent_decorator_default_values():
    """Test @agent applies default values."""

    @agent()
    def my_agent(graph, config):
        # Check defaults are applied
        assert "tools" in config
        assert "system_prompt" in config
        assert "llm" in config
        assert "temperature" in config
        assert "memory" in config
        assert "reply_function" in config
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_agent()
    assert instance.config["system_prompt"] == "You are a helpful AI assistant."
    assert instance.config["temperature"] == 0.1
    assert instance.config["memory"] is False


def test_workflow_decorator_default_state():
    """Test @workflow uses WorkflowState by default."""

    @workflow()
    def my_workflow(graph, config):
        # config should have default state_class
        assert config.get("state_class") is None or config.get("state_class") == WorkflowState
        graph.add_node("start", lambda s: s)
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_workflow()
    assert instance is not None


def test_agent_decorator_with_allowed_llms():
    """Test @agent with allowed_llms configuration."""
    llm_small = DummyLLM()
    llm_large = DummyLLM()

    @agent(allowed_llms={"small": llm_small, "large": llm_large}, allow_system_prompt=True)
    def my_agent(graph, config):
        assert "allowed_llms" in config
        assert config["allowed_llms"]["small"] == llm_small
        assert config["allowed_llms"]["large"] == llm_large
        graph.add_node("start", lambda s: {"iteration": s.get("iteration", 0) + 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_agent()
    assert instance.config["allowed_llms"] is not None


def test_workflow_invoke_basic():
    """Test workflow can be invoked."""

    @workflow()
    def my_workflow(graph, config):
        def node(state):
            return {"input": state["input"], "errors": []}

        graph.add_node("process", node)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        return graph

    wf = my_workflow()
    result = wf.invoke({"input": {"test": "data"}, "errors": []})
    assert "input" in result
