import time

import httpx

from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_generated_completion import ReasoningGeneratedCompletion


class ReasoningCompletionHandler:
    HTTP_MAX_ATTEMPTS = 3
    EMPTY_ANSWER_MAX_ATTEMPTS = 2
    RETRY_DELAY_SECONDS = 1

    def __init__(self, api_base_url: str) -> None:
        self._api_base_url = api_base_url

    def generate_completion(
        self,
        reasoning_case: ReasoningCase,
    ) -> ReasoningGeneratedCompletion:
        started_at = time.perf_counter()
        completion = None
        for _ in range(self.EMPTY_ANSWER_MAX_ATTEMPTS):
            completion = self._request_with_http_retries(reasoning_case)
            if completion.answer.strip():
                return self._with_runtime(completion, started_at)
        if completion is None:
            raise RuntimeError("Empty-answer retry loop ended unexpectedly.")
        return self._with_runtime(completion, started_at)

    def _request_with_http_retries(
        self,
        reasoning_case: ReasoningCase,
    ) -> ReasoningGeneratedCompletion:
        for attempt in range(1, self.HTTP_MAX_ATTEMPTS + 1):
            try:
                return self._request_completion(reasoning_case)
            except httpx.HTTPError:
                if attempt == self.HTTP_MAX_ATTEMPTS:
                    raise
                time.sleep(self.RETRY_DELAY_SECONDS)
        raise RuntimeError("HTTP retry loop ended unexpectedly.")

    def _request_completion(
        self,
        reasoning_case: ReasoningCase,
    ) -> ReasoningGeneratedCompletion:
        response = httpx.post(
            f"{self._api_base_url}/question",
            json={"question": reasoning_case.question},
            timeout=300.0,
        )
        response.raise_for_status()
        payload = response.json()
        return ReasoningGeneratedCompletion(
            answer=str(payload["answer"]),
            reasoning_summary=str(payload["reasoning_summary"]),
            input_prompt_characters=int(payload.get("input_prompt_characters", 0)),
        )

    @staticmethod
    def _with_runtime(
        completion: ReasoningGeneratedCompletion,
        started_at: float,
    ) -> ReasoningGeneratedCompletion:
        return ReasoningGeneratedCompletion(
            answer=completion.answer,
            reasoning_summary=completion.reasoning_summary,
            runtime_seconds=time.perf_counter() - started_at,
            input_prompt_characters=completion.input_prompt_characters,
        )
