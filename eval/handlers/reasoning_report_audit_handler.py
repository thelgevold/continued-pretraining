import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from eval.handlers.deterministic_reasoning_judge_handler import (
    DeterministicReasoningJudgeHandler,
)
from eval.handlers.historic_route_failure_detail_handler import (
    HistoricRouteFailureDetailHandler,
)
from eval.handlers.reasoning_performance_case_handler import (
    ReasoningPerformanceCaseHandler,
)


class ReasoningReportAuditHandler:
    MANUAL_PASS_REASONS = {
        "general_destination_facts_01": "Correct. The founder statues and Historic Core are two documented Founder's Square attractions.",
        "general_destination_facts_04": "Correct. The founder statues and Historic Core are two documented Founder's Square attractions.",
        "general_destination_facts_06": "Correct. Artisan Quarter and Heritage Theater are two documented Museum District Station attractions.",
        "general_destination_facts_09": "Correct. Artisan Quarter and Heritage Theater are two documented Museum District Station attractions.",
        "general_destination_facts_11": "Correct. Riverwalk and Restored Industrial District are two documented Old Mill Station attractions.",
        "general_destination_facts_12": "Correct. Restored Industrial District and Bright Mill Museum are two documented Old Mill Station attractions.",
        "general_destination_facts_14": "Correct. City Hall and Historic Core are two documented Founder's Square attractions.",
        "general_destination_facts_15": "Correct. Artisan Quarter and Heritage Theater are two documented Museum District Station attractions, and the volunteered Green Line route is accurate.",
        "general_single_line_routes_10": "Correct. The trip remains on Green Line with zero transfers; the additional Central Station membership facts are true and do not change the active route line.",
        "general_history_and_monuments_08": "Correct. The response accurately paraphrases Mercer's street, bridge, and public-square work and names both memorials.",
        "general_two_historic_sites_06": "Correct. The response supplies both access stations, the Gold-to-Blue line change at Central Station, and states that the line changes once.",
        "general_subway_membership_01": "Correct. 'Service at North Terminal is provided exclusively by the Blue Line' states the complete membership unambiguously.",
        "general_subway_adjacency_02": "Correct. Founder's Square is the immediate next station in the requested direction; the question did not require the line name.",
        "general_subway_adjacency_07": "Correct. Museum District Station is immediately before Central Station in the requested direction; the question did not require the line name.",
        "general_negative_adversarial_02": "Correct. Stating that Museum District Station is served by Green Line directly corrects the claimed Gold Line membership; an explicit 'No' is unnecessary.",
        "general_landmark_station_disambiguation_01": "Correct. In context, 'the attraction' unambiguously refers to Heritage Theater, and Museum District Station is correctly identified as its access stop.",
    }
    MANUAL_FAILURE_REASONS = {
        "general_history_and_monuments_01": "Incorrect. The requested trading-post fact, year, and Founder's Square statue are present, but the answer invents an Eleanor Ashcroft Bridge.",
        "general_history_and_monuments_07": "Incorrect. The 1789 trading-post accomplishment is correct, but the answer invents an Ashcroft Bridge.",
        "general_history_and_monuments_09": "Incorrect. The mill and commemorations are correct, but the answer wrongly attributes Mercer's street, bridge, and civic-square work to Samuel Bright.",
    }
    CORRECT_REASONING_FINAL_DIVERGENCES = {
        "general_destination_facts_03": "The reasoning identifies the founder statues, City Hall, and Historic Core at Founder's Square, but the final answer abandons those destination facts for an Eleanor Ashcroft biography.",
        "general_destination_facts_08": "The reasoning identifies two valid Museum District attractions, but the final answer introduces Founder's Square as an unsupported extra destination.",
        "general_single_line_routes_14": "The reasoning correctly identifies Gold Line and zero transfers, but the final answer changes the active line to Green Line.",
        "general_history_and_monuments_01": "The reasoning contains the correct trading-post fact, year, and Founder's Square statue; the final answer adds the nonexistent Eleanor Ashcroft Bridge.",
        "general_history_and_monuments_06": "The reasoning correctly identifies Samuel Bright, his water-powered flour mill, and both memorials; the final answer adds Ashcroft's trading-post accomplishment to Bright.",
        "general_history_and_monuments_09": "The reasoning correctly connects Bright's mill to the museum and statue; the final answer adds Mercer's street, bridge, and public-square work to Bright.",
        "general_subway_membership_07": "The reasoning separately places Central Station on Blue, Green, and Gold Lines, but the final answer reports only Blue Line.",
    }
    PARTIAL_REASONING_FINAL_DIVERGENCES = {
        "general_destination_facts_13": "The reasoning contains two valid Old Mill attractions, Riverwalk and Restored Industrial District, but also misplaces Historic Core; the final answer drops Riverwalk and adds unrelated destinations.",
        "general_negative_adversarial_04": "The reasoning recognizes that Heritage Theater is not a station and identifies Museum District Station as the confused entity, but the final answer discards that correction and assigns the theater an ordinal position.",
    }
    THINKING_ERROR_CATEGORIES = {
        "task_focus_or_question_misread": {
            "general_destination_facts_05",
            "general_destination_facts_10",
        },
        "line_or_station_graph_binding": {
            "general_single_line_routes_01",
            "general_single_line_routes_15",
            "general_transfer_routes_02",
            "general_transfer_routes_03",
            "general_transfer_routes_05",
            "general_transfer_routes_07",
            "general_transfer_routes_09",
            "general_transfer_routes_10",
            "general_subway_ordinals_04",
            "general_subway_membership_04",
            "general_subway_membership_06",
            "general_subway_membership_10",
            "general_subway_membership_11",
            "general_subway_membership_14",
            "general_subway_adjacency_03",
            "general_subway_adjacency_06",
            "general_subway_adjacency_09",
            "general_subway_adjacency_10",
        },
        "historic_site_access_binding": {
            "general_two_historic_sites_01",
            "general_two_historic_sites_02",
            "general_two_historic_sites_03",
            "general_two_historic_sites_04",
            "general_two_historic_sites_05",
            "general_two_historic_sites_07",
            "general_two_historic_sites_08",
            "general_two_historic_sites_09",
            "general_two_historic_sites_10",
        },
        "false_premise_acceptance": {
            "general_negative_adversarial_01",
            "general_negative_adversarial_03",
            "general_negative_adversarial_05",
        },
        "route_sequence_error": {"general_transfer_routes_06"},
        "unsupported_historical_inference": {
            "general_history_and_monuments_07"
        },
    }

    def __init__(self) -> None:
        self._judge = DeterministicReasoningJudgeHandler()
        self._historic_route_failure_detail_handler = (
            HistoricRouteFailureDetailHandler()
        )

    def audit(self, report_path: Path, cases_path: Path) -> dict[str, object]:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        cases = {
            case.name: case
            for case in ReasoningPerformanceCaseHandler(cases_path).load_report_cases(
                None
            )
        }
        audited_results = [
            self._audit_result(result, cases[result["name"]])
            for result in report["results"]
        ]
        report["audit_status"] = "audited"
        report["audited_at_utc"] = self._timestamp()
        report["meta"] = self._meta(audited_results)
        report["results"] = audited_results
        return report

    def write_json(self, report: dict[str, object], report_path: Path) -> None:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def write_markdown(self, report: dict[str, object], report_path: Path) -> None:
        report_path.write_text(self._markdown(report), encoding="utf-8")

    def _audit_result(self, result: dict, reasoning_case: object) -> dict:
        judgment = self._judge.evaluate_answer(
            result["actual_answer"],
            reasoning_case,
        )
        failure_details = self._historic_failure_details(
            result,
            reasoning_case,
            bool(judgment["is_correct"]),
        )
        manual_pass_reason = None
        manual_failure_reason = None
        is_correct = (
            False
            if manual_failure_reason
            else bool(judgment["is_correct"] or manual_pass_reason)
        )
        reason = (
            manual_failure_reason
            or manual_pass_reason
            or self._judgment_reason(
                judgment,
                failure_details,
            )
        )
        return {
            **result,
            "status": "passed" if is_correct else "failed",
            "is_correct": is_correct,
            "audit_reason": reason,
            "missing_facts": [] if manual_pass_reason else judgment["missing_facts"],
            "incorrect_facts": [] if manual_pass_reason else judgment["incorrect_facts"],
            "failure_details": failure_details,
            **self._reasoning_audit(result["name"], is_correct),
            "thinking_error_category": self._thinking_error_category(
                result["name"], is_correct
            ),
        }

    def _reasoning_audit(self, name: str, is_correct: bool) -> dict[str, str]:
        if is_correct:
            return {
                "reasoning_final_alignment": "final_answer_passed",
                "reasoning_audit_reason": (
                    "The final answer passed; no reasoning-to-final loss affected "
                    "the evaluation result."
                ),
            }
        if name in self.CORRECT_REASONING_FINAL_DIVERGENCES:
            return {
                "reasoning_final_alignment": "correct_reasoning_not_reflected",
                "reasoning_audit_reason": (
                    self.CORRECT_REASONING_FINAL_DIVERGENCES[name]
                ),
            }
        if name in self.PARTIAL_REASONING_FINAL_DIVERGENCES:
            return {
                "reasoning_final_alignment": "partial_reasoning_not_reflected",
                "reasoning_audit_reason": (
                    self.PARTIAL_REASONING_FINAL_DIVERGENCES[name]
                ),
            }
        return {
            "reasoning_final_alignment": "reasoning_error_carried_to_final",
            "reasoning_audit_reason": (
                "The reasoning does not establish a correct answer that was then "
                "lost only during final-answer generation."
            ),
        }

    def _thinking_error_category(self, name: str, is_correct: bool) -> str:
        if is_correct:
            return "none_final_answer_passed"
        if name in self.CORRECT_REASONING_FINAL_DIVERGENCES:
            return "final_answer_divergence"
        if name in self.PARTIAL_REASONING_FINAL_DIVERGENCES:
            return "mixed_reasoning_final_divergence"
        for category, names in self.THINKING_ERROR_CATEGORIES.items():
            if name in names:
                return category
        return "unclassified_final_answer_error"

    def _historic_failure_details(
        self,
        result: dict,
        reasoning_case: object,
        is_correct: bool,
    ) -> list[str]:
        if is_correct or getattr(reasoning_case, "section", "") != "historic_site_routes":
            return []
        return self._historic_route_failure_detail_handler.create_details(
            result["expected_answer"],
            result["actual_answer"],
        )

    def _judgment_reason(
        self,
        judgment: dict[str, object],
        failure_details: list[str],
    ) -> str:
        if judgment["is_correct"]:
            return "All required facts are correct."
        if failure_details:
            return "Incorrect: " + " ".join(failure_details)
        details = [
            *(f"Missing: {fact}." for fact in judgment["missing_facts"]),
            *(f"Incorrect: {fact}." for fact in judgment["incorrect_facts"]),
        ]
        return " ".join(details)

    def _meta(self, results: list[dict]) -> dict[str, object]:
        sections = tuple(dict.fromkeys(result["section"] for result in results))
        return {
            **self._summary(results),
            "categories": {
                section: self._summary(
                    [result for result in results if result["section"] == section]
                )
                for section in sections
            },
        }

    def _summary(self, results: list[dict]) -> dict[str, object]:
        statuses = Counter(result["status"] for result in results)
        total = len(results)
        passed = statuses["passed"]
        return {
            "total_cases": total,
            "passed": passed,
            "failed": statuses["failed"],
            "pass_percentage": round(passed * 100 / total, 1),
            "reasoning_to_final_loss_count": sum(
                result.get("reasoning_final_alignment")
                in {
                    "correct_reasoning_not_reflected",
                    "partial_reasoning_not_reflected",
                }
                for result in results
            ),
            "thinking_error_categories": dict(
                Counter(
                    result["thinking_error_category"]
                    for result in results
                    if result["status"] == "failed"
                )
            ),
        }

    def _markdown(self, report: dict[str, object]) -> str:
        meta = report["meta"]
        lines = [
            "# Audited Reasoning Evaluation Report",
            "",
            f"Generated at (UTC): {report['generated_at_utc']}",
            f"Audited at (UTC): {report['audited_at_utc']}",
            f"Model: {report['model_name']}",
            "Audit status: audited",
            "",
            "## Summary",
            "",
            f"Passed: {meta['passed']}/{meta['total_cases']} ({meta['pass_percentage']}%)",
            f"Failed: {meta['failed']}/{meta['total_cases']}",
            (
                "Reasoning-to-final losses among failures: "
                f"{meta['reasoning_to_final_loss_count']}"
            ),
            "",
            "### Thinking-error categories",
            "",
            *(
                f"- {category}: {count}"
                for category, count in meta["thinking_error_categories"].items()
            ),
            "",
            "| Category | Passed | Failed | Total | Pass rate | Reasoning-to-final losses |",
            "|---|---:|---:|---:|---:|---:|",
            *self._category_rows(meta["categories"]),
            "",
        ]
        for result in report["results"]:
            lines.extend(self._result_lines(result))
        return "\n".join(lines)

    def _category_rows(self, categories: dict[str, dict]) -> list[str]:
        return [
            f"| {section} | {summary['passed']} | {summary['failed']} | "
            f"{summary['total_cases']} | {summary['pass_percentage']}% | "
            f"{summary['reasoning_to_final_loss_count']} |"
            for section, summary in categories.items()
        ]

    def _result_lines(self, result: dict) -> list[str]:
        return [
            f"## {result['name']}",
            "",
            f"- Status: **{result['status']}**",
            f"- Audit reason: {result['audit_reason']}",
            f"- Reasoning/final alignment: {result['reasoning_final_alignment']}",
            f"- Reasoning audit: {result['reasoning_audit_reason']}",
            f"- Thinking error category: {result['thinking_error_category']}",
            "",
            f"Question: {result['question']}",
            "",
            f"Expected: {result['expected_answer']}",
            "",
            f"Actual: {result['actual_answer']}",
            "",
            f"Reasoning summary: {result.get('reasoning_summary') or 'not recorded'}",
            "",
        ]

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
