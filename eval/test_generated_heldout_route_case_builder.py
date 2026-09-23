import json
from pathlib import Path

from eval.handlers.generated_heldout_route_case_builder import (
    GeneratedHeldoutRouteCaseBuilder,
)


def test_generated_suite_contains_500_unique_connected_cases(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = tmp_path / "generated_cases.jsonl"

    GeneratedHeldoutRouteCaseBuilder().build(
        baseline_path=project_root / "eval/cases/transfer_heldout_json_cases.jsonl",
        cpt_corpus_path=project_root / "city_training/data/city_lines.jsonl",
        sft_corpus_path=project_root / "schema_training/data/schema_sft_alpaca.jsonl",
        output_path=output_path,
    )

    cases = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]

    assert len(cases) == 500
    assert len({case["name"] for case in cases}) == 500
    assert all(
        all(
            current["to_station"] == next_leg["from_station"]
            for current, next_leg in zip(
                case["expected_answer"]["answer"][:-1],
                case["expected_answer"]["answer"][1:],
            )
        )
        for case in cases
    )
