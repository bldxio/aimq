# CLI UX Examples and Visual Design

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: patterns

## Overview

Real-world examples of CLI UX patterns in action, plus visual design guidelines for creating beautiful, helpful command-line interfaces.

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

## Related

- [@cli-ux-core.md](./cli-ux-core.md) - Core principles and implementation patterns
- [@progressive-disclosure.md](./progressive-disclosure.md) - Show info progressively
- [@error-handling.md](./error-handling.md) - Error handling patterns
- [@../quick-references/aimq-pitfalls.md](../quick-references/aimq-pitfalls.md) - Common issues
- [Testing Strategy](./testing-strategy.md) - Testing patterns
- [Demo-Driven Development](./demo-driven-development.md) - User-first development

## References

- [Rich Console Library](https://rich.readthedocs.io/)
- [Click CLI Framework](https://click.palletsprojects.com/)
- [Command Line Interface Guidelines](https://clig.dev/)

---

**Remember**: Beautiful CLIs make users happy! ✨
