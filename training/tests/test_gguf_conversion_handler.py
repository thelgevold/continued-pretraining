from pathlib import Path
from unittest.mock import Mock, patch

from model_export.gguf_conversion_handler import GgufConversionHandler


def test_conversion_excludes_mtp_head(tmp_path: Path) -> None:
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    config = Mock()
    config.llama_cpp_path = tmp_path / "llama.cpp"
    handler = GgufConversionHandler(config)

    with patch("model_export.gguf_conversion_handler.subprocess.run") as run:
        handler._convert_to_full_precision(model_dir, tmp_path / "model.f16.gguf")

    assert run.call_args.args[0][-1] == "--no-mtp"
