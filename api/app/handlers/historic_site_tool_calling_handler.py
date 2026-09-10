import asyncio

from app.clients.historic_site_retrieval_client import HistoricSiteRetrievalClient
from app.clients.historic_site_ollama_client import HistoricSiteOllamaClient
from app.models import OllamaInference
from fastmcp.exceptions import ToolError


class HistoricSiteToolCallingHandler:
    def __init__(
        self,
        ollama_client: HistoricSiteOllamaClient,
        retrieval_client: HistoricSiteRetrievalClient,
    ) -> None:
        self._ollama_client = ollama_client
        self._retrieval_client = retrieval_client
        self._tools: list[dict[str, object]] | None = None

    async def generate(
        self,
        question: str,
        inference_seed: int,
        system_prompt: str,
    ) -> OllamaInference:
        tools = await self._tool_definitions()
        result = await self._ollama_client.start_tool_call_generation(
            question,
            inference_seed,
            self._tool_calling_prompt(system_prompt),
            tools,
        )
        if not result.tool_calls:
            return result.inference
        tool_messages = await self._tool_messages(result.tool_calls)
        return await self._ollama_client.generate_after_tool_results(
            (*result.messages, *tool_messages),
            inference_seed,
        )

    async def _tool_definitions(self) -> list[dict[str, object]]:
        if self._tools is None:
            self._tools = await self._retrieval_client.tool_definitions()
        return self._tools

    async def _tool_messages(
        self,
        tool_calls: tuple[dict[str, object], ...],
    ) -> tuple[dict[str, object], ...]:
        return tuple(
            await asyncio.gather(
                *(self._tool_message(tool_call) for tool_call in tool_calls)
            )
        )

    async def _tool_message(self, tool_call: dict[str, object]) -> dict[str, object]:
        function = tool_call["function"]
        if not isinstance(function, dict):
            raise RuntimeError("Ollama tool call must contain a function.")
        arguments = function["arguments"]
        if not isinstance(arguments, dict):
            raise RuntimeError("Ollama tool call must contain function arguments.")
        internal_name = str(arguments["internal_site_name"])
        return {
            "role": "tool",
            "tool_name": str(function["name"]),
            "content": await self._tool_content(internal_name),
        }

    async def _tool_content(self, internal_name: str) -> str:
        try:
            return await self._retrieval_client.retrieve(internal_name)
        except ToolError:
            return "Historic-site retrieval was unavailable. Continue without it."

    @staticmethod
    def _tool_calling_prompt(system_prompt: str) -> str:
        return (
            f"{system_prompt}\n\n"
            "You already know the complete Awesomeville subway network from your "
            "trained city data. Answer every station-to-station route directly; "
            "never say that a routing tool is unavailable, request a routing tool, "
            "or present a route as an assumption. The available historic-site tool "
            "is optional enrichment only. Do not call it for a station-only route. "
            "For historic-site retrieval, the public-name keys are: Founder's Square "
            "= blue_historic_site_three; Bright Mill Museum = gold_historic_site_two; "
            "Museum of Greatness History = green_historic_site_two_a; Heritage Theater "
            "= green_historic_site_two_b. "
            "Never invent a tool name, output raw tool markup, or describe your "
            "planning instead of giving the final answer. "
            "Call it once for each requested internal historic-site name only when "
            "the user combines directions between historic sites with a request for "
            "historic-site facts. Use retrieved content only for those facts. "
            "Mention stations only while describing the subway route; do not state "
            "or infer a station location in a historic-site description."
        )
