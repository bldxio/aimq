"""Tests for MultiAgentWorkflow."""

from unittest.mock import MagicMock, patch

import pytest  # noqa: F401

from aimq.workflows.multi_agent import MultiAgentWorkflow


def mock_researcher_agent(state):
    """Mock researcher agent function."""
    return {
        "messages": [{"role": "researcher", "content": "Research findings"}],
        "tool_output": "Research done",
    }


def mock_analyst_agent(state):
    """Mock analyst agent function."""
    return {
        "messages": [{"role": "analyst", "content": "Analysis complete"}],
        "tool_output": "Analysis done",
    }


def mock_writer_agent(state):
    """Mock writer agent function."""
    return {
        "messages": [{"role": "writer", "content": "Report written"}],
        "tool_output": "Writing done",
    }


def test_multi_agent_workflow_initialization():
    """Test MultiAgentWorkflow can be initialized."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
        },
        supervisor_llm="mistral-large-latest",
    )

    assert workflow is not None
    assert len(workflow.agents) == 2
    assert workflow.supervisor_llm == "mistral-large-latest"


def test_multi_agent_workflow_graph_compilation():
    """Test workflow compiles graph successfully."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
        }
    )

    assert workflow._compiled is not None
    assert workflow._graph is not None


def test_multi_agent_workflow_has_supervisor_node():
    """Test graph has supervisor node."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
        }
    )

    nodes = workflow._graph.nodes
    assert "supervisor" in nodes


def test_multi_agent_workflow_has_agent_nodes():
    """Test graph has all agent nodes."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
            "writer": mock_writer_agent,
        }
    )

    nodes = workflow._graph.nodes
    assert "researcher" in nodes
    assert "analyst" in nodes
    assert "writer" in nodes


@patch("aimq.clients.mistral.get_mistral_client")
def test_supervisor_node_routes_to_agent(mock_client_func):
    """Test supervisor node selects next agent."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="researcher"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_client_func.return_value = mock_client

    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
        }
    )

    state = {
        "messages": [],
        "tools": [],
        "iteration": 0,
        "errors": [],
    }

    result = workflow._supervisor_node(state)

    assert result["current_tool"] == "researcher"
    assert result["iteration"] == 1


@patch("aimq.clients.mistral.get_mistral_client")
def test_supervisor_node_ends_workflow(mock_client_func):
    """Test supervisor can end workflow."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="end"))]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_client_func.return_value = mock_client

    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
        }
    )

    state = {
        "messages": [],
        "tools": [],
        "iteration": 0,
        "errors": [],
    }

    result = workflow._supervisor_node(state)

    assert result["current_tool"] == "end"


def test_route_to_agent_normal():
    """Test routing to next agent."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
        }
    )

    state = {
        "messages": [],
        "tools": [],
        "iteration": 5,
        "errors": [],
        "current_tool": "analyst",
    }

    route = workflow._route_to_agent(state)
    assert route == "analyst"


def test_route_to_agent_max_iterations():
    """Test routing ends at max iterations."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
        }
    )

    state = {
        "messages": [],
        "tools": [],
        "iteration": 20,  # At max
        "errors": [],
        "current_tool": "analyst",
    }

    route = workflow._route_to_agent(state)
    assert route == "end"


def test_route_to_agent_end():
    """Test routing to end."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
        }
    )

    state = {
        "messages": [],
        "tools": [],
        "iteration": 5,
        "errors": [],
        "current_tool": "end",
    }

    route = workflow._route_to_agent(state)
    assert route == "end"


def test_build_supervisor_prompt():
    """Test supervisor prompt building."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
            "analyst": mock_analyst_agent,
            "writer": mock_writer_agent,
        }
    )

    state = {
        "messages": [
            {"role": "user", "content": "Start the task"},
            {"role": "researcher", "content": "Research done"},
        ],
        "tools": [],
        "iteration": 1,
        "errors": [],
    }

    prompt = workflow._build_supervisor_prompt(state)

    assert "researcher" in prompt
    assert "analyst" in prompt
    assert "writer" in prompt
    assert "coordinating" in prompt.lower()


def test_format_progress():
    """Test progress formatting."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
        }
    )

    state = {
        "messages": [
            {"role": "user", "content": "Task description"},
            {"role": "researcher", "content": "Findings"},
        ],
        "tools": [],
        "iteration": 1,
        "errors": [],
    }

    progress = workflow._format_progress(state)

    assert "user" in progress
    assert "researcher" in progress


def test_format_progress_limits_messages():
    """Test progress formatting limits to last 5 messages."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
        }
    )

    messages = [{"role": f"agent{i}", "content": f"Message {i}"} for i in range(10)]

    state = {
        "messages": messages,
        "tools": [],
        "iteration": 5,
        "errors": [],
    }

    progress = workflow._format_progress(state)

    # Should only show last 5 messages
    assert "Message 9" in progress
    assert "Message 0" not in progress


@patch("aimq.clients.mistral.get_mistral_client")
def test_supervisor_node_error_handling(mock_client_func):
    """Test supervisor node handles errors."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_client_func.return_value = mock_client

    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
        }
    )

    state = {
        "messages": [],
        "tools": [],
        "iteration": 0,
        "errors": [],
    }

    result = workflow._supervisor_node(state)

    assert "errors" in result
    assert len(result["errors"]) > 0


def test_multi_agent_workflow_with_checkpointer():
    """Test MultiAgentWorkflow with checkpointer enabled."""
    with patch("aimq.workflows.base.get_checkpointer"):
        workflow = MultiAgentWorkflow(
            agents={
                "researcher": mock_researcher_agent,
            },
            checkpointer=True,
        )

        assert workflow._compiled is not None


def test_multi_agent_workflow_single_agent():
    """Test workflow with single agent."""
    workflow = MultiAgentWorkflow(
        agents={
            "researcher": mock_researcher_agent,
        }
    )

    assert len(workflow.agents) == 1
    assert workflow._graph is not None
