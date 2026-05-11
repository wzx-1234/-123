from pathlib import Path
import time
import tracemalloc

from knowledge_store import (
    ToyKnowledgeModel,
    collect_locality_facts,
    evaluate_record,
    mean_metric,
    read_jsonl,
    write_json,
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "fact_updates_10.jsonl"
RESULT_PATH = ROOT / "results" / "rome_results.json"


def run():
    tracemalloc.start()
    start = time.perf_counter()
    records = read_jsonl(DATA_PATH)
    locality_facts = collect_locality_facts(records)
    evaluations = []
    for row in records:
        model = ToyKnowledgeModel(records, locality_facts)
        model.edit(row)
        evaluations.append(evaluate_record(model, row))
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    summary = {
        "method": "ROME-style single fact editing with model reset",
        "num_edits": len(records),
        "elapsed_seconds": elapsed,
        "peak_memory_mb": peak / (1024 * 1024),
        "ES": mean_metric(evaluations, "ES"),
        "PS": mean_metric(evaluations, "PS"),
        "NS": mean_metric(evaluations, "NS"),
        "records": evaluations,
    }
    write_json(RESULT_PATH, summary)
    print("Task 2 ROME-style editing")
    print(f"edits: {summary['num_edits']}")
    print(f"ES: {summary['ES']:.3f}")
    print(f"PS: {summary['PS']:.3f}")
    print(f"NS: {summary['NS']:.3f}")
    print(f"elapsed_seconds: {summary['elapsed_seconds']:.6f}")
    print(f"peak_memory_mb: {summary['peak_memory_mb']:.3f}")
    print(f"saved: {RESULT_PATH}")


if __name__ == "__main__":
    run()
