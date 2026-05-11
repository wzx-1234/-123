import subprocess
import sys
import json
import platform
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
LOG_DIR = RESULTS / "run_logs"


def run(script):
    print(f"\n===== {script} =====", flush=True)
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(ROOT / script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    elapsed = time.perf_counter() - start
    log_text = "\n".join(
        [
            f"command: {Path(sys.executable).name} {script}",
            f"cwd: {ROOT}",
            f"return_code: {proc.returncode}",
            f"wall_time_seconds: {elapsed:.6f}",
            "",
            "[stdout]",
            proc.stdout.rstrip(),
            "",
            "[stderr]",
            proc.stderr.rstrip(),
            "",
        ]
    )
    (LOG_DIR / f"{Path(script).stem}.txt").write_text(log_text, encoding="utf-8")
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return {"script": script, "return_code": proc.returncode, "wall_time_seconds": elapsed}


if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    for old_log in LOG_DIR.glob("*.txt"):
        old_log.unlink()
    environment = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "working_directory": str(ROOT),
        "timestamp_local": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (RESULTS / "environment_info.json").write_text(
        json.dumps(environment, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    run_rows = []
    for script in ["baseline.py", "edit_rome.py", "edit_memit.py", "evaluate.py", "rag_compare.py"]:
        run_rows.append(run(script))
    (RESULTS / "run_summary.json").write_text(
        json.dumps(run_rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    subprocess.run([sys.executable, str(ROOT / "generate_assets.py")], cwd=ROOT, check=True)
    print("\nAll tasks finished.")
