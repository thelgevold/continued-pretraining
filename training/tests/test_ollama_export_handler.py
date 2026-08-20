from unittest.mock import Mock

from model_export.ollama_export_handler import OllamaExportHandler


def test_generated_modelfile_has_valid_assistant_response_block() -> None:
    handler = OllamaExportHandler(Mock())

    modelfile = "\n".join(handler._create_modelfile_lines("model.Q4_K_M.gguf"))

    assert "FROM ./model.Q4_K_M.gguf" in modelfile
    assert "{{ end }}{{ .Response }}" not in modelfile
    assert "{{ .Response }}{{ if .Response }}<|im_end|>{{ end }}" in modelfile
