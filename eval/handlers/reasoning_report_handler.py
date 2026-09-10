import json
import re
from datetime import datetime, timezone
from pathlib import Path

from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_completion_result import ReasoningCompletionResult
from eval.models.reasoning_generated_completion import ReasoningGeneratedCompletion


class ReasoningReportHandler:
    def __init__(
        self,
        report_directory: Path,
        expected_cases: list[ReasoningCase],
        model_name: str,
        experiment_label: str | None = None,
    ) -> None:
        self._report_directory = report_directory
        self._expected_cases = expected_cases
        self._model_name = model_name
        self._experiment_label = experiment_label
        self._results_by_name: dict[str, ReasoningCompletionResult] = {}
        self._write_reports()

    def record_completion(
        self,
        reasoning_case: ReasoningCase,
        completion: ReasoningGeneratedCompletion,
    ) -> None:
        self._results_by_name[reasoning_case.name] = ReasoningCompletionResult(
            name=reasoning_case.name,
            question=reasoning_case.question,
            expected_answer=reasoning_case.expected_answer,
            actual_answer=completion.answer,
            reasoning_summary=completion.reasoning_summary,
            runtime_seconds=completion.runtime_seconds,
            input_prompt_characters=completion.input_prompt_characters,
        )
        self._write_reports()

    def _write_reports(self) -> None:
        self._report_directory.mkdir(parents=True, exist_ok=True)
        generated_at_utc = self._get_generated_at_utc()
        case_payloads = [
            self._create_case_payload(reasoning_case)
            for reasoning_case in self._expected_cases
        ]
        self._write_json_report(case_payloads, generated_at_utc)
        self._write_markdown_report(case_payloads, generated_at_utc)

    def _write_json_report(
        self,
        case_payloads: list[dict[str, object]],
        generated_at_utc: str,
    ) -> None:
        payload = {
            "generated_at_utc": generated_at_utc,
            "model_name": self._model_name,
            "audit_status": "not_audited",
            "meta": self._create_meta(case_payloads),
            "results": case_payloads,
        }
        self._write_report_file(
            "reasoning_eval_report",
            "json",
            json.dumps(payload, indent=2),
        )

    def _write_markdown_report(
        self,
        case_payloads: list[dict[str, object]],
        generated_at_utc: str,
    ) -> None:
        self._write_report_file(
            "reasoning_eval_report",
            "md",
            self._create_markdown_report(case_payloads, generated_at_utc),
        )

    def _create_markdown_report(
        self,
        case_payloads: list[dict[str, object]],
        generated_at_utc: str,
    ) -> str:
        meta = self._create_meta(case_payloads)
        lines = [
            "# Reasoning Completion Report",
            "",
            f"Generated at (UTC): {generated_at_utc}",
            f"Model: {self._model_name}",
            "Audit status: not audited",
            "",
            "## Meta",
            "",
            f"Total cases: {meta['total_cases']}",
            f"Completions recorded: {meta['completions_recorded']}",
            f"Awaiting audit: {meta['awaiting_audit']}",
            f"Missing completions: {meta['missing_completions']}",
            (
                "Overall generation runtime (seconds): "
                f"{meta['overall_generation_runtime_seconds']:.3f}"
            ),
            "",
            "| Category | Recorded | Awaiting audit | Missing | Total |",
            "|---|---:|---:|---:|---:|",
            *self._category_table_rows(meta),
            "",
            "## Runtime and Prompt Size by Test",
            "",
            "| Test | Runtime (seconds) | Input prompt characters |",
            "|---|---:|---:|",
            *self._timing_table_rows(case_payloads),
            "",
        ]
        for payload in case_payloads:
            lines.extend(
                [
                    f"## {payload['name']}",
                    "",
                    f"- Status: {payload['status']}",
                    (
                        "- Runtime (seconds): "
                        f"{float(payload['runtime_seconds']):.3f}"
                    ),
                    (
                        "- Input prompt characters: "
                        f"{payload['input_prompt_characters']}"
                    ),
                    "",
                    f"Question: {payload['question']}",
                    "",
                    f"Expected: {json.dumps(payload['expected_answer'], ensure_ascii=False)}",
                    "",
                    f"Actual: {self._format_actual_answer(payload['actual_answer'])}",
                    "",
                    (
                        "Reasoning summary: "
                        f"{payload['reasoning_summary'] or 'not recorded'}"
                    ),
                    "",
                ]
            )
        return "\n".join(lines)

    def _create_meta(
        self,
        case_payloads: list[dict[str, object]],
    ) -> dict[str, object]:
        category_payloads: dict[str, list[dict[str, object]]] = {}
        for payload in case_payloads:
            section = str(payload["section"])
            category_payloads.setdefault(section, []).append(payload)
        return {
            **self._completion_summary(case_payloads),
            "overall_generation_runtime_seconds": sum(
                float(payload["runtime_seconds"]) for payload in case_payloads
            ),
            "categories": {
                section: self._completion_summary(payloads)
                for section, payloads in category_payloads.items()
            },
        }

    def _completion_summary(
        self,
        payloads: list[dict[str, object]],
    ) -> dict[str, int]:
        recorded = sum(
            1 for payload in payloads if payload["status"] == "awaiting_audit"
        )
        return {
            "total_cases": len(payloads),
            "completions_recorded": recorded,
            "awaiting_audit": recorded,
            "missing_completions": len(payloads) - recorded,
        }

    def _category_table_rows(self, meta: dict[str, object]) -> list[str]:
        return [
            (
                f"| {section} | {summary['completions_recorded']} | "
                f"{summary['awaiting_audit']} | {summary['missing_completions']} | "
                f"{summary['total_cases']} |"
            )
            for section, summary in meta["categories"].items()
        ]

    def _timing_table_rows(
        self,
        case_payloads: list[dict[str, object]],
    ) -> list[str]:
        return [
            (
                f"| {payload['name']} | "
                f"{float(payload['runtime_seconds']):.3f} | "
                f"{payload['input_prompt_characters']} |"
            )
            for payload in case_payloads
        ]

    def _create_case_payload(self, reasoning_case: ReasoningCase) -> dict[str, object]:
        result = self._results_by_name.get(reasoning_case.name)
        return {
            "name": reasoning_case.name,
            "section": reasoning_case.section,
            "question": reasoning_case.question,
            "expected_answer": reasoning_case.expected_answer,
            "actual_answer": result.actual_answer if result else {},
            "reasoning_summary": result.reasoning_summary if result else "",
            "runtime_seconds": result.runtime_seconds if result else 0.0,
            "input_prompt_characters": (
                result.input_prompt_characters if result else 0
            ),
            "status": "awaiting_audit" if result else "pending_generation",
        }

    def _format_actual_answer(self, answer: object) -> str:
        if not answer:
            return "not recorded"
        return json.dumps(answer, ensure_ascii=False)

    def _write_report_file(self, stem: str, extension: str, content: str) -> None:
        latest_report_path = self._report_directory / f"{stem}.{extension}"
        latest_report_path.write_text(content, encoding="utf-8")
        suffixed_report_path = (
            self._report_directory
            / f"{stem}_{self._get_model_name_file_suffix()}.{extension}"
        )
        suffixed_report_path.write_text(content, encoding="utf-8")
        if self._experiment_label:
            experiment_report_path = (
                self._report_directory
                / (
                    f"{stem}-{self._get_experiment_label_file_suffix()}_"
                    f"{self._get_model_name_file_suffix()}.{extension}"
                )
            )
            experiment_report_path.write_text(content, encoding="utf-8")

    def _get_generated_at_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _get_model_name_file_suffix(self) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "-", self._model_name).strip("-")

    def _get_experiment_label_file_suffix(self) -> str:
        return re.sub(
            r"[^A-Za-z0-9._-]+",
            "-",
            self._experiment_label or "",
        ).strip("-")
