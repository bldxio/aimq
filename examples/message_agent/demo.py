"""
Quick demo script for testing message routing.

This script sends test messages to demonstrate:
1. Default routing (no @mention)
2. @mention routing to specific agents
3. Response format with agent sender

Usage:
    # Make sure the worker is running first!
    # Terminal 1: uv run python examples/message_agent/message_worker.py

    # Terminal 2: Run this demo
    uv run python examples/message_agent/demo.py
"""

import json
import subprocess
import time

WORKSPACE_ID = "demo_workspace_123"
CHANNEL_ID = "demo_channel_456"
THREAD_ID = "demo_thread_789"


def send_message(message_id: str, body: str, sender: str = "demo_user@example.com"):
    """Send a message to the incoming-messages queue."""
    payload = {
        "message_id": message_id,
        "body": body,
        "sender": sender,
        "workspace_id": WORKSPACE_ID,
        "channel_id": CHANNEL_ID,
        "thread_id": THREAD_ID,
    }

    cmd = ["aimq", "send", "incoming-messages", json.dumps(payload)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error sending message: {result.stderr}")
        return None

    print(f"✅ Sent: {body[:50]}...")
    return result


def main():
    """Run the demo."""
    print("🚀 Message Agent Demo\n")
    print("=" * 60)

    print("\n📨 Test 1: General message (no @mention)")
    print("-" * 60)
    send_message("demo_msg_001", "Hello! Can you tell me what you can do?")
    print("Expected: Routes to default-assistant\n")
    time.sleep(2)

    print("\n📨 Test 2: Message with @react-assistant mention")
    print("-" * 60)
    send_message("demo_msg_002", "@react-assistant Can you help me analyze some data?")
    print("Expected: Routes to react-assistant\n")
    time.sleep(2)

    print("\n📨 Test 3: Message with @default-assistant mention")
    print("-" * 60)
    send_message("demo_msg_003", "@default-assistant What's the weather like?")
    print("Expected: Routes to default-assistant\n")
    time.sleep(2)

    print("\n📨 Test 4: Message with multiple mentions")
    print("-" * 60)
    send_message("demo_msg_004", "Hey @react-assistant and @default-assistant, can you both help?")
    print("Expected: Routes to react-assistant (first valid mention)\n")
    time.sleep(2)

    print("\n📨 Test 5: Message with invalid mention")
    print("-" * 60)
    send_message("demo_msg_005", "@unknown-user can you help?")
    print("Expected: Routes to default-assistant (fallback)\n")

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("\nCheck the worker logs to see routing decisions and responses.")
    print("Look for messages like:")
    print("  - 'Routed message demo_msg_001 to default-assistant'")
    print("  - 'Response from default-assistant@demo_workspace_123'")


if __name__ == "__main__":
    main()
