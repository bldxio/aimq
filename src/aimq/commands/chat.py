"""Interactive chat command."""

import os
import time
import uuid
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.text import Text

from aimq.clients.supabase import supabase
from aimq.logger import Logger
from aimq.realtime import RealtimeChatListener

# Load environment variables
load_dotenv()

console = Console()
logger = Logger()

OUTBOUND_QUEUE = "outgoing-messages"

realtime_listener: Optional[RealtimeChatListener] = None


def send_message(
    body: str,
    workspace_id: str = "demo_workspace_123",
    channel_id: str = "demo_channel_456",
    thread_id: Optional[str] = None,
    sender: str = "cli_user@example.com",
) -> str:
    """Send a message to the incoming-messages queue."""
    client = supabase.client
    message_id = f"cli_msg_{uuid.uuid4().hex[:8]}"

    payload = {
        "message_id": message_id,
        "body": body,
        "sender": sender,
        "workspace_id": workspace_id,
        "channel_id": channel_id,
        "thread_id": thread_id,
    }

    response = (
        client.schema("pgmq_public")
        .rpc("send", {"queue_name": "incoming-messages", "message": payload})
        .execute()
    )

    if not response.data:
        raise Exception("Failed to send message to queue")

    return message_id


def wait_for_response(message_id: str, timeout: int = 60) -> Optional[dict]:
    """Wait for a response using realtime (if available) or polling fallback."""
    global realtime_listener  # noqa: F824

    if realtime_listener and realtime_listener.is_connected:
        logger.debug(f"Waiting for realtime response: {message_id}")
        payload = realtime_listener.wait_for_message(message_id, timeout=timeout)

        if payload:
            msg = payload.get("message", {})
            job_id = payload.get("job_id")

            agent_response = msg.get("agent_response", {})
            messages = agent_response.get("messages", [])

            result = {
                "content": messages[-1].get("content", "") if messages else "",
                "agent_response": agent_response,
                "metadata": msg.get("metadata", {}),
                "job_id": job_id,
            }

            try:
                supabase.client.schema("pgmq_public").rpc(
                    "archive", {"queue_name": OUTBOUND_QUEUE, "message_id": job_id}
                ).execute()
            except Exception as e:
                logger.warning(f"Failed to archive message: {e}")

            return result

    return poll_for_response(message_id, timeout)


def poll_for_response(
    message_id: str, timeout: int = 60, poll_interval: float = 0.2
) -> Optional[dict]:
    """Poll the outbound queue for a response to our message."""
    client = supabase.client
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = (
                client.schema("pgmq_public")
                .rpc("read", {"queue_name": OUTBOUND_QUEUE, "sleep_seconds": 1, "n": 10})
                .execute()
            )

            if response.data:
                for job in response.data:
                    msg = job.get("message", {})
                    job_id = job.get("msg_id")

                    if msg.get("message_id") == message_id:
                        agent_response = msg.get("agent_response", {})
                        messages = agent_response.get("messages", [])

                        result = {
                            "content": messages[-1].get("content", "") if messages else "",
                            "agent_response": agent_response,
                            "metadata": msg.get("metadata", {}),
                            "job_id": job_id,
                        }

                        client.schema("pgmq_public").rpc(
                            "archive", {"queue_name": OUTBOUND_QUEUE, "message_id": job_id}
                        ).execute()

                        return result

        except KeyboardInterrupt:
            raise
        except Exception as e:
            console.print(f"[yellow]Poll error: {e}[/yellow]")

        time.sleep(poll_interval)

    return None


def format_agent_name(agent: str) -> str:
    """Format agent name for display."""
    return agent.replace("-", " ").title()


def show_welcome():
    """Display welcome banner."""
    welcome = """
# 🤖 AIMQ Message Agent Chat

Welcome to the interactive chat demo! You can:
- Ask questions to the **default-assistant**
- Mention **@react-assistant** for tool-powered responses
- Get **weather** information for any location
- Query the **competitors** database (sports teams & players)

**Example queries:**
- `What's the weather in San Francisco?`
- `@react-assistant Show me NBA teams`
- `@react-assistant Find players on the Lakers`
- `@react-assistant Query competitors where sport_code is basketball`

Type `/quit` or `/exit` to leave.
"""
    console.print(Panel(Markdown(welcome), border_style="cyan", padding=(1, 2)))


def chat(
    agent: str = typer.Option("default-assistant", help="Default agent to chat with"),
    workspace: str = typer.Option("demo_workspace_123", help="Workspace ID"),
    channel: str = typer.Option("demo_channel_456", help="Channel ID"),
    thread: Optional[str] = typer.Option(None, help="Thread ID"),
    no_realtime: bool = typer.Option(False, help="Disable realtime notifications"),
):
    """Start an interactive chat session with an AI agent.

    Example:
        aimq chat
        aimq chat --agent react-assistant
        aimq chat --workspace my-workspace --channel my-channel
    """
    global realtime_listener

    show_welcome()

    if not no_realtime:
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if supabase_url and supabase_key:
                realtime_listener = RealtimeChatListener(
                    url=supabase_url,
                    key=supabase_key,
                    channel_name="aimq:jobs",
                    event_name="job_enqueued",
                    logger=logger,
                )
                realtime_listener.start()
                console.print("[dim]⚡ Realtime notifications enabled[/dim]")
            else:
                console.print(
                    "[dim]⚠️  Realtime disabled (missing SUPABASE_URL or SUPABASE_KEY)[/dim]"
                )
        except Exception as e:
            logger.warning(f"Failed to start realtime listener: {e}")
            console.print("[dim]⚠️  Realtime disabled, using polling fallback[/dim]")

    console.print(f"\n[dim]Connected to workspace: {workspace}[/dim]")
    console.print(f"[dim]Default agent: {format_agent_name(agent)}[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            if user_input.lower() in ["/quit", "/exit", "quit", "exit"]:
                console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                break

            if not user_input.strip():
                continue

            target_agent = agent
            if "@react-assistant" in user_input.lower():
                target_agent = "react-assistant"
            elif "@default-assistant" in user_input.lower():
                target_agent = "default-assistant"

            with Live(
                Spinner("dots", text=f"[dim]Sending to {format_agent_name(target_agent)}...[/dim]"),
                console=console,
                transient=True,
            ):
                message_id = send_message(
                    body=user_input, workspace_id=workspace, channel_id=channel, thread_id=thread
                )

            with Live(
                Spinner(
                    "dots",
                    text=f"[dim]Waiting for {format_agent_name(target_agent)} response...[/dim]",
                ),
                console=console,
                transient=True,
            ):
                response = wait_for_response(message_id, timeout=60)

            if response:
                content = response["content"]

                title = Text()
                title.append("🤖 ", style="bold")
                title.append("Assistant", style="bold green")

                console.print()
                console.print(
                    Panel(Markdown(content), title=title, border_style="green", padding=(1, 2))
                )
            else:
                console.print(
                    "\n[yellow]⏱️  Response timeout - agent may still be processing[/yellow]"
                )

        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")
            console.print("[dim]Make sure the worker is running![/dim]\n")

    if realtime_listener:
        realtime_listener.stop()
