from pathlib import Path
from typing import Literal

from fastmcp import FastMCP

from rag.app.historic_site_index import HistoricSiteIndex


historic_site_index = HistoricSiteIndex(Path("/app/rag/documents"))
mcp = FastMCP("Awesomeville Historic Site Retrieval")


@mcp.tool
def get_historic_site_facts(
    internal_site_name: Literal[
        "blue_historic_site_three",
        "gold_historic_site_two",
        "green_historic_site_two_a",
        "green_historic_site_two_b",
    ],
) -> str:
    """Retrieve facts for one key: blue_historic_site_three, gold_historic_site_two, green_historic_site_two_a, or green_historic_site_two_b."""
    return historic_site_index.retrieve(internal_site_name)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
