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

from langchain_core.runnables import RunnableLambda

from aimq.agents import ReActAgent
from aimq.clients.supabase import supabase
from aimq.tools.ocr import ImageOCR
from aimq.tools.supabase import QueryTable, ReadFile, ReadRecord
from aimq.tools.weather import Weather
from aimq.worker import Worker
from aimq.workflows import MessageRoutingWorkflow

worker = Worker()

OUTBOUND_QUEUE = "outgoing-messages"


def create_agent_with_outbound(agent):
    """Wrap an agent to send responses to the outbound queue.

    Args:
        agent: The agent to wrap

    Returns:
        A runnable that processes messages and sends responses to outbound queue
    """

    def process_and_respond(state: dict) -> dict:
        result = agent.invoke(state)

        outbound_payload = {
            "message_id": state.get("metadata", {}).get("message_id"),
            "sender": state.get("metadata", {}).get("sender"),
            "workspace_id": state.get("metadata", {}).get("workspace_id"),
            "channel_id": state.get("metadata", {}).get("channel_id"),
            "thread_id": state.get("metadata", {}).get("thread_id"),
            "agent_response": result,
            "metadata": state.get("metadata", {}),
        }

        supabase.client.schema("pgmq_public").rpc(
            "send", {"queue_name": OUTBOUND_QUEUE, "message": outbound_payload}
        ).execute()

        worker.logger.info(
            f"Sent response for message {outbound_payload['message_id']} to {OUTBOUND_QUEUE}",
            {"message_id": outbound_payload["message_id"], "queue": OUTBOUND_QUEUE},
        )

        return result

    return RunnableLambda(process_and_respond)


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

worker.assign(create_agent_with_outbound(default_agent), queue="default-assistant", timeout=300)


react_agent = ReActAgent(
    tools=[
        Weather(),
        QueryTable(),
        ReadFile(),
        ReadRecord(),
        ImageOCR(),
    ],
    system_prompt="""You are a helpful ReAct assistant with access to tools.
    You can get weather information, query sports databases, read files, extract text from images, and more.
    Use your tools to gather information and provide accurate, helpful responses.

    Available tools:
    - weather: Get current weather for any location (accepts natural language)
    - query_table: Query the competitors table (teams, players, sports data)
    - read_file: Read files from Supabase storage
    - read_record: Read database records
    - image_ocr: Extract text from images

    When using tools:
    - Be thorough but efficient
    - Explain what you're doing
    - Provide clear, actionable answers
    - Format sports data in a readable way""",
    llm="mistral-large-latest",
    temperature=0.1,
    memory=False,
    max_iterations=10,
)

worker.assign(create_agent_with_outbound(react_agent), queue="react-assistant", timeout=600)


if __name__ == "__main__":
    from pathlib import Path

    motd_path = Path(__file__).parent / "message_worker_MOTD.md"
    worker.start(motd=str(motd_path) if motd_path.exists() else None, show_info=True)
