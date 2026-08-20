# Awesomeville city training

`city_training` is the sole supported experiment. Its locked continued-
pretraining corpus is [city_lines.jsonl](city_training/data/city_lines.jsonl).
No corpus-generation workflow is part of the supported project flow.

## Train and evaluate

```powershell
.\scripts\run-city-line-training-with-eval.ps1 -BaseModel "Qwen/Qwen3-4B"
```

This trains the City model from the locked corpus, exports it to Ollama, and
runs all reasoning cases in `city_training/eval`.

## Evaluate an existing City model

```powershell
.\scripts\run-pytest-reasoning-tests.ps1 `
  -ModelName "awesomeville-city-lines-qwen3-4b-q4_k_m" `
  -ExperimentLabel "city-lines" `
  -CasesPath "/app/city_training/eval"
```

Evaluation reports are written to `eval/reports/`.
