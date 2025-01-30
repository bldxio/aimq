"""AIMQ command line interface."""

import typer

from .init import init
from .send import send
from .start import start

app = typer.Typer(no_args_is_help=True)

app.command()(init)
app.command()(send)
app.command()(start)
