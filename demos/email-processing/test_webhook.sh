#!/bin/bash

# Test the resend-inbound edge function locally

FUNCTION_URL="http://127.0.0.1:64321/functions/v1/resend-inbound"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"

echo "Testing CC email (monitoring only)..."
curl -i --location --request POST "$FUNCTION_URL" \
  --header "Authorization: Bearer $ANON_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "from": "john@example.com",
    "to": ["external@example.com"],
    "cc": ["support@acme.acme.bldx.run"],
    "subject": "Project Update",
    "text": "Here is the latest project update...",
    "message_id": "test-cc-001"
  }'

echo -e "\n\n"

echo "Testing TO email (direct response)..."
curl -i --location --request POST "$FUNCTION_URL" \
  --header "Authorization: Bearer $ANON_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "from": "jane@example.com",
    "to": ["support@acme.acme.bldx.run"],
    "subject": "Need Help",
    "text": "Can you help me with this issue?",
    "html": "<p>Can you help me with this issue?</p>",
    "message_id": "test-to-001",
    "attachments": [
      {
        "filename": "screenshot.png",
        "content_type": "image/png",
        "size": 12345,
        "url": "https://api.resend.com/attachments/test-123"
      }
    ]
  }'
