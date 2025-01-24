# Task Templates

This module provides template task definitions that can be used as examples or starting points for creating your own tasks.

## Module Documentation

::: aimq.commands.shared.templates.tasks
    options:
      show_root_heading: true
      show_source: true

## Example Task

The module includes a basic example task that demonstrates the worker task pattern:

```python
@worker.task()
def example(data: Dict[str, Any]) -> Dict[str, str]:
    text = data.get('text', '')
    return {'result': text.upper()}
```

## Using Templates

1. Import the worker instance:

   ```python
   from aimq.commands.shared.templates.tasks import worker
   ```

1. Use the example task:

   ```python
   result = await worker.enqueue('example', {'text': 'hello world'})
   ```

1. Create your own tasks based on the template:

   ```python
   @worker.task()
   def my_task(data: Dict[str, Any]) -> Dict[str, Any]:
       # Your task logic here
       return {'result': process_data(data)}
   ```
