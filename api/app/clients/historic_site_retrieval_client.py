from fastmcp import Client


class HistoricSiteRetrievalClient:
    def __init__(self, server_url: str) -> None:
        self._server_url = server_url

    async def retrieve(self, internal_site_name: str) -> str:
        async with Client(self._server_url) as client:
            result = await client.call_tool(
                "get_historic_site_facts",
                {"internal_site_name": internal_site_name},
            )
        return str(result.data)

    async def tool_definitions(self) -> list[dict[str, object]]:
        async with Client(self._server_url) as client:
            tools = await client.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools
        ]
