from training.config import TrainingConfig


def test_city_training_uses_its_own_output_directory(monkeypatch) -> None:
    values = {
        "TRAINING_BASE_MODEL": "Qwen/Qwen3-4B",
        "TRAINING_PIPELINE_MODE": "city_training",
        "TRAINING_CORPUS_PATH": "city_training/data/blue_line.jsonl",
        "TRAINING_OUTPUT_DIR": "outputs",
        "UNSLOTH_LLAMA_CPP_PATH": "llama.cpp",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    config = TrainingConfig()

    assert config.training_parameters.output_directory_name == "city_training"
    assert config.training_parameters.num_train_epochs == 3
    assert config.training_parameters.batch_size == 1
    assert config.training_parameters.batch_size == 1
