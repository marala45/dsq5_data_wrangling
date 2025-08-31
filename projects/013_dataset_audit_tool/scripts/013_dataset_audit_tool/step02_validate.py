"""
Author: Mahmoud Rahnama
GitHub: https://github.com/marala45
Filename: step02_validate.py
Date: 2025-08-25
Description:
    Project 013 – Step 02: Validate input CSV files against required columns.

What you learn:
    - Parse a YAML config
    - Use structured logging with run context (CTX)
    - Read CSV safely and validate headers
    - Write machine‑readable results to results/{project}/
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict
import csv
import glob
import sys
import yaml

from python_toolkit.logger import get_json_logger, CTX, CtxAdapter


# ---------- data model ----------
@dataclass
class ValidationResult:
    file: str
    missing_required: List[str]
    row_count: int


# ---------- helpers ----------
def load_cfg() -> dict:
    cfg_path = Path("configs/013_audit.yaml")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def required_check(header: List[str], required: Iterable[str]) -> List[str]:
    hs = {h.strip() for h in header}
    return [col for col in required if col not in hs]


def validate_file(path: str, required_cols: List[str]) -> ValidationResult:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        missing = required_check(header, required_cols)
        rows = sum(1 for _ in reader)
    return ValidationResult(file=path, missing_required=missing, row_count=rows)


# ---------- main ----------
def main() -> int:
    cfg = load_cfg()

    # structured logging with run-wide context
    CTX.set({"project": "013_dataset_audit_tool"})
    log = CtxAdapter(
        get_json_logger(
            "audit.validate",
            log_filename="audit_validate.log",
            base_dir=cfg.get("log_dir", "logs/013"),
        ),
        {},
    )

    # collect files using glob
    files = glob.glob(cfg["input_glob"])
    if not files:
        log.warning("no_input_files", extra={"glob": cfg["input_glob"]})
        return 0

    required = list(cfg.get("required_columns", []))
    results: List[Dict[str, object]] = []
    fail_any = False

    for fpath in files:
        vr = validate_file(fpath, required)
        results.append(
            {
                "file": vr.file,
                "rows": vr.row_count,
                "missing": "|".join(vr.missing_required) if vr.missing_required else "",
            }
        )

        if cfg.get("fail_on_missing_required", True) and vr.missing_required:
            fail_any = True
            log.error("missing_required", extra={"file": vr.file, "missing": vr.missing_required})
        else:
            log.info("validated", extra={"file": vr.file, "rows": vr.row_count})

    # write machine-readable results
    outp = Path(cfg.get("results_dir", "results/013")) / "validation_results.csv"
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as w:
        writer = csv.DictWriter(w, fieldnames=["file", "rows", "missing"])
        writer.writeheader()
        writer.writerows(results)

    if fail_any:
        log.warning("validation_failed_some_files", extra={"count": len(results)})
        return 2

    log.info("validation_ok", extra={"count": len(results)})
    return 0


if __name__ == "__main__":
    sys.exit(main())
