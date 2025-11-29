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
    from pathlib import Path

    motd_path = Path(__file__).parent / "using_builtin_react_MOTD.md"
    worker.start(motd=str(motd_path), show_info=True)
