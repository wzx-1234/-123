"""Optional EasyEdit adapter sketch for real-model experiments.

The default coursework package uses a deterministic backend so it can run on
CPU-only machines. This file documents the replacement point for a formal
Qwen2.5-0.5B + EasyEdit experiment. It is intentionally optional because
EasyEdit, PyTorch, model weights, and GPU drivers are not part of the default
runtime in this workspace.
"""


def build_easyedit_requests(records):
    requests = []
    for row in records:
        requests.append(
            {
                "prompt": row["edit_prompts"][0],
                "subject": row["subject"],
                "target_new": row["new_target"],
                "ground_truth": row["old_target"],
                "rephrase_prompt": row["paraphrase_prompts"][0],
                "locality": {
                    "prompt": row["locality_prompts"][0]["prompt"],
                    "ground_truth": row["locality_prompts"][0]["target"],
                },
            }
        )
    return requests


def run_with_easyedit(records, method="ROME"):
    raise RuntimeError(
        "This optional path requires installing EasyEdit, PyTorch, and a local "
        "causal language model such as Qwen2.5-0.5B. Keep the JSONL data and "
        "evaluation scripts, replace the deterministic edit calls with "
        "easyeditor.BaseEditor.edit or BaseEditor.batch_edit, then rerun "
        "evaluate.py to refresh the report assets."
    )
