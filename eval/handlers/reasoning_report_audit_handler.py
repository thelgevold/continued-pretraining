import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from eval.handlers.deterministic_reasoning_judge_handler import (
    DeterministicReasoningJudgeHandler,
)
from eval.handlers.reasoning_performance_case_handler import (
    ReasoningPerformanceCaseHandler,
)


class ReasoningReportAuditHandler:
    def __init__(self) -> None:
        self._judge = DeterministicReasoningJudgeHandler()

    def audit(
        self,
        report_path: Path,
        cases_path: Path | tuple[Path, ...],
    ) -> dict[str, object]:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        cases = self._cases_by_name(cases_path)
        results = [self._audit_result(result, cases) for result in report["results"]]
        report["audit_status"] = "audited"
        report["audited_at_utc"] = self._timestamp()
        report["meta"] = self._meta(results)
        report["results"] = results
        return report

    @staticmethod
    def write_json(report: dict[str, object], report_path: Path) -> None:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def write_markdown(self, report: dict[str, object], report_path: Path) -> None:
        lines = [
            "# Reasoning Evaluation Report",
            "",
            (
                "Overall correctness: "
                f"{float(report['meta']['correctness_percentage']):.1f}%"
            ),
            "",
        ]
        for result in report["results"]:
            lines.extend(
                [
                    f"## {result['name']}",
                    "",
                    f"- Status: {result['status']}",
                    f"- Correctness: {float(result['score']):.1f}%",
                    f"- Audit reason: {result['audit_reason']}",
                    "",
                ]
            )
        report_path.write_text("\n".join(lines), encoding="utf-8")

    def _cases_by_name(
        self,
        cases_path: Path | tuple[Path, ...],
    ) -> dict[str, object]:
        cases = ReasoningPerformanceCaseHandler(cases_path).load_report_cases(None)
        return {case.name: case for case in cases}

    def _audit_result(
        self,
        result: dict[str, object],
        cases: dict[str, object],
    ) -> dict[str, object]:
        judgment = self._judge.evaluate_answer(
            self._answer_to_judge(result["actual_answer"]),
            cases[str(result["name"])],
        )
        is_correct = bool(judgment["is_correct"])
        return {
            **result,
            "status": "passed" if is_correct else "failed",
            "is_correct": is_correct,
            "score": judgment["score"],
            "match_type": judgment["match_type"],
            "audit_reason": judgment["reason"],
            "missing_facts": judgment["missing_facts"],
            "incorrect_facts": judgment["incorrect_facts"],
        }

    @staticmethod
    def _answer_to_judge(answer: object) -> object:
        if isinstance(answer, dict) and set(answer) == {"answer"}:
            return answer["answer"]
        return answer

    def _meta(self, results: list[dict[str, object]]) -> dict[str, object]:
        sections = tuple(dict.fromkeys(str(result["section"]) for result in results))
        return {
            **self._summary(results),
            "overall_generation_runtime_seconds": sum(
                float(result.get("runtime_seconds", 0.0)) for result in results
            ),
            "categories": {
                section: self._summary(
                    [result for result in results if result["section"] == section]
                )
                for section in sections
            },
        }

    @staticmethod
    def _summary(results: list[dict[str, object]]) -> dict[str, object]:
        statuses = Counter(str(result["status"]) for result in results)
        total = len(results)
        passed = statuses["passed"]
        return {
            "total_cases": total,
            "passed": passed,
            "failed": statuses["failed"],
            "pass_percentage": round(passed * 100 / total, 1) if total else 0.0,
            "correctness_percentage": (
                round(
                    sum(float(result.get("score", 0.0)) for result in results)
                    / total,
                    1,
                )
                if total
                else 0.0
            ),
        }

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
