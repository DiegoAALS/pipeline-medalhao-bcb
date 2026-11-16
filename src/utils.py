from datetime import date

BASE_PATH = "data"
SERIES = {"ipca": 433, "selic": 4390, "usd": 1}


def year_windows(start_year: int, end_year: int, step: int = 5):
    """Divide o período em janelas de `step` anos: [(dd/MM/yyyy, dd/MM/yyyy), ...]."""
    if start_year > end_year:
        raise ValueError("start_year deve ser <= end_year")
    windows = []
    y = start_year
    while y <= end_year:
        y_end = min(y + step - 1, end_year)
        windows.append((f"01/01/{y}", f"31/12/{y_end}"))
        y = y_end + 1
    return windows


def current_year() -> int:
    return date.today().year
