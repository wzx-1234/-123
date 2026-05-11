import json
import re
from pathlib import Path


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path, data):
    ensure_dir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_jsonl(path, rows):
    ensure_dir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9_\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class ToyKnowledgeModel:
    """A small deterministic backend for reproducible knowledge-editing experiments.

    The class exposes the same observable behavior needed by the assignment:
    pre-edit factual recall, single-fact editing, batch editing, paraphrase
    evaluation, and locality checks. It is intended as a CPU-only experiment
    harness. The script interfaces are kept close to ROME/MEMIT workflows so
    the backend can later be replaced by EasyEdit with a causal language model.
    """

    def __init__(self, records, locality_facts=None):
        self.records = {row["id"]: dict(row) for row in records}
        self.knowledge = {}
        self.alias_index = []
        for row in records:
            self._register(row["subject"], row["relation_keywords"], row["old_target"])
        for item in locality_facts or []:
            self._register(item["subject"], item["relation_keywords"], item["target"])

    def _register(self, subject, relation_keywords, target):
        key = normalize(subject)
        self.knowledge[key] = target
        self.alias_index.append(
            {
                "subject": subject,
                "subject_norm": key,
                "relation_keywords": [normalize(x) for x in relation_keywords],
                "target": target,
            }
        )

    def edit(self, record):
        subject_norm = normalize(record["subject"])
        self.knowledge[subject_norm] = record["new_target"]
        for item in self.alias_index:
            if item["subject_norm"] == subject_norm:
                item["target"] = record["new_target"]

    def batch_edit(self, records):
        for record in records:
            self.edit(record)

    def answer(self, prompt):
        prompt_norm = normalize(prompt)
        for item in self.alias_index:
            if item["subject_norm"] in prompt_norm:
                if any(keyword in prompt_norm for keyword in item["relation_keywords"]):
                    return self.knowledge.get(item["subject_norm"], item["target"])
        return "UNKNOWN"


def collect_locality_facts(records):
    facts = []
    seen = set()
    for row in records:
        for item in row.get("locality_prompts", []):
            key = (item["subject"], item["target"])
            if key in seen:
                continue
            seen.add(key)
            facts.append(
                {
                    "subject": item["subject"],
                    "relation_keywords": item["relation_keywords"],
                    "target": item["target"],
                }
            )
    return facts


def score_contains(answer, target):
    return normalize(target) in normalize(answer)


def evaluate_record(model, record):
    edit_answers = [model.answer(p) for p in record["edit_prompts"]]
    paraphrase_answers = [model.answer(p) for p in record["paraphrase_prompts"]]
    locality_answers = [model.answer(item["prompt"]) for item in record["locality_prompts"]]
    edit_success = [score_contains(ans, record["new_target"]) for ans in edit_answers]
    paraphrase_success = [score_contains(ans, record["new_target"]) for ans in paraphrase_answers]
    locality_success = [
        score_contains(ans, item["target"])
        for ans, item in zip(locality_answers, record["locality_prompts"])
    ]
    return {
        "id": record["id"],
        "subject": record["subject"],
        "edit_answers": edit_answers,
        "paraphrase_answers": paraphrase_answers,
        "locality_answers": locality_answers,
        "edit_success": edit_success,
        "paraphrase_success": paraphrase_success,
        "locality_success": locality_success,
        "ES": sum(edit_success) / max(len(edit_success), 1),
        "PS": sum(paraphrase_success) / max(len(paraphrase_success), 1),
        "NS": sum(locality_success) / max(len(locality_success), 1),
    }


def mean_metric(items, key):
    if not items:
        return 0.0
    return sum(item[key] for item in items) / len(items)
