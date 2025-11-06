# Phase 7: Testing

**Status**: ⏳ Not Started
**Priority**: 1 (Critical)
**Estimated**: 4-5 hours
**Dependencies**: Phases 1, 2, 3, 4 (Complete)

---

## Objectives

Achieve comprehensive test coverage (>89%) for all LangGraph functionality:
1. Unit tests for decorators and base classes
2. Unit tests for agents and workflows
3. Unit tests for checkpointing and utilities
4. Integration tests for end-to-end scenarios
5. Security and validation tests

## Coverage Target

**Minimum**: 89% overall coverage
**Goal**: 95%+ coverage

---

## Implementation Steps

### 7.1 Decorator Tests (1 hour)

**File**: `tests/aimq/langgraph/test_decorators.py`

```python
"""Tests for @workflow and @agent decorators."""

import pytest
from aimq.langgraph import workflow, agent
from langgraph.graph import StateGraph, END
from langchain.tools import BaseTool
from aimq.langgraph.states import AgentState, WorkflowState


class DummyTool(BaseTool):
    """Dummy tool for testing."""
    name = "dummy"
    description = "Test tool"

    def _run(self, input: str) -> str:
        return f"Result: {input}"


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
    assert hasattr(instance, 'invoke')
    assert hasattr(instance, 'stream')


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
        graph.add_node("start", lambda s: {"iteration": 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_agent()
    assert instance is not None
    assert hasattr(instance, 'invoke')
    assert hasattr(instance, 'stream')


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
        graph.add_node("start", lambda s: {"iteration": 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance = my_agent()
    assert instance is not None


def test_agent_decorator_llm_resolution():
    """Test LLM parameter resolution."""
    from langchain_mistralai import ChatMistralAI

    # String model name
    @agent(llm="mistral-small-latest")
    def agent1(graph, config):
        graph.add_node("start", lambda s: {"iteration": 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance1 = agent1()
    assert instance1.config["llm"] is not None

    # LLM object
    llm_obj = ChatMistralAI(model="mistral-large-latest")

    @agent(llm=llm_obj)
    def agent2(graph, config):
        graph.add_node("start", lambda s: {"iteration": 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    instance2 = agent2()
    assert instance2.config["llm"] == llm_obj


def test_agent_decorator_config_override():
    """Test factory-level config overrides."""
    @agent(system_prompt="Default", temperature=0.1)
    def my_agent(graph, config):
        graph.add_node("start", lambda s: {"iteration": 1})
        graph.set_entry_point("start")
        graph.add_edge("start", END)
        return graph

    # Override at factory level
    instance = my_agent(system_prompt="Override", temperature=0.7)
    assert instance.config["system_prompt"] == "Override"
    assert instance.config["temperature"] == 0.7
```

---

### 7.2 Checkpoint Tests (45 minutes)

**File**: `tests/aimq/langgraph/test_checkpoint.py`

