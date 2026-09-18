from schema_training.handlers.schema_sft_training_handler import SchemaSftTrainingHandler
from schema_training.handlers.schema_training_memory_cleanup_handler import (
    SchemaTrainingMemoryCleanupHandler,
)
from schema_training.sft_config import SchemaSftConfig


def main() -> None:
    SchemaSftTrainingHandler(
        config=SchemaSftConfig(),
        memory_cleanup_handler=SchemaTrainingMemoryCleanupHandler(),
    ).run()


if __name__ == "__main__":
    main()
