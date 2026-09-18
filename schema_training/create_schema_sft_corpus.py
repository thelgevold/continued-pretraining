from pathlib import Path

from schema_training.handlers.schema_sft_corpus_builder import SchemaSftCorpusBuilder


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    SchemaSftCorpusBuilder().build(
        held_out_path=project_root / "city_training/eval/transfer_heldout_json_cases.jsonl",
        output_path=project_root / "schema_training/data/schema_sft_alpaca.jsonl",
    )


if __name__ == "__main__":
    main()
