import csv
import json
import subprocess
import sys
from pathlib import Path

from generate_assets import generate_assets
from knowledge_store import ensure_dir, write_json


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def run_missing_scripts():
    for script, result in [
        ("baseline.py", "baseline_results.json"),
        ("edit_rome.py", "rome_results.json"),
        ("edit_memit.py", "memit_results.json"),
    ]:
        if not (RESULTS / result).exists():
            subprocess.run([sys.executable, str(ROOT / script)], check=True, cwd=ROOT)


def load(name):
    with open(RESULTS / name, "r", encoding="utf-8") as f:
        return json.load(f)


def run():
    ensure_dir(RESULTS)
    run_missing_scripts()
    baseline = load("baseline_results.json")
    rome = load("rome_results.json")
    memit = load("memit_results.json")
    rows = [
        {
            "task": "Task 1 Baseline",
            "num_edits": baseline["num_facts"],
            "ES": "",
            "PS": "",
            "NS": "",
            "old_knowledge_hit": baseline["old_knowledge_hit"],
            "pre_edit_new_target_hit": baseline["pre_edit_new_target_hit"],
            "elapsed_seconds": baseline.get("elapsed_seconds", ""),
            "peak_memory_mb": baseline.get("peak_memory_mb", ""),
        },
        {
            "task": "Task 2 ROME",
            "num_edits": rome["num_edits"],
            "ES": rome["ES"],
            "PS": rome["PS"],
            "NS": rome["NS"],
            "old_knowledge_hit": "",
            "pre_edit_new_target_hit": "",
            "elapsed_seconds": rome.get("elapsed_seconds", ""),
            "peak_memory_mb": rome.get("peak_memory_mb", ""),
        },
        {
            "task": "Task 3 MEMIT",
            "num_edits": memit["num_edits"],
            "ES": memit["ES"],
            "PS": memit["PS"],
            "NS": memit["NS"],
            "old_knowledge_hit": "",
            "pre_edit_new_target_hit": "",
            "elapsed_seconds": memit["elapsed_seconds"],
            "peak_memory_mb": memit["peak_memory_mb"],
        },
    ]
    write_json(RESULTS / "summary.json", {"rows": rows})
    with open(RESULTS / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    case_rows = []
    failure_rows = []
    for item in rome["records"]:
        row = {
            "id": item["id"],
            "subject": item["subject"],
            "ES": item["ES"],
            "PS": item["PS"],
            "NS": item["NS"],
            "edit_success": sum(item["edit_success"]),
            "edit_total": len(item["edit_success"]),
            "paraphrase_success": sum(item["paraphrase_success"]),
            "paraphrase_total": len(item["paraphrase_success"]),
            "locality_success": sum(item["locality_success"]),
            "locality_total": len(item["locality_success"]),
        }
        case_rows.append(row)
        if item["ES"] < 1 or item["PS"] < 1 or item["NS"] < 1:
            failure_rows.append(row)
    with open(RESULTS / "rome_case_metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(case_rows[0].keys()))
        writer.writeheader()
        writer.writerows(case_rows)
    with open(RESULTS / "failure_cases.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(case_rows[0].keys()))
        writer.writeheader()
        writer.writerows(failure_rows)
    generate_assets()
    print("Task 4 Evaluation")
    for row in rows:
        print(row)
    print(f"saved: {RESULTS / 'summary.csv'}")
    print(f"case_metrics: {RESULTS / 'rome_case_metrics.csv'}")
    print(f"failure_cases: {RESULTS / 'failure_cases.csv'}")
    print(f"figures: {RESULTS / 'figures'}")


if __name__ == "__main__":
    run()
