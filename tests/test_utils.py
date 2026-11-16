import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from utils import year_windows  # noqa: E402


def test_year_windows_basico():
    assert year_windows(2015, 2019) == [("01/01/2015", "31/12/2019")]


def test_year_windows_multiplas_janelas():
    assert year_windows(2015, 2026) == [
        ("01/01/2015", "31/12/2019"),
        ("01/01/2020", "31/12/2024"),
        ("01/01/2025", "31/12/2026"),
    ]


def test_year_windows_invalido():
    with pytest.raises(ValueError):
        year_windows(2026, 2020)
