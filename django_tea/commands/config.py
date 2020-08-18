import typer

from django_tea.console import command
from django_tea.config import ConfigEntry
from django_tea.engine.config_engine import ConfigEngine


app = typer.Typer(name="config", help="Configuration set/get.")


@command(app, model=ConfigEntry, name="list")
def list_values():
    """List all configuration values."""
    return ConfigEngine.list()


@command(app, model=ConfigEntry, name="set")
def set_value(key: str, value: str):
    """Set a configuration key."""
    return ConfigEngine.set(key=key, value=value)
