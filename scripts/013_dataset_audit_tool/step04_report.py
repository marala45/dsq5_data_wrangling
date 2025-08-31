"""
Project 013 – Step 04: Build a Markdown report from validation & profiling outputs.
"""
from __future__ import annotations
import argparse, csv, sys, yaml
from pathlib import Path

Q5_ROOT = Path(__file__).resolve().parents[2]
CFG_DEFAULT = Q5_ROOT / "configs/013_audit.yaml"

from python_toolkit.logger import get_file_logger


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
    ap = argparse.ArgumentParser(description="Step 04 – markdown report.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT), help="Path to YAML config.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"[step04] config not found: {cfg_path}")
        return 2

    cfg = load_cfg(cfg_path)
    log = get_file_logger("audit.report", log_filename="audit_report.log", base_dir=cfg.get("log_dir", "logs/013"))

    results_dir = Path(cfg.get("results_dir", "results/013"))
    val_csv = results_dir / "validation_results.csv"
    prof_csv = results_dir / "numeric_profile.csv"

    report_dir = Path(cfg.get("report_dir", "reports/013"))
    report_dir.mkdir(parents=True, exist_ok=True)
    out_md = report_dir / "audit_report.md"

    sections = ["# Dataset Audit Report\n", "## Validation results\n"]
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
