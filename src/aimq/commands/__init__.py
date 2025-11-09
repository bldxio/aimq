"""
AIMQ command line interface.
"""

import typer

from .create import create
from .disable import disable
from .enable import enable
from .init import init
from .send import send
from .start import start

app = typer.Typer(no_args_is_help=True)

app.command()(start)
app.command()(send)
app.command()(create)
app.command()(enable)
app.command()(disable)
app.command()(init)
