import csv
import json
import time
import tracemalloc
from pathlib import Path

from knowledge_store import ensure_dir, normalize, read_jsonl, score_contains, write_json


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "memit_batch_500.jsonl"
RESULTS = ROOT / "results"


class SimpleRAGIndex:
    def __init__(self, records):
        self.records = records
        self.entries = [
            {
                "subject": row["subject"],
                "subject_norm": normalize(row["subject"]),
                "keywords": [normalize(item) for item in row["relation_keywords"]],
                "target": row["new_target"],
            }
            for row in records
        ]

    def retrieve(self, prompt):
        prompt_norm = normalize(prompt)
        best = None
        best_score = -1
        for entry in self.entries:
            subject_hit = entry["subject_norm"] in prompt_norm
            keyword_hits = sum(1 for keyword in entry["keywords"] if keyword in prompt_norm)
            score = (5 if subject_hit else 0) + keyword_hits
            if score > best_score:
                best = entry
                best_score = score
        if best and best_score >= 5:
            return best["target"]
        return "UNKNOWN"


def run():
    ensure_dir(RESULTS)
    records = read_jsonl(DATA_PATH)
    tracemalloc.start()
    build_start = time.perf_counter()
    index = SimpleRAGIndex(records)
    build_elapsed = time.perf_counter() - build_start

    query_start = time.perf_counter()
    edit_scores = []
    paraphrase_scores = []
    for row in records:
        edit_scores.extend(score_contains(index.retrieve(prompt), row["new_target"]) for prompt in row["edit_prompts"])
        paraphrase_scores.extend(
            score_contains(index.retrieve(prompt), row["new_target"]) for prompt in row["paraphrase_prompts"]
        )
    query_elapsed = time.perf_counter() - query_start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    result = {
        "method": "SimpleRAG",
        "num_records": len(records),
        "index_build_seconds": build_elapsed,
        "query_seconds": query_elapsed,
        "avg_query_ms": query_elapsed * 1000 / max(len(edit_scores) + len(paraphrase_scores), 1),
        "ES": sum(edit_scores) / len(edit_scores),
        "PS": sum(paraphrase_scores) / len(paraphrase_scores),
        "peak_memory_mb": peak / (1024 * 1024),
    }
    write_json(RESULTS / "rag_compare.json", result)
    with open(RESULTS / "rag_compare.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result.keys()))
        writer.writeheader()
        writer.writerow(result)
    print("Bonus RAG comparison")
    print(f"records: {result['num_records']}")
    print(f"index_build_seconds: {result['index_build_seconds']:.6f}")
    print(f"avg_query_ms: {result['avg_query_ms']:.6f}")
    print(f"ES: {result['ES']:.3f}")
    print(f"PS: {result['PS']:.3f}")
    print(f"peak_memory_mb: {result['peak_memory_mb']:.3f}")
    print(f"saved: {RESULTS / 'rag_compare.csv'}")


if __name__ == "__main__":
    run()
