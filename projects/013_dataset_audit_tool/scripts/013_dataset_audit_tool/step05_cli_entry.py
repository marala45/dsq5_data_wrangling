"""
Author: Mahmoud Rahnama
GitHub: https://github.com/marala45
Filename: step05_cli_entry.py
Date: 2025-08-25
Description:
    Project 013 – Step 05: One-shot runner that executes the audit pipeline
    in order: scaffold -> validate -> profile -> report.

What you learn:
    - Orchestrating multiple steps from a single entry point
    - Using sys.executable for venv consistency
    - Propagating return codes safely
"""

from __future__ import annotations

import subprocess
import sys
from typing import List


def run(cmd: List[str]) -> int:
    """Run a subprocess command and return its exit code."""
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
    # 1) Ensure scaffold (creates folders and sanity logs)
    rc = run([sys.executable, "scripts/013_dataset_audit_tool/step01_scaffold.py"])
    if rc != 0:
        print("Step01 failed. Stopping.")
        return rc

    # 2) Validate (return code 2 means some files failed validation; we still continue)
    rc = run([sys.executable, "scripts/013_dataset_audit_tool/step02_validate.py"])
    if rc not in (0, 2):
        print("Step02 failed with an unexpected error. Stopping.")
        return rc
    if rc == 2:
        print("Step02 finished with validation failures. Continuing to profile and report...")

    # 3) Profile numeric columns
    rc = run([sys.executable, "scripts/013_dataset_audit_tool/step03_profile.py"])
    if rc != 0:
        print("Step03 failed. Stopping.")
        return rc

    # 4) Build Markdown report
    rc = run([sys.executable, "scripts/013_dataset_audit_tool/step04_report.py"])
    if rc != 0:
        print("Step04 failed. Stopping.")
        return rc

    print("All steps completed. See reports/013/audit_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
