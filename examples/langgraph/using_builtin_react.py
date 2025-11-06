"""
Example: Using built-in ReActAgent

Demonstrates how to configure and use the pre-built ReAct agent
for document question answering with tools.

The ReAct (Reasoning + Acting) pattern enables the agent to:
1. Reason about what action to take next
2. Execute tools to gather information
3. Observe results and continue reasoning
4. Provide final answers based on gathered evidence

Usage:
    # Terminal 1: Start worker
    uv run python examples/langgraph/using_builtin_react.py

    # Terminal 2: Send test job
    aimq send doc-qa '{
      "messages": [
        {"role": "user", "content": "What files are in the documents folder?"}
      ],
      "tools": ["read_file"],
      "iteration": 0,
      "errors": []
    }'
"""

from aimq.agents import ReActAgent
from aimq.tools.ocr import ImageOCR
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.worker import Worker

# Initialize worker
worker = Worker()

# Configure ReAct agent with tools
agent = ReActAgent(
    tools=[
        ReadFile(),  # Read files from Supabase storage
        ReadRecord(),  # Read records from Supabase database
        ImageOCR(),  # Extract text from images
    ],
    system_prompt="""You are a helpful document assistant.
    You can read files, extract text from images, and query databases.
    Always provide clear, concise answers based on the information you gather.

    When reading files:
    - Use read_file for text files and documents
    - Use image_ocr for images and scanned documents
    - Use read_record to query structured data

    Be thorough but efficient in your tool usage.""",
    llm="mistral-large-latest",
    temperature=0.1,  # Low temperature for consistent, focused responses
    memory=True,  # Enable checkpointing for resumable workflows
    max_iterations=10,  # Prevent infinite loops
)

# Assign to queue
# timeout=900 (15 minutes) allows for complex multi-step reasoning
# delete_on_finish=False keeps jobs for debugging/replay
worker.assign(agent, queue="doc-qa", timeout=900, delete_on_finish=False)

if __name__ == "__main__":
    print("=" * 60)
    print("ReAct Agent Worker - Document Q&A")
    print("=" * 60)
    print("\nConfiguration:")
    print("  Queue: doc-qa")
    print("  Timeout: 900s (15 minutes)")
    print("  Tools: ReadFile, ReadRecord, ImageOCR")
    print("  LLM: mistral-large-latest")
    print("  Memory: Enabled (checkpointing)")
    print("  Max Iterations: 10")

    print("\n" + "-" * 60)
    print("Example Jobs")
    print("-" * 60)

    print("\n1. Simple file query:")
    print("   aimq send doc-qa '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "Read the file at documents/report.pdf"}')
    print("     ],")
    print('     "tools": ["read_file"],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n2. Multi-step reasoning:")
    print("   aimq send doc-qa '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "Compare sales data from Q1 and Q2 reports"}')
    print("     ],")
    print('     "tools": ["read_file", "read_record"],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n3. OCR processing:")
    print("   aimq send doc-qa '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "Extract text from images/invoice.jpg"}')
    print("     ],")
    print('     "tools": ["image_ocr"],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n4. Resumable workflow (with thread_id):")
    print("   aimq send doc-qa '{")
    print('     "messages": [')
    print('       {"role": "user", "content": "Continue analyzing the document"}')
    print("     ],")
    print('     "thread_id": "user-123-session-456",')
    print('     "tools": ["read_file"],')
    print('     "iteration": 0,')
    print('     "errors": []')
    print("   }'")

    print("\n" + "=" * 60)
    print("Starting worker... Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    worker.start()