```python
"""Tests for checkpointing functionality."""

import pytest
from unittest.mock import patch, MagicMock
from aimq.langgraph.checkpoint import (
    _build_connection_string,
    get_checkpointer,
    CheckpointerError
)


@patch('aimq.langgraph.checkpoint.config')
def test_build_connection_string_success(mock_config):
    """Test connection string building with valid config."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "test-key"

    conn_str = _build_connection_string()

    assert "postgresql://" in conn_str
    assert "postgres:" in conn_str
    assert "test-project" in conn_str
    assert "@db.test-project.supabase.co:5432/postgres" in conn_str


@patch('aimq.langgraph.checkpoint.config')
def test_build_connection_string_url_encoding(mock_config):
    """Test password URL encoding."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = "key-with-special!@#$%chars"

    conn_str = _build_connection_string()

    # Special chars should be URL-encoded
    assert "key-with-special" in conn_str or "%" in conn_str
    assert "!@#$%" not in conn_str  # Raw special chars shouldn't appear


@patch('aimq.langgraph.checkpoint.config')
def test_build_connection_string_missing_url(mock_config):
    """Test error when SUPABASE_URL missing."""
    mock_config.supabase_url = ""
    mock_config.supabase_key = "test-key"

    with pytest.raises(CheckpointerError, match="SUPABASE_URL required"):
        _build_connection_string()


@patch('aimq.langgraph.checkpoint.config')
def test_build_connection_string_missing_key(mock_config):
    """Test error when SUPABASE_KEY missing."""
    mock_config.supabase_url = "https://test-project.supabase.co"
    mock_config.supabase_key = ""

    with pytest.raises(CheckpointerError, match="SUPABASE_KEY required"):
        _build_connection_string()


@patch('aimq.langgraph.checkpoint.config')
def test_build_connection_string_invalid_url(mock_config):
    """Test error with invalid URL format."""
    mock_config.supabase_url = "https://invalid-url.com"
    mock_config.supabase_key = "test-key"

    with pytest.raises(CheckpointerError, match="Invalid SUPABASE_URL format"):
        _build_connection_string()


@patch('aimq.langgraph.checkpoint.PostgresSaver')
@patch('aimq.langgraph.checkpoint._build_connection_string')
@patch('aimq.langgraph.checkpoint._ensure_schema')
def test_get_checkpointer_singleton(
    mock_ensure, mock_build, mock_saver
):
    """Test checkpointer singleton pattern."""
    mock_build.return_value = "postgresql://test"
    mock_saver_instance = MagicMock()
    mock_saver.return_value = mock_saver_instance

    # Reset singleton
    import aimq.langgraph.checkpoint as checkpoint_module
    checkpoint_module._checkpointer_instance = None

    # First call creates instance
    cp1 = get_checkpointer()
    assert cp1 is not None
    assert mock_saver.called

    # Second call returns same instance
    cp2 = get_checkpointer()
    assert cp1 is cp2
```

---

### 7.3 Agent Tests (1 hour)

**File**: `tests/aimq/agents/test_react.py`

```python
"""Tests for ReActAgent."""

import pytest
from unittest.mock import MagicMock, patch
from aimq.agents import ReActAgent
from langchain.tools import BaseTool


class MockTool(BaseTool):
    name = "mock_tool"
    description = "Mock tool for testing"

    def _run(self, input: str) -> str:
        return f"Mock result: {input}"


def test_react_agent_initialization():
    """Test ReActAgent can be initialized."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test agent",
        max_iterations=5
    )

    assert agent is not None
    assert len(agent.tools) == 1
    assert agent.max_iterations == 5
    assert agent.system_prompt == "Test agent"


def test_react_agent_graph_compilation():
    """Test agent compiles graph successfully."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test"
    )

    assert agent._compiled is not None
    assert agent._graph is not None


def test_react_agent_has_nodes():
    """Test graph has required nodes."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test"
    )

    # Check nodes exist
    nodes = agent._graph.nodes
    assert "reason" in nodes
    assert "act" in nodes


def test_react_agent_parse_action():
    """Test action parsing from LLM response."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    # Test ACTION/INPUT parsing
    response = """
THOUGHT: I need to use the tool
ACTION: mock_tool
INPUT: {"query": "test"}
"""

    action = agent._parse_action(response)
    assert action.get("tool") == "mock_tool"
    assert action.get("input") == {"query": "test"}

    # Test ANSWER parsing
    response_answer = """
THOUGHT: I have the answer
ANSWER: Final answer here
"""

    action_answer = agent._parse_action(response_answer)
    assert action_answer.get("answer") == "Final answer here"


def test_react_agent_max_iterations():
    """Test max_iterations prevents infinite loops."""
    agent = ReActAgent(
        tools=[MockTool()],
        system_prompt="Test",
        max_iterations=3
    )

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 3,  # At max
        "errors": [],
    }

    # Should route to end
    result = agent._should_continue(state)
    assert result == "end"


def test_react_agent_tool_validation():
    """Test tool input validation is used."""
    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    # Validator should be initialized
    assert agent.validator is not None


@patch('aimq.agents.react.get_mistral_client')
def test_react_agent_reasoning_node(mock_client):
    """Test reasoning node execution."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="THOUGHT: Test\nANSWER: Done"))
    ]
    mock_client.return_value.chat.completions.create.return_value = mock_response

    agent = ReActAgent(tools=[MockTool()], system_prompt="Test")

    state = {
        "messages": [],
        "tools": ["mock_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent._reasoning_node(state)

    assert "final_answer" in result
    assert result["iteration"] == 1
```

