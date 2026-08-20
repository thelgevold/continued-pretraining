from dataclasses import dataclass


@dataclass(frozen=True)
class OllamaInference:
    answer: str
    thinking: str
