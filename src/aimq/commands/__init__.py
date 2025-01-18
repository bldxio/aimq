"""
AIMQ command line interface.
"""
import typer

from .start import app as start_command

app = typer.Typer()
app.add_typer(start_command)