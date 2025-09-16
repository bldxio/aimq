# Writing Tasks

Tasks are the fundamental building blocks in AIMQ that define how to process and transform data. This guide will help you understand how to write effective tasks that can be composed into powerful AI workflows.

## Task Structure

A task in AIMQ is typically composed of:

1. Input definition
2. Processing logic
3. Output transformation
4. Error handling

### Basic Task Example

```python
from aimq.helpers import select, assign
from langchain_core.runnables import RunnablePassthrough

def create_summarization_task():
    """Create a task that summarizes text content."""
    return (
        # 1. Select input
        select("content")
        # 2. Process with LLM
        | summarize_with_llm
        # 3. Format output
        | assign({
            "summary": RunnablePassthrough(),
            "metadata": const({
                "task": "summarization",
                "timestamp": datetime.now().isoformat()
            })
        })
    )
```

## Task Composition

Tasks can be composed together using the pipeline operator (`|`). AIMQ's helper functions make it easy to transform data between tasks.

### Example: Multi-Step Task

```python
def create_analysis_pipeline():
    """Create a pipeline that summarizes and analyzes text."""
    return (
        # Extract relevant content
        select("text")
        # Summarize the text
        | create_summarization_task()
        # Analyze sentiment
        | create_sentiment_task()
        # Combine results
        | assign({
            "summary": pick("summary"),
            "sentiment": pick("sentiment"),
            "metadata": orig("metadata")
        })
    )
```

## Best Practices

### 1. Input Validation

Always validate your input data at the start of your task:

```python
def validate_input(input_data):
    if "content" not in input_data:
        raise ValueError("Input must contain 'content' key")
    if not isinstance(input_data["content"], str):
        raise TypeError("Content must be a string")
```

### 2. Error Handling

Implement proper error handling to make debugging easier:

```python
def create_robust_task():
    return (
        # Validate input
        RunnableLambda(validate_input)
        # Process data with error handling
        | handle_errors(process_data)
        # Format output
        | format_output
    )
```

### 3. Type Safety

Use type hints and ensure type safety throughout your task:

```python
from typing import TypedDict, Optional

class TaskInput(TypedDict):
    content: str
    metadata: Optional[dict]

class TaskOutput(TypedDict):
    result: str
    error: Optional[str]

def process_task(input_data: TaskInput) -> TaskOutput:
    ...
```

### 4. Documentation

Document your tasks thoroughly:

```python
def create_classification_task():
    """Create a task for text classification.
    
    This task processes input text and classifies it into predefined categories
    using a specified classification model.
    
    Returns:
        A runnable pipeline that:
        1. Validates input text
        2. Preprocesses text for classification
        3. Applies classification model
        4. Formats results with confidence scores
    
    Example:
        ```python
        classifier = create_classification_task()
        result = classifier.invoke({
            "text": "Sample text to classify",
            "categories": ["A", "B", "C"]
        })
        ```
    """
    ...
```

## Testing Tasks

### 1. Unit Tests

Write unit tests for individual components:

```python
def test_summarization_task():
    task = create_summarization_task()
    result = task.invoke({"content": "Test content"})
    
    assert "summary" in result
    assert isinstance(result["summary"], str)
```

### 2. Integration Tests

Test task composition and data flow:

```python
def test_analysis_pipeline():
    pipeline = create_analysis_pipeline()
    result = pipeline.invoke({
        "text": "Test content",
        "metadata": {"source": "test"}
    })
    
    assert "summary" in result
    assert "sentiment" in result
    assert result["metadata"]["source"] == "test"
```

## Common Patterns

### 1. Data Transformation

Use helpers to transform data between tasks:

```python
# Transform output format
result = task | assign({
    "data": pick("result"),
    "metadata": orig("metadata")
})
```

### 2. Conditional Processing

Implement conditional logic in your tasks:

```python
def conditional_process(input_data):
    if input_data.get("skip_summary"):
        return select("content")
    return create_summarization_task()
```

### 3. Parallel Processing

Run tasks in parallel when possible:

```python
def parallel_analysis():
    return RunnableParallel({
        "summary": create_summarization_task(),
        "sentiment": create_sentiment_task(),
        "categories": create_classification_task()
    })
```

## Debugging Tasks

1. Use the `echo` helper to inspect data flow:

```python
pipeline = (
    select("content")
    | echo  # Print content
    | process_data
    | echo  # Print processed data
)
```

1. Add logging for complex operations:

```python
def log_step(name):
    def _log(data):
        logger.debug(f"Step {name}: {data}")
        return data
    return RunnableLambda(_log)

pipeline = (
    select("content")
    | log_step("input")
    | process_data
    | log_step("output")
)
