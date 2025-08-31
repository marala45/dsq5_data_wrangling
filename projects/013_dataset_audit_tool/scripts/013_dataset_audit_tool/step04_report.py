"""
Author: Mahmoud Rahnama
GitHub: https://github.com/marala45
Filename: step04_report.py
Date: 2025-08-25
Description:
    Project 013 – Step 04: Build a Markdown report from validation and profiling outputs.

What you learn:
    - Read config (YAML)
    - Aggregate CSV outputs from previous steps
    - Render a simple Markdown table
    - Write a final report to reports/{project}/
    - File-based logging to logs/{project}/
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import yaml
from python_toolkit.logger import get_file_logger


def load_cfg() -> dict:
    cfg_path = Path("configs/013_audit.yaml")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def md_table(rows, headers):
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def main() -> int:
    cfg = load_cfg()
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

    # Validation section
    sections.append("## Validation results\n")
    if val_csv.exists():
        with val_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        sections.append(md_table(rows, ["file", "rows", "missing"]))
        sections.append("")  # spacing
    else:
        sections.append("No validation results found.\n")

    # Profiling section
    sections.append("## Numeric profiling\n")
    if prof_csv.exists():
        with prof_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        sections.append(md_table(rows, ["file", "column", "count", "mean", "min", "max"]))
        sections.append("")  # spacing
    else:
        sections.append("No numeric profile found.\n")

    out_md.write_text("\n".join(sections), encoding="utf-8")
    log.info("report_written", extra={"path": str(out_md)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
