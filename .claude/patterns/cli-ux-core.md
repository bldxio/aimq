# CLI UX Core Patterns

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: patterns

## Overview

Command-line interfaces should be helpful, not cryptic. Good CLI UX means users know what went wrong and what to do next, without needing to read documentation or search Stack Overflow.

## Core Principles

### 1. Detect Common Issues

Anticipate what will go wrong and handle it gracefully:

```python
# ❌ Bad: Cryptic error
Error: PGRST202

# ✅ Good: Helpful error
⚠️  Migrations not applied yet!

Run one of these commands:
  supabase db reset  (local dev)
  supabase db push   (remote db)
```

### 2. Provide Actionable Guidance

Tell users exactly what to do:

```python
# ❌ Bad: Vague
Error: Configuration missing

# ✅ Good: Specific
Missing required environment variables:
  SUPABASE_URL
  SUPABASE_KEY

Add them to your .env file:
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key
```

### 3. Use Context-Specific Instructions

Different contexts need different solutions:

```python
# ❌ Bad: One-size-fits-all
Error: Database not ready. Run migrations.

# ✅ Good: Context-aware
⚠️  Migrations not applied yet!

For local development:
  supabase db reset

For remote database:
  supabase db push

For custom setup:
  aimq create my-queue --migration
```

## Implementation Patterns

### Pattern 1: Error Detection and Translation

Translate technical errors into user-friendly messages:

```python
def handle_error(error: Exception) -> None:
    """Translate technical errors into helpful messages"""
    error_msg = str(error)

    # Detect specific error patterns
    if "PGRST202" in error_msg or "does not exist" in error_msg:
        show_migration_help()
    elif "ECONNREFUSED" in error_msg:
        show_connection_help()
    elif "authentication failed" in error_msg:
        show_auth_help()
    else:
        # Fall back to original error
        console.print(f"[red]Error:[/red] {error_msg}")

def show_migration_help():
    """Show helpful migration instructions"""
    console.print("[yellow]⚠️  Migrations not applied yet![/yellow]\n")
    console.print("The database functions needed by AIMQ haven't been created yet.\n")
    console.print("Run one of these commands:\n")
    console.print("  [cyan]supabase db reset[/cyan]  (local development)")
    console.print("  [cyan]supabase db push[/cyan]   (remote database)\n")
    console.print("[dim]Or generate a migration file:[/dim]")
    console.print("  [cyan]aimq create my-queue --migration[/cyan]")
```

### Pattern 2: Progressive Disclosure

Show essential info first, details on demand:

```python
# ❌ Bad: Information overload
Error: PostgreSQL error 42P01: relation "pgmq_public.create_queue" does not exist
Hint: Check that the schema exists and the function is defined
Details: SELECT * FROM pgmq_public.create_queue($1, $2)
Context: PL/pgSQL function inline_code_block line 3 at SQL statement

# ✅ Good: Essential info + optional details
⚠️  Migrations not applied yet!

Run: supabase db reset

[dim]Need more details? Run with --verbose[/dim]
```

```python
@click.command()
@click.option('--verbose', is_flag=True, help='Show detailed error messages')
def list_queues(verbose: bool):
    try:
        queues = provider.list_queues()
        show_queues(queues)
    except Exception as e:
        if verbose:
            # Show full technical details
            console.print_exception()
        else:
            # Show user-friendly message
            handle_error(e)
```

### Pattern 3: Environment Detection

Provide context-specific guidance:

```python
def detect_environment() -> str:
    """Detect if running locally or against remote DB"""
    if os.path.exists('.git') and os.path.exists('supabase'):
        return 'local'
    elif config.supabase_url and 'localhost' not in config.supabase_url:
        return 'remote'
    else:
        return 'unknown'

def show_migration_help():
    env = detect_environment()

    if env == 'local':
        console.print("Run: [cyan]supabase db reset[/cyan]")
    elif env == 'remote':
        console.print("Run: [cyan]supabase db push[/cyan]")
    else:
        console.print("Run one of these commands:")
        console.print("  [cyan]supabase db reset[/cyan]  (local)")
        console.print("  [cyan]supabase db push[/cyan]   (remote)")
```

### Pattern 4: Helpful Hints

Provide tips based on context:

```python
def show_queues(queues: list):
    """Display queues with helpful hints"""
    table = Table(title="AIMQ Queues")
    table.add_column("Queue")
    table.add_column("Realtime")

    for queue in queues:
        table.add_row(
            queue['name'],
            '✓' if queue['realtime'] else '✗'
        )

    console.print(table)

    # Show hint if relevant
    queues_without_realtime = [q for q in queues if not q['realtime']]
    if queues_without_realtime:
        console.print(
            "\n[dim]💡 Tip: Enable realtime on queues with:[/dim] "
            "[cyan]aimq enable-realtime <queue-name>[/cyan]"
        )
```

### Pattern 5: Confirmation and Feedback

Confirm actions and show what happened:

```python
@click.command()
@click.argument('queue_name')
@click.option('--realtime/--no-realtime', default=True)
def create(queue_name: str, realtime: bool):
    """Create a new queue"""
    # Show what we're doing
    console.print(f"Creating queue: [cyan]{queue_name}[/cyan]")

    try:
        provider.create_queue(queue_name, with_realtime=realtime)

        # Confirm success
        console.print(f"[green]✓[/green] Queue created successfully!")

        # Show next steps
        if realtime:
            console.print(f"\n[dim]Workers will wake instantly when jobs are added[/dim]")
        else:
            console.print(f"\n[dim]Enable realtime with:[/dim] "
                        f"[cyan]aimq enable-realtime {queue_name}[/cyan]")

    except Exception as e:
        # Show what went wrong
        console.print(f"[red]✗[/red] Failed to create queue")
        handle_error(e)
```

## Benefits

### Reduced Support Burden

Users can self-serve instead of asking for help:

```
Before: "I get error PGRST202, what do I do?"
After: Error message tells them exactly what to do
```

### Faster Onboarding

New users can get started without reading docs:

```
Before: Read docs → Find setup section → Run commands
After: Run command → Get helpful error → Follow instructions
```

### Better User Experience

Users feel guided, not frustrated:

```
Before: "This tool is broken!"
After: "Oh, I just need to run this command"
```

## Related

- [CLI UX Examples](./cli-ux-examples.md) - Real-world examples and visual design
- [Progressive Disclosure](./progressive-disclosure.md) - Show info progressively
- [Error Handling](./error-handling.md) - Error handling patterns
- [AIMQ Pitfalls](../quick-references/aimq-pitfalls.md) - Common issues

## References

- [Rich Console Library](https://rich.readthedocs.io/)
- [Click CLI Framework](https://click.palletsprojects.com/)
- [Command Line Interface Guidelines](https://clig.dev/)

---

**Remember**: Good CLI UX turns frustration into action! 💡✨
