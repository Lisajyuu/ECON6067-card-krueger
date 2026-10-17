"""
Reproducible workflow: run the full replication-and-extension pipeline.

Run from the project root:

    python src/run_all.py

This runs src/01_inspect_data.py through src/07_extension_price_did.py in
order, using the current Python interpreter (the same one running this file).
Each step is announced before it runs. If any step fails, the workflow stops
immediately and reports the failing script and its exit code (the step's own
error output is shown on screen). On success it lists the key generated files.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCRIPTS = [
    "src/01_inspect_data.py",
    "src/02_prepare_analysis.py",
    "src/03_reproduce_table2.py",
    "src/04_reproduce_table3.py",
    "src/05_reproduce_table4.py",
    "src/06_reproduce_figure1.py",
    "src/07_extension_price_did.py",
]

OUTPUTS = [
    "output/analysis_data.csv",
    "output/tables/table2_replication.csv",
    "output/tables/table2_replication.xlsx",
    "output/tables/table3_replication.csv",
    "output/tables/table3_replication.xlsx",
    "output/tables/table4_replication.csv",
    "output/tables/table4_replication.xlsx",
    "output/tables/figure1_wage_distribution.csv",
    "output/tables/figure1_wage_distribution.xlsx",
    "output/figures/figure1_replication.png",
    "output/tables/extension_price_did.csv",
    "output/tables/extension_price_did.xlsx",
    "output/figures/extension_price_did.png",
    "report/report.md",
    "report/report.html",
]


def main():
    print("=" * 62)
    print("Card & Krueger (1994) replication and extension workflow")
    print(f"Python interpreter: {sys.executable}")
    print("=" * 62)

    total = len(SCRIPTS)
    for i, script in enumerate(SCRIPTS, start=1):
        print(f"\n[{i}/{total}] Running {script} ...", flush=True)
        result = subprocess.run([sys.executable, str(ROOT / script)], cwd=str(ROOT))
        if result.returncode != 0:
            print(f"\nFAILED: {script} exited with code {result.returncode}.", flush=True)
            print("Stopping the workflow.", flush=True)
            sys.exit(result.returncode)
        print(f"[{i}/{total}] {script} completed successfully.", flush=True)

    print("\n" + "=" * 62)
    print("Workflow completed successfully. Key outputs:")
    for path in OUTPUTS:
        full = ROOT / path
        status = "OK    " if full.exists() else "MISSING"
        print(f"  [{status}] {path}")
    print("=" * 62)


if __name__ == "__main__":
    main()
