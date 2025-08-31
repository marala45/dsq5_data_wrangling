"""
Project 013 – Step 01: Scaffold config + output folders.

Usage:
    python scripts/013_dataset_audit_tool/step01_scaffold.py
    python scripts/013_dataset_audit_tool/step01_scaffold.py --config /full/path/013_audit.yaml
"""
from __future__ import annotations
from pathlib import Path
import argparse, sys, yaml

# Q5 root (…/dsq5_data_wrangling)
Q5_ROOT = Path(__file__).resolve().parents[2]
CFG_DEFAULT = Q5_ROOT / "configs/013_audit.yaml"

# logging utilities from local toolkit
from python_toolkit.logger import get_json_logger, CTX, CtxAdapter


def load_yaml(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 01 – scaffold folders for the audit tool.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT), help="Path to YAML config.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)

    if not cfg_path.exists():
        print(f"[step01] config not found: {cfg_path}")
        print("Hint: pass --config /full/path/to/013_audit.yaml or create the default file.")
        return 2

    cfg = load_yaml(cfg_path)
    CTX.set({"project": "013_dataset_audit_tool"})
    log = CtxAdapter(
        get_json_logger("audit.scaffold", log_filename="audit.log", base_dir=cfg.get("log_dir", "logs/013")),
        {},
    )
    log.info("scaffold_start", extra={"cfg_path": str(cfg_path)})

    # Create output folders
    Path(cfg.get("report_dir", "reports/013")).mkdir(parents=True, exist_ok=True)
    Path(cfg.get("results_dir", "results/013")).mkdir(parents=True, exist_ok=True)
    Path(cfg.get("log_dir", "logs/013")).mkdir(parents=True, exist_ok=True)

    log.info(
        "scaffold_ok",
        extra={
            "report_dir": cfg.get("report_dir", "reports/013"),
            "results_dir": cfg.get("results_dir", "results/013"),
            "log_dir": cfg.get("log_dir", "logs/013"),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
