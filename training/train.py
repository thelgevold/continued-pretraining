from training.config import CONFIG
from training.handlers import (
    CorpusDataHandler,
    DocumentBoundaryHandler,
    CorpusTrainingHandler,
    DataSplitHandler,
    HuggingFaceMergeHandler,
    OllamaExportHandler,
    TrainingMemoryCleanupHandler,
    TrainingPipelineHandler,
)


def main() -> None:
    corpus_data_handler = CorpusDataHandler(CONFIG)
    document_boundary_handler = DocumentBoundaryHandler()
    data_split_handler = DataSplitHandler(
        CONFIG.training_parameters.eval_percentage,
        CONFIG.training_parameters.random_state,
    )
    hugging_face_merge_handler = HuggingFaceMergeHandler(CONFIG)
    ollama_export_handler = OllamaExportHandler(CONFIG)
    training_memory_cleanup_handler = TrainingMemoryCleanupHandler()
    corpus_training_handler = CorpusTrainingHandler(
        config=CONFIG,
        data_handler=corpus_data_handler,
        document_boundary_handler=document_boundary_handler,
        data_split_handler=data_split_handler,
        hugging_face_merge_handler=hugging_face_merge_handler,
        training_memory_cleanup_handler=training_memory_cleanup_handler,
    )
    training_pipeline_handler = TrainingPipelineHandler(
        config=CONFIG,
        corpus_training_handler=corpus_training_handler,
        ollama_export_handler=ollama_export_handler,
        training_memory_cleanup_handler=training_memory_cleanup_handler,
    )
    training_pipeline_handler.run()


if __name__ == "__main__":
    main()
