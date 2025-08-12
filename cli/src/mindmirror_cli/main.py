"""MindMirror CLI main application."""

import typer
from mindmirror_cli.commands import qdrant, supabase
from mindmirror_cli.commands import seed_habits

app = typer.Typer(
    name="mindmirror",
    help="MindMirror knowledge base management CLI",
    add_completion=False,
)

app.add_typer(qdrant.app, name="qdrant")
app.add_typer(supabase.app, name="supabase")
app.add_typer(seed_habits.app, name="seed-habits")

if __name__ == "__main__":
    app() 