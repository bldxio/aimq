# Phase 2: Built-in Agents

**Status**: ⏳ Not Started
**Priority**: 1 (Critical)
**Estimated**: 4-5 hours
**Dependencies**: Phase 1 (Complete)

---

## Objectives

Implement production-ready built-in agents using the decorator infrastructure:
1. Create BaseAgent class for agent implementations
2. Implement ReActAgent (Reasoning + Acting pattern)
3. Implement PlanExecuteAgent (Planning and execution pattern)
4. Integrate logger support throughout (Fix #11)
5. Add tool input validation for security (Fix #12)

## Critical Fixes Applied

- **Fix #11**: Logger integration in all agent nodes
- **Fix #12**: Tool input validation with security checks

---

## Implementation Steps

### 2.1 Base Agent Class (1 hour)

#### 2.1.1 Create Module Structure

**Action**: Create the agents module:

```bash
mkdir -p src/aimq/agents
touch src/aimq/agents/__init__.py
```

#### 2.1.2 Implement BaseAgent

**File**: `src/aimq/agents/base.py`

**Action**: Create base class for agents:

```python
"""Base class for built-in agents."""

from typing import List, Any
from langchain.tools import BaseTool
from langgraph.graph import StateGraph
from aimq.langgraph.checkpoint import get_checkpointer
from aimq.langgraph.states import AgentState


class BaseAgent:
    """Base class for built-in agents.

    Provides common functionality for agent implementations:
    - Graph building and compilation
    - Checkpointing integration
    - Runnable interface (invoke, stream)
    """

    def __init__(
        self,
        tools: List[BaseTool],
        system_prompt: str,
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
    ):
        """Initialize agent.

        Args:
            tools: List of LangChain tools the agent can use
            system_prompt: Agent instructions
            llm: LLM model name (default: "mistral-large-latest")
            temperature: LLM temperature (default: 0.1)
            memory: Enable conversation memory (default: False)
        """
        self.tools = tools
        self.system_prompt = system_prompt
        self.llm = llm
        self.temperature = temperature
        self.memory = memory

        # Build and compile graph
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the agent's graph. Override in subclasses."""
        raise NotImplementedError

    def _compile(self):
        """Compile the graph with optional checkpointing."""
        checkpointer = get_checkpointer() if self.memory else None
        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """Invoke the agent (implements Runnable interface)."""
        return self._compiled.invoke(input, config)

    def stream(self, input: dict, config: dict | None = None):
        """Stream agent execution (implements Runnable interface)."""
        return self._compiled.stream(input, config)
```

#### 2.1.3 Update Module Exports

**File**: `src/aimq/agents/__init__.py`

**Action**: Export agents:

```python
"""Built-in LangGraph agents for AIMQ."""

from aimq.agents.react import ReActAgent
from aimq.agents.plan_execute import PlanExecuteAgent

__all__ = ["ReActAgent", "PlanExecuteAgent"]
```

**Validation**: Test import:

```bash
uv run python -c "from aimq.agents.base import BaseAgent; print('BaseAgent imported')"
```

---

### 2.2 ReActAgent (2 hours)

**File**: `src/aimq/agents/react.py`

**Action**: Implement ReAct agent with tool validation (Fix #12) and logging (Fix #11):

```python
"""ReAct (Reasoning + Acting) Agent implementation."""

from typing import List, Literal
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from aimq.agents.base import BaseAgent
from aimq.langgraph.states import AgentState
from aimq.langgraph.validation import ToolInputValidator
from aimq.langgraph.exceptions import ToolValidationError
import logging

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """
    ReAct agent that reasons about actions and executes tools iteratively.

    Pattern:
    1. Reason about what to do
    2. Execute tool if needed
    3. Observe results
    4. Repeat until done

    Args:
        tools: List of LangChain tools the agent can use
        system_prompt: Agent instructions
        llm: LLM model name (default: "mistral-large-latest")
        temperature: LLM temperature (default: 0.1)
        memory: Enable conversation memory (default: False)
        max_iterations: Max reasoning loops (default: 10)

    Example:
        from aimq.agents import ReActAgent
        from aimq.tools.supabase import ReadFile
        from aimq.tools.ocr import ImageOCR

        agent = ReActAgent(
            tools=[ReadFile(), ImageOCR()],
            system_prompt="You are a document assistant",
            memory=True
        )

        worker.assign(agent, queue="doc-agent")
    """

    def __init__(
        self,
        tools: List[BaseTool],
        system_prompt: str = "You are a helpful AI assistant.",
        llm: str = "mistral-large-latest",
        temperature: float = 0.1,
        memory: bool = False,
        max_iterations: int = 10,
    ):
        self.max_iterations = max_iterations
        self.validator = ToolInputValidator()  # Fix #12
        super().__init__(tools, system_prompt, llm, temperature, memory)

    def _build_graph(self) -> StateGraph:
        """Build ReAct agent graph."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("reason", self._reasoning_node)
        graph.add_node("act", self._action_node)

        # Add conditional routing
        graph.add_conditional_edges(
            "reason",
            self._should_continue,
            {
                "act": "act",
                "reason": "reason",
                "end": END,
            }
        )

        # After action, go back to reasoning
        graph.add_edge("act", "reason")

        # Start with reasoning
        graph.set_entry_point("reason")

        return graph

    def _reasoning_node(self, state: AgentState) -> AgentState:
        """Reasoning node: decide what to do next (Fix #11)."""
        from aimq.clients.mistral import get_mistral_client

        logger.info(f"ReAct reasoning step {state['iteration']}")  # Fix #11

        client = get_mistral_client()

        # Build ReAct prompt
        prompt = self._build_react_prompt(state)

        try:
            # Get LLM decision
            response = client.chat.completions.create(
                model=self.llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )

            # Parse action from response
            action = self._parse_action(response.choices[0].message.content)

            logger.debug(f"Reasoning result: {action}")  # Fix #11

            return {
                "messages": [{
                    "role": "assistant",
                    "content": response.choices[0].message.content
                }],
                "current_tool": action.get("tool"),
                "tool_input": action.get("input"),
                "final_answer": action.get("answer"),
                "iteration": state["iteration"] + 1,
            }

        except Exception as e:
            logger.error(f"Reasoning failed: {e}", exc_info=True)  # Fix #11
            return {
                "errors": [f"Reasoning error: {str(e)}"],
                "iteration": state["iteration"] + 1,
            }

    def _action_node(self, state: AgentState) -> AgentState:
        """Action node: execute the chosen tool with validation (Fix #11, #12)."""
        tool_name = state.get("current_tool")
        tool_input = state.get("tool_input", {})

        logger.info(f"Executing tool: {tool_name}")  # Fix #11

        # Find tool
        tool = next((t for t in self.tools if t.name == tool_name), None)

        if not tool:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)  # Fix #11
            return {
                "messages": [{"role": "system", "content": error_msg}],
                "tool_output": error_msg,
                "errors": [error_msg],
            }

        # Validate tool input (Fix #12)
        try:
            validated_input = self.validator.validate(tool, tool_input)
            logger.debug(f"Tool input validated: {validated_input}")  # Fix #11
        except ToolValidationError as e:
            logger.error(f"Tool validation failed: {e}")  # Fix #11
            return {
                "messages": [{"role": "system", "content": str(e)}],
                "tool_output": str(e),
                "errors": [str(e)],
            }

        # Execute tool
        try:
            result = tool.invoke(validated_input)
            logger.info(f"Tool execution successful: {tool_name}")  # Fix #11
            return {
                "messages": [{
                    "role": "system",
                    "content": f"Tool result: {result}"
                }],
                "tool_output": str(result),
            }
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(error_msg, exc_info=True)  # Fix #11
            return {
                "messages": [{"role": "system", "content": error_msg}],
                "tool_output": error_msg,
                "errors": [str(e)],
            }

    def _should_continue(
        self, state: AgentState
    ) -> Literal["act", "reason", "end"]:
        """Decide next step based on state."""
        # Stop if we have an answer or hit max iterations
        if state.get("final_answer") or state["iteration"] >= self.max_iterations:
            if state["iteration"] >= self.max_iterations:
                logger.warning(
                    f"Max iterations reached: {self.max_iterations}"
                )  # Fix #11
            return "end"

        # Execute tool if one was chosen
        if state.get("current_tool"):
            return "act"

        # Continue reasoning
        return "reason"

    def _build_react_prompt(self, state: AgentState) -> str:
        """Build ReAct prompt with history."""
        system = f"""{self.system_prompt}

You have access to these tools:
{self._format_tools()}

Respond in this format:
THOUGHT: <your reasoning>
ACTION: <tool_name>
INPUT: <tool input as JSON>

OR if you have the final answer:
THOUGHT: <your reasoning>
ANSWER: <final answer>
"""

        history = "\n\n".join([
            f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}"
            for msg in state.get("messages", [])
        ])

        return f"{system}\n\n{history}"

    def _format_tools(self) -> str:
        """Format tool descriptions."""
        return "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])

    def _parse_action(self, content: str) -> dict:
        """Parse LLM response into action dict."""
        import json

        lines = content.strip().split("\n")
        action = {}

        for line in lines:
            if line.startswith("ACTION:"):
                action["tool"] = line.replace("ACTION:", "").strip()
            elif line.startswith("INPUT:"):
                try:
                    action["input"] = json.loads(
                        line.replace("INPUT:", "").strip()
                    )
                except json.JSONDecodeError:
                    action["input"] = {}
            elif line.startswith("ANSWER:"):
                action["answer"] = line.replace("ANSWER:", "").strip()

        return action
```

**Validation**: Test import and instantiation:

```bash
uv run python -c "
from aimq.agents import ReActAgent
from langchain.tools import BaseTool

# Create dummy tool
class DummyTool(BaseTool):
    name = 'dummy'
    description = 'Test tool'
    def _run(self, input): return 'result'

agent = ReActAgent(tools=[DummyTool()], system_prompt='Test')
print('ReActAgent created successfully')
"
```

---

### 2.3 PlanExecuteAgent (1-2 hours)

**File**: `src/aimq/agents/plan_execute.py`

**Action**: Implement Plan-Execute agent with logging (Fix #11):

```python
"""Plan-and-Execute Agent implementation."""

from typing import List, TypedDict, Annotated
from operator import add
from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END
from aimq.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)


class PlanExecuteState(TypedDict):
    """State for plan-execute agent."""
    input: str
    plan: list[str]
    current_step: int
    step_results: Annotated[list[dict], add]
    final_output: dict | None
    needs_replan: bool


class PlanExecuteAgent(BaseAgent):
    """
    Plan-and-Execute agent that creates a plan then executes steps sequentially.

    Pattern:
    1. Create execution plan
    2. Execute each step
    3. Collect results
    4. Replan if needed

    Args:
        tools: List of LangChain tools
        system_prompt: Agent instructions
        llm: LLM model name
        temperature: LLM temperature
        memory: Enable checkpointing

    Example:
        agent = PlanExecuteAgent(
            tools=[ReadFile(), WriteRecord()],
            system_prompt="You are a task planner",
            memory=True
        )

        worker.assign(agent, queue="planner")
    """

    def _build_graph(self) -> StateGraph:
        """Build plan-execute graph."""
        graph = StateGraph(PlanExecuteState)

        graph.add_node("plan", self._plan_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("finalize", self._finalize_node)

        graph.add_edge("plan", "execute")
        graph.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "execute": "execute",
                "replan": "plan",
                "finalize": "finalize",
            }
        )
        graph.add_edge("finalize", END)

        graph.set_entry_point("plan")

        return graph

    def _plan_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Generate execution plan (Fix #11)."""
        from aimq.clients.mistral import get_mistral_client

        logger.info("Creating execution plan")  # Fix #11

        client = get_mistral_client()

        prompt = f"""{self.system_prompt}

Task: {state['input']}

Available tools: {self._format_tools()}

Create a step-by-step plan. Respond with a numbered list:
1. <step 1>
2. <step 2>
...
"""

        try:
            response = client.chat.completions.create(
                model=self.llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )

            # Parse plan
            steps = self._parse_plan(response.choices[0].message.content)

            logger.info(f"Plan created with {len(steps)} steps")  # Fix #11

            return {
                "plan": steps,
                "current_step": 0,
            }

        except Exception as e:
            logger.error(f"Planning failed: {e}", exc_info=True)  # Fix #11
            return {
                "plan": ["Error: Failed to create plan"],
                "current_step": 0,
            }

    def _execute_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Execute current step (Fix #11)."""
        current = state["plan"][state["current_step"]]

        logger.info(
            f"Executing step {state['current_step'] + 1}/{len(state['plan'])}: {current[:50]}..."
        )  # Fix #11

        # Execute with tools (simplified)
        result = self._execute_step_with_tools(current)

        logger.debug(f"Step result: {result}")  # Fix #11

        return {
            "step_results": [{
                "step": current,
                "result": result,
                "step_number": state["current_step"],
            }],
            "current_step": state["current_step"] + 1,
        }

    def _finalize_node(self, state: PlanExecuteState) -> PlanExecuteState:
        """Compile final output (Fix #11)."""
        logger.info("Finalizing results")  # Fix #11

        return {
            "final_output": {
                "task": state["input"],
                "plan": state["plan"],
                "results": state["step_results"],
                "status": "completed",
            }
        }

    def _should_continue(self, state: PlanExecuteState):
        """Decide next step."""
        if state["current_step"] >= len(state["plan"]):
            return "finalize"
        if state.get("needs_replan"):
            return "replan"
        return "execute"

    def _format_tools(self) -> str:
        """Format tool descriptions."""
        return "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])

    def _parse_plan(self, content: str) -> list[str]:
        """Parse plan from LLM response."""
        lines = content.strip().split("\n")
        steps = []
        for line in lines:
            # Remove numbering (1., 2., etc.)
            if line.strip() and (
                line[0].isdigit() or line.strip()[0] in ['-', '*']
            ):
                step = line.split(".", 1)[-1].strip()
                if step:
                    steps.append(step)
        return steps

    def _execute_step_with_tools(self, step: str) -> str:
        """Execute a step using available tools (simplified)."""
        # Simplified implementation - in production, this would:
        # 1. Parse step to identify needed tool
        # 2. Extract tool inputs
        # 3. Execute tool with validation
        # 4. Return result
        return f"Executed: {step}"
```

**Validation**: Test import and instantiation:

```bash
uv run python -c "
from aimq.agents import PlanExecuteAgent
from langchain.tools import BaseTool

# Create dummy tool
class DummyTool(BaseTool):
    name = 'dummy'
    description = 'Test tool'
    def _run(self, input): return 'result'

agent = PlanExecuteAgent(tools=[DummyTool()], system_prompt='Planner')
print('PlanExecuteAgent created successfully')
"
```

---

## Testing & Validation

### Unit Tests

**File**: `tests/aimq/agents/test_react.py`

```python
import pytest
from aimq.agents import ReActAgent
from langchain.tools import BaseTool


class DummyTool(BaseTool):
    name = "dummy"
    description = "Test tool"

    def _run(self, input: str) -> str:
        return f"Result: {input}"


def test_react_agent_initialization():
    """Test ReActAgent can be initialized."""
    agent = ReActAgent(
        tools=[DummyTool()],
        system_prompt="Test agent",
        max_iterations=5
    )

    assert agent is not None
    assert len(agent.tools) == 1
    assert agent.max_iterations == 5


def test_react_agent_has_compiled_graph():
    """Test agent compiles graph successfully."""
    agent = ReActAgent(
        tools=[DummyTool()],
        system_prompt="Test"
    )

    assert agent._compiled is not None
```

**File**: `tests/aimq/agents/test_plan_execute.py`

```python
import pytest
from aimq.agents import PlanExecuteAgent
from langchain.tools import BaseTool


class DummyTool(BaseTool):
    name = "dummy"
    description = "Test tool"

    def _run(self, input: str) -> str:
        return f"Result: {input}"


def test_plan_execute_agent_initialization():
    """Test PlanExecuteAgent can be initialized."""
    agent = PlanExecuteAgent(
        tools=[DummyTool()],
        system_prompt="Test planner"
    )

    assert agent is not None
    assert len(agent.tools) == 1


def test_parse_plan():
    """Test plan parsing from LLM response."""
    agent = PlanExecuteAgent(
        tools=[DummyTool()],
        system_prompt="Test"
    )

    plan_text = """
    1. Read the file
    2. Process the data
    3. Write results
    """

    steps = agent._parse_plan(plan_text)
    assert len(steps) == 3
    assert "Read the file" in steps[0]
```

---

## Definition of Done

### Code Complete

- [ ] BaseAgent class implemented
- [ ] ReActAgent fully implemented with tool validation (Fix #12)
- [ ] PlanExecuteAgent fully implemented
- [ ] Logger integration throughout (Fix #11)
- [ ] All docstrings complete

### Validation

- [ ] All imports successful
- [ ] Agents instantiate without errors
- [ ] Graphs compile successfully
- [ ] Tool validation working (Fix #12)
- [ ] Logger outputs visible in tests (Fix #11)

### Testing

- [ ] Unit tests created and passing
- [ ] Agent initialization tests pass
- [ ] Graph compilation tests pass
- [ ] Tool validation tests pass

### Documentation

- [ ] All classes documented
- [ ] Usage examples in docstrings
- [ ] Module exports correct

---

## Common Pitfalls

### Missing Tool Validation

**Pitfall**: Executing tools without input validation (security risk)

**Solution**: Always use ToolInputValidator (Fix #12)
```python
# Wrong
result = tool.invoke(tool_input)  # No validation!

# Correct
validator = ToolInputValidator()
validated_input = validator.validate(tool, tool_input)
result = tool.invoke(validated_input)
```

### Missing Logger Integration

**Pitfall**: No visibility into agent execution

**Solution**: Add logger calls at key points (Fix #11)
```python
logger.info(f"Executing tool: {tool_name}")
logger.debug(f"Tool input: {tool_input}")
logger.error(f"Tool failed: {e}", exc_info=True)
```

### State Type Mismatches

**Pitfall**: Using wrong state class in graph

**Solution**: Ensure state matches graph definition
```python
# ReActAgent uses AgentState
graph = StateGraph(AgentState)

# PlanExecuteAgent uses PlanExecuteState
graph = StateGraph(PlanExecuteState)
```

---

## Next Phase

Once Phase 2 is complete:
- [ ] Update PROGRESS.md
- [ ] Move to **Phase 3: Built-in Workflows** ([PHASE3.md](./PHASE3.md))

---

**Phase Owner**: Implementation Team
**Started**: ___________
**Completed**: ___________
**Actual Hours**: ___________
