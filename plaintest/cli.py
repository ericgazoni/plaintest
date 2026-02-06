import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from plaintest.config import get_test_cases_dir, get_max_tc_id
from plaintest.template import TEMPLATE

console = Console()


@click.group()
def main():
    """Plaintest CLI"""
    pass


@main.command()
def init():
    """Initialize test cases directory"""
    test_dir = get_test_cases_dir()
    test_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Initialized {test_dir}")


@main.command()
@click.argument("title", type=str, required=False)
def add(title: str):
    """Add new test case(s) interactively"""
    test_dir = get_test_cases_dir()

    # Ensure test directory exists
    if not test_dir.exists():
        console.print(
            f"[yellow]Test directory {test_dir} doesn't exist. Initializing...[/yellow]"
        )
        test_dir.mkdir(parents=True, exist_ok=True)

    while True:
        # Get title from argument or prompt
        if title is None:
            title = Prompt.ask("[bold cyan]Enter test case title[/bold cyan]")

        # Create test case
        tc_id = get_max_tc_id(test_dir) + 1
        output_dir = test_dir / f"{tc_id:0>3}"
        output_dir.mkdir(parents=True, exist_ok=True)
        tc_file = output_dir / "case.md"
        tc_file.write_text(TEMPLATE.safe_substitute(title=title))
        console.print(f"[green]✓[/green] Created {tc_file}")

        # Ask if user wants to add another
        if not Confirm.ask(
            "[bold]Add another test case?[/bold]", default=True
        ):
            break

        # Reset title for next iteration
        title = None

    console.print("[bold green]Done![/bold green]")
