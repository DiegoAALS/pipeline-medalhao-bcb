"""BRONZE: baixa as séries do BCB e salva o JSON bruto com data de ingestão."""
import json
import os
from datetime import datetime, timezone

import requests

from utils import BASE_PATH, SERIES, current_year, year_windows

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"


def fetch_series(code: int, start: str, end: str) -> list[dict]:
    resp = requests.get(
        URL.format(code=code),
        params={"formato": "json", "dataInicial": start, "dataFinal": end},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def main(start_year: int = 2015) -> None:
    out_dir = os.path.join(BASE_PATH, "bronze")
    os.makedirs(out_dir, exist_ok=True)
    ingested_at = datetime.now(timezone.utc).isoformat()

    for name, code in SERIES.items():
        rows = []
        for start, end in year_windows(start_year, current_year()):
            rows.extend(fetch_series(code, start, end))
        payload = [{**r, "serie": name, "ingested_at": ingested_at} for r in rows]
        path = os.path.join(out_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        print(f"[bronze] {name}: {len(payload)} registros -> {path}")


if __name__ == "__main__":
    main()
