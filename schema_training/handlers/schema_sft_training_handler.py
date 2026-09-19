import json
from pathlib import Path

from model_export.hugging_face_merge_handler import HuggingFaceMergeHandler
from model_export.ollama_export_handler import OllamaExportHandler
from schema_training.handlers.schema_training_memory_cleanup_handler import (
    SchemaTrainingMemoryCleanupHandler,
)
from schema_training.prompts.schema_instruction import SCHEMA_INSTRUCTION
from schema_training.sft_config import SchemaSftConfig


class SchemaSftTrainingHandler:
    def __init__(
        self,
        config: SchemaSftConfig,
        memory_cleanup_handler: SchemaTrainingMemoryCleanupHandler,
    ) -> None:
        self._config = config
        self._memory_cleanup_handler = memory_cleanup_handler
        self._merge_handler = HuggingFaceMergeHandler(config)
        self._export_handler = OllamaExportHandler(config)

    def run(self) -> None:
        records = self._load_records()
        model, tokenizer = self._load_model()
        trainer = self._create_trainer(model, tokenizer, records)
        trainer.train()
        adapter_dir = self._save_adapter(trainer, tokenizer)
        del trainer, model, tokenizer
        self._memory_cleanup_handler.cleanup()
        merged_model_dir = self._phase_output_dir() / "merged_model"
        self._merge_handler.merge_adapter(adapter_dir, merged_model_dir)
        self._export_handler.export_merged_model(merged_model_dir)

    def _load_records(self) -> list[dict[str, str]]:
        records = [
            json.loads(line)
            for line in self._config.corpus_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self._validate_records(records)
        return [{"text": self._format_record(record)} for record in records]

    def _validate_records(self, records: list[dict[str, object]]) -> None:
        if len(records) != 310:
            raise RuntimeError("Schema SFT training requires exactly 310 records.")
        for transfer_count in (1, 2, 3):
            count = sum(
                record["transfer_count"] == transfer_count
                and not record.get("is_historic_site_reinforcement", False)
                for record in records
            )
            if count != 100:
                raise RuntimeError(
                    f"Schema SFT training requires 100 {transfer_count}-transfer records."
                )

    def _format_record(self, record: dict[str, object]) -> str:
        return (
            "<|im_start|>user\n"
            "Below is an instruction that describes a task. Write a response that "
            "appropriately completes the request.\n\n"
            f"### Instruction:\n{SCHEMA_INSTRUCTION}\n\n"
            f"### Input:\n{record['input']}\n\n"
            "### Response:\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
            f"{record['output']}<|im_end|>"
        )

    def _load_model(self):
        from unsloth import FastLanguageModel

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=self._config.base_model_name,
            max_seq_length=self._config.max_seq_length,
            dtype=None,
            load_in_4bit=True,
            text_only=True,
            use_gradient_checkpointing=True,
        )
        return (
            FastLanguageModel.get_peft_model(
                model,
                r=self._config.lora_rank,
                target_modules=[
                    "q_proj",
                    "k_proj",
                    "v_proj",
                    "o_proj",
                    "gate_proj",
                    "up_proj",
                    "down_proj",
                ],
                lora_alpha=self._config.lora_alpha,
                lora_dropout=self._config.lora_dropout,
                bias="none",
                use_gradient_checkpointing=True,
                random_state=self._config.random_state,
            ),
            tokenizer,
        )

    def _create_trainer(self, model, tokenizer, records: list[dict[str, str]]):
        import torch
        from datasets import Dataset
        from unsloth import UnslothTrainer, UnslothTrainingArguments
        from unsloth.chat_templates import train_on_responses_only

        trainer = UnslothTrainer(
            model=model,
            train_dataset=Dataset.from_list(records),
            processing_class=tokenizer,
            args=UnslothTrainingArguments(
                output_dir=str(self._phase_output_dir() / "checkpoints"),
                do_train=True,
                per_device_train_batch_size=self._config.batch_size,
                gradient_accumulation_steps=self._config.gradient_accumulation_steps,
                learning_rate=self._config.learning_rate,
                num_train_epochs=self._config.num_train_epochs,
                logging_steps=1,
                save_strategy="epoch",
                report_to="none",
                dataset_text_field="text",
                max_length=self._config.max_seq_length,
                dataset_num_proc=1,
                fp16=not torch.cuda.is_bf16_supported(),
                bf16=torch.cuda.is_bf16_supported(),
            ),
        )
        return train_on_responses_only(
            trainer,
            instruction_part="<|im_start|>user\n",
            response_part="<|im_start|>assistant\n",
        )

    def _phase_output_dir(self) -> Path:
        return self._config.output_dir / self._config.output_directory_name

    def _save_adapter(self, trainer, tokenizer) -> Path:
        adapter_dir = self._phase_output_dir() / "adapter"
        adapter_dir.mkdir(parents=True, exist_ok=True)
        trainer.save_model(str(adapter_dir))
        tokenizer.save_pretrained(adapter_dir)
        return adapter_dir
