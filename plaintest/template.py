from pathlib import Path
from jinja2 import Environment, BaseLoader, TemplateNotFound

DEFAULT_TEMPLATE = """---
title: {{ title | capitalize }}
tags: []
---

## Steps
1. 

## Expected


"""


class CustomTemplateLoader(BaseLoader):
    def __init__(self, test_cases_dir: Path):
        self.test_cases_dir = test_cases_dir

    def get_source(self, environment, template):
        if template == "case":
            custom_template_path = self.test_cases_dir / ".template"
            if custom_template_path.exists():
                source = custom_template_path.read_text()
                return (
                    source,
                    str(custom_template_path),
                    lambda: True,
                )
            else:
                return DEFAULT_TEMPLATE, None, lambda: True
        raise TemplateNotFound(template)


def get_case_template(test_cases_dir: Path) -> Environment:
    loader = CustomTemplateLoader(test_cases_dir)
    env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
    return env


def render_case_template(test_cases_dir: Path, **kwargs) -> str:
    env = get_case_template(test_cases_dir)
    template = env.get_template("case")
    return template.render(**kwargs)
