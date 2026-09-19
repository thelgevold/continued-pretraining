import os
from pathlib import Path


class EvaluationCasePathHandler:
    """Resolves the explicit evaluation-case files for one test run."""

    def resolve(self) -> tuple[Path, ...]:
        value = os.getenv("EVAL_CASES_PATH")
        if not value:
            raise RuntimeError("Missing required environment variable: EVAL_CASES_PATH")
        return tuple(Path(path.strip()) for path in value.split(",") if path.strip())
