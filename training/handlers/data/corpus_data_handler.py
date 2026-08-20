import json
from pathlib import Path

from training.config import TrainingConfig


class CorpusDataHandler:
    def __init__(self, config: TrainingConfig) -> None:
        self._config = config

    def load_records(self) -> list[dict[str, str]]:
        raw_records = self._load_raw_records()
        records = [self._format_record(record) for record in raw_records if "text" in record]
        if not records:
            raise RuntimeError("Continued pretraining requires at least 1 canon text record.")
        return records

    def _load_raw_records(self) -> list[dict[str, object]]:
        data_path = self._config.training_corpus_path
        if data_path.suffix.casefold() != ".jsonl":
            raise RuntimeError(
                "Continued pretraining requires one explicit JSONL corpus file."
            )
        return self._load_jsonl_records(data_path)

    def _load_jsonl_records(self, jsonl_path: Path) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for line_number, raw_line in enumerate(
            jsonl_path.read_text(encoding="utf-8-sig").splitlines(),
            start=1,
        ):
            line = raw_line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise RuntimeError(
                    f"Expected a JSON object on line {line_number} in {jsonl_path}."
                )
            records.append(record)
        return records

    def _format_record(self, record: dict[str, object]) -> dict[str, str]:
        text = str(record["text"]).strip()
        section = str(record.get("section", "training")).strip()
        if not text:
            raise RuntimeError("Continued pretraining text records must not be empty.")
        return {
            "section": section,
            "text": text,
        }
