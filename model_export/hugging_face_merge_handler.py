import json
import shutil
from pathlib import Path

from training.config import TrainingConfig


class HuggingFaceMergeHandler:
    def __init__(self, config: TrainingConfig) -> None:
        self._config = config

    def merge_adapter(self, adapter_dir: Path, output_dir: Path) -> None:
        tokenizer = self._load_tokenizer(adapter_dir)
        model = self._load_base_model(adapter_dir)
        merged_model = self._merge_adapter(model, adapter_dir)
        self._reset_output_dir(output_dir)
        merged_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        self._remove_quantization_metadata(output_dir)

    def _load_tokenizer(self, adapter_dir: Path):
        from transformers import AutoTokenizer

        return AutoTokenizer.from_pretrained(adapter_dir)

    def _load_base_model(self, adapter_dir: Path):
        import torch
        from transformers import AutoModelForCausalLM

        return AutoModelForCausalLM.from_pretrained(
            self._resolve_export_base_model_name(adapter_dir),
            dtype=torch.float16,
            low_cpu_mem_usage=True,
        )

    def _load_adapter_base_model_name(self, adapter_dir: Path) -> str:
        adapter_config_path = adapter_dir / "adapter_config.json"
        adapter_config = json.loads(adapter_config_path.read_text(encoding="utf-8"))
        return str(adapter_config["base_model_name_or_path"])

    def _resolve_export_base_model_name(self, adapter_dir: Path) -> str:
        adapter_base_model_name = self._load_adapter_base_model_name(adapter_dir)
        if self._is_quantized_base_model_name(adapter_base_model_name):
            return self._config.base_model_name
        return adapter_base_model_name

    def _is_quantized_base_model_name(self, model_name: str) -> bool:
        normalized_name = model_name.lower()
        return "bnb-4bit" in normalized_name or "unsloth/" in normalized_name

    def _reset_output_dir(self, output_dir: Path) -> None:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    def _remove_quantization_metadata(self, output_dir: Path) -> None:
        config_path = output_dir / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config.pop("quantization_config", None)
        config.pop("_load_in_4bit", None)
        config.pop("_load_in_8bit", None)
        config.pop("load_in_4bit", None)
        config.pop("load_in_8bit", None)
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def _merge_adapter(self, model, adapter_dir: Path):
        from peft import PeftModel

        peft_model = PeftModel.from_pretrained(
            model,
            adapter_dir,
            device_map={"": "cpu"},
            low_cpu_mem_usage=True,
        )
        return peft_model.merge_and_unload()
