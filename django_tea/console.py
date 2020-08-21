import functools
from typing import List, Union, Type, Optional

import typer
from rich import print
from rich.console import Console

from django_tea import serde
from django_tea import errors
from django_tea.config import Config
from django_tea.enums import ConsoleFormat
from django_tea.table import RichTableMixin


def output(
    fmt: ConsoleFormat,
    model: Optional[Type[RichTableMixin]],
    objs: Union[List[RichTableMixin], RichTableMixin],
):
    console = Console()

    if fmt == ConsoleFormat.json:
        console.print(serde.json_dumps(objs))

    elif fmt == ConsoleFormat.text:
        if model is None:
            console.print(objs)
            return

        if objs is None or (isinstance(objs, list) and len(objs) == 0):
            console.print(f"[cyan]No {model.__name__}s found.[/cyan]")
            return

        if not isinstance(objs, list):
            objs = [objs]

        table = model.get_rich_table()
        for o in objs:
            table.add_row(*o.to_rich_row())

        console.print(table)


def command(
    app: typer.Typer,
    model: Optional[Type[RichTableMixin]] = None,
    name: Optional[str] = None,
    *,
    help: Optional[str] = None,
    epilog: Optional[str] = None,
    short_help: Optional[str] = None,
    options_metavar: str = "[OPTIONS]",
    add_help_option: bool = True,
    no_args_is_help: bool = False,
    hidden: bool = False,
    deprecated: bool = False,
):
    def decorator(func):
        @app.command(
            name=name,
            help=help,
            epilog=epilog,
            short_help=short_help,
            options_metavar=options_metavar,
            add_help_option=add_help_option,
            no_args_is_help=no_args_is_help,
            hidden=hidden,
            deprecated=deprecated,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                config = Config.get_application_config()
                result = func(*args, **kwargs)
                if model is not None:
                    output(fmt=config.format, model=model, objs=result)
                else:
                    return output(fmt=config.format, model=None, objs=result)
            except errors.DjangoTeaError as e:
                config = Config.get_application_config()
                if config.format == config.Format.text:
                    print(f"[red]{e.message}[/red]")
                elif config.format == config.Format.json:
                    print(serde.json_dumps({"error": e.message}))

        return wrapper

    return decorator
