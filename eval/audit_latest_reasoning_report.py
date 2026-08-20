import sys
from pathlib import Path

from eval.handlers.evaluation_case_path_handler import EvaluationCasePathHandler
from eval.handlers.reasoning_report_audit_handler import (
    ReasoningReportAuditHandler,
)


class LatestReasoningReportAuditRunner:
    def run(self, source_path: Path | None = None) -> None:
        report_directory = Path("eval/reports")
        cases_path = EvaluationCasePathHandler().resolve()
        handler = ReasoningReportAuditHandler()
        source_path = source_path or report_directory / "reasoning_eval_report.json"
        report = handler.audit(source_path, cases_path)
        handler.write_json(report, source_path)
        handler.write_markdown(report, source_path.with_suffix(".md"))


def main() -> None:
    source_path = Path(sys.argv[1]) if len(sys.argv) == 2 else None
    LatestReasoningReportAuditRunner().run(source_path)


if __name__ == "__main__":
    main()
