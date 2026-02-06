import ast
from pathlib import Path
from typing import Tuple

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader


def get_test_function_source(
    file_path: Path,
    function_name: str,
    class_name: str | None = None,
) -> str:
    """
    Extract the source code of a specific test function from a Python file.

    Args:
        file_path: Path to the Python test file
        function_name: Name of the test function
        class_name: Name of the containing class (if any)

    Returns:
        Source code of the function as a string
    """
    try:
        content = file_path.read_text()
        lines = content.splitlines()
        tree = ast.parse(content, filename=str(file_path))

        # Find the function in the AST
        for node in ast.walk(tree):
            if class_name:
                # Look for class first, then function within it
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if (
                            isinstance(item, ast.FunctionDef)
                            and item.name == function_name
                        ):
                            return _extract_node_source(item, lines)
            else:
                # Look for standalone function
                if (
                    isinstance(node, ast.FunctionDef)
                    and node.name == function_name
                ):
                    return _extract_node_source(node, lines)

        return f"# Could not find function {function_name}"
    except Exception as e:
        return f"# Error reading source: {e}"


def _extract_node_source(node: ast.AST, lines: list[str]) -> str:
    """
    Extract source code for an AST node including decorators.

    Args:
        node: AST node (typically FunctionDef)
        lines: Lines of the source file

    Returns:
        Source code as string
    """
    if not hasattr(node, "lineno"):
        return ""

    # Include decorators if present
    start_line = node.lineno
    if hasattr(node, "decorator_list") and node.decorator_list:
        start_line = node.decorator_list[0].lineno

    end_line = node.end_lineno if hasattr(node, "end_lineno") else node.lineno

    # Extract lines (convert from 1-based to 0-based indexing)
    source_lines = lines[start_line - 1 : end_line]

    return "\n".join(source_lines)


def parse_test_node_id(
    test_node: str, root_dir: Path
) -> Tuple[Path, str, str | None]:
    """
    Parse a pytest node ID into file path, function name, and optional class name.

    Args:
        test_node: Node ID like "tests/test_file.py::test_function" or
                   "tests/test_file.py::TestClass::test_method"
        root_dir: Root directory of the project

    Returns:
        Tuple of (file_path, function_name, class_name)
    """
    parts = test_node.split("::")
    file_path = root_dir / parts[0]

    if len(parts) == 2:
        # Standalone function
        return file_path, parts[1], None
    elif len(parts) == 3:
        # Class method
        return file_path, parts[2], parts[1]
    else:
        return file_path, test_node, None


def generate_html_report(
    test_cases_dir: Path,
    decorated_tests: dict[str, list[str]],
    tests_dir: Path,
    output_path: Path,
) -> None:
    """
    Generate an HTML report showing test cases with their pytest implementations.

    Args:
        test_cases_dir: Directory containing test case Markdown files
        decorated_tests: dictionary mapping test case IDs to list of test node IDs
        tests_dir: Test files directory
        output_path: Where to write the HTML report
    """
    # Collect all test case data
    test_case_data = []

    for tc_id in sorted(decorated_tests.keys(), key=lambda x: int(x)):
        case_file = test_cases_dir / tc_id / "case.md"

        if not case_file.exists():
            continue

        # Parse the Markdown file
        with case_file.open("r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            title = post.get("title", f"Test Case {tc_id}")
            tags = post.get("tags", [])
            markdown_content = post.content

        # Convert Markdown to HTML
        md = markdown.Markdown(extensions=["fenced_code", "tables", "nl2br"])
        html_content = md.convert(markdown_content)

        # Get source code for all tests linked to this case
        test_sources = []
        for test_node in decorated_tests[tc_id]:
            file_path, func_name, class_name = parse_test_node_id(
                test_node, tests_dir
            )
            source_code = get_test_function_source(
                file_path, func_name, class_name
            )
            test_sources.append({"node_id": test_node, "source": source_code})

        test_case_data.append(
            {
                "id": tc_id,
                "title": title,
                "tags": tags,
                "markdown_html": html_content,
                "test_sources": test_sources,
            }
        )

    # Generate HTML
    html = _generate_html_template(test_case_data)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def _generate_html_template(test_case_data: list[dict]) -> str:
    """Generate the complete HTML document using Jinja2 templates."""
    # Set up Jinja2 environment
    templates_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Load templates
    report_template = env.get_template("report.html.j2")
    styles_template = env.get_template("styles.css.j2")

    # Process test case data to highlight source code
    for tc in test_case_data:
        for test_src in tc["test_sources"]:
            test_src["source"] = _highlight_python_code(test_src["source"])

    # Render the styles
    styles = styles_template.render()

    # Render the report
    html = report_template.render(test_cases=test_case_data, styles=styles)

    return html


def _highlight_python_code(code: str) -> str:
    """Apply syntax highlighting to Python code using Pygments."""
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter

    # Use HtmlFormatter with inline styles and the 'monokai' style
    formatter = HtmlFormatter(noclasses=True, style="monokai", nowrap=True)

    # Highlight the code
    highlighted = highlight(code, PythonLexer(), formatter)

    return highlighted
