"""
Project 013 – Step 02: Validate CSV files against required columns.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict
import argparse, csv, glob, sys, yaml

Q5_ROOT = Path(__file__).resolve().parents[2]
CFG_DEFAULT = Q5_ROOT / "configs/013_audit.yaml"

from python_toolkit.logger import get_json_logger, CTX, CtxAdapter


@dataclass
class ValidationResult:
    file: str
    missing_required: List[str]
    row_count: int


def load_cfg(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def required_missing(header: List[str], required: Iterable[str]) -> List[str]:
    hs = {h.strip() for h in header}
    return [col for col in required if col not in hs]


def validate_file(path: str, required_cols: List[str]) -> ValidationResult:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        missing = required_missing(header, required_cols)
        rows = sum(1 for _ in reader)
    return ValidationResult(file=path, missing_required=missing, row_count=rows)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 02 – validate CSV headers.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT), help="Path to YAML config.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"[step02] config not found: {cfg_path}")
        return 2

    cfg = load_cfg(cfg_path)
    CTX.set({"project": "013_dataset_audit_tool"})
    log = CtxAdapter(
        get_json_logger("audit.validate", log_filename="audit_validate.log", base_dir=cfg.get("log_dir", "logs/013")),
        {},
    )

    files = glob.glob(cfg["input_glob"])
    if not files:
        log.warning("no_input_files", extra={"glob": cfg["input_glob"]})
        return 0

    required = list(cfg.get("required_columns", []))
    results: List[Dict[str, object]] = []
    fail_any = False

    for fpath in files:
        vr = validate_file(fpath, required)
        results.append({"file": vr.file, "rows": vr.row_count, "missing": "|".join(vr.missing_required)})
        if cfg.get("fail_on_missing_required", True) and vr.missing_required:
            fail_any = True
            log.error("missing_required", extra={"file": vr.file, "missing": vr.missing_required})
        else:
            log.info("validated", extra={"file": vr.file, "rows": vr.row_count})

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
    raise SystemExit(main())
