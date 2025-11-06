# Agents Guide

Agents are autonomous AI systems that use tools and reasoning to accomplish tasks. AIMQ provides a decorator-based framework for building production-ready agents powered by LangGraph.

## What Are Agents?

An agent is a program that:

1. **Reasons** about what action to take
2. **Acts** by executing tools
3. **Observes** the results
4. **Repeats** until the task is complete

Unlike traditional workflows with fixed steps, agents make dynamic decisions based on the current context and available information.

### When to Use Agents

**Use agents when:**

- Task requires dynamic decision-making
- Multiple tools available, but which to use depends on context
- Multi-turn conversations or research needed
- Problem-solving approach varies by input
- Need to handle unexpected scenarios adaptively

**Use workflows instead when:**

- Steps are known upfront and deterministic
- Simple ETL or pipeline processing
- No reasoning required
- Performance is critical (workflows are faster)

**Examples:**

- ✅ **Agent**: "Analyze these documents and answer questions" (tools: read, search, summarize)
- ✅ **Agent**: "Research topic X and compile a report" (tools: web search, database query)
- ❌ **Workflow**: "Read file → Parse CSV → Store in DB" (fixed steps)
- ❌ **Workflow**: "OCR image → Extract fields → Validate" (deterministic)

## Built-in Agents

AIMQ includes two production-ready agent implementations.

### ReActAgent

**Pattern**: Reasoning + Acting

The ReAct agent implements the "Reasoning and Acting" pattern from [Yao et al. 2022](https://arxiv.org/abs/2210.03629). It alternates between thinking about what to do and executing actions until reaching a final answer.

**How It Works:**

```
1. Reason: Think about what to do next
2. Act: Execute a tool (or provide final answer)
3. Observe: See the tool result
4. Repeat: Go back to reasoning with new information
```

**Use Cases:**

- Question answering with tools
- Document analysis and research
- Multi-step information gathering
- Complex problem-solving
- Interactive assistance

**Example Usage:**

```python
from aimq.agents import ReActAgent
from aimq.tools.supabase import ReadFile, ReadRecord
from aimq.tools.ocr import ImageOCR
from aimq.worker import Worker

worker = Worker()

agent = ReActAgent(
    tools=[
        ReadFile(),      # Read files from Supabase storage
        ReadRecord(),    # Query Supabase database
        ImageOCR(),      # Extract text from images
    ],
    system_prompt="""You are a helpful document assistant.

    Available tools:
    - read_file: Read text files and documents
    - read_record: Query structured data in database
    - image_ocr: Extract text from images

    Always:
    - Use tools to gather evidence before answering
    - Cite sources in your responses
    - Be thorough but efficient
    - Provide clear, actionable answers
    """,
    llm="mistral-large-latest",
    temperature=0.1,      # Low for consistent reasoning
    memory=True,          # Enable conversation history
    max_iterations=10     # Prevent infinite loops
)

worker.assign(agent, queue="doc-qa", timeout=900, delete_on_finish=False)
```

**Configuration Options:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tools` | List[BaseTool] | [] | Tools the agent can use |
| `system_prompt` | str | "You are a helpful AI assistant." | Agent instructions |
| `llm` | str \| BaseChatModel | "mistral-large-latest" | LLM model |
| `temperature` | float | 0.1 | LLM temperature |
| `memory` | bool | False | Enable checkpointing |
| `max_iterations` | int | 10 | Maximum reasoning loops |

**Job Format:**

```json
{
  "messages": [
    {"role": "user", "content": "What is in the Q1 sales report?"}
  ],
  "tools": ["read_file", "read_record"],
  "iteration": 0,
  "errors": []
}
```

**Multi-turn Example:**

```json
// First message
{
  "messages": [
    {"role": "user", "content": "Read the Q1 report"}
  ],
  "thread_id": "user-123-session-1",
  "tools": ["read_file"],
  "iteration": 0,
  "errors": []
}

// Follow-up message
{
  "messages": [
    {"role": "user", "content": "Now compare it to Q2"}
  ],
  "thread_id": "user-123-session-1",  // Same thread
  "tools": ["read_file"],
  "iteration": 0,
  "errors": []
}
```

### PlanExecuteAgent

**Pattern**: Planning then Execution

The Plan-Execute agent first creates a complete plan, then executes steps sequentially. It can replan if steps fail or new information emerges.

**How It Works:**

```
1. Plan: Create step-by-step plan
2. Execute: Run each step in order
3. Observe: Check results
4. Replan: Adjust plan if needed (optional)
5. Finalize: Compile results
```

**Use Cases:**

- Complex tasks requiring upfront planning
- Multi-step workflows with dependencies
- Batch processing
- Tasks where order matters
- Structured project execution

**Example Usage:**

```python
from aimq.agents import PlanExecuteAgent
from aimq.tools.supabase import ReadFile, WriteRecord

worker = Worker()

agent = PlanExecuteAgent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="""You are an expert task planner.

    When creating plans:
    - Break tasks into clear, actionable steps
    - Order steps logically with dependencies
    - Be specific about what each step accomplishes
    - Include validation and error handling steps

    When executing:
    - Follow the plan systematically
    - Verify each step completes successfully
    - Replan if you encounter unexpected issues
    """,
    llm="mistral-large-latest",
    temperature=0.2,  # Slight creativity for planning
    memory=True
)

