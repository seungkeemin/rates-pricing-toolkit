import json
from pathlib import Path

import pytest

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def inputs():
    return json.loads((FIX / "inputs.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def excel():
    """Values from my own Excel answers (the assignment workbooks), used as the reference."""
    return json.loads((FIX / "excel_expected.json").read_text(encoding="utf-8"))
