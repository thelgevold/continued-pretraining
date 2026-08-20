import os
from pathlib import Path

from city_training.city_training_config import CityTrainingConfig

class OllamaConfig:
    def __init__(self) -> None:
        self.export_directory_name = "ollama"
        self.gguf_quantization_method = "q4_k_m"


class TrainingConfig:
    def __init__(self) -> None:
        self.base_model_name = self._require("TRAINING_BASE_MODEL")
        self.pipeline_mode = self._require("TRAINING_PIPELINE_MODE")
        self.training_corpus_path = Path(
            self._require("TRAINING_CORPUS_PATH")
        )
        self.output_dir = Path(self._require("TRAINING_OUTPUT_DIR"))
        self.llama_cpp_path = Path(self._require("UNSLOTH_LLAMA_CPP_PATH"))
        self.training_parameters = self._training_parameters()
        self.ollama = OllamaConfig()
        self.random_state = 3407
        self.max_seq_length = 2048
        self.gradient_accumulation_steps = 4
        self.logging_steps = 1
        self.dataset_num_proc = 1

    def _require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

    def _training_parameters(self) -> CityTrainingConfig:
        if self.pipeline_mode == "city_training":
            return CityTrainingConfig()
        raise RuntimeError("TRAINING_PIPELINE_MODE must be 'city_training'.")


CONFIG = TrainingConfig()
