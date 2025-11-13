"""
Message Agent Worker - Demo of composable message routing and agent responses.

This example demonstrates:
1. Message ingestion with routing workflow
2. Agent queue handlers (default-assistant, react-assistant)
3. Composable tools for mention detection and queue resolution
4. End-to-end message → routing → agent → response flow

Architecture:
- incoming-messages queue: Routes messages to appropriate agents
- default-assistant queue: Handles general messages
- react-assistant queue: Handles messages with tools/reasoning

Usage:
    # Terminal 1: Start worker
    uv run python examples/message_agent/message_worker.py

    # Terminal 2: Send test messages
    aimq send incoming-messages '{
      "message_id": "msg_001",
      "body": "Hello, can you help me?",
      "sender": "user@example.com",
      "workspace_id": "workspace_123",
      "channel_id": "channel_456",
      "thread_id": "thread_789"
    }'

    aimq send incoming-messages '{
      "message_id": "msg_002",
      "body": "@react-assistant What files are in the documents folder?",
      "sender": "user@example.com",
      "workspace_id": "workspace_123",
      "channel_id": "channel_456",
      "thread_id": "thread_789"
    }'
"""

from aimq.agents import ReActAgent
from aimq.tools.ocr import ImageOCR
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.worker import Worker
from aimq.workflows import MessageRoutingWorkflow

worker = Worker()


@worker.task(queue="incoming-messages", timeout=60)
def handle_incoming_message(payload: dict) -> dict:
    """Route incoming messages to appropriate agent queues.

    Args:
        payload: Message data with body, sender, workspace_id, etc.

    Returns:
        Routing decision with queue name and mentions
    """
    routing_workflow = MessageRoutingWorkflow(default_queue="default-assistant")

    result = routing_workflow.invoke({"input": payload, "errors": []})

    routing_info = result.get("final_output", {})
    queue = routing_info.get("queue", "default-assistant")
    mentions = routing_info.get("mentions", [])

    agent_state = {
        "messages": [{"role": "user", "content": payload["body"]}],
        "tools": [],
        "iteration": 0,
        "errors": [],
        "metadata": {
            "message_id": payload.get("message_id"),
            "sender": payload.get("sender"),
            "workspace_id": payload.get("workspace_id"),
            "channel_id": payload.get("channel_id"),
            "thread_id": payload.get("thread_id"),
            "mentions": mentions,
        },
    }

    worker.send(queue, agent_state)

    worker.logger.info(
        f"Routed message {payload.get('message_id')} to {queue}",
        {"queue": queue, "mentions": mentions, "message_id": payload.get("message_id")},
    )

    return {
        "routed_to": queue,
        "mentions": mentions,
        "message_id": payload.get("message_id"),
    }


default_agent = ReActAgent(
    tools=[],
    system_prompt="""You are a helpful default assistant.
    You provide friendly, concise responses to general questions.
    Be warm and professional in your communication.""",
    llm="mistral-large-latest",
    temperature=0.7,
    memory=False,
    max_iterations=5,
)

# Assign agent directly to queue - it handles message conversion automatically
worker.assign(default_agent, queue="default-assistant", timeout=300)


react_agent = ReActAgent(
    tools=[
        ReadFile(),
        ReadRecord(),
        ImageOCR(),
    ],
    system_prompt="""You are a helpful ReAct assistant with access to tools.
    You can read files, extract text from images, and query databases.
    Use your tools to gather information and provide accurate, helpful responses.

    When using tools:
    - Be thorough but efficient
    - Explain what you're doing
    - Provide clear, actionable answers""",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=False,
    max_iterations=10,
)

# Assign agent directly to queue - it handles message conversion automatically
worker.assign(react_agent, queue="react-assistant", timeout=600)


if __name__ == "__main__":
    from pathlib import Path

    motd_path = Path(__file__).parent / "message_worker_MOTD.md"
    worker.start(motd=str(motd_path) if motd_path.exists() else None, show_info=True)
