"""
Author: Mahmoud Rahnama
GitHub: https://github.com/marala45
Filename: step03_profile.py
Date: 2025-08-25
Description:
    Project 013 – Step 03: Profile numeric columns across input CSV files.

What you learn:
    - Parse a YAML config
    - Read CSV with DictReader and compute quick stats without pandas
    - Write results to results/{project}/
    - Use a simple console logger for human-readable progress
"""

from __future__ import annotations

import csv
import glob
import statistics
import sys
from pathlib import Path
from typing import Dict, List

import yaml
from python_toolkit.logger import get_console_logger


def load_cfg() -> dict:
    cfg_path = Path("configs/013_audit.yaml")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def profile_numeric_column(file: str, column: str) -> Dict[str, float]:
    vals: List[float] = []
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            v = row.get(column, "")
            if isinstance(v, str) and v.strip() == "":
                continue
            try:
                vals.append(float(v))
            except (ValueError, TypeError):
                # non-numeric values are ignored
                pass

    if not vals:
        return {"count": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}

    return {
        "count": float(len(vals)),
        "mean": statistics.fmean(vals),
        "min": min(vals),
        "max": max(vals),
    }


def main() -> int:
    cfg = load_cfg()
    log = get_console_logger("audit.profile")

    files = glob.glob(cfg["input_glob"])
    if not files:
        log.warning("no_input_files")
        return 0

    results_dir = Path(cfg.get("results_dir", "results/013"))
    results_dir.mkdir(parents=True, exist_ok=True)
    out_file = results_dir / "numeric_profile.csv"

    numeric_cols = list(cfg.get("numeric_columns", []))
    if not numeric_cols:
        log.warning("no_numeric_columns_in_config")
        return 0

    with out_file.open("w", newline="", encoding="utf-8") as w:
        fieldnames = ["file", "column", "count", "mean", "min", "max"]
        writer = csv.DictWriter(w, fieldnames=fieldnames)
        writer.writeheader()

        for fpath in files:
            for col in numeric_cols:
                stats = profile_numeric_column(fpath, col)
                writer.writerow({"file": fpath, "column": col, **stats})
                log.info(f"profiled {fpath} :: {col} -> {stats}")

    log.info(f"wrote {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
