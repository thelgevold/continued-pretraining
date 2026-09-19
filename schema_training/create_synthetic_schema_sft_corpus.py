from pathlib import Path

from schema_training.handlers.synthetic_schema_sft_corpus_builder import (
    SyntheticSchemaSftCorpusBuilder,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    SyntheticSchemaSftCorpusBuilder().build(
        city_corpus_path=project_root / "city_training/data/city_lines.jsonl",
        output_path=(
            project_root / "schema_training/data/synthetic_schema_sft_alpaca.jsonl"
        ),
    )


if __name__ == "__main__":
    main()
