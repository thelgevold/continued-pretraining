from dataclasses import dataclass

from app.models.ollama_inference import OllamaInference


@dataclass(frozen=True)
class OllamaToolCallResult:
    inference: OllamaInference
    messages: tuple[dict[str, object], ...]
    tool_calls: tuple[dict[str, object], ...]
