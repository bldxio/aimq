"""
AIMQ command line interface.
"""

import typer

from . import realtime, schema
from .chat import chat
from .create import create
from .init import init
from .list import list_queues
from .send import send
from .start import start

app = typer.Typer(no_args_is_help=True)

# Core commands
app.command()(start)
app.command()(send)
app.command()(create)
app.command(name="list")(list_queues)
app.command()(init)
app.command()(chat)

# Subcommands
app.add_typer(realtime.app, name="realtime")
app.add_typer(schema.app, name="schema")
