# projects/013_dataset_audit_tool/scripts/013_dataset_audit_tool/step03_profile.py
from __future__ import annotations

import argparse
import csv
import glob
import statistics
from pathlib import Path
from typing import Dict, List
import sys
import yaml

from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
# scripts/013_dataset_audit_tool/ -> parent
# scripts/ -> parents[1]
# <repo root: dsq5_data_wrangling> -> parents[2]
ROOT = THIS_DIR.parents[2]

def default_cfg_path() -> Path:
    return ROOT / "configs/013_audit.yaml"

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

try:
    from python_toolkit.logger import get_console_logger  # type: ignore
except Exception:
    import logging
    def get_console_logger(name: str = "app"):
        lg = logging.getLogger(name)
        if not lg.handlers:
            lg.setLevel(logging.INFO)
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s | %(name)s | %(message)s"))
            lg.addHandler(h)
            lg.propagate = False
        return lg


THIS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = THIS_DIR.parents[2]
CFG_DEFAULT = PROJECT_DIR / "configs/013_audit.yaml"


def load_cfg(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


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
                pass

    if not vals:
        return {"count": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}

    return {
        "count": float(len(vals)),
        "mean": statistics.fmean(vals),
        "min": min(vals),
        "max": max(vals),
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 03: numeric profiling for selected columns.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT),
                    help=f"Path to YAML config (default: {CFG_DEFAULT})")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"[step03] config not found: {cfg_path}")
        return 2
    cfg = load_cfg(cfg_path)
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
    raise SystemExit(main())
