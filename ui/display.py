from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from core.parser import FuzzResult
from rich import print as rprint

console = Console()


def print_status(message: str, level: str = "info") -> None:
    if level == "info":
        rprint(f"[cyan][*][/cyan] {message}")

    elif level == "found":
        rprint(f"[green][+][/green] {message}")

    elif level == "warn":
        rprint(f"[yellow][!][/yellow] {message}")


def print_banner(target: str) -> None:
    console.print(
        Panel(
            f"[bold cyan]ffuf-automation[/bold cyan]\n[white]target: {target}[/white]",
            border_style="cyan",
        )
    )


def print_results(results: list[FuzzResult], mode: str) -> None:
    table = Table(title=f"[bold]{mode.upper()} Results[/bold]", border_style="cyan")
    table.add_column("URL", style="green")
    table.add_column("Status", style="yellow", justify="center")
    table.add_column("Size", justify="right")
    table.add_column("Words", justify="right")
    table.add_column("Lines", justify="right")

    for r in results:
        table.add_row(r.url, str(r.status), str(r.size), str(r.words), str(r.lines))

    console.print(table)
