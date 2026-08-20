from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from training.handlers.training.training_pipeline_handler import (
    TrainingPipelineHandler,
)


def test_city_training_runs_and_exports() -> None:
    config = SimpleNamespace(pipeline_mode="city_training")
    corpus_training_handler = Mock()
    corpus_training_handler.run.return_value = Path("city-training-adapter")
    export_handler = Mock()
    cleanup_handler = Mock()
    pipeline = TrainingPipelineHandler(
        config=config,
        corpus_training_handler=corpus_training_handler,
        ollama_export_handler=export_handler,
        training_memory_cleanup_handler=cleanup_handler,
    )

    pipeline.run()

    corpus_training_handler.run.assert_called_once_with()
    cleanup_handler.cleanup.assert_called_once_with()
    export_handler.export.assert_called_once_with(Path("city-training-adapter"))
