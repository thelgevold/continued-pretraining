from city_training.pre_training_config import PreTrainingConfig


class CityTrainingConfig(PreTrainingConfig):
    """Training defaults for the foundational city experiment."""

    def __init__(self) -> None:
        super().__init__()
        self.output_directory_name = "city_training"
        self.learning_rate = 2e-4
        self.batch_size = 1
        self.gradient_accumulation_steps = 1
