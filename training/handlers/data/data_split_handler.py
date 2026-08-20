import math

from sklearn.model_selection import train_test_split


class DataSplitHandler:
    def __init__(self, eval_percentage: float, random_state: int) -> None:
        self._eval_percentage = eval_percentage
        self._random_state = random_state

    def split_records(
        self,
        records: list[dict[str, str]],
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        if not records:
            raise RuntimeError("Pre-training requires at least 1 training record.")
        if self._eval_percentage <= 0:
            return records, []
        if len(records) < 2:
            raise RuntimeError(
                "Pre-training requires at least 2 training records to create train and eval splits."
            )
        eval_sections = self._extract_sections(records)
        train_records, eval_records = train_test_split(
            records,
            test_size=self._eval_percentage,
            random_state=self._random_state,
            shuffle=True,
            stratify=self._create_stratify_labels(
                records,
                eval_sections,
                self._eval_percentage,
            ),
        )
        return train_records, eval_records

    def _extract_sections(self, records: list[dict[str, str]]) -> list[str]:
        return [record["section"] for record in records]

    def _create_stratify_labels(
        self,
        records: list[dict[str, str]],
        sections: list[str],
        test_size: float | int,
    ) -> list[str] | None:
        if not self._can_stratify(records, sections, test_size):
            return None
        return sections

    def _can_stratify(
        self,
        records: list[dict[str, str]],
        sections: list[str],
        test_size: float | int,
    ) -> bool:
        class_count = len(set(sections))
        if class_count < 2:
            return False
        section_counts = {section: sections.count(section) for section in set(sections)}
        if min(section_counts.values()) < 2:
            return False
        split_count = self._resolve_split_count(len(records), test_size)
        return split_count >= class_count

    def _resolve_split_count(self, record_count: int, test_size: float | int) -> int:
        if isinstance(test_size, float):
            return max(1, math.ceil(record_count * test_size))
        return int(test_size)