---

### 7.4 Workflow Tests (1 hour)

**File**: `tests/aimq/workflows/test_document.py`

```python
"""Tests for DocumentWorkflow."""

import pytest
from unittest.mock import MagicMock
from aimq.workflows import DocumentWorkflow


class MockTool:
    def invoke(self, input):
        if "path" in input:
            return b"test content"
        if "image" in input:
            return {"text": "extracted text", "confidence": 0.95}
        return {"text": "result"}


def test_document_workflow_initialization():
    """Test DocumentWorkflow can be initialized."""
    workflow = DocumentWorkflow(
        storage_tool=MockTool(),
        ocr_tool=MockTool(),
    )

    assert workflow is not None
    assert workflow._compiled is not None


def test_document_workflow_routing():
    """Test document type routing logic."""
    workflow = DocumentWorkflow(
        storage_tool=MockTool(),
        ocr_tool=MockTool(),
    )

    # Test image routing
    state = {"document_type": "image"}
    assert workflow._route_by_type(state) == "process_image"

    # Test PDF routing
    state = {"document_type": "pdf"}
    assert workflow._route_by_type(state) == "process_pdf"

    # Test unknown routing
    state = {"document_type": "unknown"}
    assert workflow._route_by_type(state) == "error"


def test_document_workflow_fetch_node():
    """Test fetch node."""
    workflow = DocumentWorkflow(
        storage_tool=MockTool(),
        ocr_tool=MockTool(),
    )

    state = {
        "document_path": "test.pdf",
        "metadata": {},
        "status": "pending"
    }

    result = workflow._fetch_node(state)

    assert result["status"] == "fetched"
    assert "raw_content" in result


@patch('aimq.workflows.document.magic')
def test_document_workflow_detect_type_node(mock_magic):
    """Test type detection node."""
    mock_magic.from_buffer.return_value = "image/png"

    workflow = DocumentWorkflow(
        storage_tool=MockTool(),
        ocr_tool=MockTool(),
    )

    state = {
        "raw_content": b"fake image data",
        "metadata": {},
        "status": "fetched"
    }

    result = workflow._detect_type_node(state)

    assert result["document_type"] == "image"
    assert result["status"] == "typed"
    assert result["metadata"]["mime_type"] == "image/png"
```

---

### 7.5 Integration Tests (1-1.5 hours)

**File**: `tests/integration/langgraph/test_react_e2e.py`

```python
"""End-to-end tests for ReActAgent."""

import pytest
from unittest.mock import patch, MagicMock
from aimq.agents import ReActAgent
from langchain.tools import BaseTool


class TestTool(BaseTool):
    name = "test_tool"
    description = "Tool for testing"

    def _run(self, query: str) -> str:
        return f"Result for: {query}"


@patch('aimq.agents.react.get_mistral_client')
def test_react_agent_full_execution(mock_client):
    """Test complete ReActAgent execution flow."""
    # Mock LLM responses
    responses = [
        # First: Choose to use tool
        MagicMock(choices=[MagicMock(message=MagicMock(
            content='THOUGHT: I should use the tool\nACTION: test_tool\nINPUT: {"query": "test"}'
        ))]),
        # Second: Provide answer
        MagicMock(choices=[MagicMock(message=MagicMock(
            content='THOUGHT: I have the result\nANSWER: The answer is 42'
        ))]),
    ]

    mock_client.return_value.chat.completions.create.side_effect = responses

    agent = ReActAgent(
        tools=[TestTool()],
        system_prompt="Test agent",
        max_iterations=10
    )

    # Execute
    initial_state = {
        "messages": [{"role": "user", "content": "What is the answer?"}],
        "tools": ["test_tool"],
        "iteration": 0,
        "errors": [],
    }

    result = agent.invoke(initial_state)

    # Should have final answer
    assert "final_answer" in result or result.get("iteration") > 0


**File**: `tests/integration/langgraph/test_custom_decorator.py`

```python
"""Tests for custom decorator usage."""

