from pathlib import Path

from knowledge_store import write_jsonl


ROOT = Path(__file__).resolve().parent
BATCH_PATH = ROOT / "data" / "memit_batch_500.jsonl"


def build_batch_records(n=500):
    rows = []
    for idx in range(n):
        subject = f"SyntheticEntity_{idx:04d}"
        old_target = f"OldValue_{idx:04d}"
        new_target = f"NewValue_{idx:04d}"
        rows.append(
            {
                "id": f"batch_{idx:04d}",
                "subject": subject,
                "relation": "synthetic_attribute",
                "relation_keywords": ["attribute", "value", "identifier"],
                "old_target": old_target,
                "new_target": new_target,
                "edit_prompts": [
                    f"What attribute value is assigned to {subject}?",
                    f"Give the identifier value of {subject}.",
                ],
                "paraphrase_prompts": [
                    f"Which value should be returned for {subject}?",
                    f"State the updated attribute of {subject}.",
                ],
                "locality_prompts": [
                    {
                        "prompt": "What city is the Colosseum located in?",
                        "subject": "Colosseum",
                        "relation_keywords": ["city", "located", "stands"],
                        "target": "Rome",
                    }
                ],
            }
        )
    return rows


if __name__ == "__main__":
    write_jsonl(BATCH_PATH, build_batch_records())
    print(f"wrote {BATCH_PATH}")
