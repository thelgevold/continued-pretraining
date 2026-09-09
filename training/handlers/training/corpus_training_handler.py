import json
import math
from pathlib import Path

from training.config import TrainingConfig
from training.handlers.data.corpus_data_handler import (
    CorpusDataHandler,
)
from training.handlers.data.document_boundary_handler import (
    DocumentBoundaryHandler,
)
from training.handlers.data.data_split_handler import DataSplitHandler
from model_export.hugging_face_merge_handler import (
    HuggingFaceMergeHandler,
)
from training.handlers.training.training_memory_cleanup_handler import (
    TrainingMemoryCleanupHandler,
)


class CorpusTrainingHandler:
    def __init__(
        self,
        config: TrainingConfig,
        data_handler: CorpusDataHandler,
        document_boundary_handler: DocumentBoundaryHandler,
        data_split_handler: DataSplitHandler,
        hugging_face_merge_handler: HuggingFaceMergeHandler,
        training_memory_cleanup_handler: TrainingMemoryCleanupHandler,
    ) -> None:
        self._config = config
        self._data_handler = data_handler
        self._document_boundary_handler = document_boundary_handler
        self._data_split_handler = data_split_handler
        self._hugging_face_merge_handler = hugging_face_merge_handler
        self._training_memory_cleanup_handler = training_memory_cleanup_handler

    def run(self) -> Path:
        records = self._data_handler.load_records()
        model, tokenizer = self._load_model()
        records = self._document_boundary_handler.append_end_of_document_token(
            records,
            tokenizer.eos_token,
        )
        train_records, eval_records = self._data_split_handler.split_records(records)
        phase_output_dir = self._get_phase_output_dir()
        self._save_split(phase_output_dir, "train", train_records)
        self._save_split(phase_output_dir, "eval", eval_records)
        trainer = self._create_trainer(model, tokenizer, train_records, eval_records)
        train_result = trainer.train()
        eval_metrics = trainer.evaluate() if eval_records else {}
        epoch_eval_metrics = self._epoch_eval_metrics(trainer)
        adapter_dir = self._save_adapter(phase_output_dir, trainer, tokenizer)
        train_metrics = dict(train_result.metrics)
        del train_result, trainer, model, tokenizer
        self._training_memory_cleanup_handler.cleanup()
        merged_model_dir = phase_output_dir / "merged_model"
        self._hugging_face_merge_handler.merge_adapter(adapter_dir, merged_model_dir)
        self._save_metrics(
            phase_output_dir=phase_output_dir,
            adapter_dir=adapter_dir,
            train_count=len(train_records),
            eval_count=len(eval_records),
            train_metrics=train_metrics,
            eval_metrics=eval_metrics,
            epoch_eval_metrics=epoch_eval_metrics,
            merged_model_dir=merged_model_dir,
        )
        return adapter_dir

    def _get_phase_output_dir(self) -> Path:
        return self._config.output_dir / self._config.training_parameters.output_directory_name

    def _load_model(self):
        from unsloth import FastLanguageModel

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=self._config.base_model_name,
            max_seq_length=self._config.training_parameters.max_seq_length,
            dtype=None,
            load_in_4bit=True,
            text_only=True,
            use_gradient_checkpointing=True,
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=self._config.training_parameters.lora_rank,
            target_modules=self._config.training_parameters.lora_target_modules,
            lora_alpha=self._config.training_parameters.lora_alpha,
            lora_dropout=self._config.training_parameters.lora_dropout,
            bias="none",
            use_gradient_checkpointing=True,
            random_state=self._config.random_state,
        )
        return model, tokenizer

    def _create_trainer(
        self,
        model,
        tokenizer,
        train_records: list[dict[str, str]],
        eval_records: list[dict[str, str]],
    ):
        import torch
        from datasets import Dataset
        from unsloth import UnslothTrainer, UnslothTrainingArguments

        training_args = UnslothTrainingArguments(
            output_dir=str(self._get_phase_output_dir() / "checkpoints"),
            do_train=True,
            do_eval=bool(eval_records),
            per_device_train_batch_size=self._config.training_parameters.batch_size,
            per_device_eval_batch_size=(
                self._config.training_parameters.evaluation_batch_size
            ),
            gradient_accumulation_steps=(
                self._config.training_parameters.gradient_accumulation_steps
            ),
            learning_rate=self._config.training_parameters.learning_rate,
            embedding_learning_rate=(
                self._config.training_parameters.embedding_learning_rate
            ),
            num_train_epochs=self._config.training_parameters.num_train_epochs,
            warmup_steps=self._get_warmup_steps(train_records),
            weight_decay=self._config.training_parameters.weight_decay,
            lr_scheduler_type=self._config.training_parameters.lr_scheduler_type,
            logging_steps=self._config.logging_steps,
            save_strategy="epoch",
            eval_strategy="epoch" if eval_records else "no",
            report_to="none",
            dataset_text_field="text",
            max_length=self._config.training_parameters.max_seq_length,
            dataset_num_proc=self._config.dataset_num_proc,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
    
        )
        trainer_kwargs = {
            "model": model,
            "args": training_args,
            "train_dataset": Dataset.from_list(train_records),
            "processing_class": tokenizer,
        }
        if eval_records:
            trainer_kwargs["eval_dataset"] = Dataset.from_list(eval_records)
        return UnslothTrainer(**trainer_kwargs)

    def _get_warmup_steps(self, train_records: list[dict[str, str]]) -> int:
        parameters = self._config.training_parameters
        batches_per_epoch = math.ceil(
            len(train_records) / parameters.batch_size
        )
        optimizer_steps_per_epoch = math.ceil(
            batches_per_epoch / parameters.gradient_accumulation_steps
        )
        total_steps = optimizer_steps_per_epoch * parameters.num_train_epochs
        return int(total_steps * parameters.warmup_ratio)

    def _save_adapter(self, phase_output_dir: Path, trainer, tokenizer) -> Path:
        adapter_dir = phase_output_dir / "adapter"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        trainer.save_model(str(adapter_dir))
        tokenizer.save_pretrained(str(adapter_dir))
        return adapter_dir

    def _save_split(
        self,
        phase_output_dir: Path,
        split_name: str,
        records: list[dict[str, str]],
    ) -> None:
        split_dir = phase_output_dir / "splits"
        split_dir.mkdir(parents=True, exist_ok=True)
        split_path = split_dir / f"{split_name}.json"
        split_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def _save_metrics(
        self,
        phase_output_dir: Path,
        adapter_dir: Path,
        train_count: int,
        eval_count: int,
        train_metrics: dict[str, object],
        eval_metrics: dict[str, object],
        epoch_eval_metrics: list[dict[str, float]],
        merged_model_dir: Path,
    ) -> None:
        report_dir = phase_output_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "phase": self._config.training_parameters.output_directory_name,
            "adapter_directory": str(adapter_dir),
            "train_record_count": train_count,
            "eval_record_count": eval_count,
            "train_metrics": train_metrics,
            "eval_metrics": eval_metrics,
            "epoch_eval_metrics": epoch_eval_metrics,
            "merged_model_directory": str(merged_model_dir),
        }
        report_path = report_dir / "metrics.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def _epoch_eval_metrics(self, trainer) -> list[dict[str, float]]:
        metrics_by_epoch = {
            float(entry["epoch"]): {
                "epoch": float(entry["epoch"]),
                "eval_loss": float(entry["eval_loss"]),
            }
            for entry in trainer.state.log_history
            if "epoch" in entry and "eval_loss" in entry
        }
        return [metrics_by_epoch[epoch] for epoch in sorted(metrics_by_epoch)]
