# Helper Functions

AIMQ provides a set of helper functions to simplify working with LangChain runnables and task composition. These helpers are designed to make it easier to build and chain together different components of your AI workflows.

## Available Helpers

### echo

```python
@chain
def echo(input: T) -> T
```

Echo the input value back while also printing it to stdout. This is useful for debugging and monitoring the flow of data through your pipeline.

**Example:**

```python
from aimq.helpers import echo

result = echo("Testing pipeline") | next_step
# Prints: Testing pipeline
# And passes "Testing pipeline" to next_step
```

### select

```python
def select(key: str | list[str] | dict[str, str] | None = None) -> Runnable
```

Creates a runnable that selects specific keys from the input. This is particularly useful when you need to reshape or filter data between pipeline steps.

**Options:**

- `None`: Pass through the entire input
- `str`: Select a single key
- `list[str]`: Select multiple keys
- `dict[str, str]`: Map old keys to new keys

**Example:**

```python
from aimq.helpers import select

# Select a single key
single = select("content")

# Select multiple keys
multiple = select(["content", "metadata"])

# Rename keys
renamed = select({"old_key": "new_key"})
```

### const

```python
def const(value: T) -> Callable[[Any], T]
```

Creates a function that always returns a constant value. This is useful when you need to inject constant values into your pipeline.

**Example:**

```python
from aimq.helpers import const

# Add a constant model parameter
pipeline = pipeline | assign({"model": const("gpt-4")})
```

### assign

```python
def assign(runnables: dict[str, Any] = {}) -> RunnableAssign
```

Creates a RunnableAssign from a dictionary of runnables or constant values. This helper makes it easy to add or modify data in your pipeline.

**Example:**

```python
from aimq.helpers import assign, const

# Add multiple values
pipeline = pipeline | assign({
    "model": const("gpt-4"),
    "temperature": const(0.7),
    "processed_text": text_processor
})
```

### pick

```python
def pick(key: str | list[str]) -> RunnablePick
```

Creates a RunnablePick to select specific keys from the input. Similar to `select` but more focused on simple key selection.

**Example:**

```python
from aimq.helpers import pick

# Pick a single key
result = pipeline | pick("content")

# Pick multiple keys
result = pipeline | pick(["content", "metadata"])
```

### orig

```python
def orig(key: str | list[str] | None = None) -> Runnable[Any, dict[str, Any]]
```

Creates a runnable that retrieves the original configuration. This is useful when you need to access the initial configuration later in your pipeline.

**Example:**

```python
from aimq.helpers import orig

# Get all original config
config = pipeline | orig()

# Get specific config keys
model_config = pipeline | orig(["model", "temperature"])
```

## Best Practices

1. **Pipeline Composition**

   - Use `select` when you need to reshape data between steps
   - Use `assign` to add new data or transform existing data
   - Use `echo` for debugging complex pipelines

2. **Data Flow**

   - Keep your data transformations clear and explicit
   - Use type hints to ensure type safety
   - Document any assumptions about data structure

3. **Error Handling**

   - Handle potential errors when selecting non-existent keys
   - Validate input data structure before processing
   - Use appropriate error messages for debugging
