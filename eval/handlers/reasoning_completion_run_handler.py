from eval.handlers.reasoning_completion_handler import ReasoningCompletionHandler
from eval.handlers.reasoning_report_handler import ReasoningReportHandler
from eval.models.reasoning_case import ReasoningCase


class ReasoningCompletionRunHandler:
    def __init__(
        self,
        completion_handler: ReasoningCompletionHandler,
        report_handler: ReasoningReportHandler,
    ) -> None:
        self._completion_handler = completion_handler
        self._report_handler = report_handler

    def run(self, cases: list[ReasoningCase]) -> None:
        for case_number, reasoning_case in enumerate(cases, start=1):
            print(
                f"[{case_number}/{len(cases)}] {reasoning_case.name}: "
                "generating completion...",
                flush=True,
            )
            completion = self._completion_handler.generate_completion(reasoning_case)
            self._report_handler.record_completion(reasoning_case, completion)
        print(
            f"Recorded {len(cases)} completions. Audit status: not audited.",
            flush=True,
        )
