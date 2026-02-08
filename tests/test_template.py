"""Tests for the template functionality."""

import tempfile
from pathlib import Path

from plaintest.template import render_case_template, get_case_template


class TestDefaultTemplate:
    """Tests for the default template."""

    def test_render_default_template_with_title(self):
        """Test rendering the default template with just a title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            result = render_case_template(test_dir, title="My Test Case")

            assert "title: My test case" in result
            assert "## Steps" in result
            assert "## Expected" in result
            assert "tags: []" in result

    def test_render_default_template_no_custom_file(self):
        """Test that default template is used when no .template file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Ensure no .template file exists
            assert not (test_dir / ".template").exists()

            result = render_case_template(test_dir, title="Test")
            assert "title: Test" in result


class TestCustomTemplate:
    """Tests for custom template functionality."""

    def test_render_custom_template(self):
        """Test rendering with a custom .template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create a custom template
            custom_template = test_dir / ".template"
            custom_template.write_text("""---
title: {{ title }}
author: {{ author }}
---

Custom content for {{ title }}
""")

            result = render_case_template(
                test_dir, title="Custom Test", author="John Doe"
            )

            assert "title: Custom Test" in result
            assert "author: John Doe" in result
            assert "Custom content for Custom Test" in result

    def test_custom_template_with_defaults(self):
        """Test custom template with Jinja2 default filters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create a custom template with defaults
            custom_template = test_dir / ".template"
            custom_template.write_text("""---
title: {{ title }}
priority: {{ priority | default("low") }}
---
""")

            # Render without providing priority
            result = render_case_template(test_dir, title="Test")
            assert "priority: low" in result

            # Render with priority
            result = render_case_template(
                test_dir, title="Test", priority="high"
            )
            assert "priority: high" in result

    def test_custom_template_with_loops(self):
        """Test custom template with Jinja2 loops."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create a custom template with loops
            custom_template = test_dir / ".template"
            custom_template.write_text("""---
title: {{ title }}
---

## Tags
{% for tag in tags %}
- {{ tag }}
{% endfor %}
""")

            result = render_case_template(
                test_dir, title="Test", tags=["urgent", "bug", "regression"]
            )

            assert "- urgent" in result
            assert "- bug" in result
            assert "- regression" in result

    def test_custom_template_overrides_default(self):
        """Test that custom template completely overrides the default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create a minimal custom template
            custom_template = test_dir / ".template"
            custom_template.write_text("Simple: {{ title }}")

            result = render_case_template(test_dir, title="Simple Test")

            # Should not contain default template elements
            assert "## Steps" not in result
            assert "## Expected" not in result
            assert "Simple: Simple Test" in result


class TestTemplateEnvironment:
    """Tests for the Jinja2 environment."""

    def test_get_case_template_returns_environment(self):
        """Test that get_case_template returns a Jinja2 Environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            env = get_case_template(test_dir)

            # Should be able to get a template from the environment
            template = env.get_template("case")
            assert template is not None

    def test_trim_blocks_enabled(self):
        """Test that trim_blocks is enabled for cleaner output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Create a template with whitespace-sensitive content
            custom_template = test_dir / ".template"
            custom_template.write_text("""Start
{% if true %}
Middle
{% endif %}
End""")

            result = render_case_template(test_dir, title="Test")

            # With trim_blocks, there shouldn't be extra blank lines
            assert "Start\nMiddle\nEnd" in result
