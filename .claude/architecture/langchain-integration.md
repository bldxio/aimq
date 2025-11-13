# LangChain Integration

## Overview

AIMQ uses LangChain's Runnable interface as the foundation for task processing. Every task in AIMQ is a LangChain Runnable, enabling composition, streaming, and integration with the broader LangChain ecosystem.

## Core Concepts

### Runnable Interface

The `Runnable` is LangChain's universal interface for components:

```python
from langchain.schema.runnable import Runnable

class Runnable:
    def invoke(self, input: dict, config: RunnableConfig | None = None) -> dict:
        """Synchronous execution"""
        pass

    async def ainvoke(self, input: dict, config: RunnableConfig | None = None) -> dict:
        """Async execution"""
        pass

    def stream(self, input: dict, config: RunnableConfig | None = None):
        """Streaming execution"""
        pass
```

### RunnableLambda

Wraps Python functions as Runnables:

```python
from langchain.schema.runnable import RunnableLambda

def process_data(data: dict) -> dict:
    return {"status": "success", "result": data}

# Wrap as Runnable
runnable = RunnableLambda(process_data)

# Now it can be invoked like any Runnable
result = runnable.invoke({"input": "test"})
```

## AIMQ's Runnable Pattern

### Task Registration

Tasks are registered using the `@worker.task()` decorator, which wraps them as Runnables:

```python
from aimq.worker import Worker

worker = Worker()

@worker.task(queue="my-queue", timeout=300)
def process_job(data: dict) -> dict:
    """Process a job from the queue"""
    return {"status": "success"}
```

**Behind the scenes**:
1. Decorator wraps function in `RunnableLambda`
2. Creates a `Queue` with the Runnable
3. Registers queue with the worker

### Queue Processing

The `Queue` class wraps Runnables with queue-specific logic:

```python
class Queue:
    def __init__(self, name: str, runnable: Runnable, timeout: int = 300):
        self.name = name
        self.runnable = runnable
        self.timeout = timeout

    def process(self, job: Job) -> dict:
        # Invoke the Runnable with job data
        config = RunnableConfig(
            metadata={
                "queue_name": self.name,
                "job_id": job.id,
            }
        )
        return self.runnable.invoke(job.data, config)
```

## RunnableConfig

Configuration passed to Runnables for metadata and callbacks:

```python
from langchain.schema.runnable import RunnableConfig

config = RunnableConfig(
    metadata={
        "worker_name": "worker-1",
        "queue_name": "my-queue",
        "job_id": 123,
    },
    callbacks=[...],  # LangSmith tracing, etc.
    tags=["production", "high-priority"],
)

result = runnable.invoke(data, config)
```

**Use cases**:
- Tracing with LangSmith
- Passing context to nested Runnables
- Tagging for monitoring
- Custom callbacks

## Composing Runnables

LangChain Runnables can be composed using the pipe operator:

```python
from langchain.schema.runnable import RunnableLambda

# Define steps
extract = RunnableLambda(lambda x: x["text"])
process = RunnableLambda(lambda x: x.upper())
format_output = RunnableLambda(lambda x: {"result": x})

# Compose into pipeline
pipeline = extract | process | format_output

# Execute
result = pipeline.invoke({"text": "hello"})
# {"result": "HELLO"}
```

**In AIMQ**:
```python
@worker.task(queue="pipeline-queue")
def pipeline_task(data: dict) -> dict:
    # Create pipeline
    pipeline = extract_step | process_step | save_step
    return pipeline.invoke(data)
```

## LangChain Tools

AIMQ tools inherit from `BaseTool`:

```python
from langchain.tools import BaseTool

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "Does something useful"

    def _run(self, input: str) -> str:
        """Synchronous execution"""
        return f"Processed: {input}"

    async def _arun(self, input: str) -> str:
        """Async execution"""
        return f"Processed: {input}"
```

**AIMQ tools**:
- `tools/ocr/image_ocr.py` - ImageOCR tool
- `tools/pdf/page_splitter.py` - PageSplitter tool
- `tools/supabase/` - Supabase operation tools
- `tools/mistral/` - Mistral AI tools

## LLM Integration

AIMQ uses LangChain's chat models:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Invoke
response = llm.invoke("What is 2+2?")
print(response.content)  # "4"

