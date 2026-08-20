from eval.handlers.reasoning_completion_handler import ReasoningCompletionHandler
from eval.handlers.reasoning_completion_run_handler import (
    ReasoningCompletionRunHandler,
)
from eval.handlers.reasoning_performance_case_handler import (
    ReasoningPerformanceCaseHandler,
)
from eval.handlers.reasoning_report_handler import ReasoningReportHandler
from eval.models.reasoning_run_config import ReasoningRunConfig


def main() -> None:
    config = ReasoningRunConfig()
    cases = ReasoningPerformanceCaseHandler(
        config.cases_path
    ).load_report_cases(
        config.case_prefix,
        config.excluded_case_prefix,
    )
    report_handler = ReasoningReportHandler(
        report_directory=config.cases_path.parent.parent / "reports",
        expected_cases=cases,
        model_name=config.ollama_model_name,
        experiment_label=config.experiment_label,
    )
    ReasoningCompletionRunHandler(
        completion_handler=ReasoningCompletionHandler(config.api_base_url),
        report_handler=report_handler,
    ).run(cases)


if __name__ == "__main__":
    main()