worker.assign(agent, queue="planner", timeout=1200, delete_on_finish=False)
```

**Configuration Options:**

Same as ReActAgent, but no `max_iterations` (determined by plan length).

**Job Format:**

```json
{
  "input": "Analyze all Q1 reports and create a summary document",
  "plan": [],
  "current_step": 0,
  "step_results": [],
  "final_output": null,
  "needs_replan": false
}
```

**When to Use vs ReAct:**

| Scenario | Use ReAct | Use Plan-Execute |
|----------|-----------|------------------|
| Unknown number of steps | ✅ | ❌ |
| Interactive exploration | ✅ | ❌ |
| Clear steps upfront | ❌ | ✅ |
| Complex dependencies | ❌ | ✅ |
| Batch processing | ❌ | ✅ |
| Real-time research | ✅ | ❌ |

## Creating Custom Agents

Build specialized agents using the `@agent` decorator.

### Step-by-Step Tutorial

#### 1. Define Agent with Decorator

```python
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph

from aimq.langgraph import agent
from aimq.tools.supabase import ReadFile, WriteRecord
from aimq.worker import Worker

@agent(
    tools=[ReadFile(), WriteRecord()],
    system_prompt="""You are a data analysis specialist.
    You analyze data files and provide insights.""",
    llm="mistral-large-latest",
    temperature=0.2,
    memory=True
)
def data_analyst(graph: StateGraph, config: dict) -> StateGraph:
    """
    Custom agent that analyzes data files.

    The config dict contains:
    - tools: List[BaseTool]
    - system_prompt: str
    - llm: str
    - temperature: float
    - memory: bool
    """

    def analyze_node(state):
        """Main analysis node."""
        from aimq.clients.mistral import get_mistral_client

        # Extract user query
        messages = state.get("messages", [])
        if not messages:
            return {"errors": ["No messages provided"]}

        user_msg = next(
            (m for m in reversed(messages) if isinstance(m, HumanMessage)),
            None
        )
        if not user_msg:
            return {"errors": ["No user message found"]}

        # Get tools from config
        read_tool = next(
            (t for t in config["tools"] if t.name == "read_file"),
            None
        )

        # Read file
        try:
            content = read_tool.invoke({"path": user_msg.content})
        except Exception as e:
            return {"errors": [f"Failed to read file: {e}"]}

        # Analyze with LLM
        client = get_mistral_client()
        response = client.chat.completions.create(
            model=config["llm"],
            messages=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": f"Analyze: {content}"}
            ],
            temperature=config["temperature"]
        )

        analysis = response.choices[0].message.content

        return {
            "messages": [AIMessage(content=analysis)],
            "final_answer": analysis,
            "iteration": state.get("iteration", 0) + 1
        }

    # Build graph
    graph.add_node("analyze", analyze_node)
    graph.add_edge("analyze", END)
    graph.set_entry_point("analyze")

    return graph
