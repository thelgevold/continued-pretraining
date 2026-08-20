import os
from pathlib import Path


class EvaluationCasePathHandler:
    """Resolves the explicit evaluation-case file for one test run."""

    def resolve(self) -> Path:
        value = os.getenv("EVAL_CASES_PATH")
        if not value:
            raise RuntimeError("Missing required environment variable: EVAL_CASES_PATH")
        return Path(value)
