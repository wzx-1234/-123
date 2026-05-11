from pathlib import Path
import time
import tracemalloc

from knowledge_store import (
    ToyKnowledgeModel,
    collect_locality_facts,
    ensure_dir,
    read_jsonl,
    score_contains,
    write_json,
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "fact_updates_10.jsonl"
RESULT_PATH = ROOT / "results" / "baseline_results.json"


def run():
    tracemalloc.start()
    start = time.perf_counter()
    records = read_jsonl(DATA_PATH)
    model = ToyKnowledgeModel(records, collect_locality_facts(records))
    rows = []
    for row in records:
        edit_answers = [model.answer(prompt) for prompt in row["edit_prompts"]]
        paraphrase_answers = [model.answer(prompt) for prompt in row["paraphrase_prompts"]]
        old_hits = [score_contains(ans, row["old_target"]) for ans in edit_answers]
        pre_edit_new_hits = [score_contains(ans, row["new_target"]) for ans in edit_answers]
        rows.append(
            {
                "id": row["id"],
                "subject": row["subject"],
                "old_target": row["old_target"],
                "new_target": row["new_target"],
                "edit_answers": edit_answers,
                "paraphrase_answers": paraphrase_answers,
                "old_knowledge_hit": sum(old_hits) / len(old_hits),
                "pre_edit_new_target_hit": sum(pre_edit_new_hits) / len(pre_edit_new_hits),
            }
        )
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    summary = {
        "num_facts": len(records),
        "old_knowledge_hit": sum(x["old_knowledge_hit"] for x in rows) / len(rows),
        "pre_edit_new_target_hit": sum(x["pre_edit_new_target_hit"] for x in rows) / len(rows),
        "elapsed_seconds": elapsed,
        "peak_memory_mb": peak / (1024 * 1024),
        "records": rows,
    }
    ensure_dir(ROOT / "results")
    write_json(RESULT_PATH, summary)
    print("Task 1 Baseline")
    print(f"facts: {summary['num_facts']}")
    print(f"old_knowledge_hit: {summary['old_knowledge_hit']:.3f}")
    print(f"pre_edit_new_target_hit: {summary['pre_edit_new_target_hit']:.3f}")
    print(f"elapsed_seconds: {summary['elapsed_seconds']:.6f}")
    print(f"peak_memory_mb: {summary['peak_memory_mb']:.3f}")
    print(f"saved: {RESULT_PATH}")


if __name__ == "__main__":
    run()
