import click
from plaintest.config import get_test_cases_dir, get_max_tc_id
from plaintest.template import TEMPLATE


@click.group()
def main():
    """Plaintest CLI"""
    pass


@main.command()
def init():
    """Initialize test cases directory"""
    test_dir = get_test_cases_dir()
    test_dir.mkdir(parents=True, exist_ok=True)
    click.echo(f"Initialized {test_dir}")


@main.command()
@click.argument("title", type=str, required=True)
def add(title: str):
    """Add new test case"""
    test_dir = get_test_cases_dir()
    tc_id = get_max_tc_id(test_dir) + 1
    output_dir = test_dir / f"{tc_id:0>3}"
    output_dir.mkdir(parents=True, exist_ok=True)
    tc_file = output_dir / "case.md"
    tc_file.write_text(TEMPLATE.safe_substitute(title=title))
    click.echo(f"Created {tc_file}")
