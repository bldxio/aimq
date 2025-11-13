"""
Example: Creating custom workflow with @workflow decorator

Demonstrates how to define a custom multi-step workflow with custom state.

The @workflow decorator provides:
- Custom state definition (TypedDict)
- Automatic checkpointing
- Error collection patterns
- Clean separation of concerns

This example shows an ETL (Extract-Transform-Load) pipeline:
1. Extract - Read data from source file
2. Transform - Apply business logic transformations
3. Load - Store results in database

Usage:
    # Terminal 1: Start worker
    uv run python examples/langgraph/custom_workflow_decorator.py

    # Terminal 2: Send test job
    aimq send etl-pipeline '{
      "source_path": "data/raw_sales.csv",
      "load_status": "",
      "errors": []
    }'
"""

from operator import add
from typing import Annotated, NotRequired, TypedDict

from langgraph.graph import END, StateGraph

from aimq import workflow
from aimq.tools.supabase import ReadFile, WriteRecord
from aimq.worker import Worker


# Define custom state for ETL workflow
class ETLState(TypedDict):
    """State for ETL pipeline.

    Required fields:
        source_path: Path to source data file
        load_status: Status of load operation
        errors: Accumulated errors (with add reducer)

    Optional fields:
        extracted_data: Raw data from extract step
        transformed_data: Processed data from transform step
        row_count: Number of records processed
        metadata: Additional workflow metadata
    """

    # Required fields (must be present at initialization)
    source_path: str
    load_status: str
    errors: Annotated[list[str], add]  # Errors accumulate across nodes

    # Optional fields (use NotRequired)
    extracted_data: NotRequired[dict]
    transformed_data: NotRequired[dict]
    row_count: NotRequired[int]
    metadata: NotRequired[dict]


# Define custom workflow
@workflow(state_class=ETLState, checkpointer=True)
def etl_workflow(graph: StateGraph, config: dict) -> StateGraph:  # noqa: C901
    """
    Custom ETL (Extract-Transform-Load) workflow.

    Steps:
    1. Extract - Read data from source file
    2. Transform - Apply business transformations
    3. Load - Store results in database

    The config dict contains:
    - checkpointer: bool - Whether checkpointing is enabled
    - state_class: Type[TypedDict] - The state class (ETLState)
    """

    def extract(state: ETLState) -> ETLState:
        """Extract data from source file."""
        print(f"[ETL] Extracting data from: {state['source_path']}")

        tool = ReadFile()
        try:
            # Read file content
            content = tool.invoke({"path": state["source_path"]})

            # Parse based on file type
            import json

            if state["source_path"].endswith(".json"):
                data = json.loads(content)
            elif state["source_path"].endswith(".csv"):
                # Simple CSV parsing (in production, use pandas or csv module)
                lines = content.strip().split("\n")
                headers = lines[0].split(",") if lines else []
                rows = [dict(zip(headers, line.split(","))) for line in lines[1:] if line]
                data = {"headers": headers, "rows": rows}
            else:
                # Plain text fallback
                data = {"raw": content}

            print(f"[ETL] Extracted {len(data.get('rows', [data]))} records")

            return {"extracted_data": data, "row_count": len(data.get("rows", [data]))}

        except Exception as e:
            error_msg = f"Extract failed: {str(e)}"
            print(f"[ETL] ERROR: {error_msg}")
            return {"errors": [error_msg]}

    def transform(state: ETLState) -> ETLState:
        """Transform extracted data."""
        print("[ETL] Transforming data...")

        if not state.get("extracted_data"):
            error_msg = "No data to transform - extract step may have failed"
            print(f"[ETL] ERROR: {error_msg}")
            return {"errors": [error_msg]}

        try:
            data = state["extracted_data"]

            # Example transformations:
            # 1. Uppercase all text values
            # 2. Add processing timestamp
            # 3. Calculate summary statistics

            transformed = {
                "original_rows": state.get("row_count", 0),
                "processed_at": "2024-10-30T12:00:00Z",  # In production: datetime.now().isoformat()
                "data": None,
            }

            if "rows" in data:
                # CSV data - transform rows
                transformed["data"] = [
                    {k: v.upper() if isinstance(v, str) else v for k, v in row.items()}
                    for row in data["rows"]
                ]
                transformed["row_count"] = len(transformed["data"])
            elif "raw" in data:
                # Text data - simple transformation
                transformed["data"] = data["raw"].upper()
                transformed["text_length"] = len(data["raw"])
            else:
                # Generic transformation
                transformed["data"] = str(data).upper()

            print(f"[ETL] Transformed {transformed.get('row_count', 'N/A')} records")

            return {"transformed_data": transformed}

        except Exception as e:
            error_msg = f"Transform failed: {str(e)}"
            print(f"[ETL] ERROR: {error_msg}")
            return {"errors": [error_msg]}

    def load(state: ETLState) -> ETLState:
        """Load transformed data into database."""
        print("[ETL] Loading data to database...")

        if not state.get("transformed_data"):
            error_msg = "No data to load - transform step may have failed"
            print(f"[ETL] ERROR: {error_msg}")
            return {"errors": [error_msg], "load_status": "failed"}

        tool = WriteRecord()
        try:
            # Store in etl_results table
            _ = tool.invoke(
                {
                    "table": "etl_results",
                    "data": {
                        "source_path": state["source_path"],
                        "row_count": state.get("row_count", 0),
                        "transformed_data": state["transformed_data"],
                        "processed_at": "NOW()",
                    },
                }
            )

            print(f"[ETL] Successfully loaded {state.get('row_count', 0)} records")

            return {"load_status": "success"}

        except Exception as e:
            error_msg = f"Load failed: {str(e)}"
            print(f"[ETL] ERROR: {error_msg}")
            return {"errors": [error_msg], "load_status": "failed"}

    # Build graph
    # The decorator provides a StateGraph pre-configured with ETLState
    graph.add_node("extract", extract)
    graph.add_node("transform", transform)
    graph.add_node("load", load)

    # Linear pipeline: extract → transform → load
    graph.add_edge("extract", "transform")
    graph.add_edge("transform", "load")
    graph.add_edge("load", END)

    # Start with extract
    graph.set_entry_point("extract")

    return graph


# Use the custom workflow
worker = Worker()
workflow_instance = etl_workflow()
worker.assign(workflow_instance, queue="etl-pipeline", timeout=600, delete_on_finish=False)

if __name__ == "__main__":
    from pathlib import Path

    motd_path = Path(__file__).parent / "custom_workflow_decorator_MOTD.md"
    worker.start(motd=str(motd_path), show_info=True)
