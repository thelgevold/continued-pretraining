from pathlib import Path

from eval.handlers.generated_heldout_route_case_builder import (
    GeneratedHeldoutRouteCaseBuilder,
)


project_root = Path(__file__).resolve().parents[1]
GeneratedHeldoutRouteCaseBuilder().build(
    baseline_path=project_root / "eval/cases/transfer_heldout_json_cases.jsonl",
    cpt_corpus_path=project_root / "city_training/data/city_lines.jsonl",
    sft_corpus_path=project_root / "schema_training/data/schema_sft_alpaca.jsonl",
    output_path=project_root / "eval/cases/generated_transfer_heldout_cases.jsonl",
)
