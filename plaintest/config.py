import re
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    test_cases_dir: str = "test-cases"


def get_config():
    pyproject_path = Path.cwd() / "pyproject.toml"

    if not pyproject_path.exists():
        return {"test_cases_dir": "test-cases"}

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
        section = data.get("tool", {}).get("plaintest", {})

        return Config(
            test_cases_dir=section.get("test_cases_dir", "test-cases"),
        )


def get_max_tc_id(test_cases_dir: Path):
    if not test_cases_dir.exists():
        return 0

    max_id = 0
    pattern = re.compile(r"\d{3,}")

    for item in test_cases_dir.iterdir():
        if item.is_dir():
            match = pattern.search(item.name)
            if match:
                tc_id = int(match.group())
                max_id = max(max_id, tc_id)

    return max_id


def get_test_cases_dir():
    config = get_config()
    return Path(config.test_cases_dir)
