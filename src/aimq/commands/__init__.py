"""
AIMQ command line interface.
"""

import typer

from .create import create
from .disable import disable
from .enable import enable
from .enable_realtime import enable_realtime
from .init import init
from .list import list_queues
from .send import send
from .start import start

app = typer.Typer(no_args_is_help=True)

app.command()(start)
app.command()(send)
app.command()(create)
app.command(name="list")(list_queues)
app.command()(enable)
app.command()(disable)
app.command(name="enable-realtime")(enable_realtime)
app.command()(init)
