import click
import frontmatter
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from plaintest.analysis import find_undecorated_tests
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


@main.command()
@click.option(
    "--tests-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("tests"),
    help="Directory containing test files",
)
def report(tests_dir: Path):
    """Generate a coverage report showing test case status"""
    test_cases_dir = get_test_cases_dir()

    if not test_cases_dir.exists():
        console.print(
            f"[red]✗[/red] Test cases directory {test_cases_dir} doesn't exist"
        )
        console.print("[yellow]Run 'plaintest init' to create it[/yellow]")
        raise click.Exit(1)

    # Perform analysis
    console.print("[dim]Analyzing test coverage...[/dim]")
    results = find_undecorated_tests(test_cases_dir, tests_dir)

    total_cases = len(results.test_cases_without_tests) + len(
        results.covered_test_cases
    )

    if total_cases == 0:
        console.print("[yellow]No test cases found[/yellow]")
        raise click.Exit(0)

    # Calculate statistics
    covered_count = len(results.covered_test_cases)
    uncovered_count = len(results.test_cases_without_tests)
    coverage_percentage = (covered_count / total_cases) * 100

    # Display summary
    console.print()
    console.print(f"Total test cases: {total_cases}")
    console.print(f"Cases with tests: [green]{covered_count}[/green]")
    console.print(f"Cases without tests: [red]{uncovered_count}[/red]")
    console.print(
        f"Coverage: [bold cyan]{coverage_percentage:.1f}%[/bold cyan]"
    )
    console.print()

    # Display uncovered cases in a table
    if uncovered_count > 0:
        console.print("[bold red]Cases without tests[/bold red]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(
            "Test Case ID", style="cyan", width=15, justify="center"
        )
        table.add_column("Case File", style="dim")
        table.add_column("Title", style="yellow")

        for tc_id in results.test_cases_without_tests:
            case_file = test_cases_dir / tc_id / "case.md"

            with case_file.open() as f:
                metadata = frontmatter.load(f)
                title = metadata.get("title", "N/A")
                table.add_row(tc_id, str(case_file), str(title))

        console.print(table)
        console.print()

    # Display tests without corresponding test cases
    if results.tests_without_test_cases:
        console.print(
            "[bold yellow]Tests Marked With Non-Existent Case IDs[/bold yellow]"
        )
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Case ID", style="cyan", width=12, justify="center")
        table.add_column("Test File", style="dim")
        table.add_column("Test Name", style="yellow")

        for tc_id in results.tests_without_test_cases:
            # Get all tests for this case ID

            for test_node in results.decorated_tests[tc_id]:
                # Parse test_node format: "path/to/file.py::TestClass::test_name" or "path/to/file.py::test_name"
                parts = test_node.split("::")
                test_file = parts[0]
                test_name = "::".join(
                    parts[1:]
                )  # Join back in case there's a class

                table.add_row(tc_id, test_file, test_name)

        console.print(table)
        console.print()

    # Exit with the number of uncovered cases
    raise SystemExit(uncovered_count)
