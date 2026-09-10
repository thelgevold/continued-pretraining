from unittest.mock import Mock, patch

import httpx

from eval.handlers.reasoning_completion_handler import ReasoningCompletionHandler
from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_expectation import ReasoningExpectation


def test_generate_completion_calls_question_api() -> None:
    response = Mock()
    response.json.return_value = {
        "answer": "Generated answer",
        "reasoning_summary": "Generated reasoning",
    }
    reasoning_case = ReasoningCase(
        name="case-name",
        section="test",
        question="Question text",
        expected_answer={"answer": "Expected answer"},
        required_phrases=("Expected",),
        expectation=ReasoningExpectation((), False, None, (), ()),
    )

    with patch(
        "eval.handlers.reasoning_completion_handler.httpx.post",
        return_value=response,
    ) as post:
        completion = ReasoningCompletionHandler(
            "http://evaluation-api"
        ).generate_completion(reasoning_case)

    assert completion.answer == "Generated answer"
    assert completion.reasoning_summary == "Generated reasoning"
    post.assert_called_once_with(
        "http://evaluation-api/question",
        json={"question": "Question text"},
        timeout=300.0,
    )
    response.raise_for_status.assert_called_once_with()


def test_generate_completion_enables_retrieval_only_when_the_case_requires_it() -> None:
    response = Mock()
    response.json.return_value = {"answer": "Generated answer", "reasoning_summary": "Reasoning"}
    reasoning_case = ReasoningCase(
        name="historic-site-case",
        section="city_historic_site_rag_routes",
        question="Question text",
        expected_answer={"answer": "Expected answer"},
        required_phrases=("Expected",),
        expectation=ReasoningExpectation((), False, None, (), ()),
        use_historic_site_retrieval=True,
    )

    with patch(
        "eval.handlers.reasoning_completion_handler.httpx.post",
        return_value=response,
    ) as post:
        ReasoningCompletionHandler("http://evaluation-api").generate_completion(
            reasoning_case
        )

    post.assert_called_once_with(
        "http://evaluation-api/historic-site-question",
        json={"question": "Question text"},
        timeout=300.0,
    )


def test_generate_completion_retries_a_transient_server_error() -> None:
    failed_response = Mock()
    failed_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "server error",
        request=Mock(),
        response=Mock(status_code=500),
    )
    successful_response = Mock()
    successful_response.json.return_value = {
        "answer": "Generated answer",
        "reasoning_summary": "Generated reasoning",
    }
    reasoning_case = ReasoningCase(
        name="case-name",
        section="test",
        question="Question text",
        expected_answer={"answer": "Expected answer"},
        required_phrases=("Expected",),
        expectation=ReasoningExpectation((), False, None, (), ()),
    )

    with (
        patch(
            "eval.handlers.reasoning_completion_handler.httpx.post",
            side_effect=(failed_response, successful_response),
        ) as post,
        patch("eval.handlers.reasoning_completion_handler.time.sleep"),
    ):
        completion = ReasoningCompletionHandler(
            "http://evaluation-api"
        ).generate_completion(reasoning_case)

    assert completion.answer == "Generated answer"
    assert completion.reasoning_summary == "Generated reasoning"
    assert post.call_count == 2


def test_generate_completion_retries_an_empty_answer_once() -> None:
    empty_response = Mock()
    empty_response.json.return_value = {
        "answer": "  ",
        "reasoning_summary": "Reasoning without a final answer",
    }
    successful_response = Mock()
    successful_response.json.return_value = {
        "answer": "Generated answer",
        "reasoning_summary": "Generated reasoning",
    }
    reasoning_case = ReasoningCase(
        name="case-name",
        section="test",
        question="Question text",
        expected_answer={"answer": "Expected answer"},
        required_phrases=("Expected",),
        expectation=ReasoningExpectation((), False, None, (), ()),
    )

    with patch(
        "eval.handlers.reasoning_completion_handler.httpx.post",
        side_effect=(empty_response, successful_response),
    ) as post:
        completion = ReasoningCompletionHandler(
            "http://evaluation-api"
        ).generate_completion(reasoning_case)

    assert completion.answer == "Generated answer"
    assert completion.reasoning_summary == "Generated reasoning"
    assert post.call_count == 2


def test_generate_completion_stops_after_one_empty_answer_retry() -> None:
    empty_responses = []
    for reasoning_summary in ("First reasoning", "Second reasoning"):
        response = Mock()
        response.json.return_value = {
            "answer": "",
            "reasoning_summary": reasoning_summary,
        }
        empty_responses.append(response)
    reasoning_case = ReasoningCase(
        name="case-name",
        section="test",
        question="Question text",
        expected_answer={"answer": "Expected answer"},
        required_phrases=("Expected",),
        expectation=ReasoningExpectation((), False, None, (), ()),
    )

    with patch(
        "eval.handlers.reasoning_completion_handler.httpx.post",
        side_effect=empty_responses,
    ) as post:
        completion = ReasoningCompletionHandler(
            "http://evaluation-api"
        ).generate_completion(reasoning_case)

    assert completion.answer == ""
    assert completion.reasoning_summary == "Second reasoning"
    assert post.call_count == 2
