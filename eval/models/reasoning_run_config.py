import os

from eval.handlers.evaluation_case_path_handler import EvaluationCasePathHandler


class ReasoningRunConfig:
    def __init__(self) -> None:
        self.api_base_url = self._require("EVAL_API_BASE_URL")
        self.ollama_model_name = self._require("OLLAMA_MODEL_NAME")
        self.experiment_label = os.getenv("EVAL_EXPERIMENT_LABEL")
        self.case_prefix = os.getenv("EVAL_CASE_PREFIX")
        self.excluded_case_prefix = os.getenv("EVAL_EXCLUDE_CASE_PREFIX")
        self.cases_path = EvaluationCasePathHandler().resolve()

    def _require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value
