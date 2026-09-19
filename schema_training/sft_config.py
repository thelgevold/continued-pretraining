import os
from pathlib import Path


class OllamaConfig:
    def __init__(self) -> None:
        self.export_directory_name = "ollama"
        self.gguf_quantization_method = "q4_k_m"


class SchemaSftConfig:
    def __init__(self) -> None:
        self.base_model_name = self._require("SCHEMA_SFT_BASE_MODEL")
        self.corpus_path = Path(self._require("SCHEMA_SFT_CORPUS_PATH"))
        self.output_dir = Path(self._require("SCHEMA_SFT_OUTPUT_DIR"))
        self.output_directory_name = self._require(
            "SCHEMA_SFT_OUTPUT_DIRECTORY_NAME"
        )
        self.llama_cpp_path = Path(self._require("UNSLOTH_LLAMA_CPP_PATH"))
        self.num_train_epochs = 1
        self.learning_rate = 2e-4
        self.batch_size = 1
        self.gradient_accumulation_steps = 1
        self.lora_rank = 16
        self.lora_alpha = 16
        self.lora_dropout = 0
        self.max_seq_length = 2048
        self.random_state = 3407
        self.ollama = OllamaConfig()

    @staticmethod
    def _require(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value
