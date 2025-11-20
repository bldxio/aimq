# CLI UX Patterns

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

## Real-World Examples

### Example 1: Missing Environment Variables

```python
# From AIMQ CLI commands
def check_environment():
    """Check that required environment variables are set"""
    missing = []

    if not config.supabase_url:
        missing.append('SUPABASE_URL')
    if not config.supabase_key:
        missing.append('SUPABASE_KEY')

    if missing:
        console.print("[red]Error:[/red] Missing required environment variables:\n")
        for var in missing:
            console.print(f"  • {var}")

        console.print("\n[dim]Add them to your .env file:[/dim]")
        console.print("  SUPABASE_URL=https://your-project.supabase.co")
        console.print("  SUPABASE_KEY=your-anon-key")

        console.print("\n[dim]Or set them in your shell:[/dim]")
        console.print("  export SUPABASE_URL=...")
        console.print("  export SUPABASE_KEY=...")

        sys.exit(1)
```

### Example 2: Queue Not Found

```python
# From SupabaseQueueProvider
def enable_realtime(self, queue_name: str):
    """Enable realtime on a queue"""
    try:
        result = self._rpc('enable_queue_realtime', {'queue_name': queue_name})
        return result
    except QueueNotFoundError:
        # Helpful error message
        console.print(f"[red]Error:[/red] Queue '{queue_name}' does not exist.\n")
        console.print("Create it first:")
        console.print(f"  [cyan]aimq create {queue_name}[/cyan]\n")
        console.print("Or list existing queues:")
        console.print("  [cyan]aimq list[/cyan]")
        sys.exit(1)
```

### Example 3: Migration Not Applied

```python
# From list command
@click.command()
def list_queues():
    """List all queues with metrics"""
    try:
        queues = provider.list_queues()
        show_queues(queues)

    except Exception as e:
        error_msg = str(e)

        # Detect migration issue
        if "PGRST202" in error_msg or "does not exist" in error_msg:
            console.print("[yellow]⚠️  Migrations not applied yet![/yellow]\n")
            console.print(
                "The database functions needed by AIMQ haven't been created yet.\n"
            )
            console.print("Run one of these commands:\n")
            console.print("  [cyan]supabase db reset[/cyan]  (local development)")
            console.print("  [cyan]supabase db push[/cyan]   (remote database)\n")
            console.print("[dim]Or generate a migration file:[/dim]")
            console.print("  [cyan]aimq init --supabase[/cyan]")
        else:
            # Unknown error - show it
            console.print(f"[red]Error:[/red] {error_msg}")

        sys.exit(1)
```

### Example 4: Success with Next Steps

```python
# From enable-realtime command
@click.command()
@click.argument('queue_name')
def enable_realtime(queue_name: str):
    """Enable realtime on an existing queue"""
    try:
        console.print(f"Enabling realtime on: [cyan]{queue_name}[/cyan]")

        result = provider.enable_realtime(queue_name)

        # Success!
        console.print(f"[green]✓[/green] Realtime enabled successfully!\n")

        # Explain what this means
        console.print("[dim]Workers will now wake instantly when jobs are added[/dim]")

        # Show how to verify
        console.print("\n[dim]Verify with:[/dim] [cyan]aimq list[/cyan]")

    except Exception as e:
        handle_error(e)
        sys.exit(1)
```

## Visual Design

### Use Rich Console Features

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Tables for structured data
table = Table(title="Queues")
table.add_column("Name")
table.add_column("Status")
console.print(table)

# Panels for important messages
console.print(Panel(
    "Migrations not applied yet!\n\n"
    "Run: supabase db reset",
    title="⚠️  Setup Required",
    border_style="yellow"
))

