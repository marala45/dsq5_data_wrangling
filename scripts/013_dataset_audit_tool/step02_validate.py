# projects/013_dataset_audit_tool/scripts/013_dataset_audit_tool/step02_validate.py
from __future__ import annotations

import argparse
import csv
import glob
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict
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
    from python_toolkit.logger import get_json_logger, CTX, CtxAdapter  # type: ignore
except Exception:
    import logging
    CTX = None  # type: ignore

    class CtxAdapter(logging.LoggerAdapter):  # type: ignore
        def process(self, msg, kwargs):
            return msg, kwargs

    def get_json_logger(name: str = "app", log_filename: str = "audit_validate.log", base_dir: str = "logs/013"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s | %(name)s | %(message)s"))
            logger.addHandler(h)
            logger.propagate = False
        return logger


THIS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = THIS_DIR.parents[2]
CFG_DEFAULT = PROJECT_DIR / "configs/013_audit.yaml"


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
    ap = argparse.ArgumentParser(description="Step 02: validate input CSV headers.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT),
                    help=f"Path to YAML config (default: {CFG_DEFAULT})")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"[step02] config not found: {cfg_path}")
        return 2
    cfg = load_cfg(cfg_path)

    if CTX is not None:
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
        results.append({
            "file": vr.file,
            "rows": vr.row_count,
            "missing": "|".join(vr.missing_required) if vr.missing_required else "",
        })
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
