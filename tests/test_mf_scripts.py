"""Ensure every CorpLang script in tests/mf_test executes without runtime errors."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MF_TEST_DIR = PROJECT_ROOT / "tests" / "mf_test"


def _collect_mf_scripts(root: Path) -> List[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.glob("*.mp")
        if path.is_file() and not path.name.startswith("_")
    )


MF_SCRIPTS: List[Path] = _collect_mf_scripts(MF_TEST_DIR)


@pytest.mark.parametrize("script_path", MF_SCRIPTS, ids=lambda path: path.name)
def test_mf_script_executes(script_path: Path) -> None:
    """Run each CorpLang test script through mf.py and assert successful execution."""

    command = [sys.executable, "mf.py", str(script_path)]
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (
        result.returncode == 0
    ), f"Script {script_path.name} failed with code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
