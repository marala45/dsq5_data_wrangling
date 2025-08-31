"""
Project 013 – Step 05: One-shot runner: scaffold -> validate -> profile -> report.
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
from typing import List
# Q5-ROOT must be the following Address: /Users/maramaca/dev/dslabs/dsq5_data_wrangling/configs/013_audit.yaml

Q5_ROOT = Path(__file__).resolve().parents[2]
CFG_DEFAULT = Q5_ROOT / "configs/013_audit.yaml"

STEPS = [
    "step01_scaffold.py",
    "step02_validate.py",
    "step03_profile.py",
    "step04_report.py",
]

def run(cmd: List[str]) -> int:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    try:
        cp = subprocess.run(cmd, check=False)
        return int(cp.returncode)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    except Exception as e:
        print(f"Error running command: {e}")
        return 1


def main() -> int:
    cfg = str(CFG_DEFAULT)  # absolute path
    py = sys.executable
    base = Q5_ROOT / "scripts/013_dataset_audit_tool"  # <-- corrected here

    # 1) scaffold
    rc = run([py, str(base / STEPS[0]), "--config", cfg])
    if rc != 0:
        print("Step01 failed. Stopping.")
        return rc

    # 2) validate (2 means some files failed – continue)
    rc = run([py, str(base / STEPS[1]), "--config", cfg])
    if rc not in (0, 2):
        print("Step02 failed with an unexpected error. Stopping.")
        return rc
    if rc == 2:
        print("Step02 finished with validation failures. Continuing...")

    # 3) profile
    rc = run([py, str(base / STEPS[2]), "--config", cfg])
    if rc != 0:
        print("Step03 failed. Stopping.")
        return rc

    # 4) report
    rc = run([py, str(base / STEPS[3]), "--config", cfg])
    if rc != 0:
        print("Step04 failed. Stopping.")
        return rc

    print("All steps completed. See reports/013/audit_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
