import json
from pathlib import Path

from training.config import TrainingConfig
from model_export.gguf_conversion_handler import GgufConversionHandler
from model_export.hugging_face_merge_handler import (
    HuggingFaceMergeHandler,
)


class OllamaExportHandler:
    def __init__(self, config: TrainingConfig) -> None:
        self._config = config
        self._hugging_face_merge_handler = HuggingFaceMergeHandler(config)
        self._gguf_conversion_handler = GgufConversionHandler(config)

    def export(self, adapter_dir: Path) -> dict:
        export_dir = self._get_export_dir()
        export_dir.mkdir(parents=True, exist_ok=True)
        merged_model_dir = export_dir / "model"
        self._hugging_face_merge_handler.merge_adapter(
            adapter_dir,
            merged_model_dir,
        )
        return self.export_merged_model(merged_model_dir)

    def export_merged_model(self, merged_model_dir: Path) -> dict:
        export_dir = self._get_export_dir()
        return self.export_merged_model_to(merged_model_dir, export_dir)

    def export_merged_model_to(
        self,
        merged_model_dir: Path,
        export_dir: Path,
    ) -> dict:
        export_dir.mkdir(parents=True, exist_ok=True)
        export_result = self._gguf_conversion_handler.convert(
            merged_model_dir,
            export_dir / "model_gguf",
        )
        self._update_modelfile(export_result)
        self._save_export_result(export_dir, export_result)
        return export_result

    def _get_export_dir(self):
        return self._config.output_dir / self._config.ollama.export_directory_name

    def _update_modelfile(self, export_result: dict) -> None:
        modelfile_path = self._resolve_modelfile_path(export_result)
        gguf_path = Path(export_result["gguf_files"][0])
        modelfile_path.write_text(
            "\n".join(self._create_modelfile_lines(gguf_path.name)) + "\n",
            encoding="utf-8",
        )

    def _resolve_modelfile_path(self, export_result: dict) -> Path:
        modelfile_location = export_result.get("modelfile_location")
        if modelfile_location:
            return Path(str(modelfile_location))
        return Path(str(export_result["gguf_directory"])) / "Modelfile"

    def _create_modelfile_lines(self, gguf_file_name: str) -> list[str]:
        return [
            f"FROM ./{gguf_file_name}",
            'TEMPLATE """{{- if .System }}<|im_start|>system',
            "{{ .System }}<|im_end|>",
            "{{ end }}{{ if .Prompt }}<|im_start|>user",
            "{{ .Prompt }}<|im_end|>",
            "{{ end }}<|im_start|>assistant",
            '{{ .Response }}{{ if .Response }}<|im_end|>{{ end }}"""',
            'PARAMETER stop "<|im_end|>"',
            'PARAMETER stop "<|im_start|>"',
            "PARAMETER temperature 0",
            "PARAMETER repeat_penalty 1.1",
        ]

    def _save_export_result(self, export_dir, export_result: dict) -> None:
        export_result_path = export_dir / "export-result.json"
        export_result_path.write_text(
            json.dumps(export_result, indent=2),
            encoding="utf-8",
        )
