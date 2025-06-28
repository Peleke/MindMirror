"""MindMirror CLI main application."""

import typer
from mindmirror_cli.commands import qdrant

app = typer.Typer(
    name="mindmirror",
    help="MindMirror knowledge base management CLI",
    add_completion=False,
)

app.add_typer(qdrant.app, name="qdrant")

if __name__ == "__main__":
    app() 