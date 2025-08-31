# projects/013_dataset_audit_tool/scripts/013_dataset_audit_tool/step01_scaffold.py
from __future__ import annotations

import argparse
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

# Optional: use shared logger if available; otherwise fallback
try:
    from python_toolkit.logger import get_json_logger, CTX, CtxAdapter  # type: ignore
    _HAS_TOOLKIT = True
except Exception:
    _HAS_TOOLKIT = False
    CTX = None  # type: ignore
    import logging

    class CtxAdapter(logging.LoggerAdapter):  # type: ignore
        def process(self, msg, kwargs):
            return msg, kwargs

    def get_json_logger(name: str = "app", log_filename: str = "audit.log", base_dir: str = "logs/013"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s | %(name)s | %(message)s"))
            logger.addHandler(h)
            logger.propagate = False
        return logger


# ---------- paths & config ----------
THIS_DIR = Path(__file__).resolve().parent                # .../scripts/013_dataset_audit_tool
PROJECT_DIR = THIS_DIR.parents[2]                         # .../projects/013_dataset_audit_tool
CFG_DEFAULT = PROJECT_DIR / "configs/013_audit.yaml"      # default config

def load_yaml(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 01: scaffold folders for dataset audit tool.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT),
                    help=f"Path to YAML config (default: {CFG_DEFAULT})")
    return ap.parse_args()


# ---------- main ----------
def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config)

    if not cfg_path.exists():
        print(f"[step01] config not found: {cfg_path}")
        print("Hint: pass --config /full/path/to/013_audit.yaml or create the default file.")
        return 2

    cfg = load_yaml(cfg_path)

    log_dir = cfg.get("log_dir", "logs/013")
    base_log = get_json_logger("audit.scaffold", log_filename="audit.log", base_dir=log_dir)
    log = CtxAdapter(base_log, {})

    if _HAS_TOOLKIT and CTX is not None:
        CTX.set({"project": "013_dataset_audit_tool"})

    # Validate minimal keys (not strictly required here but helpful)
    report_dir = Path(cfg.get("report_dir", "reports/013"))
    results_dir = Path(cfg.get("results_dir", "results/013"))
    report_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    log.info("scaffold_ok", extra={
        "cfg": str(cfg_path),
        "report_dir": str(report_dir),
        "results_dir": str(results_dir),
        "log_dir": str(log_dir),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
