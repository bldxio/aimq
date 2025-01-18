# AIMQ Documentation

AIMQ (AI Message Queue) is a Python library designed to simplify working with Supabase's queue system, which is built on top of pgmq. It provides an elegant way to process queued jobs using LangChain Runnables, making it perfect for AI-powered task processing and background job handling.

## Features

- **Simple Task Definition**: Define queue processors using the `@worker.task` decorator to transform functions into LangChain RunnableLambda processors
- **Supabase Integration**: Built on Supabase's queue system (pgmq) for reliable and scalable message queuing
- **LangChain Compatibility**: Native support for LangChain Runnables, making it easy to integrate AI workflows
- **Type Safety**: Full type hints and runtime validation using Pydantic
- **Flexible Job Processing**: Support for delayed jobs, job timeouts, and customizable job completion handling

## Quick Start

1. Enable Supabase Queue Integration:
   - In your Supabase project, enable the Queue integration
   - Make sure "Expose Queues via PostgREST" is turned on
   - Create your queues through the Supabase interface

2. Configure Environment:
   ```env
   SUPABASE_URL=your-project-url
   SUPABASE_KEY=your-service-role-key
   ```

3. Create Tasks:
   ```python
   from aimq import Worker

   worker = Worker()

   @worker.task(queue="process_text")
   def process_text(job_data):
       # Process job_data using LangChain
       return {"result": "processed"}

   worker.start()
   ```

## Quick Links

- [Installation](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [API Reference](api/overview.md)
- [Contributing Guide](development/contributing.md)

## Project Status

AIMQ is currently in beta. While it is being used in production environments, the API may still undergo changes as we gather feedback from users.

## License

AIMQ is released under the MIT License. See the [LICENSE](https://github.com/bldxio/aimq/blob/main/LICENSE) file for more details.
