import asyncio
from unittest.mock import AsyncMock, Mock

from app.handlers.historic_site_tool_calling_handler import HistoricSiteToolCallingHandler
from app.models import OllamaInference, OllamaToolCallResult


def test_tool_call_retrieves_each_requested_historic_site_before_completion() -> None:
    ollama_client = Mock()
    retrieval_client = Mock()
    retrieval_client.tool_definitions = AsyncMock(return_value=[{"type": "function"}])
    ollama_client.start_tool_call_generation = AsyncMock(
        return_value=OllamaToolCallResult(
            inference=OllamaInference(answer="", thinking=""),
            messages=({"role": "user", "content": "Question"}, {"role": "assistant"}),
            tool_calls=(
                {
                    "function": {
                        "name": "get_historic_site_facts",
                        "arguments": {"internal_site_name": "blue_historic_site_three"},
                    }
                },
                {
                    "function": {
                        "name": "get_historic_site_facts",
                        "arguments": {"internal_site_name": "gold_historic_site_two"},
                    }
                },
            ),
        )
    )
    retrieval_client.retrieve = AsyncMock(
        side_effect=["Founder's Square facts", "Bright Mill facts"]
    )
    completed_inference = OllamaInference(answer="Route and facts", thinking="Reasoning")
    ollama_client.generate_after_tool_results = AsyncMock(
        return_value=completed_inference
    )

    inference = asyncio.run(
        HistoricSiteToolCallingHandler(ollama_client, retrieval_client).generate(
            question="Question",
            inference_seed=42,
            system_prompt="Prompt",
        )
    )

    assert inference == completed_inference
    assert retrieval_client.retrieve.await_args_list[0].args == ("blue_historic_site_three",)
    assert retrieval_client.retrieve.await_args_list[1].args == ("gold_historic_site_two",)
    messages = ollama_client.generate_after_tool_results.await_args.args[0]
    assert messages[-2]["content"] == "Founder's Square facts"
    assert messages[-1]["content"] == "Bright Mill facts"


def test_generation_without_a_tool_call_returns_the_initial_inference() -> None:
    ollama_client = Mock()
    retrieval_client = Mock()
    retrieval_client.tool_definitions = AsyncMock(return_value=[{"type": "function"}])
    initial_inference = OllamaInference(answer="Normal answer", thinking="Reasoning")
    ollama_client.start_tool_call_generation = AsyncMock(
        return_value=OllamaToolCallResult(
            inference=initial_inference,
            messages=(),
            tool_calls=(),
        )
    )
    retrieval_client.retrieve = AsyncMock()
    ollama_client.generate_after_tool_results = AsyncMock()

    inference = asyncio.run(
        HistoricSiteToolCallingHandler(ollama_client, retrieval_client).generate(
            question="Question",
            inference_seed=42,
            system_prompt="Prompt",
        )
    )

    assert inference == initial_inference
    retrieval_client.retrieve.assert_not_awaited()
    ollama_client.generate_after_tool_results.assert_not_awaited()


def test_tool_calling_prompt_limits_station_names_to_the_route() -> None:
    prompt = HistoricSiteToolCallingHandler._tool_calling_prompt("Base prompt")

    assert "Mention stations only while describing the subway route" in prompt
    assert "Do not call it for a station-only route" in prompt
