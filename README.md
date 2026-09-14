Blog posts:

https://www.teachmecoolstuff.com/viewarticle/teaching-a-local-llm-a-new-domain

https://www.teachmecoolstuff.com/viewarticle/comparing-rag-and-continued-pretraining-of-llms

# Awesomeville city training

`city_training` is the sole supported experiment. Its locked continued-
pretraining corpus is [city_lines.jsonl](city_training/data/city_lines.jsonl).
No corpus-generation workflow is part of the supported project flow.

## Train and evaluate

Build the training image once to install Qwen 3.5 support:

```powershell
docker compose build training
```

Then train, export, import, and evaluate the Qwen 3.5 4B Base model:

```powershell
.\scripts\run-city-line-training-with-eval.ps1 -BaseModel "Qwen/Qwen3.5-4B-Base"
```

This trains the City model from the locked corpus, exports it to Ollama, and
runs all reasoning cases in `city_training/eval`.

## Evaluate an existing City model

```powershell
.\scripts\run-pytest-reasoning-tests.ps1 `
  -ModelName "awesomeville-city-lines-qwen3.5-4b-q4_k_m" `
  -ExperimentLabel "city-lines" `
  -CasesPath "/app/city_training/eval"
```

Evaluation reports are written to `eval/reports/`.
