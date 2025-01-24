"""
AIMQ command line interface.
"""
import typer

from .start import start
from .send import send
from .enable import enable
from .disable import disable
from .init import init

app = typer.Typer(no_args_is_help=True)

app.command()(start)
app.command()(send)
app.command()(enable)
app.command()(disable)
app.command()(init)
