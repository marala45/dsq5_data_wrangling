# projects/013_dataset_audit_tool/scripts/013_dataset_audit_tool/step04_report.py
from __future__ import annotations

import argparse
import csv
from pathlib import Path
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
    from python_toolkit.logger import get_file_logger  # type: ignore
except Exception:
    import logging
    def get_file_logger(name: str = "app", log_filename: str = "audit_report.log", base_dir: str = "logs/013"):
        lg = logging.getLogger(name)
        if not lg.handlers:
            lg.setLevel(logging.INFO)
            Path(base_dir).mkdir(parents=True, exist_ok=True)
            h = logging.FileHandler(Path(base_dir) / log_filename, encoding="utf-8")
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


def md_table(rows, headers):
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 04: build Markdown report.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT),
                    help=f"Path to YAML config (default: {CFG_DEFAULT})")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"[step04] config not found: {cfg_path}")
        return 2
    cfg = load_cfg(cfg_path)

    log = get_file_logger(
        "audit.report",
        log_filename="audit_report.log",
        base_dir=cfg.get("log_dir", "logs/013"),
    )

    results_dir = Path(cfg.get("results_dir", "results/013"))
    val_csv = results_dir / "validation_results.csv"
    prof_csv = results_dir / "numeric_profile.csv"

    report_dir = Path(cfg.get("report_dir", "reports/013"))
    report_dir.mkdir(parents=True, exist_ok=True)
    out_md = report_dir / "audit_report.md"

    sections = ["# Dataset Audit Report\n"]

    sections.append("## Validation results\n")
    if val_csv.exists():
        with val_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        sections.append(md_table(rows, ["file", "rows", "missing"]))
        sections.append("")
    else:
        sections.append("No validation results found.\n")

    sections.append("## Numeric profiling\n")
    if prof_csv.exists():
        with prof_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        sections.append(md_table(rows, ["file", "column", "count", "mean", "min", "max"]))
        sections.append("")
    else:
        sections.append("No numeric profile found.\n")

    out_md.write_text("\n".join(sections), encoding="utf-8")
    log.info("report_written", extra={"path": str(out_md)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
