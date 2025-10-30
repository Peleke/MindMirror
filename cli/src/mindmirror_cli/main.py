"""MindMirror CLI main application."""

import typer
from mindmirror_cli.commands import qdrant, supabase
from mindmirror_cli.commands import seed_habits, seed_movements, seed_pn_movements

app = typer.Typer(
    name="mindmirror",
    help="MindMirror knowledge base management CLI",
    add_completion=False,
)

app.add_typer(qdrant, name="qdrant")
app.add_typer(supabase, name="supabase")
app.add_typer(seed_habits, name="seed-habits")
app.add_typer(seed_movements, name="seed-movements")
app.add_typer(seed_pn_movements, name="seed-pn-movements")

if __name__ == "__main__":
    app() 