```

#### 2. Create and Assign Instance

```python
worker = Worker()
analyst = data_analyst()
worker.assign(analyst, queue="analyst", timeout=600)
```

#### 3. Send Jobs

```bash
aimq send analyst '{
  "messages": [
    {"role": "user", "content": "data/sales_2024.csv"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

### Agent State

Agents use `AgentState` by default, which provides standard fields for agentic workflows.

**Built-in AgentState:**

```python
from typing import Annotated, Any, NotRequired, Sequence
from langchain_core.messages import BaseMessage
from operator import add

class AgentState(TypedDict):
    # Required fields (must be present at initialization)
    messages: Annotated[Sequence[BaseMessage], add]  # Conversation history
    tools: list[str]                                 # Available tool names
    iteration: int                                   # Loop counter
    errors: Annotated[list[str], add]                # Accumulated errors

    # Optional fields (populated during execution)
    current_tool: NotRequired[str]                   # Tool being executed
    tool_input: NotRequired[dict]                    # Input for tool
    tool_output: NotRequired[Any]                    # Tool result
    final_answer: NotRequired[str]                   # Agent's response
    tenant_id: NotRequired[str]                      # Multi-tenancy
    metadata: NotRequired[dict[str, Any]]            # Custom metadata
```

**Field Descriptions:**

- `messages`: LangChain message history (HumanMessage, AIMessage, SystemMessage)
- `tools`: List of available tool names (strings)
- `iteration`: Counter to track reasoning loops
- `errors`: List of errors (accumulates with `add` reducer)
- `current_tool`: Name of tool being executed (optional)
- `tool_input`: Arguments for tool (optional)
- `tool_output`: Result from tool execution (optional)
- `final_answer`: Agent's final response (optional)
- `tenant_id`: For multi-tenant isolation (optional)
- `metadata`: Custom data (optional)

**Creating Custom Agent State:**

Extend `AgentState` for additional fields:

```python
from aimq.langgraph.states import AgentState

class DataAnalystState(AgentState):
    """Extended state for data analyst."""

    # Add custom fields
    data_source: NotRequired[str]
    analysis_type: NotRequired[str]
    confidence_score: NotRequired[float]
    recommendations: NotRequired[list[str]]

@agent(state_class=DataAnalystState)
def data_analyst(graph: StateGraph, config: dict) -> StateGraph:
    def analyze_node(state: DataAnalystState):
        # Access custom fields
        source = state.get("data_source")
        return {
            "confidence_score": 0.95,
            "recommendations": ["Action 1", "Action 2"]
        }

    # Build graph...
    return graph
```

### Implementing Nodes

Node functions receive state and return state updates.

**Node Function Signature:**

```python
def my_node(state: AgentState) -> AgentState:
    """
    Process state and return updates.

    Args:
        state: Current agent state

    Returns:
        Dict with state updates (not full state)
    """
    # Access state
    messages = state.get("messages", [])
    iteration = state["iteration"]

    # Process...

    # Return updates only
    return {
        "messages": [AIMessage(content="Result")],
        "iteration": iteration + 1
    }
```

**State Update Rules:**

- Return dict with fields to update (not full state)
- Fields with `add` reducer accumulate (messages, errors)
- Other fields replace previous values
- Use `NotRequired` for optional fields

**Error Handling:**

```python
def my_node(state: AgentState) -> AgentState:
    try:
        result = risky_operation()
        return {"final_answer": result}
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        return {
            "errors": [f"Error in my_node: {e}"],
            "iteration": state.get("iteration", 0) + 1
        }
```

### Adding Tools

Tools provide capabilities to agents.

**Using Built-in Tools:**

```python
from aimq.tools.supabase import ReadFile, ReadRecord, WriteFile, WriteRecord
from aimq.tools.ocr import ImageOCR
from aimq.tools.pdf import PageSplitter

@agent(
    tools=[
        ReadFile(),       # Read from Supabase storage
        WriteFile(),      # Write to Supabase storage
        ReadRecord(),     # Query Supabase database
        WriteRecord(),    # Insert into Supabase database
        ImageOCR(),       # Extract text from images
        PageSplitter(),   # Split PDF into pages
    ]
)
def my_agent(graph, config):
    # Tools available in config["tools"]
    return graph
```

**Creating Custom Tools:**

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    """Input schema for calculator."""
    expression: str = Field(..., description="Math expression to evaluate")

class Calculator(BaseTool):
    """Calculate math expressions."""

    name = "calculator"
    description = "Evaluate mathematical expressions. Example: '2 + 2'"
    args_schema = CalculatorInput

    def _run(self, expression: str) -> str:
        """Execute calculation."""
        try:
            result = eval(expression)  # Note: Use safe eval in production
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

@agent(tools=[Calculator()])
def math_agent(graph, config):
    return graph
```

**Tool Validation:**

AIMQ automatically validates tool inputs:

```python
# Tools with args_schema are validated
class MyToolInput(BaseModel):
    path: str = Field(..., description="File path")
    max_size: int = Field(default=1000, description="Max file size")

class MyTool(BaseTool):
    args_schema = MyToolInput  # Enables validation

    def _run(self, path: str, max_size: int = 1000):
        # Input is validated before this runs
        pass
```

### LLM Integration

Agents can use any LangChain-compatible LLM.

**String Model Names:**

```python
@agent(llm="mistral-large-latest")
def my_agent(graph, config):
    # config["llm"] is a ChatMistralAI instance
    return graph
```

**LLM Objects:**

```python
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

@agent(llm=ChatMistralAI(model="mistral-large-latest", temperature=0.1))
def mistral_agent(graph, config):
    return graph

@agent(llm=ChatOpenAI(model="gpt-4", temperature=0.2))
def openai_agent(graph, config):
    return graph
```

**Accessing LLM in Nodes:**

```python
@agent(llm="mistral-large-latest", temperature=0.3)
def my_agent(graph: StateGraph, config: dict) -> StateGraph:

    def reasoning_node(state):
        from aimq.clients.mistral import get_mistral_client

        # Option 1: Use config LLM (recommended)
        llm = config["llm"]
        temp = config["temperature"]

        # Option 2: Use client directly
        client = get_mistral_client()
        response = client.chat.completions.create(
            model="mistral-large-latest",
            messages=[...],
            temperature=temp
        )

        return {"messages": [AIMessage(content=response.choices[0].message.content)]}

    return graph
```

**Temperature Guidelines:**

- `0.0`: Deterministic, factual (retrieval, analysis)
- `0.1-0.3`: Focused, consistent (classification, reasoning)
- `0.4-0.7`: Balanced creativity (writing, planning)
- `0.8-1.0`: Maximum creativity (brainstorming, fiction)

## Configuration Options

### Tools

List of LangChain `BaseTool` objects:

```python
@agent(tools=[ReadFile(), ImageOCR()])
def my_agent(graph, config):
    # Access in nodes
    tools = config["tools"]
    read_tool = next(t for t in tools if t.name == "read_file")
    result = read_tool.invoke({"path": "file.txt"})
    return graph
```

### System Prompt

Agent instructions and persona:

```python
@agent(
    system_prompt="""You are a helpful research assistant.

    Your role:
    - Answer questions using available tools
    - Cite sources for all claims
    - Be thorough but concise
    - Admit uncertainty when appropriate

    Guidelines:
    - Use read_file for document access
    - Use image_ocr for images
    - Always verify information before responding
    """
)
def research_agent(graph, config):
    # Access in nodes
    prompt = config["system_prompt"]
    return graph
```

### Memory

Enable conversation history and checkpointing:

```python
@agent(memory=True)
def conversational_agent(graph, config):
    # Previous messages preserved across jobs
    # Requires thread_id in job data
    return graph
```

**Requirements:**

- Supabase connection configured
- LangGraph schema created (see [LangGraph guide](./langgraph.md#database-schema-setup))
- `thread_id` in job data

### Reply Function

Custom callback for sending agent responses:

```python
def custom_reply(message: str, metadata: dict):
    """Custom reply handler."""
    print(f"Agent says: {message}")
    print(f"Metadata: {metadata}")

@agent(reply_function=custom_reply)
def my_agent(graph, config):
    def my_node(state):
        # Send update
        config["reply_function"]("Processing step 1", {"step": 1})
        return {}

    return graph
```

**Default Reply Function:**

Enqueues responses to `process_agent_response` queue:

```python
def default_reply_function(message: str, metadata: dict):
    provider = SupabaseQueueProvider()
    provider.send("process_agent_response", {
        "message": message,
        "metadata": metadata,
        "timestamp": datetime.now().isoformat()
    })
```

### Security Controls

Whitelist allowed LLM overrides and prompt changes:

```python
from langchain_mistralai import ChatMistralAI

@agent(
    llm="mistral-large-latest",
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    },
    allow_system_prompt=True  # Allow job-level prompt override
)
def secure_agent(graph, config):
    return graph
```

**Job Override Example:**

```json
{
  "messages": [...],
  "llm": "small",
  "system_prompt": "Be very concise",
  "tools": [],
  "iteration": 0,
  "errors": []
}
```

**Security Rules:**

- LLM override only allowed if key in `allowed_llms`
- System prompt override only allowed if `allow_system_prompt=True`
- Raises `OverrideSecurityError` on violation

## Advanced Topics

### Multi-turn Conversations

Use `thread_id` for conversation continuity:

```python
@agent(memory=True)
def chat_agent(graph, config):
    return graph

# First message
{
  "messages": [{"role": "user", "content": "Hello"}],
  "thread_id": "conversation-123",
  "tools": [],
  "iteration": 0,
  "errors": []
}

# Follow-up (history preserved)
{
  "messages": [{"role": "user", "content": "Tell me more"}],
  "thread_id": "conversation-123",  # Same ID
  "tools": [],
  "iteration": 0,
  "errors": []
}
```

### Tool Output Processing

Handle tool results in reasoning loop:

```python
def reasoning_node(state):
    # Check if tool output available
    tool_output = state.get("tool_output")

    if tool_output:
        # Process tool result
        analysis = analyze(tool_output)
        return {"final_answer": analysis}

    # No output yet, decide what tool to call
    return {
        "current_tool": "read_file",
        "tool_input": {"path": "data.txt"}
    }
```

### Error Handling

Collect and handle errors gracefully:

```python
def my_node(state):
    errors = state.get("errors", [])

    # Check for previous errors
    if errors:
        logger.warning(f"Previous errors: {errors}")
        # Decide how to handle: retry, skip, or fail

    try:
        result = operation()
        return {"result": result}
    except Exception as e:
        # Add to error list
        return {"errors": [f"Node failed: {e}"]}
```

### Performance Tuning

Optimize agent performance:

**1. Set Max Iterations:**

```python
agent = ReActAgent(max_iterations=5)  # Faster but less thorough
agent = ReActAgent(max_iterations=20)  # Slower but more capable
```

**2. Adjust Temperature:**

```python
@agent(temperature=0.0)  # Deterministic, fast
@agent(temperature=0.5)  # Balanced
```

**3. Use Smaller Models:**

```python
@agent(
    llm="mistral-small-latest",  # Faster, cheaper
    allowed_llms={
        "small": ChatMistralAI(model="mistral-small-latest"),
        "large": ChatMistralAI(model="mistral-large-latest"),
    }
)
```

**4. Disable Checkpointing:**

```python
@agent(memory=False)  # Faster, no database overhead
```

**5. Limit Tools:**

```python
# Provide only necessary tools
@agent(tools=[ReadFile()])  # Not all 10 tools
```

## Examples

Complete working examples in `examples/langgraph/`:

**Using Built-in ReAct Agent:**

```bash
uv run python examples/langgraph/using_builtin_react.py
```

**Using Built-in Plan-Execute Agent:**

```bash
uv run python examples/langgraph/using_builtin_plan_execute.py
```

**Custom Agent with Decorator:**

```bash
uv run python examples/langgraph/custom_agent_decorator.py
```

**Job-Level Overrides:**

```bash
uv run python examples/langgraph/job_level_overrides.py
```

## API Reference

See complete API documentation: [LangGraph API Reference](../api/langgraph.md)

**Key Classes:**

- `aimq.agents.ReActAgent`: Built-in ReAct agent
- `aimq.agents.PlanExecuteAgent`: Built-in Plan-Execute agent
- `aimq.langgraph.states.AgentState`: Standard agent state
- `aimq.langgraph.decorators.agent`: Agent decorator

**Key Functions:**

- `resolve_llm()`: Convert LLM parameter to instance
- `get_default_llm()`: Get configured default LLM
- `default_reply_function()`: Default response handler

## Next Steps

- **[Workflows Guide](./workflows.md)**: Learn about non-agentic workflows
- **[LangGraph Integration](./langgraph.md)**: Main integration guide
- **[API Reference](../api/langgraph.md)**: Complete API documentation
- **Examples**: `examples/langgraph/` for working code
