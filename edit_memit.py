import time
import tracemalloc
from pathlib import Path

from generate_data import BATCH_PATH, build_batch_records
from knowledge_store import (
    ToyKnowledgeModel,
    collect_locality_facts,
    evaluate_record,
    mean_metric,
    read_jsonl,
    write_json,
    write_jsonl,
)


ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "results" / "memit_results.json"


def load_or_create_batch():
    if not BATCH_PATH.exists():
        write_jsonl(BATCH_PATH, build_batch_records())
    return read_jsonl(BATCH_PATH)


def run():
    records = load_or_create_batch()
    locality_facts = collect_locality_facts(records)
    model = ToyKnowledgeModel(records, locality_facts)
    tracemalloc.start()
    start = time.perf_counter()
    model.batch_edit(records)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    evaluations = [evaluate_record(model, row) for row in records]
    summary = {
        "method": "MEMIT-style batch editing",
        "num_edits": len(records),
        "elapsed_seconds": elapsed,
        "peak_memory_mb": peak / (1024 * 1024),
        "ES": mean_metric(evaluations, "ES"),
        "PS": mean_metric(evaluations, "PS"),
        "NS": mean_metric(evaluations, "NS"),
        "records_sample": evaluations[:20],
    }
    write_json(RESULT_PATH, summary)
    print("Task 3 MEMIT-style batch editing")
    print(f"edits: {summary['num_edits']}")
    print(f"elapsed_seconds: {summary['elapsed_seconds']:.6f}")
    print(f"peak_memory_mb: {summary['peak_memory_mb']:.3f}")
    print(f"ES: {summary['ES']:.3f}")
    print(f"PS: {summary['PS']:.3f}")
    print(f"NS: {summary['NS']:.3f}")
    print(f"saved: {RESULT_PATH}")


if __name__ == "__main__":
    run()
