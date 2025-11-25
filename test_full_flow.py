#!/usr/bin/env python
"""Test the full email processing flow without external services."""

import os

os.environ["DRY_RUN"] = "true"  # Don't actually send emails

from aimq.agents.email import process_email_response  # noqa: E402
from aimq.clients.supabase import supabase  # noqa: E402

print("=== Email Processing Full Flow Test ===\n")

# Step 1: Create a test message (simulating what the edge function would do)
print("Step 1: Creating test message...")

workspace_result = (
    supabase.client.table("workspaces").select("id").eq("short_name", "acme").single().execute()
)
workspace_id = workspace_result.data["id"]

channel_result = (
    supabase.client.table("channels")
    .select("id")
    .eq("workspace_id", workspace_id)
    .eq("short_name", "support")
    .single()
    .execute()
)
channel_id = channel_result.data["id"]

member_result = (
    supabase.client.table("members")
    .select("id")
    .eq("workspace_id", workspace_id)
    .limit(1)
    .execute()
)
from_member_id = member_result.data[0]["id"]

message_result = (
    supabase.client.table("messages")
    .insert(
        {
            "workspace_id": workspace_id,
            "channel_id": channel_id,
            "type": "email",
            "from_member_id": from_member_id,
            "status": "pending",
            "processing_stage": "awaiting_agent_response",
            "email_subject": "Test: Need Help",
            "email_to": ["support@acme.acme.bldx.run"],
            "content_text": "Hi, I need help with my account. Can you assist?",
        }
    )
    .select()
    .single()
    .execute()
)

message_id = message_result.data["id"]
print(f"✓ Message created: {message_id}\n")

# Step 2: Process the message (simulating what the worker would do)
print("Step 2: Processing message with agent...")
print("(This will call OpenAI API - make sure OPENAI_API_KEY is set)\n")

try:
    result = process_email_response(
        {
            "message_id": message_id,
            "workspace_id": workspace_id,
            "channel_id": channel_id,
            "action": "generate_response",
        }
    )

    print(f"✓ Processing result: {result}\n")

    # Step 3: Verify the results
    print("Step 3: Verifying results...")

    # Check original message status
    original = supabase.client.table("messages").select("*").eq("id", message_id).single().execute()
    print(f"✓ Original message status: {original.data['status']}")
    print(f"  Processing stage: {original.data['processing_stage']}")

    # Check response message
    response = (
        supabase.client.table("messages")
        .select("*")
        .eq("reply_to_id", message_id)
        .single()
        .execute()
    )
    print(f"\n✓ Response message created: {response.data['id']}")
    print(f"  Subject: {response.data['email_subject']}")
    print(f"  Status: {response.data['status']}")
    print("\n  Response text (first 200 chars):")
    print(f"  {response.data['content_text'][:200]}...")

    print("\n=== ✅ Full Flow Test PASSED ===")

except Exception as e:
    print("\n=== ❌ Full Flow Test FAILED ===")
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()

    # Cleanup
    print("\nCleaning up test message...")
    supabase.client.table("messages").delete().eq("id", message_id).execute()
