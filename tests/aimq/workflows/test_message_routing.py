"""Tests for MessageRoutingWorkflow."""

from aimq.workflows import MessageRoutingWorkflow


class TestMessageRoutingWorkflow:
    """Test suite for MessageRoutingWorkflow."""

    def test_route_to_react_assistant(self):
        """Test routing message with @react-assistant mention."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_001",
                    "body": "@react-assistant help me",
                    "workspace_id": "ws_123",
                    "channel_id": "ch_456",
                    "thread_id": "th_789",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "react-assistant"
        assert "react-assistant" in result["final_output"]["mentions"]
        assert result["final_output"]["message_id"] == "msg_001"
        assert result["final_output"]["workspace_id"] == "ws_123"

    def test_route_to_default_assistant(self):
        """Test routing message with no valid mentions."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_002",
                    "body": "Hello, can you help?",
                    "workspace_id": "ws_123",
                    "channel_id": "ch_456",
                    "thread_id": "th_789",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "default-assistant"
        assert result["final_output"]["mentions"] == []

    def test_route_with_multiple_mentions(self):
        """Test routing with multiple mentions uses first valid one."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_003",
                    "body": "@user123 @react-assistant @default-bot help",
                    "workspace_id": "ws_123",
                    "channel_id": "ch_456",
                    "thread_id": "th_789",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "react-assistant"
        assert "react-assistant" in result["final_output"]["mentions"]

    def test_route_with_custom_default_queue(self):
        """Test routing with custom default queue."""
        workflow = MessageRoutingWorkflow(default_queue="custom-assistant")

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_004",
                    "body": "Hello",
                    "workspace_id": "ws_123",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "custom-assistant"

    def test_route_preserves_metadata(self):
        """Test that routing preserves all metadata fields."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_005",
                    "body": "@react-assistant help",
                    "workspace_id": "ws_123",
                    "channel_id": "ch_456",
                    "thread_id": "th_789",
                },
                "errors": [],
            }
        )

        output = result["final_output"]
        assert output["message_id"] == "msg_005"
        assert output["workspace_id"] == "ws_123"
        assert output["channel_id"] == "ch_456"
        assert output["thread_id"] == "th_789"

    def test_route_with_bot_suffix(self):
        """Test routing with -bot suffix."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_006",
                    "body": "@helper-bot please assist",
                    "workspace_id": "ws_123",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "helper-bot"

    def test_workflow_has_step_results(self):
        """Test that workflow records step results."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_007",
                    "body": "@react-assistant help",
                    "workspace_id": "ws_123",
                },
                "errors": [],
            }
        )

        assert "step_results" in result
        assert len(result["step_results"]) > 0

        steps = [r["step"] for r in result["step_results"]]
        assert "detect_mentions" in steps
        assert "resolve_queue" in steps

    def test_workflow_handles_missing_body(self):
        """Test workflow handles missing body gracefully."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_008",
                    "workspace_id": "ws_123",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "default-assistant"
        assert result["final_output"]["mentions"] == []

    def test_workflow_with_empty_body(self):
        """Test workflow with empty body string."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_009",
                    "body": "",
                    "workspace_id": "ws_123",
                },
                "errors": [],
            }
        )

        assert result["final_output"]["queue"] == "default-assistant"

    def test_workflow_current_step_tracking(self):
        """Test that workflow tracks current step."""
        workflow = MessageRoutingWorkflow()

        result = workflow.invoke(
            {
                "input": {
                    "message_id": "msg_010",
                    "body": "@react-assistant help",
                    "workspace_id": "ws_123",
                },
                "errors": [],
            }
        )

        assert "current_step" in result
        assert result["current_step"] == "resolve_queue"
