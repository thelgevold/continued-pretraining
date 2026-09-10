import os


class AppConfig:
    def __init__(self) -> None:
        self.ollama_base_url = self._require("OLLAMA_BASE_URL")
        self.ollama_model_name = self._require("OLLAMA_MODEL_NAME")
        self.historic_site_mcp_url = self._require("HISTORIC_SITE_MCP_URL")

    def _require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value