# With messages
from langchain.schema import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are a helpful assistant"),
    HumanMessage(content="What is 2+2?"),
]
response = llm.invoke(messages)
```

**In AIMQ** (see `common/llm.py`):
```python
from aimq.common.llm import get_llm

llm = get_llm(provider="openai", model="gpt-4")
response = llm.invoke("Process this data...")
```

## Tracing with LangSmith

Enable LangChain tracing for debugging and monitoring:

```bash
# .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-api-key
LANGCHAIN_PROJECT=aimq-production
```

**Benefits**:
- Trace Runnable execution
- Monitor LLM calls and costs
- Debug agent reasoning
- Analyze performance

## Streaming Support

LangChain Runnables support streaming:

```python
# Stream tokens from LLM
for chunk in llm.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)

# Stream pipeline results
for chunk in pipeline.stream(input_data):
    process_chunk(chunk)
```

**Future AIMQ feature**: Stream job results back to client

## Async Support

All Runnables support async execution:

```python
import asyncio

async def process_async():
    result = await runnable.ainvoke(data)
    return result

# Run async
result = asyncio.run(process_async())
```

**In AIMQ**: Agents and workflows use async for concurrent tool execution

## Batch Processing

Process multiple inputs in parallel:

```python
# Batch invoke
inputs = [{"text": "hello"}, {"text": "world"}]
results = runnable.batch(inputs)

# Async batch
results = await runnable.abatch(inputs)
```

**Use case**: Process multiple jobs from queue in parallel

## Error Handling

LangChain Runnables propagate exceptions:

```python
try:
    result = runnable.invoke(data)
except ValueError as e:
    logger.error(f"Validation error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

See `patterns/error-handling.md` for AIMQ error patterns.

## Best Practices

### 1. Use RunnableConfig for Context
```python
# ✅ Good: Pass context via config
config = RunnableConfig(metadata={"job_id": job.id})
result = runnable.invoke(data, config)

# ❌ Bad: Modify global state
global current_job_id
current_job_id = job.id
result = runnable.invoke(data)
```

### 2. Compose Runnables
```python
# ✅ Good: Compose small Runnables
pipeline = step1 | step2 | step3

# ❌ Bad: Monolithic function
def do_everything(data):
    # 100+ lines of logic
    ...
```

### 3. Use Type Hints
```python
# ✅ Good: Type hints for inputs/outputs
def process(data: dict[str, Any]) -> dict[str, Any]:
    return {"result": data}

# ❌ Bad: No type hints
def process(data):
    return {"result": data}
```

### 4. Handle Async Properly
```python
# ✅ Good: Use async when needed
async def process_with_llm(data: dict) -> dict:
    result = await llm.ainvoke(data["prompt"])
    return {"result": result.content}

# ❌ Bad: Blocking in async context
async def process_with_llm(data: dict) -> dict:
    result = llm.invoke(data["prompt"])  # Blocks!
    return {"result": result.content}
```

## Common Patterns

### Pattern: LLM Chain
```python
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("human", "{input}"),
])

chain = prompt | llm | output_parser

result = chain.invoke({"input": "What is 2+2?"})
```

### Pattern: Tool-Using Agent
```python
from langchain.agents import create_react_agent

tools = [ImageOCR(), PageSplitter(), ReadRecord()]
agent = create_react_agent(llm, tools, prompt)

result = agent.invoke({"input": "Extract text from image.jpg"})
```

### Pattern: Conditional Routing
```python
from langchain.schema.runnable import RunnableBranch

branch = RunnableBranch(
    (lambda x: x["type"] == "image", image_pipeline),
    (lambda x: x["type"] == "pdf", pdf_pipeline),
    default_pipeline,
)

result = branch.invoke({"type": "image", "data": "..."})
```

## Related

- See `architecture/langgraph-integration.md` for workflow patterns
- See `architecture/key-libraries.md` for LangChain reference
- See `common/llm.py` for LLM initialization
- See `tools/` for LangChain tool implementations

## Resources

- [LangChain Docs](https://python.langchain.com/)
- [Runnable Interface](https://python.langchain.com/docs/expression_language/)
- [LangSmith](https://smith.langchain.com/)
