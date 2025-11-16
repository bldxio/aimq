"""
Clear message agent queues.

This script purges all messages from the message agent queues,
useful for starting fresh during development.

Usage:
    uv run python examples/message_agent/clear_queues.py
"""

from aimq.clients.supabase import supabase

QUEUES = [
    "incoming-messages",
    "default-assistant",
    "react-assistant",
]


def clear_queue(queue_name: str) -> int:
    """Clear all messages from a queue.

    Args:
        queue_name: Name of the queue to clear

    Returns:
        Number of messages purged
    """
    try:
        count = 0
        # Read and delete messages in batches
        while True:
            # Pop messages (read and delete in one operation)
            result = (
                supabase.client.schema("pgmq_public")
                .rpc("pop", {"queue_name": queue_name})
                .execute()
            )

            if not result.data:
                break

            count += 1

            # Safety limit to avoid infinite loop
            if count > 1000:
                print(f"⚠️  Stopped after clearing 1000 messages from {queue_name}")
                break

        print(f"✅ Cleared {count} messages from {queue_name}")
        return count
    except Exception as e:
        print(f"❌ Error clearing {queue_name}: {e}")
        return 0


def main():
    """Clear all message agent queues."""
    print("🧹 Clearing message agent queues...\n")

    total = 0
    for queue in QUEUES:
        count = clear_queue(queue)
        total += count

    print(f"\n✅ Total messages cleared: {total}")
    print("\nQueues are now empty and ready for fresh messages! 🚀")


if __name__ == "__main__":
    main()
