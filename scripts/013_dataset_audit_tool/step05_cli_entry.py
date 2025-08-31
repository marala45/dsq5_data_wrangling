# projects/013_dataset_audit_tool/scripts/013_dataset_audit_tool/step05_cli_entry.py
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

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


THIS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = THIS_DIR.parents[2]  # .../projects/013_dataset_audit_tool
CFG_DEFAULT = PROJECT_DIR / "configs/013_audit.yaml"

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Step 05: run scaffold -> validate -> profile -> report.")
    ap.add_argument("--config", type=str, default=str(CFG_DEFAULT),
                    help=f"Path to YAML config (default: {CFG_DEFAULT})")
    return ap.parse_args()


def run(cmd: List[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    try:
        completed = subprocess.run(cmd, check=False)
        return int(completed.returncode)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def main() -> int:
    args = parse_args()
    py = sys.executable

    s01 = THIS_DIR / "step01_scaffold.py"
    s02 = THIS_DIR / "step02_validate.py"
    s03 = THIS_DIR / "step03_profile.py"
    s04 = THIS_DIR / "step04_report.py"

    # 1) Scaffold
    rc = run([py, str(s01), "--config", args.config])
    if rc != 0:
        print("Step01 failed. Stopping.")
        return rc

    # 2) Validate (rc==2 means some files missing columns; keep going)
    rc = run([py, str(s02), "--config", args.config])
    if rc not in (0, 2):
        print("Step02 failed with an unexpected error. Stopping.")
        return rc
    if rc == 2:
        print("Step02 finished with validation failures. Continuing to profile and report...")

    # 3) Profile
    rc = run([py, str(s03), "--config", args.config])
    if rc != 0:
        print("Step03 failed. Stopping.")
        return rc

    # 4) Report
    rc = run([py, str(s04), "--config", args.config])
    if rc != 0:
        print("Step04 failed. Stopping.")
        return rc

    print("All steps completed. See reports/013/audit_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
