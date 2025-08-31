"""
Author: Mahmoud Rahnama
GitHub: https://github.com/marala45
Filename: step01_scaffold.py
Date: 2025-08-25
Description:
    Project 013 – Step 01: Scaffold config + data folders for dataset audit tool.

What you learn:
    - Parse a YAML config
    - Use structured logging with run context (CTX)
    - Safely create folders (reports, results)
"""

from __future__ import annotations

from pathlib import Path
import sys
import yaml

# Prefer our shared logger utilities; fall back to a simple console logger if missing.
try:
    from python_toolkit.logger import get_json_logger, CTX, CtxAdapter  # type: ignore
    _HAS_TOOLKIT = True
except Exception:
    import logging

    _HAS_TOOLKIT = False
    CTX = None  # type: ignore

    def get_json_logger(name: str = "app", log_filename: str = "audit.log", base_dir: str = "logs/013"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s | %(name)s | %(message)s"))
            logger.addHandler(h)
            logger.propagate = False
        return logger

    class CtxAdapter(logging.LoggerAdapter):  # type: ignore
        def process(self, msg, kwargs):
            return msg, kwargs


def load_config(p: Path) -> dict:
    """Read and parse a YAML config file."""
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    cfg_path = Path("configs/013_audit.yaml")
    if not cfg_path.exists():
        print(f"[step01] config not found: {cfg_path}")
        return 2

    cfg = load_config(cfg_path)

    # Configure logging
    log_dir = cfg.get("log_dir", "logs/013")
    base_log = get_json_logger("audit.json", log_filename="audit.log", base_dir=log_dir)

    if _HAS_TOOLKIT and CTX is not None:
        CTX.set({"project": "013_dataset_audit_tool"})
        log = CtxAdapter(base_log, {})
    else:
        log = CtxAdapter(base_log, {})  # no CTX injection in fallback

    log.info("scaffold_start", extra={"cfg_loaded": True, "cfg_path": str(cfg_path)})

    # Basic config validation
    required_keys = ["input_glob", "report_dir", "results_dir"]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        log.error("missing_config_keys", extra={"missing": missing})
        return 1

    # Create output folders
    report_dir = Path(cfg["report_dir"])
    results_dir = Path(cfg["results_dir"])
    report_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    log.info(
        "scaffold_ok",
        extra={"report_dir": str(report_dir), "results_dir": str(results_dir), "log_dir": log_dir},
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
