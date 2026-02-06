import ast
from pathlib import Path
from typing import Tuple

import frontmatter
import markdown


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
    root_dir: Path,
    output_path: Path,
) -> None:
    """
    Generate an HTML report showing test cases with their pytest implementations.

    Args:
        test_cases_dir: Directory containing test case markdown files
        decorated_tests: dictionary mapping test case IDs to list of test node IDs
        root_dir: Root directory of the project (for resolving test file paths)
        output_path: Where to write the HTML report
    """
    # Collect all test case data
    test_case_data = []

    for tc_id in sorted(decorated_tests.keys(), key=lambda x: int(x)):
        case_file = test_cases_dir / tc_id / "case.md"

        if not case_file.exists():
            continue

        # Parse the markdown file
        with case_file.open("r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            title = post.get("title", f"Test Case {tc_id}")
            tags = post.get("tags", [])
            markdown_content = post.content

        # Convert markdown to HTML
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
    """Generate the complete HTML document."""

    # Build the test case sections
    test_case_sections = []
    for tc in test_case_data:
        tags_html = " ".join(
            [f'<span class="tag">{tag}</span>' for tag in tc["tags"]]
        )

        # Build test source sections
        test_sources_html = []
        for test_src in tc["test_sources"]:
            test_sources_html.append(f"""
                <div class="test-source">
                    <div class="test-node-id">{test_src['node_id']}</div>
                    <pre><code class="language-python">{_escape_html(test_src['source'])}</code></pre>
                </div>
            """)

        test_case_sections.append(f"""
        <div class="test-case-container" id="tc-{tc['id']}">
            <div class="test-case-header">
                <h2>Test Case {tc['id']}: {_escape_html(tc['title'])}</h2>
                <div class="tags">{tags_html}</div>
            </div>
            <div class="split-view">
                <div class="test-case-markdown">
                    <h3>Test Case Specification</h3>
                    {tc['markdown_html']}
                </div>
                <div class="test-implementation">
                    <h3>Test Implementation</h3>
                    {''.join(test_sources_html)}
                </div>
            </div>
        </div>
        """)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plaintest Validation Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .container {{
            max-width: 100%;
            padding: 2rem;
        }}
        
        .test-case-container {{
            background: white;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .test-case-header {{
            padding: 1.5rem;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .test-case-header h2 {{
            color: #667eea;
            margin-bottom: 0.5rem;
        }}
        
        .tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .tag {{
            background: #667eea;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
        }}
        
        .split-view {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 400px;
        }}
        
        .test-case-markdown,
        .test-implementation {{
            padding: 2rem;
            overflow-y: auto;
        }}
        
        .test-case-markdown {{
            border-right: 2px solid #e9ecef;
            background: #fafafa;
        }}
        
        .test-case-markdown h3,
        .test-implementation h3 {{
            color: #495057;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .test-case-markdown h2 {{
            color: #343a40;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            font-size: 1.3rem;
        }}
        
        .test-case-markdown ul,
        .test-case-markdown ol {{
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .test-case-markdown li {{
            margin-bottom: 0.5rem;
        }}
        
        .test-case-markdown p {{
            margin-bottom: 1rem;
        }}
        
        .test-source {{
            margin-bottom: 2rem;
        }}
        
        .test-node-id {{
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            background: #f1f3f5;
            padding: 0.5rem 1rem;
            border-left: 4px solid #667eea;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #495057;
            border-radius: 4px;
        }}
        
        pre {{
            background: #282c34;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 0;
        }}
        
        code {{
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 0.9rem;
            color: #abb2bf;
        }}
        
        .language-python {{
            display: block;
        }}
        
        @media (max-width: 1200px) {{
            .split-view {{
                grid-template-columns: 1fr;
            }}
            
            .test-case-markdown {{
                border-right: none;
                border-bottom: 2px solid #e9ecef;
            }}
        }}
        
        /* Syntax highlighting for Python */
        .language-python {{
            color: #abb2bf;
        }}
    </style>
</head>
<body>
    <header>
        <h1>📋 Plaintest Validation Report</h1>
        <p>Test Case Specifications vs. Pytest Implementations</p>
    </header>
    
    <div class="container">
        {''.join(test_case_sections)}
    </div>
    
    <script>
        // Add syntax highlighting for Python keywords
        document.addEventlistener('DOMContentLoaded', function() {{
            const keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 
                            'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'assert',
                            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'];
            
            document.querySelectorAll('code.language-python').forEach(block => {{
                let html = block.innerHTML;
                
                // Highlight decorators
                html = html.replace(/(@\w+)/g, '<span style="color: #c678dd;">$1</span>');
                
                // Highlight strings
                html = html.replace(/(".*?"|'.*?')/g, '<span style="color: #98c379;">$1</span>');
                
                // Highlight comments
                html = html.replace(/(#.*$)/gm, '<span style="color: #5c6370;">$1</span>');
                
                // Highlight keywords
                keywords.forEach(keyword => {{
                    const regex = new RegExp('\\\\b(' + keyword + ')\\\\b', 'g');
                    html = html.replace(regex, '<span style="color: #c678dd;">$1</span>');
                }});
                
                block.innerHTML = html;
            }});
        }});
    </script>
</body>
</html>"""


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