import pytest
from aimq.langgraph import workflow, agent
from langgraph.graph import StateGraph, END
from typing import TypedDict


class CustomState(TypedDict):
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
    from aimq.langgraph.states import AgentState

    @agent(system_prompt="Custom agent")
    def custom_agent(graph, config):
        def node(state):
            return {"iteration": state["iteration"] + 1, "final_answer": "done"}

        graph.add_node("node", node)
        graph.set_entry_point("node")
        graph.add_edge("node", END)
        return graph

    ag = custom_agent()
    result = ag.invoke({
        "messages": [],
        "tools": [],
        "iteration": 0,
        "errors": []
    })

    assert result["iteration"] > 0
```

---

### 7.6 Coverage Check (15 minutes)

**Action**: Run pytest with coverage and verify target met:

```bash
uv run pytest --cov=src/aimq/langgraph --cov=src/aimq/agents --cov=src/aimq/workflows --cov-report=term-missing --cov-report=html

# Check coverage percentage
# Target: >89%
```

**Coverage Report Review**:

```bash
# View HTML report
open htmlcov/index.html

# Check specific modules
uv run pytest --cov=src/aimq/langgraph/decorators --cov-report=term
uv run pytest --cov=src/aimq/agents/react --cov-report=term
```

---

## Testing Checklist

### Unit Tests

- [ ] Decorator tests (`test_decorators.py`)
- [ ] Checkpoint tests (`test_checkpoint.py`)
- [ ] ReActAgent tests (`test_react.py`)
- [ ] PlanExecuteAgent tests (`test_plan_execute.py`)
- [ ] DocumentWorkflow tests (`test_document.py`)
- [ ] MultiAgentWorkflow tests (`test_multi_agent.py`)
- [ ] Utility function tests
- [ ] Exception tests

### Integration Tests

- [ ] ReAct end-to-end (`test_react_e2e.py`)
- [ ] Document workflow end-to-end (`test_document_e2e.py`)
- [ ] Custom decorator usage (`test_custom_decorator.py`)

### Security Tests

- [ ] Tool input validation tests
- [ ] Path traversal prevention
- [ ] SQL injection prevention
- [ ] Override security tests

### Coverage

- [ ] Overall coverage >89%
- [ ] langgraph module >90%
- [ ] agents module >85%
- [ ] workflows module >85%
- [ ] No critical uncovered code

---

## Definition of Done

### Tests Complete

- [ ] All unit tests written and passing
- [ ] All integration tests written and passing
- [ ] All security tests written and passing
- [ ] No flaky tests
- [ ] Tests run in <30 seconds

### Coverage Met

- [ ] Overall coverage >89%
- [ ] Coverage report generated
- [ ] Uncovered lines reviewed and justified
- [ ] Critical paths 100% covered

### CI Integration

- [ ] Tests pass in CI
- [ ] Coverage uploaded to Codecov
- [ ] No warnings or errors
- [ ] Tests run on Python 3.11, 3.12, 3.13

### Documentation

- [ ] Test docstrings complete
- [ ] Testing guide updated
- [ ] Coverage badge added to README

---

## Common Pitfalls

### Mocking External Dependencies

**Pitfall**: Tests fail without Supabase/Mistral configured

**Solution**: Mock external clients
```python
@patch('aimq.clients.mistral.get_mistral_client')
def test_with_mock(mock_client):
    mock_client.return_value.chat.completions.create.return_value = ...
```

### Async State Updates

**Pitfall**: State not properly merged between nodes

**Solution**: Test full graph execution, not just individual nodes

### Coverage False Positives

**Pitfall**: High coverage but critical paths untested

**Solution**: Review coverage report, add tests for error paths

---

## Next Steps

Once Phase 7 is complete:
- [ ] Update PROGRESS.md with 100% completion
- [ ] All phases complete
- [ ] Ready for beta release (v0.2.0b1)
- [ ] Update CHANGELOG.md

---

**Phase Owner**: Testing Team
**Started**: ___________
**Completed**: ___________
**Actual Hours**: ___________
