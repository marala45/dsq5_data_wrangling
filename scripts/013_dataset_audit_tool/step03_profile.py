"""
Project 013 – Step 03: Profile numeric columns across input CSV files.
"""
from __future__ import annotations
import argparse, csv, glob, statistics, sys, yaml
from pathlib import Path
from typing import Dict, List

Q5_ROOT = Path(__file__).resolve().parents[2]
CFG_DEFAULT = Q5_ROOT / "configs/013_audit.yaml"

from python_toolkit.logger import get_console_logger


def load_cfg(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def numeric_profile(file: str, column: str) -> Dict[str, float]:
    vals: List[float] = []
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            v = row.get(column, "")
            if isinstance(v, str) and not v.strip():
                continue
            try:
                vals.append(float(v))
            except Exception:
                pass
    if not vals:
        return {"count": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}
    return {"count": float(len(vals)), "mean": statistics.fmean(vals), "min": min(vals), "max": max(vals)}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 03 – numeric profiling.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT), help="Path to YAML config.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    log = get_console_logger("audit.profile")

    if not cfg_path.exists():
        log.error(f"[step03] config not found: {cfg_path}")
        return 2

    cfg = load_cfg(cfg_path)
    files = glob.glob(cfg["input_glob"])
    if not files:
        log.warning("no_input_files")
        return 0

    out_dir = Path(cfg.get("results_dir", "results/013"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "numeric_profile.csv"

    numeric_cols = list(cfg.get("numeric_columns", []))
    if not numeric_cols:
        log.warning("no_numeric_columns_in_config")
        return 0

    with out_file.open("w", newline="", encoding="utf-8") as w:
        writer = csv.DictWriter(w, fieldnames=["file", "column", "count", "mean", "min", "max"])
        writer.writeheader()
        for fpath in files:
            for col in numeric_cols:
                stats = numeric_profile(fpath, col)
                writer.writerow({"file": fpath, "column": col, **stats})
                log.info(f"profiled {fpath} :: {col} -> {stats}")

    log.info(f"wrote {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