# Colors for emphasis
console.print("[green]✓[/green] Success!")
console.print("[red]✗[/red] Failed")
console.print("[yellow]⚠️[/yellow] Warning")
console.print("[cyan]aimq list[/cyan]")  # Commands
console.print("[dim]Optional info[/dim]")  # Less important
```

### Consistent Symbols

```python
# Status indicators
✓  # Success
✗  # Failure
⚠️  # Warning
💡 # Tip/hint
🔧 # Configuration
📝 # Documentation
🚀 # Action/command

# Usage
console.print("[green]✓[/green] Queue created")
console.print("[red]✗[/red] Connection failed")
console.print("[yellow]⚠️[/yellow] Migrations needed")
console.print("[dim]💡 Tip: Use --help for more options[/dim]")
```

## Testing UX

### Test Error Messages

```python
def test_helpful_error_on_missing_migration():
    """Should show helpful message when migrations not applied"""
    with patch('aimq.providers.supabase.supabase') as mock:
        mock.client.schema().rpc().execute.side_effect = Exception(
            "PGRST202: relation does not exist"
        )

        result = runner.invoke(cli, ['list'])

        assert result.exit_code == 1
        assert "Migrations not applied" in result.output
        assert "supabase db reset" in result.output
        assert "supabase db push" in result.output

def test_helpful_error_on_queue_not_found():
    """Should show helpful message when queue doesn't exist"""
    with patch('aimq.providers.supabase.supabase') as mock:
        mock.client.schema().rpc().execute.side_effect = QueueNotFoundError(
            "Queue 'test' does not exist"
        )

        result = runner.invoke(cli, ['enable-realtime', 'test'])

        assert result.exit_code == 1
        assert "does not exist" in result.output
        assert "aimq create test" in result.output
        assert "aimq list" in result.output
```

### Test Success Messages

```python
def test_success_message_on_create():
    """Should show success message and next steps"""
    with patch('aimq.providers.supabase.supabase') as mock:
        mock.client.schema().rpc().execute.return_value.data = {'success': True}

        result = runner.invoke(cli, ['create', 'test'])

        assert result.exit_code == 0
        assert "✓" in result.output or "Success" in result.output
        assert "test" in result.output
```

## Anti-Patterns

### ❌ Cryptic Errors

```python
# Bad
Error: 42P01

# Good
⚠️  Migrations not applied yet!
Run: supabase db reset
```

### ❌ No Actionable Guidance

```python
# Bad
Error: Configuration missing

# Good
Missing environment variables:
  SUPABASE_URL
  SUPABASE_KEY

Add them to .env:
  SUPABASE_URL=https://...
  SUPABASE_KEY=...
```

### ❌ Information Overload

```python
# Bad
Error: PostgreSQL error 42P01: relation "pgmq_public.create_queue" does not exist
Hint: Check that the schema exists and the function is defined
Details: SELECT * FROM pgmq_public.create_queue($1, $2)
Context: PL/pgSQL function inline_code_block line 3 at SQL statement
Stack trace: [50 lines of traceback]

# Good
⚠️  Migrations not applied yet!
Run: supabase db reset

[dim]Use --verbose for details[/dim]
```

### ❌ Assuming Knowledge

```python
# Bad
Error: PGRST202
(User has to Google what PGRST202 means)

# Good
⚠️  Database functions not found
The AIMQ functions haven't been created yet.
Run: supabase db reset
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

- [@.claude/patterns/progressive-disclosure.md](./progressive-disclosure.md) - Show info progressively
- [@.claude/standards/error-handling.md](../standards/error-handling.md) - Error handling patterns
- [@.claude/quick-references/aimq-pitfalls.md](../quick-references/aimq-pitfalls.md) - Common issues
- [@.claude/patterns/demo-driven-development-core.md](./demo-driven-development-core.md) - User-first development

## References

- [Rich Console Library](https://rich.readthedocs.io/)
- [Click CLI Framework](https://click.palletsprojects.com/)
- [Command Line Interface Guidelines](https://clig.dev/)

---

**Remember**: Good CLI UX turns frustration into action! 💡✨
