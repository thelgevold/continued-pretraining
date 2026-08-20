class PreTrainingConfig:
    """Base continued-pretraining parameters for the City experiment."""

    def __init__(self) -> None:
        self.eval_percentage = 0
        self.random_state = 3407
        self.max_seq_length = 1024
        self.batch_size = 1
        self.evaluation_batch_size = 1
        self.gradient_accumulation_steps = 8
        self.learning_rate = 5e-5
        self.embedding_learning_rate = 5e-6
        self.num_train_epochs = 3
        self.warmup_ratio = 0.03
        self.weight_decay = 0.01
        self.lr_scheduler_type = "cosine"
        self.lora_rank = 32
        self.lora_alpha = 32
        self.lora_dropout = 0
        self.lora_target_modules = [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
