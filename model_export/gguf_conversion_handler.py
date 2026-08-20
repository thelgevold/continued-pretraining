import subprocess
from pathlib import Path

from training.config import TrainingConfig


class GgufConversionHandler:
    def __init__(self, config: TrainingConfig) -> None:
        self._config = config

    def convert(self, model_dir: Path, output_dir: Path) -> dict[str, str | list[str]]:
        output_dir.mkdir(parents=True, exist_ok=True)
        self._delete_existing_gguf_files(output_dir)
        full_precision_path = output_dir / "model.f16.gguf"
        quantized_path = output_dir / self._create_quantized_file_name()
        self._convert_to_full_precision(model_dir, full_precision_path)
        self._quantize(full_precision_path, quantized_path)
        full_precision_path.unlink()
        return {
            "gguf_directory": str(output_dir),
            "gguf_files": [str(quantized_path)],
        }

    def _delete_existing_gguf_files(self, output_dir: Path) -> None:
        for gguf_path in output_dir.glob("*.gguf"):
            gguf_path.unlink()

    def _create_quantized_file_name(self) -> str:
        quantization_name = self._config.ollama.gguf_quantization_method.upper()
        return f"model.{quantization_name}.gguf"

    def _convert_to_full_precision(
        self,
        model_dir: Path,
        full_precision_path: Path,
    ) -> None:
        command = [
            "python",
            str(self._config.llama_cpp_path / "convert_hf_to_gguf.py"),
            str(model_dir),
            "--outfile",
            str(full_precision_path),
            "--outtype",
            "f16",
        ]
        subprocess.run(command, check=True)

    def _quantize(self, full_precision_path: Path, quantized_path: Path) -> None:
        command = [
            str(self._config.llama_cpp_path / "llama-quantize"),
            str(full_precision_path),
            str(quantized_path),
            self._config.ollama.gguf_quantization_method.upper(),
        ]
        subprocess.run(command, check=True)
