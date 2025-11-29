"""Message routing workflow for intelligent agent selection."""

from typing import Any

from langgraph.graph import END, StateGraph

from aimq.tools.routing import DetectMentions, ResolveQueue
from aimq.workflows.base import BaseWorkflow
from aimq.workflows.states import WorkflowState


class MessageRoutingWorkflow(BaseWorkflow):
    """Workflow for routing messages to appropriate agent queues.

    Uses composable tools to:
    1. Detect @mentions in message text
    2. Resolve mentions to queue names
    3. Return routing decision

    Args:
        detect_mentions_tool: Tool for extracting @mentions (default: DetectMentions)
        resolve_queue_tool: Tool for mapping mentions to queues (default: ResolveQueue)
        default_queue: Fallback queue name (default: "default-assistant")
        checkpointer: Enable state persistence (default: False)

    Example:
        workflow = MessageRoutingWorkflow(default_queue="my-assistant")

        result = workflow.invoke({
            "input": {
                "message_id": "msg_123",
                "body": "@react-assistant help me",
                "workspace_id": "ws_456"
            },
            "errors": []
        })

        # result["final_output"]["queue"] == "react-assistant"
    """

    def __init__(
        self,
        detect_mentions_tool: DetectMentions | None = None,
        resolve_queue_tool: ResolveQueue | None = None,
        default_queue: str = "default-assistant",
        checkpointer: bool = False,
    ):
        self.detect_mentions_tool = detect_mentions_tool or DetectMentions()
        self.resolve_queue_tool = resolve_queue_tool or ResolveQueue()
        self.default_queue = default_queue
        super().__init__(checkpointer=checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build message routing graph."""
        graph = StateGraph(WorkflowState)

        graph.add_node("detect_mentions", self._detect_mentions_node)
        graph.add_node("resolve_queue", self._resolve_queue_node)

        graph.set_entry_point("detect_mentions")
        graph.add_edge("detect_mentions", "resolve_queue")
        graph.add_edge("resolve_queue", END)

        return graph

    def _detect_mentions_node(self, state: WorkflowState) -> dict[str, Any]:
        """Extract @mentions from message body."""
        body = state["input"].get("body", "")

        try:
            mentions = self.detect_mentions_tool.run({"text": body})

            return {
                "step_results": [
                    {
                        "step": "detect_mentions",
                        "mentions": mentions,
                        "body": body,
                    }
                ],
                "current_step": "detect_mentions",
            }
        except Exception as e:
            return {
                "errors": [f"Error detecting mentions: {str(e)}"],
                "step_results": [
                    {
                        "step": "detect_mentions",
                        "mentions": [],
                        "error": str(e),
                    }
                ],
                "current_step": "detect_mentions",
            }

    def _resolve_queue_node(self, state: WorkflowState) -> dict[str, Any]:
        """Resolve mentions to a queue name."""
        step_results = state.get("step_results", [])
        mentions = []

        for result in step_results:
            if result.get("step") == "detect_mentions":
                mentions = result.get("mentions", [])
                break

        try:
            queue = self.resolve_queue_tool.run(
                {"mentions": mentions, "default_queue": self.default_queue}
            )

            return {
                "step_results": [
                    {
                        "step": "resolve_queue",
                        "queue": queue,
                        "mentions": mentions,
                    }
                ],
                "current_step": "resolve_queue",
                "final_output": {
                    "queue": queue,
                    "mentions": mentions,
                    "message_id": state["input"].get("message_id"),
                    "workspace_id": state["input"].get("workspace_id"),
                    "channel_id": state["input"].get("channel_id"),
                    "thread_id": state["input"].get("thread_id"),
                },
            }
        except Exception as e:
            return {
                "errors": [f"Error resolving queue: {str(e)}"],
                "step_results": [
                    {
                        "step": "resolve_queue",
                        "queue": self.default_queue,
                        "error": str(e),
                    }
                ],
                "current_step": "resolve_queue",
                "final_output": {
                    "queue": self.default_queue,
                    "mentions": mentions,
                    "message_id": state["input"].get("message_id"),
                    "workspace_id": state["input"].get("workspace_id"),
                    "channel_id": state["input"].get("channel_id"),
                    "thread_id": state["input"].get("thread_id"),
                },
            }
