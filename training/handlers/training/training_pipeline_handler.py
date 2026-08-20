from training.config import TrainingConfig
from training.handlers.training.corpus_training_handler import (
    CorpusTrainingHandler,
)
from training.handlers.training.training_memory_cleanup_handler import (
    TrainingMemoryCleanupHandler,
)
from model_export.ollama_export_handler import OllamaExportHandler


class TrainingPipelineHandler:
    def __init__(
        self,
        config: TrainingConfig,
        corpus_training_handler: CorpusTrainingHandler,
        ollama_export_handler: OllamaExportHandler,
        training_memory_cleanup_handler: TrainingMemoryCleanupHandler,
    ) -> None:
        self._config = config
        self._corpus_training_handler = corpus_training_handler
        self._ollama_export_handler = ollama_export_handler
        self._training_memory_cleanup_handler = training_memory_cleanup_handler

    def run(self) -> None:
        if self._config.pipeline_mode == "city_training":
            adapter_dir = self._corpus_training_handler.run()
            self._training_memory_cleanup_handler.cleanup()
            self._ollama_export_handler.export(adapter_dir)
            return
        raise RuntimeError("TRAINING_PIPELINE_MODE must be 'city_training'.")
