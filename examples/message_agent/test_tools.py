"""Quick test script for the new tools."""

from rich.console import Console
from rich.panel import Panel

from aimq.tools.supabase import QueryTable
from aimq.tools.weather import Weather

console = Console()


def test_weather():
    """Test the weather tool."""
    console.print("\n[bold cyan]Testing Weather Tool...[/bold cyan]")

    tool = Weather()
    locations = ["San Francisco", "New York", "Tokyo"]

    for location in locations:
        try:
            result = tool.run(location)
            console.print(Panel(result, title=f"Weather: {location}", border_style="green"))
        except Exception as e:
            console.print(f"[red]Error for {location}: {e}[/red]")


def test_query_table():
    """Test the query table tool."""
    console.print("\n[bold cyan]Testing QueryTable Tool...[/bold cyan]")

    tool = QueryTable()

    queries = [
        {
            "name": "All competitors (limit 3)",
            "table": "competitors",
            "limit": 3,
        },
        {
            "name": "Basketball teams",
            "table": "competitors",
            "filters": "sport_code:eq:basketball,entity_type:eq:team",
            "limit": 5,
        },
        {
            "name": "Players only",
            "table": "competitors",
            "filters": "entity_type:eq:player",
            "columns": "first_name,last_name,position,jersey",
            "limit": 5,
        },
    ]

    for query in queries:
        try:
            result = tool.run(**query)
            console.print(Panel(result, title=query["name"], border_style="blue"))
        except Exception as e:
            console.print(f"[red]Error for {query['name']}: {e}[/red]")


if __name__ == "__main__":
    console.print("[bold green]🧪 Testing New Tools[/bold green]\n")

    test_weather()
    test_query_table()

    console.print("\n[bold green]✓ All tests complete![/bold green]\n")
