# Phase 3: Built-in Workflows

**Status**: ⏳ Not Started
**Priority**: 1 (Critical)
**Estimated**: 3-4 hours
**Dependencies**: Phase 1 (Complete)

---

## Objectives

Implement production-ready built-in workflows:
1. Create BaseWorkflow class
2. Implement DocumentWorkflow (multi-step document processing)
3. Implement MultiAgentWorkflow (supervisor pattern)
4. Integrate logger support throughout (Fix #11)

## Critical Fixes Applied

- **Fix #11**: Logger integration in all workflow nodes

---

## Implementation Steps

### 3.1 Base Workflow Class (30 minutes)

#### 3.1.1 Create Module Structure

**Action**: Create workflows module:

```bash
mkdir -p src/aimq/workflows
touch src/aimq/workflows/__init__.py
```

#### 3.1.2 Implement BaseWorkflow

**File**: `src/aimq/workflows/base.py`

```python
"""Base class for built-in workflows."""

from typing import Any
from langgraph.graph import StateGraph
from aimq.langgraph.checkpoint import get_checkpointer


class BaseWorkflow:
    """Base class for built-in workflows."""

    def __init__(self, checkpointer: bool = False):
        """Initialize workflow.

        Args:
            checkpointer: Enable state persistence (default: False)
        """
        self.checkpointer_enabled = checkpointer

        # Build and compile graph
        self._graph = self._build_graph()
        self._compiled = self._compile()

    def _build_graph(self) -> StateGraph:
        """Build the workflow's graph. Override in subclasses."""
        raise NotImplementedError

    def _compile(self):
        """Compile the graph with optional checkpointing."""
        checkpointer = get_checkpointer() if self.checkpointer_enabled else None
        return self._graph.compile(checkpointer=checkpointer)

    def invoke(self, input: dict, config: dict | None = None):
        """Invoke the workflow (implements Runnable interface)."""
        return self._compiled.invoke(input, config)

    def stream(self, input: dict, config: dict | None = None):
        """Stream workflow execution (implements Runnable interface)."""
        return self._compiled.stream(input, config)
```

#### 3.1.3 Update Module Exports

**File**: `src/aimq/workflows/__init__.py`

```python
"""Built-in LangGraph workflows for AIMQ."""

from aimq.workflows.document import DocumentWorkflow
from aimq.workflows.multi_agent import MultiAgentWorkflow

__all__ = ["DocumentWorkflow", "MultiAgentWorkflow"]
```

**Validation**:

```bash
uv run python -c "from aimq.workflows.base import BaseWorkflow; print('BaseWorkflow imported')"
```

---

### 3.2 DocumentWorkflow (1.5 hours)

**File**: `src/aimq/workflows/document.py`

```python
"""Document processing workflow."""

from typing import Literal, TypedDict, NotRequired
from langgraph.graph import StateGraph, END
from aimq.workflows.base import BaseWorkflow
import logging

logger = logging.getLogger(__name__)


class DocumentState(TypedDict):
    """State for document workflow."""
    document_path: str
    raw_content: NotRequired[bytes]
    document_type: NotRequired[Literal["image", "pdf", "docx"]]
    text: NotRequired[str]
    metadata: dict
    status: str


class DocumentWorkflow(BaseWorkflow):
    """
    Multi-step document processing pipeline.

    Steps:
    1. Fetch document from storage
    2. Detect document type
    3. Route to appropriate processor (OCR, PDF, etc.)
    4. Extract metadata
    5. Store results

    Args:
        storage_tool: Tool for reading files (e.g., ReadFile())
        ocr_tool: Tool for OCR processing (e.g., ImageOCR())
        pdf_tool: Tool for PDF processing (e.g., PageSplitter())
        checkpointer: Enable state persistence

    Example:
        from aimq.workflows import DocumentWorkflow
        from aimq.tools.supabase import ReadFile, WriteRecord
        from aimq.tools.ocr import ImageOCR

        workflow = DocumentWorkflow(
            storage_tool=ReadFile(),
            ocr_tool=ImageOCR(),
            checkpointer=True
        )

        worker.assign(workflow, queue="documents")
    """

    def __init__(
        self,
        storage_tool,
        ocr_tool,
        pdf_tool=None,
        checkpointer: bool = False,
    ):
        self.storage_tool = storage_tool
        self.ocr_tool = ocr_tool
        self.pdf_tool = pdf_tool
        super().__init__(checkpointer=checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build document processing graph."""
        graph = StateGraph(DocumentState)

        graph.add_node("fetch", self._fetch_node)
        graph.add_node("detect", self._detect_type_node)
        graph.add_node("process_image", self._process_image_node)
        graph.add_node("process_pdf", self._process_pdf_node)
        graph.add_node("store", self._store_node)

        graph.add_edge("fetch", "detect")
        graph.add_conditional_edges(
            "detect",
            self._route_by_type,
            {
                "process_image": "process_image",
                "process_pdf": "process_pdf",
                "error": END,
            }
        )
        graph.add_edge("process_image", "store")
        graph.add_edge("process_pdf", "store")
        graph.add_edge("store", END)

        graph.set_entry_point("fetch")

        return graph

    def _fetch_node(self, state: DocumentState) -> DocumentState:
        """Fetch document from storage (Fix #11)."""
        logger.info(f"Fetching document: {state['document_path']}")

        try:
            content = self.storage_tool.invoke({"path": state["document_path"]})
            logger.debug(f"Document fetched: {len(content)} bytes")
            return {
                "raw_content": content,
                "status": "fetched",
            }
        except Exception as e:
            logger.error(f"Fetch failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _detect_type_node(self, state: DocumentState) -> DocumentState:
        """Detect document type (Fix #11)."""
        import magic

        logger.info("Detecting document type")

        try:
            mime = magic.from_buffer(state["raw_content"], mime=True)

            if mime.startswith("image/"):
                doc_type = "image"
            elif mime == "application/pdf":
                doc_type = "pdf"
            else:
                doc_type = "unknown"

            logger.info(f"Detected type: {doc_type} (mime: {mime})")

            return {
                "document_type": doc_type,
                "metadata": {**state.get("metadata", {}), "mime_type": mime},
                "status": "typed",
            }
        except Exception as e:
            logger.error(f"Type detection failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _process_image_node(self, state: DocumentState) -> DocumentState:
        """Process image with OCR (Fix #11)."""
        from aimq.attachment import Attachment

        logger.info("Processing image with OCR")

        try:
            attachment = Attachment(state["raw_content"])
            result = self.ocr_tool.invoke({"image": attachment})

            logger.info(f"OCR complete: {len(result.get('text', ''))} characters")

            return {
                "text": result["text"],
                "metadata": {
                    **state.get("metadata", {}),
                    "ocr_confidence": result.get("confidence")
                },
                "status": "processed",
            }
        except Exception as e:
            logger.error(f"OCR processing failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _process_pdf_node(self, state: DocumentState) -> DocumentState:
        """Process PDF (Fix #11)."""
        if not self.pdf_tool:
            logger.error("PDF tool not configured")
            return {"status": "error", "text": "No PDF tool configured"}

        logger.info("Processing PDF")

        try:
            pages = self.pdf_tool.invoke({"pdf": state["raw_content"]})
            text = "\n\n".join([p["text"] for p in pages])

            logger.info(f"PDF processed: {len(pages)} pages, {len(text)} characters")

            return {
                "text": text,
                "metadata": {**state.get("metadata", {}), "page_count": len(pages)},
                "status": "processed",
            }
        except Exception as e:
            logger.error(f"PDF processing failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _store_node(self, state: DocumentState) -> DocumentState:
        """Store results (Fix #11)."""
        from aimq.tools.supabase import WriteRecord

        logger.info("Storing results")

        try:
            write_tool = WriteRecord()
            write_tool.invoke({
                "table": "processed_documents",
                "data": {
                    "path": state["document_path"],
                    "text": state.get("text"),
                    "metadata": state.get("metadata"),
                }
            })

            logger.info("Results stored successfully")
            return {"status": "stored"}

        except Exception as e:
            logger.error(f"Storage failed: {e}", exc_info=True)
            return {
                "status": "error",
                "metadata": {**state.get("metadata", {}), "error": str(e)},
            }

    def _route_by_type(self, state: DocumentState) -> str:
        """Route based on document type."""
        doc_type = state.get("document_type")

        if doc_type == "image":
            logger.debug("Routing to image processor")
            return "process_image"
        elif doc_type == "pdf":
            logger.debug("Routing to PDF processor")
            return "process_pdf"

        logger.error(f"Unknown document type: {doc_type}")
        return "error"
```

**Validation**:

```bash
uv run python -c "
from aimq.workflows import DocumentWorkflow

# Create with mock tools
class MockTool:
    def invoke(self, input): return b'data'

wf = DocumentWorkflow(storage_tool=MockTool(), ocr_tool=MockTool())
print('DocumentWorkflow created')
"
```

---

### 3.3 MultiAgentWorkflow (1-2 hours)

**File**: `src/aimq/workflows/multi_agent.py`

```python
"""Multi-agent collaboration workflow."""

from typing import Dict, Callable
from langgraph.graph import StateGraph, END
from aimq.workflows.base import BaseWorkflow
from aimq.langgraph.states import AgentState
import logging

logger = logging.getLogger(__name__)


class MultiAgentWorkflow(BaseWorkflow):
    """
    Multi-agent collaboration with supervisor pattern.

    Pattern:
    1. Supervisor assigns work to specialized agents
    2. Each agent completes their portion
    3. Supervisor coordinates and decides next steps
    4. Process continues until task complete

    Args:
        agents: Dict of agent_name -> agent_function
        supervisor_llm: LLM for supervisor decisions
        checkpointer: Enable state persistence

    Example:
        from aimq.workflows import MultiAgentWorkflow

        workflow = MultiAgentWorkflow(
            agents={
                "researcher": researcher_func,
                "analyst": analyst_func,
                "writer": writer_func,
            },
            supervisor_llm="mistral-large-latest",
            checkpointer=True
        )

        worker.assign(workflow, queue="multi-agent")
    """

    def __init__(
        self,
        agents: Dict[str, Callable],
        supervisor_llm: str = "mistral-large-latest",
        checkpointer: bool = False,
    ):
        self.agents = agents
        self.supervisor_llm = supervisor_llm
        super().__init__(checkpointer=checkpointer)

    def _build_graph(self) -> StateGraph:
        """Build multi-agent graph."""
        graph = StateGraph(AgentState)

        # Add supervisor
        graph.add_node("supervisor", self._supervisor_node)

        # Add agent nodes
        for agent_name, agent_func in self.agents.items():
            graph.add_node(agent_name, agent_func)
            # Each agent reports back to supervisor
            graph.add_edge(agent_name, "supervisor")

        # Supervisor routes to agents or ends
        graph.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {**{name: name for name in self.agents.keys()}, "end": END}
        )

        graph.set_entry_point("supervisor")

        return graph

    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor decides which agent to invoke (Fix #11)."""
        from aimq.clients.mistral import get_mistral_client

        logger.info(f"Supervisor coordinating (iteration {state['iteration']})")

        client = get_mistral_client()

        # Build coordination prompt
        prompt = self._build_supervisor_prompt(state)

        try:
            response = client.chat.completions.create(
                model=self.supervisor_llm,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            next_agent = response.choices[0].message.content.strip().lower()

            logger.info(f"Supervisor routing to: {next_agent}")

            return {
                "messages": [{
                    "role": "supervisor",
                    "content": f"Routing to: {next_agent}"
                }],
                "current_tool": next_agent,  # Reuse field for next agent
                "iteration": state["iteration"] + 1,
            }

        except Exception as e:
            logger.error(f"Supervisor failed: {e}", exc_info=True)
            return {
                "errors": [f"Supervisor error: {str(e)}"],
                "iteration": state["iteration"] + 1,
            }

    def _route_to_agent(self, state: AgentState) -> str:
        """Route to next agent."""
        next_agent = state.get("current_tool", "end")

        # Safety: prevent infinite loops
        if state["iteration"] >= 20:
            logger.warning("Max iterations reached, ending workflow")
            return "end"

        logger.debug(f"Routing to agent: {next_agent}")
        return next_agent

    def _build_supervisor_prompt(self, state: AgentState) -> str:
        """Build supervisor coordination prompt."""
        agent_list = ", ".join(self.agents.keys())

        return f"""You are coordinating a team of agents.

Available agents: {agent_list}

Task progress:
{self._format_progress(state)}

Which agent should work next? Respond with just the agent name, or "end" if complete.
"""

    def _format_progress(self, state: AgentState) -> str:
        """Format task progress from state."""
        messages = state.get("messages", [])
        return "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..."
            for msg in messages[-5:]  # Last 5 messages
        ])
```

**Validation**:

```bash
uv run python -c "
from aimq.workflows import MultiAgentWorkflow

def agent_func(state): return {}

wf = MultiAgentWorkflow(agents={'agent1': agent_func})
print('MultiAgentWorkflow created')
"
```

---

## Testing & Validation

### Unit Tests

**File**: `tests/aimq/workflows/test_document.py`

```python
import pytest
from aimq.workflows import DocumentWorkflow


class MockTool:
    def invoke(self, input):
        if "path" in input:
            return b"test content"
        return {"text": "extracted text"}


def test_document_workflow_initialization():
    """Test DocumentWorkflow can be initialized."""
    workflow = DocumentWorkflow(
        storage_tool=MockTool(),
        ocr_tool=MockTool(),
    )

    assert workflow is not None
    assert workflow._compiled is not None


def test_document_workflow_routing():
    """Test document type routing."""
    workflow = DocumentWorkflow(
        storage_tool=MockTool(),
        ocr_tool=MockTool(),
    )

    # Test image routing
    state = {"document_type": "image"}
    assert workflow._route_by_type(state) == "process_image"

    # Test PDF routing
    state = {"document_type": "pdf"}
    assert workflow._route_by_type(state) == "process_pdf"
```

---

## Definition of Done

### Code Complete

- [ ] BaseWorkflow class implemented
- [ ] DocumentWorkflow fully implemented
- [ ] MultiAgentWorkflow fully implemented
- [ ] Logger integration throughout (Fix #11)
- [ ] All docstrings complete

### Validation

- [ ] All imports successful
- [ ] Workflows instantiate without errors
- [ ] Graphs compile successfully
- [ ] Conditional routing works

### Testing

- [ ] Unit tests created and passing
- [ ] Workflow initialization tests pass
- [ ] Routing tests pass

---

## Common Pitfalls

### State Type Mismatches

**Pitfall**: Using AgentState for DocumentWorkflow

**Solution**: Use correct state class
```python
# DocumentWorkflow uses DocumentState
graph = StateGraph(DocumentState)

# MultiAgentWorkflow uses AgentState
graph = StateGraph(AgentState)
```

### Missing Error Handling in Nodes

**Pitfall**: Node crashes break entire workflow

**Solution**: Add try/catch and update state
```python
def _fetch_node(self, state):
    try:
        content = self.storage_tool.invoke(...)
        return {"raw_content": content, "status": "fetched"}
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return {"status": "error", "metadata": {"error": str(e)}}
```

---

## Next Phase

Once Phase 3 is complete:
- [ ] Update PROGRESS.md
- [ ] Move to **Phase 4: Tools & Checkpointing** ([PHASE4.md](./PHASE4.md))

---

**Phase Owner**: Implementation Team
**Started**: ___________
**Completed**: ___________
**Actual Hours**: ___________
